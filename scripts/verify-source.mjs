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
requireFragment(html, 'class="app-header"', 'UI2 integrated application header');
requireFragment(html, 'class="tabs app-nav"', 'UI2 primary navigation');
requireFragment(html, '<span class="nav-label">Progress</span>', 'learner-facing Progress navigation label');
requireFragment(html, 'class="panel practice-hero"', 'UI2 practice hero');
requireFragment(html, 'class="practice-support-grid"', 'UI2 supporting practice hierarchy');
requireFragment(html, 'id="practiceSetupHeading"', 'UI2 session setup heading');
requireFragment(html, '<h2>Progress</h2>', 'progress view heading');
requireFragment(html, '<h2>Vocabulary</h2>', 'vocabulary view heading');
requireFragment(html, 'position:fixed;left:0;right:0;bottom:0;top:auto;z-index:70', 'mobile bottom navigation');
requireFragment(html, 'grid-template-columns:minmax(210px,1fr) auto minmax(210px,1fr)', 'desktop shell layout');
requireFragment(html, '.modal-backdrop{z-index:80}', 'dialogs above application chrome');
requireFragment(html, 'class="practice-screen ui3-practice"', 'UI3 polished practice surface');
requireFragment(html, 'class="answer-key"', 'UI3 structured article answer controls');
requireFragment(html, 'class="panel stats-grid progress-overview"', 'UI3 learner-oriented progress overview');
requireFragment(html, 'class="progress-meta"', 'UI3 secondary progress metrics');
requireFragment(html, 'library-primary-toolbar library-filter-bar', 'UI3 vocabulary filter bar');
requireFragment(html, 'class="panel library-table-panel"', 'UI3 vocabulary reference surface');
requireFragment(html, '/* UI3 — practice, vocabulary, and progress surface polish */', 'UI3 surface style contract');
requireFragment(html, '/* UI4 — motion, interaction states, accessibility, and responsive finish */', 'UI4 finish style contract');
requireFragment(html, '/* UI5 — editorial rebuild: typography and rules instead of dashboard cards */', 'UI5 editorial rebuild');
requireFragment(html, '/* V2-1 — vocabulary track architecture */', 'V2-1 vocabulary track styles');
requireFragment(html, 'const VOCABULARY_TRACKS = Object.freeze', 'V2-1 vocabulary track registry');
requireFragment(html, 'track:track==="bridge"?"bridge":"challenge"', 'V2-1 vocabulary row track');
requireFragment(html, 'aggregatesByTrack', 'V2-1 per-track aggregate storage');
requireFragment(html, 'id="vocabularyTrackSelect"', 'V2-1 Practice vocabulary selector');
requireFragment(html, 'id="bridgeTrackBtn"', 'V2-1 Bridge home action');
requireFragment(html, 'id="progressTrackSelect"', 'V2-1 Progress vocabulary scope');
requireFragment(html, 'id="libraryTrackSelect"', 'V2-1 Vocabulary scope');
requireFragment(html, 'target?.focus?.({preventScroll:true});', 'synchronous Practice focus restoration');
requireFragment(html, 'const V21StatisticsRender = StatisticsView.render.bind(StatisticsView);', 'Progress render-time track availability guard');
requireFragment(html, 'const V21VocabularyRender = VocabularyView.render.bind(VocabularyView);', 'Vocabulary render-time track availability guard');
requireFragment(html, '--accent:#d45532', 'UI5 terracotta accent');
requireFragment(html, '--bg:#f7f4ee', 'UI5 paper background');
requireFragment(html, '--font-display:', 'UI5 editorial display typography');
requireFragment(html, '.practice-hero{display:block', 'UI5 borderless practice landing');
requireFragment(html, '.practice-hero-articles{display:none}', 'UI5 removed decorative article trio');
requireFragment(html, '.ui3-practice .quiz-card{border:0!important', 'UI5 cardless practice canvas');
requireFragment(html, '.article-chip{min-width:0;padding:0;border:0', 'UI5 typographic article labels');
requireFragment(html, '/* UI5.1 — visual acceptance fixes */', 'UI5.1 visual acceptance contract');
requireFragment(html, 'fitNounPrompt(){', 'dynamic German-compound fitting');
requireFragment(html, 'noun-single-line', 'single-line standard noun prompt');
requireFragment(html, '--mobile-nav-reserve:104px', 'mobile navigation exclusion zone');
requireFragment(html, 'id="libraryMobileFilterToggle"', 'mobile Vocabulary filter disclosure');
requireFragment(html, 'id="progressDiagnostics"', 'mobile Progress diagnostics disclosure');
requireFragment(html, 'aria-pressed="false" title="Switch to dark mode"', 'theme toggle pressed-state semantics');
requireFragment(html, '--focus-ring:var(--accent)', 'visible focus token');
requireFragment(html, '@media(prefers-reduced-motion:reduce)', 'reduced-motion support');
requireFragment(html, '@keyframes ui4SurfaceIn{from{opacity:.985}to{opacity:1}}', 'scroll-neutral practice entrance motion');
requireFragment(html, '@media(forced-colors:active)', 'forced-colors support');
requireFragment(html, 'scroll-padding-bottom:calc(86px + env(safe-area-inset-bottom))', 'mobile focus-not-obscured spacing');
requireFragment(html, 'const wasOpen=!screen.hidden;', 'practice focus-return preservation');
requireFragment(html, 'this.setAppInert(true);', 'modal background inertness');
requireFragment(html, 'this.setBackgroundInert(true);', 'practice background inertness');
requireFragment(html, 'this.prefersReducedMotion()?"auto":"smooth"', 'motion-aware programmatic scrolling');
requireFragment(html, 'themeMeta.setAttribute("content",dark?"#181614":"#d45532")', 'theme-color synchronization');
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
try { await access(join(rootDir, 'docs', 'ui4-interaction-accessibility.md')); }
catch { fail('Missing UI4 interaction/accessibility specification.'); }
try { await access(join(rootDir, 'docs', 'ui5-editorial-rebuild.md')); }
catch { fail('Missing UI5 editorial rebuild specification.'); }
try { await access(join(rootDir, 'docs', 'ui5-1-visual-acceptance.md')); }
catch { fail('Missing UI5.1 visual acceptance specification.'); }
const manifest = JSON.parse(await readFile(join(rootDir, 'site.webmanifest'), 'utf8'));
if (manifest?.name !== 'Artikelwerk' || manifest?.theme_color !== '#d45532') fail('Invalid Artikelwerk manifest identity.');
if (!Array.isArray(manifest.icons) || !manifest.icons.some(icon => icon.sizes === '192x192') || !manifest.icons.some(icon => icon.sizes === '512x512')) fail('Manifest must expose 192px and 512px icons.');
const faviconSvg = await readFile(join(rootDir, 'favicon.svg'), 'utf8');
if (faviconSvg.includes('gradient') || !faviconSvg.includes('#d45532') || !faviconSvg.includes('#f7f4ee') || !faviconSvg.includes('#191715')) fail('Favicon must use the flat UI5 editorial palette without gradients.');
requireFragment(html, '<script src="translations.js"></script>', 'local translation asset');
requireFragment(html, 'provenance:Object.freeze(window.ARTIKELWERK_TRANSLATION_PROVENANCE||{})', 'runtime translation certification gate');
requireFragment(html, 'contentCertification:window.ARTIKELWERK_TRANSLATION_PROVENANCE?.[id]||null', 'per-word content certification metadata');
requireFragment(html, 'const APP_VERSION = "1.2.0";', 'application version 1.2.0');
requireFragment(html, 'const VOCAB_SCHEMA_VERSION = 15;', 'vocabulary schema version 15');
requireFragment(html, 'const SCHEMA_VERSION = 10;', 'persistence schema version 10');
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
