import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const scriptsDir = dirname(fileURLToPath(import.meta.url));
const rootDir = dirname(scriptsDir);
const generatedDir = join(rootDir, '.generated-v23');
const read = (...parts) => readFile(join(rootDir, ...parts), 'utf8');
const fail = (message) => { throw new Error(message); };

const corpusSource = await read('bridge-corpus.js');
const translationSource = await read('bridge-translations.js');
const sourceProvenance = JSON.parse(await read('content', 'bridge-provenance.json'));
const reviewLedger = JSON.parse(await read('content', 'bridge-replacement-review.json'));

const corpusContext = { window: {} };
vm.runInNewContext(corpusSource, corpusContext, { filename: 'bridge-corpus.js' });
const sourceRows = corpusContext.window.ARTIKELWERK_BRIDGE_CORPUS;
const sourceMeta = corpusContext.window.ARTIKELWERK_BRIDGE_CORPUS_META || {};
if (!Array.isArray(sourceRows) || sourceRows.length !== 1000) fail('Expected the immutable V2-2 Bridge corpus to contain 1,000 rows.');

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

const replacements = reviewLedger.entries || {};
const replacementIds = new Set(Object.keys(replacements));
if (replacementIds.size !== 28) fail(`Expected 28 reviewed V2-3 replacements, found ${replacementIds.size}.`);

const seenOldIds = new Set();
const effectiveRows = sourceRows.map((row) => {
  const oldId = row[0];
  const review = replacements[oldId];
  if (!review) return row;
  seenOldIds.add(oldId);
  const s = review.successor;
  if (!s) fail(`Missing reviewed successor for ${oldId}.`);
  if (s.level !== row[3] || s.cefrEstimate !== row[10]?.cefrEstimate) {
    fail(`Successor contract mismatch for ${oldId}: ${row[3]}/${row[10]?.cefrEstimate} -> ${s.level}/${s.cefrEstimate}`);
  }
  return [
    s.id,
    s.noun,
    s.article,
    s.level,
    review.rule,
    review.example,
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
      replaces: oldId,
      reviewedSenseIds: review.reviewedSenseIds,
    },
  ];
});

for (const id of replacementIds) if (!seenOldIds.has(id)) fail(`Replacement slot not found in source corpus: ${id}`);

const effectiveTranslations = { ...sourceTranslations };
const effectiveTranslationProvenance = { ...sourceTranslationProvenance };
const effectiveProvenanceEntries = { ...(sourceProvenance.entries || {}) };

for (const [oldId, review] of Object.entries(replacements)) {
  const s = review.successor;
  const oldProvenance = effectiveProvenanceEntries[oldId];
  if (!oldProvenance) fail(`Missing source provenance for replaced Bridge entry ${oldId}.`);
  delete effectiveTranslations[oldId];
  delete effectiveTranslationProvenance[oldId];
  delete effectiveProvenanceEntries[oldId];

  effectiveTranslations[s.id] = review.gloss;
  effectiveTranslationProvenance[s.id] = Object.freeze({
    source: 'v23-editorial-review',
    sourceKind: 'wiktionary-bridge-editorial',
    materializedFrom: oldId,
    reviewedSenseIds: review.reviewedSenseIds,
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
      materializedFrom: oldId,
      reviewedSenseIds: review.reviewedSenseIds,
      componentReview: review.componentReview,
      b1LowerBoundCheck: review.b1LowerBoundCheck,
    },
  };
}

const corpusMeta = {
  ...sourceMeta,
  editorialPhase: 'V2-3',
  materializedFromPhase: sourceMeta.phase || 'V2-2',
  replacementCount: replacementIds.size,
  sourceAssetsImmutable: true,
};
const contentCertification = {
  ...sourceContentCertification,
  editorialPhase: 'V2-3',
  materializedFromPhase: sourceContentCertification.phase || 'V2-2',
  replacementCount: replacementIds.size,
  sourceAssetsImmutable: true,
  releaseReviewed: false,
};
const effectiveProvenance = {
  ...sourceProvenance,
  phase: 'V2-3',
  materializedFromPhase: sourceProvenance.phase || 'V2-2',
  replacementCount: replacementIds.size,
  sourceAssetsImmutable: true,
  entries: effectiveProvenanceEntries,
};

const js = (value) => JSON.stringify(value, null, 0);
const generatedCorpusSource = `/* Generated V2-3 editorial materialization. Do not edit; source Bridge assets remain V2-2. */\nwindow.ARTIKELWERK_BRIDGE_CORPUS=Object.freeze(${js(effectiveRows)});\nwindow.ARTIKELWERK_BRIDGE_CORPUS_META=Object.freeze(${js(corpusMeta)});\n`;
const generatedTranslationSource = `/* Generated V2-3 editorial Bridge gloss materialization. Do not edit. */\n(() => {\n  const bridgeTranslations=Object.freeze(${js(effectiveTranslations)});\n  const bridgeProvenance=Object.freeze(${js(effectiveTranslationProvenance)});\n  window.ARTIKELWERK_TRANSLATIONS=Object.freeze({...window.ARTIKELWERK_TRANSLATIONS,...bridgeTranslations});\n  window.ARTIKELWERK_TRANSLATION_PROVENANCE=Object.freeze({...window.ARTIKELWERK_TRANSLATION_PROVENANCE,...bridgeProvenance});\n  window.ARTIKELWERK_BRIDGE_CONTENT_CERTIFICATION=Object.freeze(${js(contentCertification)});\n})();\n`;
const materializationManifest = {
  schema: 1,
  phase: 'V2-3',
  materializedFromPhase: 'V2-2',
  replacementCount: replacementIds.size,
  sourceAssetsImmutable: true,
  replacementMap: Object.fromEntries(Object.entries(replacements).map(([oldId, review]) => [oldId, review.successor.id])),
};

await rm(generatedDir, { recursive: true, force: true });
await mkdir(join(generatedDir, 'content'), { recursive: true });
await writeFile(join(generatedDir, 'bridge-corpus.js'), generatedCorpusSource, 'utf8');
await writeFile(join(generatedDir, 'bridge-translations.js'), generatedTranslationSource, 'utf8');
await writeFile(join(generatedDir, 'content', 'bridge-provenance.json'), `${JSON.stringify(effectiveProvenance, null, 2)}\n`, 'utf8');
await writeFile(join(generatedDir, 'content', 'bridge-v23-materialization.json'), `${JSON.stringify(materializationManifest, null, 2)}\n`, 'utf8');

console.log(`Materialized V2-3 Bridge runtime: ${effectiveRows.length} rows, ${replacementIds.size} reviewed replacements.`);
