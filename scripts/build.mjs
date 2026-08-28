import { createHash } from 'node:crypto';
import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptsDir = dirname(fileURLToPath(import.meta.url));
const rootDir = dirname(scriptsDir);
const distDir = join(rootDir, 'dist');

const releaseFiles = [
  ['.nojekyll', '.nojekyll'],
  ['index.html', 'index.html'],
  ['translations.js', 'translations.js'],
  ['THIRD_PARTY_NOTICES.md', 'THIRD_PARTY_NOTICES.md'],
  ['LICENSES/GPL-3.0.txt', 'LICENSES/GPL-3.0.txt'],
  ['docs/translation-coverage.txt', 'docs/translation-coverage.txt'],
];

const sha256 = (value) => createHash('sha256').update(value).digest('hex');

await rm(distDir, { recursive: true, force: true });
const manifestFiles = {};

for (const [sourceRelative, outputRelative] of releaseFiles) {
  const sourcePath = join(rootDir, sourceRelative);
  const outputPath = join(distDir, outputRelative);
  const content = await readFile(sourcePath);
  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, content);
  manifestFiles[outputRelative] = {
    bytes: content.byteLength,
    sha256: sha256(content),
  };
}

const manifest = {
  schema: 1,
  source: 'index.html',
  files: Object.fromEntries(Object.entries(manifestFiles).sort(([a], [b]) => a.localeCompare(b))),
};

await writeFile(join(distDir, 'build-manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
console.log(`Built ${Object.keys(manifest.files).length} certified files in dist/.`);
