import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';

async function readJson(path) {
  return JSON.parse(await readFile(path, 'utf8'));
}

async function listJsonFiles(dir) {
  try {
    return (await readdir(dir, { withFileTypes: true }))
      .filter((entry) => entry.isFile() && entry.name.endsWith('.json'))
      .map((entry) => entry.name)
      .sort();
  } catch (error) {
    if (error?.code === 'ENOENT') return [];
    throw error;
  }
}

function mergeUnique(target, incoming, sourceLabel) {
  for (const [id, value] of Object.entries(incoming || {})) {
    if (Object.hasOwn(target, id)) throw new Error(`Duplicate V2-3 review id ${id} in ${sourceLabel}.`);
    target[id] = value;
  }
}

async function mergeDecisionBatches(root, entries, dirName, kind, decision) {
  const dir = join(root, 'content', dirName);
  const batches = [];
  for (const file of await listJsonFiles(dir)) {
    const batch = await readJson(join(dir, file));
    if (batch.schema !== 1 || batch.phase !== 'V2-3' || batch.kind !== kind || batch.status !== 'complete') {
      throw new Error(`Invalid ${kind} metadata: ${file}`);
    }
    for (const [id, review] of Object.entries(batch.entries || {})) {
      if (review?.decision !== decision) throw new Error(`${kind} ${file} contains ${String(review?.decision)} decision for ${id}.`);
    }
    mergeUnique(entries, batch.entries, file);
    batches.push({ file, entries: Object.keys(batch.entries || {}).length });
  }
  return batches;
}

export async function loadEditorialReview(root) {
  const base = await readJson(join(root, 'content', 'bridge-editorial-review.json'));
  if (base.schema !== 1 || base.phase !== 'V2-3' || base.status !== 'in-progress') {
    throw new Error('Bridge editorial review ledger metadata is invalid.');
  }

  const entries = { ...(base.entries || {}) };
  const retainedBatches = await mergeDecisionBatches(
    root,
    entries,
    'bridge-retained-review-batches',
    'retained-review-batch',
    'retain',
  );
  const replacementDecisionBatches = await mergeDecisionBatches(
    root,
    entries,
    'bridge-replacement-decision-batches',
    'replacement-decision-batch',
    'replace',
  );

  return { ...base, entries, retainedBatches, replacementDecisionBatches };
}

export async function loadReplacementReview(root) {
  const base = await readJson(join(root, 'content', 'bridge-replacement-review.json'));
  if (base.schema !== 1 || base.phase !== 'V2-3' || base.status !== 'in-progress') {
    throw new Error('Bridge replacement review ledger metadata is invalid.');
  }

  const entries = { ...(base.entries || {}) };
  const dir = join(root, 'content', 'bridge-replacement-review-batches');
  const batches = [];
  for (const file of await listJsonFiles(dir)) {
    const batch = await readJson(join(dir, file));
    if (batch.schema !== 1 || batch.phase !== 'V2-3' || batch.kind !== 'replacement-review-batch' || batch.status !== 'complete') {
      throw new Error(`Invalid replacement review batch metadata: ${file}`);
    }
    mergeUnique(entries, batch.entries, file);
    batches.push({ file, entries: Object.keys(batch.entries || {}).length });
  }

  return { ...base, entries, replacementReviewBatches: batches };
}

export async function loadRetainedB1Review(root) {
  const base = await readJson(join(root, 'content', 'bridge-retained-b1-review.json'));
  if (base.schema !== 1 || base.phase !== 'V2-3' || base.status !== 'in-progress') {
    throw new Error('Bridge retained B1 review ledger metadata is invalid.');
  }

  const entries = { ...(base.entries || {}) };
  const batchDir = join(root, 'content', 'bridge-retained-b1-batches');
  const batches = [];
  for (const file of await listJsonFiles(batchDir)) {
    const batch = await readJson(join(batchDir, file));
    if (batch.schema !== 1 || batch.phase !== 'V2-3' || batch.kind !== 'retained-b1-batch' || batch.status !== 'complete') {
      throw new Error(`Invalid retained B1 batch metadata: ${file}`);
    }
    mergeUnique(entries, batch.entries, file);
    batches.push({ file, entries: Object.keys(batch.entries || {}).length });
  }

  return { ...base, entries, retainedBatches: batches };
}
