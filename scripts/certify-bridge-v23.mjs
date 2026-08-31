import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import { loadEditorialReview, loadReplacementReview } from './load-bridge-review-ledgers.mjs';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const generated = join(root, '.generated-v23');
const readRoot = (...parts) => readFile(join(root, ...parts), 'utf8');
const readGenerated = (...parts) => readFile(join(generated, ...parts), 'utf8');
const fail = (message) => { throw new Error(message); };

function evalCorpus(source, filename) {
  const context = { window: {} };
  vm.runInNewContext(source, context, { filename });
  return {
    rows: context.window.ARTIKELWERK_BRIDGE_CORPUS || [],
    meta: context.window.ARTIKELWERK_BRIDGE_CORPUS_META || {},
  };
}

function evalTranslations(source, filename) {
  const context = { window: { ARTIKELWERK_TRANSLATIONS: Object.freeze({}), ARTIKELWERK_TRANSLATION_PROVENANCE: Object.freeze({}) } };
  vm.runInNewContext(source, context, { filename });
  return {
    translations: context.window.ARTIKELWERK_TRANSLATIONS || {},
    provenance: context.window.ARTIKELWERK_TRANSLATION_PROVENANCE || {},
    certification: context.window.ARTIKELWERK_BRIDGE_CONTENT_CERTIFICATION || {},
  };
}

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

const source = evalCorpus(await readRoot('bridge-corpus.js'), 'bridge-corpus.js');
const effective = evalCorpus(await readGenerated('bridge-corpus.js'), '.generated-v23/bridge-corpus.js');
const translation = evalTranslations(await readGenerated('bridge-translations.js'), '.generated-v23/bridge-translations.js');
const provenance = JSON.parse(await readGenerated('content', 'bridge-provenance.json'));
const manifest = JSON.parse(await readGenerated('content', 'bridge-v23-materialization.json'));
const replacementLedger = await loadReplacementReview(root);
const editorialLedger = await loadEditorialReview(root);

const replacements = replacementLedger.entries || {};
const replacementIds = new Set(Object.keys(replacements));
const retainedReviews = Object.fromEntries(Object.entries(editorialLedger.entries || {}).filter(([, review]) => review?.decision === 'retain'));
const retainedReviewIds = new Set(Object.keys(retainedReviews));
const replacementCount = replacementIds.size;
const replacementDecisionBatchCount = editorialLedger.replacementDecisionBatches?.length || 0;
const replacementReviewBatchCount = replacementLedger.replacementReviewBatches?.length || 0;
const retainedReviewCount = retainedReviewIds.size;
const retainedBatchCount = editorialLedger.retainedBatches?.length || 0;
const releaseReviewedCount = Object.values(replacements).filter(replacementReleaseReviewed).length
  + Object.values(retainedReviews).filter(retainedReleaseReviewed).length;
const releaseReviewed = releaseReviewedCount === source.rows.length;

if (
  manifest.schema !== 2
  || manifest.phase !== 'V2-3'
  || manifest.materializedFromPhase !== 'V2-2'
  || manifest.replacementCount !== replacementCount
  || manifest.replacementDecisionBatchCount !== replacementDecisionBatchCount
  || manifest.replacementReviewBatchCount !== replacementReviewBatchCount
  || manifest.retainedReviewCount !== retainedReviewCount
  || manifest.retainedBatchCount !== retainedBatchCount
  || manifest.releaseReviewedCount !== releaseReviewedCount
  || manifest.releaseReviewed !== releaseReviewed
) {
  fail('Invalid V2-3 materialization manifest.');
}
if (effective.rows.length !== 1000) fail(`Effective Normal must contain 1,000 rows; found ${effective.rows.length}.`);
if (source.rows.length !== 1000) fail(`Immutable source Normal must remain 1,000 rows; found ${source.rows.length}.`);

const sourceById = new Map(source.rows.map((row) => [row[0], row]));
const effectiveById = new Map(effective.rows.map((row) => [row[0], row]));
const effectiveIds = new Set();
const effectiveNouns = new Set();
const levelCounts = { 1: 0, 2: 0, 3: 0 };
const cefrCounts = { B2: 0, C1: 0 };

for (const row of effective.rows) {
  const [id, noun, article, level,,,,,,, evidence] = row;
  if (effectiveIds.has(id)) fail(`Duplicate effective Normal id: ${id}`);
  effectiveIds.add(id);
  const nounKey = String(noun).toLocaleLowerCase('de-DE');
  if (effectiveNouns.has(nounKey)) fail(`Duplicate effective Normal noun: ${noun}`);
  effectiveNouns.add(nounKey);
  if (!['der', 'die', 'das'].includes(article)) fail(`Invalid article in effective Normal: ${id}`);
  if (!(level in levelCounts)) fail(`Invalid level in effective Normal: ${id}`);
  levelCounts[level]++;
  if (!(evidence?.cefrEstimate in cefrCounts)) fail(`Invalid CEFR estimate in effective Normal: ${id}`);
  cefrCounts[evidence.cefrEstimate]++;
  if (!translation.translations[id]) fail(`Missing materialized translation for ${id}`);
  if (!translation.provenance[id]) fail(`Missing materialized translation provenance for ${id}`);
  if (!provenance.entries?.[id]) fail(`Missing materialized content provenance for ${id}`);
}

if (JSON.stringify(levelCounts) !== JSON.stringify({ 1: 400, 2: 350, 3: 250 })) fail(`Level counts changed: ${JSON.stringify(levelCounts)}`);
if (JSON.stringify(cefrCounts) !== JSON.stringify({ B2: 600, C1: 400 })) fail(`CEFR counts changed: ${JSON.stringify(cefrCounts)}`);
if (Object.keys(translation.translations).length !== 1000) fail(`Expected 1,000 effective Normal translations, found ${Object.keys(translation.translations).length}.`);
if (Object.keys(provenance.entries || {}).length !== 1000) fail(`Expected 1,000 effective provenance entries, found ${Object.keys(provenance.entries || {}).length}.`);

for (const [oldId, review] of Object.entries(replacements)) {
  const s = review.successor;
  const sourceRow = sourceById.get(oldId);
  if (!sourceRow) fail(`Immutable source no longer contains replacement slot ${oldId}.`);
  if (sourceById.has(s.id)) fail(`Immutable source unexpectedly contains V2-3 successor ${s.id}.`);
  if (effectiveById.has(oldId)) fail(`Rejected V2-2 entry still present in effective runtime: ${oldId}.`);
  const row = effectiveById.get(s.id);
  if (!row) fail(`Reviewed V2-3 successor missing from effective runtime: ${s.id}.`);
  if (row[1] !== s.noun || row[2] !== s.article || row[3] !== s.level || row[4] !== review.rule || row[5] !== review.example || row[6] !== s.group) {
    fail(`Materialized row does not match successor ledger for ${oldId} -> ${s.id}.`);
  }
  if (row[10]?.cefrEstimate !== s.cefrEstimate || row[10]?.frequencyRank !== s.frequencyRank || row[10]?.frequencyCount !== s.frequencyCount) {
    fail(`Materialized evidence does not match successor ledger for ${s.id}.`);
  }
  if (row[10]?.editorialDecision !== 'replace' || row[10]?.replaces !== oldId) fail(`Missing replacement editorial evidence for ${s.id}.`);
  if (translation.translations[s.id] !== review.gloss) fail(`Materialized gloss mismatch for ${s.id}.`);
  if (translation.translations[oldId]) fail(`Rejected translation still present for ${oldId}.`);
  const p = provenance.entries[s.id];
  if (p?.v23Editorial?.materializedFrom !== oldId || p?.v23Editorial?.decision !== 'replace' || p?.cefrEstimate !== s.cefrEstimate || p?.frequencyRank !== s.frequencyRank) {
    fail(`Materialized provenance mismatch for ${s.id}.`);
  }
}

for (const [id, review] of Object.entries(retainedReviews)) {
  if (replacementIds.has(id)) fail(`Normal slot cannot be both retained and replaced: ${id}.`);
  const sourceRow = sourceById.get(id);
  const row = effectiveById.get(id);
  if (!sourceRow || !row) fail(`Retained editorial row missing for ${id}.`);
  if (row[0] !== sourceRow[0] || row[1] !== sourceRow[1] || row[2] !== sourceRow[2] || row[3] !== sourceRow[3] || row[6] !== sourceRow[6]) {
    fail(`Retained editorial review changed immutable lexical identity for ${id}.`);
  }
  if (row[4] !== (review.rule ?? sourceRow[4]) || row[5] !== (review.example ?? sourceRow[5])) {
    fail(`Retained editorial row does not match review ledger for ${id}.`);
  }
  if (row[10]?.editorialDecision !== 'retain' || row[10]?.editorialPhase !== 'V2-3') fail(`Missing retained editorial evidence for ${id}.`);
  if (translation.translations[id] !== (review.gloss ?? translation.translations[id])) fail(`Retained editorial gloss mismatch for ${id}.`);
  const p = provenance.entries[id];
  if (p?.v23Editorial?.decision !== 'retain' || p?.v23Editorial?.reviewStatus !== (review.reviewStatus || 'partial-editorial')) {
    fail(`Retained editorial provenance mismatch for ${id}.`);
  }
}

for (const sourceRow of source.rows) {
  const id = sourceRow[0];
  if (replacementIds.has(id) || retainedReviewIds.has(id)) continue;
  const row = effectiveById.get(id);
  if (!row || JSON.stringify(row) !== JSON.stringify(sourceRow)) fail(`Unreviewed source row changed during V2-3 materialization: ${id}.`);
}

if (
  effective.meta.editorialPhase !== 'V2-3'
  || effective.meta.replacementCount !== replacementCount
  || effective.meta.replacementDecisionBatchCount !== replacementDecisionBatchCount
  || effective.meta.replacementReviewBatchCount !== replacementReviewBatchCount
  || effective.meta.retainedReviewCount !== retainedReviewCount
  || effective.meta.retainedBatchCount !== retainedBatchCount
  || effective.meta.releaseReviewedCount !== releaseReviewedCount
  || effective.meta.sourceAssetsImmutable !== true
) {
  fail('Effective Normal corpus metadata does not identify V2-3 materialization.');
}
if (
  translation.certification.editorialPhase !== 'V2-3'
  || translation.certification.replacementCount !== replacementCount
  || translation.certification.replacementDecisionBatchCount !== replacementDecisionBatchCount
  || translation.certification.replacementReviewBatchCount !== replacementReviewBatchCount
  || translation.certification.retainedReviewCount !== retainedReviewCount
  || translation.certification.retainedBatchCount !== retainedBatchCount
  || translation.certification.releaseReviewedCount !== releaseReviewedCount
  || translation.certification.releaseReviewed !== releaseReviewed
) {
  fail('Effective Normal translation certification metadata is invalid.');
}
if (
  provenance.phase !== 'V2-3'
  || provenance.replacementCount !== replacementCount
  || provenance.replacementDecisionBatchCount !== replacementDecisionBatchCount
  || provenance.replacementReviewBatchCount !== replacementReviewBatchCount
  || provenance.retainedReviewCount !== retainedReviewCount
  || provenance.retainedBatchCount !== retainedBatchCount
  || provenance.releaseReviewedCount !== releaseReviewedCount
  || provenance.releaseReviewed !== releaseReviewed
  || provenance.sourceAssetsImmutable !== true
) {
  fail('Effective Normal provenance metadata is invalid.');
}

console.log(JSON.stringify({
  phase: 'V2-3',
  effectiveRows: effective.rows.length,
  replacementsMaterialized: replacementCount,
  replacementDecisionBatchCount,
  replacementReviewBatchCount,
  retainedReviewsMaterialized: retainedReviewCount,
  retainedBatchCount,
  releaseReviewedCount,
  levelCounts,
  cefrCounts,
  translations: Object.keys(translation.translations).length,
  provenanceEntries: Object.keys(provenance.entries || {}).length,
  sourceRowsPreserved: source.rows.length,
  releaseReviewed,
}, null, 2));
console.log('V2-3 materialized Normal runtime certification passed.');
