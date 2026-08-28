import { access, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const scriptsDir = dirname(fileURLToPath(import.meta.url));
const rootDir = dirname(scriptsDir);
const sourcePath = join(rootDir, 'index.html');
const translationsPath = join(rootDir, 'translations.js');
const coveragePath = join(rootDir, 'docs', 'translation-coverage.txt');

const html = await readFile(sourcePath, 'utf8');
const translationsSource = await readFile(translationsPath, 'utf8');
const coverage = await readFile(coveragePath, 'utf8');

function fail(message) {
  throw new Error(message);
}

function requireFragment(source, fragment, label = fragment) {
  if (!source.includes(fragment)) fail(`Missing required fragment: ${label}`);
}

if (!/^<!doctype html>/i.test(html.trimStart())) fail('index.html must begin with a doctype.');
if (Buffer.byteLength(html, 'utf8') < 580_000) fail('index.html is unexpectedly small; the complete readable application source is required.');

requireFragment(html, '<meta name="viewport"', 'viewport metadata');
requireFragment(html, '<title>Artikelwerk', 'application title');
requireFragment(html, '<link rel="icon" href="favicon.svg" type="image/svg+xml" />', 'SVG favicon');
requireFragment(html, '<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png" />', 'Apple touch icon');
requireFragment(html, '<link rel="manifest" href="site.webmanifest" />', 'web app manifest');
requireFragment(html, '--accent:#1d6f5f', 'UI1 primary accent');
requireFragment(html, '--bg:#f6f3ec', 'UI1 warm light background');
requireFragment(html, '--bg:#131817', 'UI1 dark background');
requireFragment(html, '--radius:12px', 'UI1 restrained radius');
requireFragment(html, 'box-shadow:var(--shadow-sm)', 'UI1 restrained surface elevation');
requireFragment(html, '<img src="favicon.svg" alt="" width="40" height="40">', 'UI1 brand mark');

const uiAssetPaths = [
  'favicon.svg','favicon.ico','favicon-16x16.png','favicon-32x32.png','apple-touch-icon.png',
  'safari-pinned-tab.svg','site.webmanifest','icon-192.png','icon-512.png','docs/ui1-visual-identity.md'
];
for (const relativePath of uiAssetPaths) {
  try { await access(join(rootDir, relativePath)); }
  catch { fail(`Missing UI1 identity asset: ${relativePath}`); }
}
const manifest = JSON.parse(await readFile(join(rootDir, 'site.webmanifest'), 'utf8'));
if (manifest?.name !== 'Artikelwerk' || manifest?.theme_color !== '#1d6f5f') fail('Invalid Artikelwerk manifest identity.');
if (!Array.isArray(manifest.icons) || !manifest.icons.some(icon => icon.sizes === '192x192') || !manifest.icons.some(icon => icon.sizes === '512x512')) fail('Manifest must expose 192px and 512px icons.');
const faviconSvg = await readFile(join(rootDir, 'favicon.svg'), 'utf8');
if (faviconSvg.includes('gradient') || !faviconSvg.includes('#1d6f5f') || !faviconSvg.includes('#fffaf0')) fail('Favicon must use the flat UI1 brand palette without gradients.');
requireFragment(html, '<script src="translations.js"></script>', 'local translation asset');
requireFragment(html, 'provenance:Object.freeze(window.ARTIKELWERK_TRANSLATION_PROVENANCE||{})', 'runtime translation certification gate');
requireFragment(html, 'contentCertification:window.ARTIKELWERK_TRANSLATION_PROVENANCE?.[id]||null', 'per-word content certification metadata');
requireFragment(html, 'const APP_VERSION = "1.1.0";', 'application version 1.1.0');
requireFragment(html, 'const VOCAB = [', 'vocabulary bank');
requireFragment(html, 'const PracticeScreen = {', 'native practice controller');
requireFragment(html, 'const App = {', 'application entrypoint');
requireFragment(html, 'App.init();', 'application initialization');

const forbiddenFragments = [
  'payload/00.txt',
  'DecompressionStream',
  'document.write(html)',
  'api.mymemory.translated.net',
  'aw-practice-shell',
  'aw-practice-launch',
];
for (const fragment of forbiddenFragments) {
  if (html.includes(fragment) || translationsSource.includes(fragment)) {
    fail(`Forbidden legacy or remote-runtime fragment remains: ${fragment}`);
  }
}

const obsoletePaths = [
  'app-source.html',
  'src/practice-screen.css',
  'src/practice-screen.js',
  'tests/practice-screen.spec.js',
  'tools/recover_payload.py',
  'tools/build_payload.py',
];
for (const relativePath of obsoletePaths) {
  try {
    await access(join(rootDir, relativePath));
    fail(`Obsolete source path still exists: ${relativePath}`);
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
  }
}

const firstScript = html.search(/<script(?:\s|>)/i);
const staticMarkup = firstScript >= 0 ? html.slice(0, firstScript) : html;
const staticIds = [...staticMarkup.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);
const duplicateStaticIds = [...new Set(staticIds.filter((id, index) => staticIds.indexOf(id) !== index))].sort();
if (duplicateStaticIds.length) fail(`Duplicate static HTML ids: ${duplicateStaticIds.join(', ')}`);

const requiredIds = [
  'practiceScreen',
  'openPracticeBtn',
  'closePracticeBtn',
  'showTranslationBtn',
  'translationHint',
  'translationText',
  'feedbackMore',
  'quizCard',
  'nextBtn',
];
const staticIdSet = new Set(staticIds);
const missingIds = requiredIds.filter((id) => !staticIdSet.has(id));
if (missingIds.length) fail(`Missing native practice ids: ${missingIds.join(', ')}`);

const externalScripts = [...html.matchAll(/<script\s+[^>]*src="([^"]+)"[^>]*><\/script>/gi)].map((match) => match[1]);
if (JSON.stringify(externalScripts) !== JSON.stringify(['translations.js'])) {
  fail(`Unexpected script dependencies: ${externalScripts.join(', ') || 'none'}`);
}

const validArticles = new Set(['der', 'die', 'das']);
const vocabulary = [];
for (const line of html.split(/\r?\n/)) {
  const value = line.trim();
  if (!value.startsWith('["') || !value.endsWith('],')) continue;
  let parsed;
  try {
    parsed = JSON.parse(value.slice(0, -1));
  } catch {
    continue;
  }
  if (!Array.isArray(parsed) || parsed.length < 7) continue;
  if (!validArticles.has(parsed[2]) || !Number.isInteger(parsed[3])) continue;
  vocabulary.push(parsed);
}

if (vocabulary.length !== 1000) fail(`Expected exactly 1000 vocabulary entries, found ${vocabulary.length}.`);

const vocabularyIds = new Set();
for (const [id, noun, article, level, explanation, example, group] of vocabulary) {
  if (typeof id !== 'string' || !/^[a-z0-9][a-z0-9_-]*$/.test(id)) fail(`Invalid vocabulary id: ${String(id)}`);
  if (vocabularyIds.has(id)) fail(`Duplicate vocabulary id: ${id}`);
  vocabularyIds.add(id);
  if (typeof noun !== 'string' || noun.trim().length < 2) fail(`Invalid noun for ${id}.`);
  if (!validArticles.has(article)) fail(`Invalid article for ${id}: ${String(article)}`);
  if (![1, 2, 3].includes(level)) fail(`Invalid fixed level for ${id}: ${String(level)}`);
  if (typeof explanation !== 'string' || explanation.trim().length < 8) fail(`Missing explanation for ${id}.`);
  if (typeof example !== 'string' || example.trim().length < 8) fail(`Missing example for ${id}.`);
  if (typeof group !== 'string' || !group.trim()) fail(`Missing semantic group for ${id}.`);
}

const inlineScripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map((match) => match[1]);
const applicationScript = [...inlineScripts].reverse().find((script) => script.includes('const App ='));
if (!applicationScript) fail('Could not locate the inline application JavaScript.');
try {
  new vm.Script(applicationScript, { filename: 'index.html:inline-app.js' });
  new vm.Script(translationsSource, { filename: 'translations.js' });
} catch (error) {
  fail(`JavaScript syntax error: ${error.message}`);
}

const translationPrefix = 'window.ARTIKELWERK_TRANSLATIONS=Object.freeze(';
const fallbackMarker = ');\nwindow.ARTIKELWERK_TRANSLATION_FALLBACKS=Object.freeze(';
const translationStart = translationsSource.indexOf(translationPrefix);
const fallbackStart = translationsSource.indexOf(fallbackMarker, translationStart + translationPrefix.length);
if (translationStart < 0 || fallbackStart < 0) fail('Could not parse generated translation data.');

const translationJson = translationsSource.slice(translationStart + translationPrefix.length, fallbackStart);
const fallbackJsonStart = fallbackStart + fallbackMarker.length;
const fallbackJsonEnd = translationsSource.indexOf(');', fallbackJsonStart);
if (fallbackJsonEnd < 0) fail('Could not parse translation fallback metadata.');

const translations = JSON.parse(translationJson);
const fallbackIds = JSON.parse(translationsSource.slice(fallbackJsonStart, fallbackJsonEnd));
const translationIds = Object.keys(translations);
if (translationIds.length !== vocabularyIds.size) fail(`Expected ${vocabularyIds.size} translations, found ${translationIds.length}.`);
const missingTranslations = [...vocabularyIds].filter((id) => typeof translations[id] !== 'string' || !translations[id].trim());
const unknownTranslations = translationIds.filter((id) => !vocabularyIds.has(id));
if (missingTranslations.length) fail(`Missing English glosses: ${missingTranslations.slice(0, 10).join(', ')}`);
if (unknownTranslations.length) fail(`Unknown translation ids: ${unknownTranslations.slice(0, 10).join(', ')}`);
if (!Array.isArray(fallbackIds) || fallbackIds.some((id) => !vocabularyIds.has(id))) fail('Translation fallback metadata contains invalid vocabulary ids.');

requireFragment(coverage, 'vocabulary_entries=1000', 'complete translation coverage report');
const coverageRatio = Number(coverage.match(/^coverage_ratio=([0-9.]+)$/m)?.[1]);
if (!Number.isFinite(coverageRatio) || coverageRatio < 0.9) fail(`English gloss coverage is below 90%: ${String(coverageRatio)}`);

console.log(`Source verification passed: ${vocabulary.length} nouns, ${translationIds.length} local glosses, ${staticIds.length} static ids.`);
