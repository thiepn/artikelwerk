import { createHash } from 'node:crypto';
import { readFile, readdir, stat } from 'node:fs/promises';
import { dirname, join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptsDir = dirname(fileURLToPath(import.meta.url));
const rootDir = dirname(scriptsDir);
const distDir = join(rootDir, 'dist');
const manifestPath = join(distDir, 'build-manifest.json');
const sha256 = (value) => createHash('sha256').update(value).digest('hex');

async function listFiles(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const absolute = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await listFiles(absolute));
    else if (entry.isFile()) files.push(relative(distDir, absolute).split(sep).join('/'));
    else throw new Error(`Unexpected non-file artifact: ${absolute}`);
  }
  return files.sort();
}

const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
if (manifest?.schema !== 1 || manifest?.source !== 'index.html' || manifest?.bridgeMaterialization !== 'V2-3') {
  throw new Error('Invalid deterministic build manifest metadata.');
}

const expectedFiles = [...Object.keys(manifest.files), 'build-manifest.json'].sort();
const actualFiles = await listFiles(distDir);
if (JSON.stringify(actualFiles) !== JSON.stringify(expectedFiles)) {
  throw new Error(`Unexpected dist contents: ${actualFiles.join(', ')}`);
}

for (const [relativePath, metadata] of Object.entries(manifest.files)) {
  const declaredSource = metadata.source || relativePath;
  if (declaredSource.includes('..') || declaredSource.startsWith('/')) throw new Error(`Invalid declared build source for ${relativePath}: ${declaredSource}`);
  const sourcePath = join(rootDir, declaredSource);
  const outputPath = join(distDir, relativePath);
  const source = await readFile(sourcePath);
  const output = await readFile(outputPath);
  if (!source.equals(output)) throw new Error(`dist/${relativePath} differs from declared source ${declaredSource}.`);
  if (metadata.bytes !== source.byteLength) throw new Error(`Manifest byte count mismatch for ${relativePath}.`);
  if (metadata.sha256 !== sha256(source)) throw new Error(`Manifest hash mismatch for ${relativePath}.`);
  if (!(await stat(outputPath)).isFile()) throw new Error(`dist/${relativePath} must be a regular file.`);
}

for (const runtimeAsset of ['normal-corpus.js', 'normal-translations.js', 'content/bridge-provenance.json']) {
  const declared = manifest.files?.[runtimeAsset]?.source;
  if (!declared?.startsWith('.generated-v23/')) throw new Error(`${runtimeAsset} must come from the V2-3 generated layer.`);
}

const runtimePairs = [
  ['normal-corpus.js', '.generated-v23/bridge-corpus.js'],
  ['normal-translations.js', '.generated-v23/bridge-translations.js'],
];
for (const [checkedInRelative, generatedRelative] of runtimePairs) {
  const checkedIn = await readFile(join(rootDir, checkedInRelative));
  const generated = await readFile(join(rootDir, generatedRelative));
  if (!checkedIn.equals(generated)) throw new Error(`${checkedInRelative} is stale relative to the certified V2-3 materialization.`);
}
const runtimeHtml = await readFile(join(rootDir, 'index.html'), 'utf8');
for (const fragment of ['<script src=\"normal-translations.js\"></script>', '<script src=\"normal-corpus.js\"></script>', '.concat((window.ARTIKELWERK_BRIDGE_CORPUS||[]).map(createVocabularyEntry))']) {
  if (!runtimeHtml.includes(fragment)) throw new Error(`Normal runtime integration missing from index.html: ${fragment}`);
}
console.log(`Build verification passed: ${Object.keys(manifest.files).length} certified files with active V2-3 Normal runtime sources.`);
