import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

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

const source = evalCorpus(await readRoot('bridge-corpus.js'), 'bridge-corpus.js');
const effective = evalCorpus(await readGenerated('bridge-corpus.js'), '.generated-v23/bridge-corpus.js');
const translation = evalTranslations(await readGenerated('bridge-translations.js'), '.generated-v23/bridge-translations.js');
const provenance = JSON.parse(await readGenerated('content', 'bridge-provenance.json'));
const manifest = JSON.parse(await readGenerated('content', 'bridge-v23-materialization.json'));
const ledger = JSON.parse(await readRoot('content', 'bridge-replacement-review.json'));

if (manifest.schema !== 1 || manifest.phase !== 'V2-3' || manifest.materializedFromPhase !== 'V2-2' || manifest.replacementCount !== 28) {
  fail('Invalid V2-3 materialization manifest.');
}
if (effective.rows.length !== 1000) fail(`Effective Bridge must contain 1,000 rows; found ${effective.rows.length}.`);
if (source.rows.length !== 1000) fail(`Immutable source Bridge must remain 1,000 rows; found ${source.rows.length}.`);

const sourceById = new Map(source.rows.map((row) => [row[0], row]));
const effectiveById = new Map(effective.rows.map((row) => [row[0], row]));
const effectiveIds = new Set();
const effectiveNouns = new Set();
const levelCounts = { 1: 0, 2: 0, 3: 0 };
const cefrCounts = { B2: 0, C1: 0 };

for (const row of effective.rows) {
  const [id, noun, article, level,,,,,,, evidence] = row;
  if (effectiveIds.has(id)) fail(`Duplicate effective Bridge id: ${id}`);
  effectiveIds.add(id);
  const nounKey = String(noun).toLocaleLowerCase('de-DE');
  if (effectiveNouns.has(nounKey)) fail(`Duplicate effective Bridge noun: ${noun}`);
  effectiveNouns.add(nounKey);
  if (!['der', 'die', 'das'].includes(article)) fail(`Invalid article in effective Bridge: ${id}`);
  if (!(level in levelCounts)) fail(`Invalid level in effective Bridge: ${id}`);
  levelCounts[level]++;
  if (!(evidence?.cefrEstimate in cefrCounts)) fail(`Invalid CEFR estimate in effective Bridge: ${id}`);
  cefrCounts[evidence.cefrEstimate]++;
  if (!translation.translations[id]) fail(`Missing materialized translation for ${id}`);
  if (!translation.provenance[id]) fail(`Missing materialized translation provenance for ${id}`);
  if (!provenance.entries?.[id]) fail(`Missing materialized content provenance for ${id}`);
}

if (JSON.stringify(levelCounts) !== JSON.stringify({ 1: 400, 2: 350, 3: 250 })) fail(`Level counts changed: ${JSON.stringify(levelCounts)}`);
if (JSON.stringify(cefrCounts) !== JSON.stringify({ B2: 600, C1: 400 })) fail(`CEFR counts changed: ${JSON.stringify(cefrCounts)}`);
if (Object.keys(translation.translations).length !== 1000) fail(`Expected 1,000 effective Bridge translations, found ${Object.keys(translation.translations).length}.`);
if (Object.keys(provenance.entries || {}).length !== 1000) fail(`Expected 1,000 effective provenance entries, found ${Object.keys(provenance.entries || {}).length}.`);

for (const [oldId, review] of Object.entries(ledger.entries || {})) {
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
  if (translation.translations[s.id] !== review.gloss) fail(`Materialized gloss mismatch for ${s.id}.`);
  if (translation.translations[oldId]) fail(`Rejected translation still present for ${oldId}.`);
  const p = provenance.entries[s.id];
  if (p?.v23Editorial?.materializedFrom !== oldId || p?.cefrEstimate !== s.cefrEstimate || p?.frequencyRank !== s.frequencyRank) {
    fail(`Materialized provenance mismatch for ${s.id}.`);
  }
}

if (effective.meta.editorialPhase !== 'V2-3' || effective.meta.replacementCount !== 28 || effective.meta.sourceAssetsImmutable !== true) {
  fail('Effective Bridge corpus metadata does not identify V2-3 materialization.');
}
if (translation.certification.editorialPhase !== 'V2-3' || translation.certification.replacementCount !== 28 || translation.certification.releaseReviewed !== false) {
  fail('Effective Bridge translation certification metadata is invalid.');
}
if (provenance.phase !== 'V2-3' || provenance.replacementCount !== 28 || provenance.sourceAssetsImmutable !== true) {
  fail('Effective Bridge provenance metadata is invalid.');
}

console.log(JSON.stringify({
  phase: 'V2-3',
  effectiveRows: effective.rows.length,
  replacementsMaterialized: 28,
  levelCounts,
  cefrCounts,
  translations: Object.keys(translation.translations).length,
  provenanceEntries: Object.keys(provenance.entries || {}).length,
  sourceRowsPreserved: source.rows.length,
  releaseReviewed: false,
}, null, 2));
console.log('V2-3 materialized Bridge runtime certification passed.');
