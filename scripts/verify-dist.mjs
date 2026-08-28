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
if (manifest?.schema !== 1 || manifest?.source !== 'index.html') throw new Error('Invalid deterministic build manifest metadata.');

const expectedFiles = [...Object.keys(manifest.files), 'build-manifest.json'].sort();
const actualFiles = await listFiles(distDir);
if (JSON.stringify(actualFiles) !== JSON.stringify(expectedFiles)) {
  throw new Error(`Unexpected dist contents: ${actualFiles.join(', ')}`);
}

for (const [relativePath, metadata] of Object.entries(manifest.files)) {
  const sourcePath = join(rootDir, relativePath);
  const outputPath = join(distDir, relativePath);
  const source = await readFile(sourcePath);
  const output = await readFile(outputPath);
  if (!source.equals(output)) throw new Error(`dist/${relativePath} differs from canonical source.`);
  if (metadata.bytes !== source.byteLength) throw new Error(`Manifest byte count mismatch for ${relativePath}.`);
  if (metadata.sha256 !== sha256(source)) throw new Error(`Manifest hash mismatch for ${relativePath}.`);
  if (!(await stat(outputPath)).isFile()) throw new Error(`dist/${relativePath} must be a regular file.`);
}

console.log(`Build verification passed: ${Object.keys(manifest.files).length} certified files.`);
