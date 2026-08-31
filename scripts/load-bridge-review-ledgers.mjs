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

function expandCompactRetainedEntries(batch, file) {
  const expanded = {};
  for (const [id, value] of Object.entries(batch.entries || {})) {
    if (!Array.isArray(value) || value.length !== 4 || value.some((item) => typeof item !== 'string' || !item.trim())) {
      throw new Error(`Compact retained review ${file} has an invalid tuple for ${id}.`);
    }
    const [gloss, example, rule, senseId] = value;
    expanded[id] = {
      decision: 'retain',
      gloss,
      example,
      reviewedSenseIds: [senseId],
      glossReview: 'editorial',
      exampleReview: 'editorial',
      rule,
      ruleReview: 'editorial',
      levelReview: 'editorial',
      reviewStatus: 'release-reviewed',
    };
  }
  return expanded;
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

async function mergeRetainedBatches(root, entries) {
  const dir = join(root, 'content', 'bridge-retained-review-batches');
  const batches = [];
  for (const file of await listJsonFiles(dir)) {
    const batch = await readJson(join(dir, file));
    if (batch.schema !== 1 || batch.phase !== 'V2-3' || batch.status !== 'complete') {
      throw new Error(`Invalid retained review batch metadata: ${file}`);
    }
    let incoming;
    if (batch.kind === 'retained-review-batch') {
      incoming = batch.entries || {};
      for (const [id, review] of Object.entries(incoming)) {
        if (review?.decision !== 'retain') throw new Error(`Retained review batch ${file} contains non-retain decision for ${id}.`);
      }
    } else if (batch.kind === 'retained-review-batch-compact') {
      incoming = expandCompactRetainedEntries(batch, file);
    } else {
      throw new Error(`Invalid retained review batch kind ${String(batch.kind)} in ${file}.`);
    }
    mergeUnique(entries, incoming, file);
    batches.push({ file, entries: Object.keys(incoming).length, compact: batch.kind.endsWith('-compact') });
  }
  return batches;
}

export async function loadEditorialReview(root) {
  const base = await readJson(join(root, 'content', 'bridge-editorial-review.json'));
  if (base.schema !== 1 || base.phase !== 'V2-3' || base.status !== 'in-progress') {
    throw new Error('Normal editorial review ledger metadata is invalid.');
  }

  const entries = { ...(base.entries || {}) };
  const retainedBatches = await mergeRetainedBatches(root, entries);
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
    throw new Error('Normal replacement review ledger metadata is invalid.');
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
    throw new Error('Normal retained B1 review ledger metadata is invalid.');
  }

  const entries = { ...(base.entries || {}) };
  const batchDir = join(root, 'content', 'bridge-retained-b1-batches');
  const batches = [];
  for (const file of await listJsonFiles(batchDir)) {
    const batch = await readJson(join(batchDir, file));
    if (batch.schema !== 1 || batch.phase !== 'V2-3' || batch.status !== 'complete') {
      throw new Error(`Invalid retained B1 batch metadata: ${file}`);
    }
    let incoming;
    if (batch.kind === 'retained-b1-batch') {
      incoming = batch.entries || {};
    } else if (batch.kind === 'retained-b1-batch-compact') {
      if (!Array.isArray(batch.ids) || batch.ids.some((id) => typeof id !== 'string' || !id)) {
        throw new Error(`Compact retained B1 batch ${file} has invalid ids.`);
      }
      if (new Set(batch.ids).size !== batch.ids.length) throw new Error(`Compact retained B1 batch ${file} contains duplicate ids.`);
      incoming = Object.fromEntries(batch.ids.map((id) => [id, {
        result: 'no-exact-match',
        evidenceType: 'official-list-text-search',
      }]));
    } else {
      throw new Error(`Invalid retained B1 batch kind ${String(batch.kind)} in ${file}.`);
    }
    mergeUnique(entries, incoming, file);
    batches.push({ file, entries: Object.keys(incoming).length, compact: batch.kind.endsWith('-compact') });
  }

  return { ...base, entries, retainedBatches: batches };
}
