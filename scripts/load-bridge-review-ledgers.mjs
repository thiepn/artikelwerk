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

export async function loadEditorialReview(root) {
  const base = await readJson(join(root, 'content', 'bridge-editorial-review.json'));
  if (base.schema !== 1 || base.phase !== 'V2-3' || base.status !== 'in-progress') {
    throw new Error('Bridge editorial review ledger metadata is invalid.');
  }

  const entries = { ...(base.entries || {}) };
  const batchDir = join(root, 'content', 'bridge-retained-review-batches');
  const batches = [];
  for (const file of await listJsonFiles(batchDir)) {
    const batch = await readJson(join(batchDir, file));
    if (batch.schema !== 1 || batch.phase !== 'V2-3' || batch.kind !== 'retained-review-batch' || batch.status !== 'complete') {
      throw new Error(`Invalid retained review batch metadata: ${file}`);
    }
    for (const [id, review] of Object.entries(batch.entries || {})) {
      if (review?.decision !== 'retain') throw new Error(`Retained review batch ${file} contains non-retain decision for ${id}.`);
    }
    mergeUnique(entries, batch.entries, file);
    batches.push({ file, entries: Object.keys(batch.entries || {}).length });
  }

  return { ...base, entries, retainedBatches: batches };
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
