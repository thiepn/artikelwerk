import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import { loadEditorialReview, loadReplacementReview } from './load-bridge-review-ledgers.mjs';

const scriptsDir = dirname(fileURLToPath(import.meta.url));
const rootDir = dirname(scriptsDir);
const generatedDir = join(rootDir, '.generated-v23');
const read = (...parts) => readFile(join(rootDir, ...parts), 'utf8');
const fail = (message) => { throw new Error(message); };

const corpusSource = await read('bridge-corpus.js');
const translationSource = await read('bridge-translations.js');
const sourceProvenance = JSON.parse(await read('content', 'bridge-provenance.json'));
const replacementLedger = await loadReplacementReview(rootDir);
const editorialLedger = await loadEditorialReview(rootDir);

const corpusContext = { window: {} };
vm.runInNewContext(corpusSource, corpusContext, { filename: 'bridge-corpus.js' });
const sourceRows = corpusContext.window.ARTIKELWERK_BRIDGE_CORPUS;
const sourceMeta = corpusContext.window.ARTIKELWERK_BRIDGE_CORPUS_META || {};
if (!Array.isArray(sourceRows) || sourceRows.length !== 1000) fail('Expected the immutable V2-2 Normal corpus to contain 1,000 rows.');

const translationContext = {
  window: {
    ARTIKELWERK_TRANSLATIONS: Object.freeze({}),
    ARTIKELWERK_TRANSLATION_PROVENANCE: Object.freeze({}),
  },
};
vm.runInNewContext(translationSource, translationContext, { filename: 'bridge-translations.js' });
const sourceTranslations = translationContext.window.ARTIKELWERK_TRANSLATIONS || {};
const sourceTranslationProvenance = translationContext.window.ARTIKELWERK_TRANSLATION_PROVENANCE || {};
const sourceContentCertification = translationContext.window.ARTIKELWERK_BRIDGE_CONTENT_CERTIFICATION || {};

if (replacementLedger.phase !== 'V2-3' || replacementLedger.status !== 'in-progress') fail('Invalid V2-3 replacement ledger metadata.');
if (editorialLedger.phase !== 'V2-3' || editorialLedger.status !== 'in-progress') fail('Invalid V2-3 editorial ledger metadata.');

const replacements = replacementLedger.entries || {};
const replacementIds = new Set(Object.keys(replacements));
const editorialEntries = editorialLedger.entries || {};
const retainedReviews = Object.fromEntries(Object.entries(editorialEntries).filter(([, review]) => review?.decision === 'retain'));
const retainedReviewIds = new Set(Object.keys(retainedReviews));

function retainedComponents(review) {
  return {
    gloss: review?.glossReview || 'pending',
    example: review?.exampleReview || 'pending',
    rule: review?.ruleReview || 'pending',
    level: review?.levelReview || 'pending',
  };
}

function retainedReleaseReviewed(review) {
  if (review?.reviewStatus !== 'release-reviewed') return false;
  if (!Array.isArray(review.reviewedSenseIds) || review.reviewedSenseIds.length < 1) return false;
  return Object.values(retainedComponents(review)).every((status) => status === 'editorial');
}

function replacementReleaseReviewed(review) {
  if (!review?.successor || !Array.isArray(review.reviewedSenseIds) || review.reviewedSenseIds.length < 1) return false;
  if (review.b1LowerBoundCheck !== 'no-exact-match') return false;
  return ['gloss', 'example', 'rule', 'level'].every((component) => review.componentReview?.[component] === 'editorial');
}

const replacementCount = replacementIds.size;
const replacementDecisionBatchCount = editorialLedger.replacementDecisionBatches?.length || 0;
const replacementReviewBatchCount = replacementLedger.replacementReviewBatches?.length || 0;
const retainedReviewCount = retainedReviewIds.size;
const retainedBatchCount = editorialLedger.retainedBatches?.length || 0;
const releaseReviewedCount = Object.values(replacements).filter(replacementReleaseReviewed).length
  + Object.values(retainedReviews).filter(retainedReleaseReviewed).length;
const releaseReviewed = releaseReviewedCount === sourceRows.length;

const seenOldIds = new Set();
const seenRetainedIds = new Set();
const effectiveRows = sourceRows.map((row) => {
  const oldId = row[0];
  const replacement = replacements[oldId];
  if (replacement) {
    seenOldIds.add(oldId);
    const s = replacement.successor;
    if (!s) fail(`Missing reviewed successor for ${oldId}.`);
    if (s.level !== row[3] || s.cefrEstimate !== row[10]?.cefrEstimate) {
      fail(`Successor contract mismatch for ${oldId}: ${row[3]}/${row[10]?.cefrEstimate} -> ${s.level}/${s.cefrEstimate}`);
    }
    return [
      s.id,
      s.noun,
      s.article,
      s.level,
      replacement.rule,
      replacement.example,
      s.group,
      row[7],
      row[8],
      row[9],
      {
        cefrEstimate: s.cefrEstimate,
        frequencyRank: s.frequencyRank,
        frequencyCount: s.frequencyCount,
        genderCorroborated: true,
        editorialPhase: 'V2-3',
        editorialDecision: 'replace',
        replaces: oldId,
        reviewedSenseIds: replacement.reviewedSenseIds,
        componentReview: replacement.componentReview,
      },
    ];
  }

  const review = retainedReviews[oldId];
  if (!review) return row;
  seenRetainedIds.add(oldId);
  return [
    row[0],
    row[1],
    row[2],
    row[3],
    review.rule ?? row[4],
    review.example ?? row[5],
    row[6],
    row[7],
    row[8],
    row[9],
    {
      ...(row[10] || {}),
      editorialPhase: 'V2-3',
      editorialDecision: 'retain',
      reviewedSenseIds: review.reviewedSenseIds || [],
      componentReview: retainedComponents(review),
      reviewStatus: review.reviewStatus || 'partial-editorial',
    },
  ];
});

for (const id of replacementIds) if (!seenOldIds.has(id)) fail(`Replacement slot not found in source corpus: ${id}`);
for (const id of retainedReviewIds) if (!seenRetainedIds.has(id)) fail(`Retained editorial slot not found in source corpus: ${id}`);

const effectiveTranslations = { ...sourceTranslations };
const effectiveTranslationProvenance = { ...sourceTranslationProvenance };
const effectiveProvenanceEntries = { ...(sourceProvenance.entries || {}) };

for (const [oldId, review] of Object.entries(replacements)) {
  const s = review.successor;
  const oldProvenance = effectiveProvenanceEntries[oldId];
  const oldTranslationProvenance = effectiveTranslationProvenance[oldId] || {};
  if (!oldProvenance) fail(`Missing source provenance for replaced Normal entry ${oldId}.`);
  delete effectiveTranslations[oldId];
  delete effectiveTranslationProvenance[oldId];
  delete effectiveProvenanceEntries[oldId];

  effectiveTranslations[s.id] = review.gloss;
  effectiveTranslationProvenance[s.id] = Object.freeze({
    source: 'v23-editorial-review',
    sourceKind: 'wiktionary-bridge-editorial',
    sourceStatus: oldTranslationProvenance.reviewStatus || 'source-certified',
    reviewStatus: replacementReleaseReviewed(review) ? 'release-reviewed' : 'partial-editorial',
    materializedFrom: oldId,
    editorialDecision: 'replace',
    reviewedSenseIds: review.reviewedSenseIds,
    componentReview: review.componentReview,
    b1LowerBoundCheck: review.b1LowerBoundCheck,
  });
  effectiveProvenanceEntries[s.id] = {
    ...oldProvenance,
    reviewStatus: 'source-certified-editorial-reviewed',
    cefrEstimate: s.cefrEstimate,
    frequencyRank: s.frequencyRank,
    frequencyCount: s.frequencyCount,
    genderCorroborated: true,
    v23Editorial: {
      decision: 'replace',
      materializedFrom: oldId,
      reviewStatus: replacementReleaseReviewed(review) ? 'release-reviewed' : 'partial-editorial',
      reviewedSenseIds: review.reviewedSenseIds,
      componentReview: review.componentReview,
      b1LowerBoundCheck: review.b1LowerBoundCheck,
    },
  };
}

for (const [id, review] of Object.entries(retainedReviews)) {
  const oldProvenance = effectiveProvenanceEntries[id];
  if (!oldProvenance) fail(`Missing source provenance for retained Normal entry ${id}.`);
  effectiveTranslations[id] = review.gloss ?? sourceTranslations[id];
  effectiveTranslationProvenance[id] = Object.freeze({
    ...(sourceTranslationProvenance[id] || {}),
    sourceStatus: sourceTranslationProvenance[id]?.reviewStatus || 'source-certified',
    reviewStatus: retainedReleaseReviewed(review) ? 'release-reviewed' : 'partial-editorial',
    editorialSource: 'v23-editorial-review',
    editorialDecision: 'retain',
    reviewedSenseIds: review.reviewedSenseIds || [],
    componentReview: retainedComponents(review),
  });
  effectiveProvenanceEntries[id] = {
    ...oldProvenance,
    v23Editorial: {
      decision: 'retain',
      reviewStatus: review.reviewStatus || 'partial-editorial',
      reviewedSenseIds: review.reviewedSenseIds || [],
      componentReview: retainedComponents(review),
    },
  };
}

const corpusMeta = {
  ...sourceMeta,
  editorialPhase: 'V2-3',
  materializedFromPhase: sourceMeta.phase || 'V2-2',
  replacementCount,
  replacementDecisionBatchCount,
  replacementReviewBatchCount,
  retainedReviewCount,
  retainedBatchCount,
  releaseReviewedCount,
  sourceAssetsImmutable: true,
};
const contentCertification = {
  ...sourceContentCertification,
  editorialPhase: 'V2-3',
  materializedFromPhase: sourceContentCertification.phase || 'V2-2',
  replacementCount,
  replacementDecisionBatchCount,
  replacementReviewBatchCount,
  retainedReviewCount,
  retainedBatchCount,
  releaseReviewedCount,
  sourceAssetsImmutable: true,
  releaseReviewed,
};
const effectiveProvenance = {
  ...sourceProvenance,
  phase: 'V2-3',
  materializedFromPhase: sourceProvenance.phase || 'V2-2',
  replacementCount,
  replacementDecisionBatchCount,
  replacementReviewBatchCount,
  retainedReviewCount,
  retainedBatchCount,
  releaseReviewedCount,
  releaseReviewed,
  sourceAssetsImmutable: true,
  entries: effectiveProvenanceEntries,
};

const js = (value) => JSON.stringify(value, null, 0);
const generatedCorpusSource = `/* Generated V2-3 editorial materialization. Do not edit; source Normal assets remain V2-2. */\nwindow.ARTIKELWERK_BRIDGE_CORPUS=Object.freeze(${js(effectiveRows)});\nwindow.ARTIKELWERK_BRIDGE_CORPUS_META=Object.freeze(${js(corpusMeta)});\n`;
const generatedTranslationSource = `/* Generated V2-3 editorial Normal gloss materialization. Do not edit. */\n(() => {\n  const bridgeTranslations=Object.freeze(${js(effectiveTranslations)});\n  const bridgeProvenance=Object.freeze(${js(effectiveTranslationProvenance)});\n  window.ARTIKELWERK_TRANSLATIONS=Object.freeze({...window.ARTIKELWERK_TRANSLATIONS,...bridgeTranslations});\n  window.ARTIKELWERK_TRANSLATION_PROVENANCE=Object.freeze({...window.ARTIKELWERK_TRANSLATION_PROVENANCE,...bridgeProvenance});\n  window.ARTIKELWERK_BRIDGE_CONTENT_CERTIFICATION=Object.freeze(${js(contentCertification)});\n})();\n`;
const materializationManifest = {
  schema: 2,
  phase: 'V2-3',
  materializedFromPhase: 'V2-2',
  replacementCount,
  replacementDecisionBatchCount,
  replacementReviewBatchCount,
  retainedReviewCount,
  retainedBatchCount,
  releaseReviewedCount,
  releaseReviewed,
  sourceAssetsImmutable: true,
  replacementMap: Object.fromEntries(Object.entries(replacements).map(([oldId, review]) => [oldId, review.successor.id])),
  retainedReviewIds: [...retainedReviewIds].sort(),
};

await rm(generatedDir, { recursive: true, force: true });
await mkdir(join(generatedDir, 'content'), { recursive: true });
await writeFile(join(generatedDir, 'bridge-corpus.js'), generatedCorpusSource, 'utf8');
await writeFile(join(generatedDir, 'bridge-translations.js'), generatedTranslationSource, 'utf8');
await writeFile(join(generatedDir, 'content', 'bridge-provenance.json'), `${JSON.stringify(effectiveProvenance, null, 2)}\n`, 'utf8');
await writeFile(join(generatedDir, 'content', 'bridge-v23-materialization.json'), `${JSON.stringify(materializationManifest, null, 2)}\n`, 'utf8');

console.log(`Materialized V2-3 Normal runtime: ${effectiveRows.length} rows, ${replacementCount} replacements across ${replacementReviewBatchCount} replacement batches, ${retainedReviewCount} retained editorial reviews across ${retainedBatchCount} retained batches, ${releaseReviewedCount} release-reviewed slots.`);
