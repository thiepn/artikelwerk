import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadEditorialReview, loadRetainedB1Review } from './load-bridge-review-ledgers.mjs';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const fail = (message) => { throw new Error(message); };

const editorial = await loadEditorialReview(root);
const screening = await loadRetainedB1Review(root);

const retainedReleaseReviewed = Object.entries(editorial.entries || {})
  .filter(([, review]) => review?.decision === 'retain' && review?.reviewStatus === 'release-reviewed')
  .map(([id]) => id)
  .sort();
const screeningEntries = screening.entries || {};
const screenedIds = Object.keys(screeningEntries).sort();

const missing = retainedReleaseReviewed.filter((id) => !Object.hasOwn(screeningEntries, id));
const extra = screenedIds.filter((id) => !retainedReleaseReviewed.includes(id));
if (missing.length || extra.length) {
  fail(`Retained B1 screening must match release-reviewed retained entries exactly. Missing=${missing.join(',') || 'none'} extra=${extra.join(',') || 'none'}`);
}

for (const id of retainedReleaseReviewed) {
  const record = screeningEntries[id];
  if (record?.result !== 'no-exact-match') fail(`Retained release-reviewed noun lacks a clean B1 lower-bound result: ${id}`);
  if (record?.evidenceType !== 'official-list-text-search') fail(`Retained B1 screening evidence type is invalid for ${id}`);
}

console.log(JSON.stringify({
  phase: 'V2-3',
  retainedReleaseReviewed: retainedReleaseReviewed.length,
  lowerBoundScreened: screenedIds.length,
  retainedReviewBatches: editorial.retainedBatches?.length || 0,
  retainedB1Batches: screening.retainedBatches?.length || 0,
  missing: 0,
  extra: 0,
  result: 'no-exact-match',
}, null, 2));
console.log('V2-3 retained B1 lower-bound certification passed.');
