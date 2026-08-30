import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const read = (...parts) => readFile(join(root, ...parts), 'utf8');
const fail = (message) => { throw new Error(message); };
const escapeRegex = (value) => String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const containsHeadword = (example, noun) => new RegExp(
  `(^|[^\\p{L}\\p{N}])${escapeRegex(noun)}(?=$|[^\\p{L}\\p{N}])`,
  'iu',
).test(example);

const corpusSource = await read('bridge-corpus.js');
const html = await read('index.html');
const editorial = JSON.parse(await read('content', 'bridge-editorial-review.json'));
const lowerBound = JSON.parse(await read('content', 'bridge-b1-lower-bound-review.json'));
const successorLedger = JSON.parse(await read('content', 'bridge-replacement-review.json'));

const corpusContext = { window: {} };
vm.runInNewContext(corpusSource, corpusContext, { filename: 'bridge-corpus.js' });
const bridge = corpusContext.window.ARTIKELWERK_BRIDGE_CORPUS || [];
const bridgeById = new Map(bridge.map((row) => [row[0], row]));
const bridgeIds = new Set(bridgeById.keys());
const bridgeNouns = new Set(bridge.map((row) => String(row[1]).toLocaleLowerCase('de-DE')));

function parseChallenge(source) {
  const valid = new Set(['der', 'die', 'das']);
  const rows = [];
  for (const line of source.split(/\r?\n/)) {
    const value = line.trim();
    if (!value.startsWith('["') || !value.endsWith('],')) continue;
    try {
      const row = JSON.parse(value.slice(0, -1));
      if (Array.isArray(row) && row.length >= 7 && valid.has(row[2]) && Number.isInteger(row[3])) rows.push(row);
    } catch {}
  }
  return rows;
}

const challenge = parseChallenge(html);
const challengeIds = new Set(challenge.map((row) => row[0]));
const challengeNouns = new Set(challenge.map((row) => String(row[1]).toLocaleLowerCase('de-DE')));

if (successorLedger.phase !== 'V2-3' || successorLedger.status !== 'in-progress' || successorLedger.schema !== 1) {
  fail('V2-3 successor ledger metadata is invalid.');
}

const decisions = { ...(editorial.entries || {}), ...(lowerBound.entries || {}) };
const replacementIds = Object.entries(decisions)
  .filter(([, value]) => value?.decision === 'replace')
  .map(([id]) => id)
  .sort();
const ledgerEntries = successorLedger.entries || {};
const ledgerIds = Object.keys(ledgerEntries).sort();
if (JSON.stringify(ledgerIds) !== JSON.stringify(replacementIds)) {
  const missing = replacementIds.filter((id) => !Object.hasOwn(ledgerEntries, id));
  const extra = ledgerIds.filter((id) => !replacementIds.includes(id));
  fail(`Successor ledger must resolve every replacement exactly once. Missing=${missing.join(',') || 'none'} extra=${extra.join(',') || 'none'}`);
}

const articles = new Set(['der', 'die', 'das']);
const successorIds = new Set();
const successorNouns = new Set();
const bucketCounts = {};
const expectedBuckets = {};
const sourceArticleCounts = { der: 0, die: 0, das: 0 };
const successorArticleCounts = { der: 0, die: 0, das: 0 };

for (const oldId of replacementIds) {
  const row = bridgeById.get(oldId);
  if (!row) fail(`Replacement references missing Bridge row: ${oldId}`);
  const sourceBucket = `L${row[3]}-${row[10]?.cefrEstimate}`;
  expectedBuckets[sourceBucket] = (expectedBuckets[sourceBucket] || 0) + 1;
}

for (const oldId of replacementIds) {
  const row = bridgeById.get(oldId);
  if (!row) fail(`Replacement references missing Bridge row: ${oldId}`);
  const [,, oldArticle, oldLevel,,,,,,, oldEvidence] = row;
  const review = ledgerEntries[oldId];
  const s = review?.successor;
  if (!s || typeof s !== 'object') fail(`Missing successor object for ${oldId}`);
  if (typeof s.id !== 'string' || !/^[a-z0-9][a-z0-9-]*$/.test(s.id)) fail(`Invalid successor id for ${oldId}: ${String(s.id)}`);
  if (successorIds.has(s.id)) fail(`Duplicate successor id: ${s.id}`);
  successorIds.add(s.id);
  const nounKey = String(s.noun).toLocaleLowerCase('de-DE');
  if (!s.noun || successorNouns.has(nounKey)) fail(`Duplicate/missing successor noun: ${String(s.noun)}`);
  successorNouns.add(nounKey);
  if (bridgeIds.has(s.id) || bridgeNouns.has(nounKey)) fail(`Successor already exists in current Bridge: ${s.id} / ${s.noun}`);
  if (challengeIds.has(s.id) || challengeNouns.has(nounKey)) fail(`Successor overlaps Challenge: ${s.id} / ${s.noun}`);
  if (!articles.has(s.article)) fail(`Invalid successor article for ${s.id}: ${s.article}`);
  if (s.level !== oldLevel) fail(`Successor level changed slot ${oldId}: ${oldLevel} -> ${s.level}`);
  if (s.cefrEstimate !== oldEvidence?.cefrEstimate) fail(`Successor CEFR bucket changed slot ${oldId}: ${oldEvidence?.cefrEstimate} -> ${s.cefrEstimate}`);
  if (!Number.isInteger(s.frequencyRank) || s.frequencyRank <= 0 || !Number.isInteger(s.frequencyCount) || s.frequencyCount <= 0) {
    fail(`Invalid source frequency evidence for ${s.id}`);
  }
  if (s.level === 1 && s.cefrEstimate !== 'B2') fail(`Level 1 successor is not B2-estimated: ${s.id}`);
  if (s.level === 3 && (s.cefrEstimate !== 'C1' || s.frequencyRank < 10500)) fail(`Level 3 successor source gate failed: ${s.id}`);
  if (typeof review.gloss !== 'string' || !review.gloss.trim() || review.gloss.length > 145) fail(`Invalid reviewed gloss for ${s.id}`);
  if (typeof review.example !== 'string' || !containsHeadword(review.example, s.noun)) fail(`Example/headword mismatch for ${s.id}: ${review.example}`);
  if (typeof review.rule !== 'string' || review.rule.length < 20) fail(`Reviewed gender guidance missing for ${s.id}`);
  if (!Array.isArray(review.reviewedSenseIds) || review.reviewedSenseIds.length !== 1) fail(`Expected one reviewed learner-facing sense for ${s.id}`);
  for (const component of ['gloss', 'example', 'rule', 'level']) {
    if (review.componentReview?.[component] !== 'editorial') fail(`Successor ${s.id} lacks editorial ${component} review.`);
  }
  if (review.b1LowerBoundCheck !== 'no-exact-match') fail(`Successor ${s.id} lacks B1 lower-bound screening.`);
  sourceArticleCounts[oldArticle]++;
  successorArticleCounts[s.article]++;
  const bucket = `L${s.level}-${s.cefrEstimate}`;
  bucketCounts[bucket] = (bucketCounts[bucket] || 0) + 1;
}

const normalizeBuckets = (value) => Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)));
if (JSON.stringify(normalizeBuckets(bucketCounts)) !== JSON.stringify(normalizeBuckets(expectedBuckets))) {
  fail(`Unexpected successor bucket counts: actual=${JSON.stringify(bucketCounts)} expected=${JSON.stringify(expectedBuckets)}`);
}

const currentArticleCounts = bridge.reduce((acc, row) => {
  acc[row[2]]++;
  return acc;
}, { der: 0, die: 0, das: 0 });
const projectedArticleCounts = Object.fromEntries(Object.keys(currentArticleCounts).map((article) => [
  article,
  currentArticleCounts[article] - sourceArticleCounts[article] + successorArticleCounts[article],
]));
if (Math.min(...Object.values(projectedArticleCounts)) < 100) fail(`Projected article balance is too narrow: ${JSON.stringify(projectedArticleCounts)}`);

console.log(JSON.stringify({
  phase: 'V2-3',
  replacementSlots: replacementIds.length,
  uniqueSuccessors: successorIds.size,
  bucketCounts,
  expectedBuckets,
  sourceArticleCounts,
  successorArticleCounts,
  projectedArticleCounts,
  challengeOverlap: 0,
  currentBridgeOverlap: 0,
  reviewedComponentsPerSuccessor: 4,
  b1LowerBoundScreened: replacementIds.length,
}, null, 2));
console.log('V2-3 Bridge successor ledger certification passed.');
