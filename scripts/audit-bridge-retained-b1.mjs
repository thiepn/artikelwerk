import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const readJson = async (...parts) => JSON.parse(await readFile(join(root, ...parts), 'utf8'));
const fail = (message) => { throw new Error(message); };

const editorial = await readJson('content', 'bridge-editorial-review.json');
const screening = await readJson('content', 'bridge-retained-b1-review.json');

if (editorial.phase !== 'V2-3' || editorial.status !== 'in-progress' || editorial.schema !== 1) {
  fail('V2-3 editorial ledger metadata is invalid.');
}
if (screening.phase !== 'V2-3' || screening.status !== 'in-progress' || screening.schema !== 1) {
  fail('V2-3 retained B1 screening metadata is invalid.');
}

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
  missing: 0,
  extra: 0,
  result: 'no-exact-match',
}, null, 2));
console.log('V2-3 retained B1 lower-bound certification passed.');
