import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const read = (...parts) => readFile(join(root, ...parts), 'utf8');
const hasFlag = (flag) => process.argv.includes(flag);

const corpusSource = await read('bridge-corpus.js');
const translationSource = await read('bridge-translations.js');
const formalProvenance = JSON.parse(await read('content', 'bridge-provenance.json'));

const corpusContext = { window: {} };
vm.runInNewContext(corpusSource, corpusContext, { filename: 'bridge-corpus.js' });
const rows = corpusContext.window.ARTIKELWERK_BRIDGE_CORPUS || [];

const translationContext = {
  window: {
    ARTIKELWERK_TRANSLATIONS: Object.freeze({}),
    ARTIKELWERK_TRANSLATION_PROVENANCE: Object.freeze({}),
  },
};
vm.runInNewContext(translationSource, translationContext, { filename: 'bridge-translations.js' });
const translations = translationContext.window.ARTIKELWERK_TRANSLATIONS || {};
const runtimeProvenance = translationContext.window.ARTIKELWERK_TRANSLATION_PROVENANCE || {};

if (rows.length !== 1000) throw new Error(`Expected 1000 Bridge rows, found ${rows.length}`);

const GENERIC_EXAMPLE_FRAGMENTS = [
  'wurde in diesem Zusammenhang genauer betrachtet',
  'wurde im weiteren Verlauf ausdrücklich erwähnt',
  'spielte bei der anschließenden Diskussion eine wichtige Rolle',
  'wurde bei der weiteren Planung berücksichtigt',
  'wurde im Bericht noch einmal genauer beschrieben',
  'wurde bei der abschließenden Bewertung einbezogen',
  'wurde im Gespräch ausführlicher erläutert',
  'wurde im vorliegenden Fall gesondert geprüft',
];
const GARBAGE_GLOSS_TERMS = [
  'flibbertigibbet', 'mittimus', 'orphanry', 'ambuscade', 'tropæum', 'quittance',
  'baldie', 'psychologie:', 'amerikanisch:', 'article', 'antetype', 'prefiguration',
  'scout movement', 'decanium', 'decanium', 'article;', '; article',
];
const SENSE_RISK_TERMS = [
  'obsolete', 'archaic', 'dated', 'regional', 'colloquial', 'figurative', 'jocular',
];
const TRANSPARENT_LOAN_SUFFIXES = ['tion', 'ität', 'ismus', 'ik', 'ie'];
const ARTICLE_CAP = { der: 'Der', die: 'Die', das: 'Das' };

function normalizeLetters(value) {
  return String(value)
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase('de-DE')
    .replace(/ä/g, 'a').replace(/ö/g, 'o').replace(/ü/g, 'u').replace(/ß/g, 'ss')
    .replace(/[^a-z]/g, '');
}

function glossParts(gloss) {
  return String(gloss).split(';').map((part) => part.trim()).filter(Boolean);
}

function isTransparentGloss(noun, gloss) {
  const nounKey = normalizeLetters(noun);
  const parts = glossParts(gloss);
  if (!parts.length) return false;
  const first = normalizeLetters(parts[0]);
  if (nounKey === first) return true;
  if (nounKey.length >= 6 && first.length >= 6 && (nounKey.startsWith(first) || first.startsWith(nounKey))) return true;
  return TRANSPARENT_LOAN_SUFFIXES.some((suffix) => nounKey.endsWith(suffix)) && nounKey === first;
}

const entries = rows.map((row) => {
  const [id, noun, article, level, rule, example, group, coverage, phase, track, evidence] = row;
  const gloss = translations[id] || '';
  const provenance = runtimeProvenance[id] || formalProvenance.entries?.[id] || {};
  const lowGloss = gloss.toLocaleLowerCase('en-US');
  const flags = [];

  if (GENERIC_EXAMPLE_FRAGMENTS.some((fragment) => example.includes(fragment))) flags.push('generic-example');
  if (String(rule).startsWith('No reliable productive ending rule is strong enough here')) flags.push('generic-rule');
  if (GARBAGE_GLOSS_TERMS.some((term) => lowGloss.includes(term))) flags.push('garbage-gloss');
  if (SENSE_RISK_TERMS.some((term) => lowGloss.includes(term))) flags.push('sense-register-risk');
  if (/\b[A-Za-zÄÖÜäöüß]+:\s/.test(gloss)) flags.push('source-annotation-in-gloss');
  if (glossParts(gloss).length > 2) flags.push('too-many-gloss-senses');
  if (isTransparentGloss(noun, gloss)) flags.push('transparent-cognate');
  if (group === 'bridge-general') flags.push('generic-taxonomy');
  if (provenance.reviewStatus !== 'release-reviewed') flags.push('not-release-reviewed');
  if (!Array.isArray(provenance.reviewedSenseIds) || provenance.reviewedSenseIds.length < 1) flags.push('missing-reviewed-sense');
  if (!example.startsWith(`${ARTICLE_CAP[article]} ${noun}`)) flags.push('article-example-mismatch');
  if (coverage !== 'core-expanded' || phase !== 'V2-2' || track !== 'bridge') flags.push('tuple-contract');

  return {
    id,
    noun,
    article,
    level,
    cefrEstimate: evidence?.cefrEstimate,
    frequencyRank: evidence?.frequencyRank,
    group,
    gloss,
    rule,
    example,
    reviewStatus: provenance.reviewStatus || null,
    flags,
  };
});

const countFlag = (flag) => entries.filter((entry) => entry.flags.includes(flag)).length;
const levelCounts = Object.fromEntries([1, 2, 3].map((level) => [level, entries.filter((entry) => entry.level === level).length]));
const summary = {
  schema: 1,
  phase: 'V2-3',
  total: entries.length,
  levelCounts,
  flags: {
    notReleaseReviewed: countFlag('not-release-reviewed'),
    missingReviewedSense: countFlag('missing-reviewed-sense'),
    genericExample: countFlag('generic-example'),
    genericRule: countFlag('generic-rule'),
    genericTaxonomy: countFlag('generic-taxonomy'),
    garbageGloss: countFlag('garbage-gloss'),
    sourceAnnotationInGloss: countFlag('source-annotation-in-gloss'),
    tooManyGlossSenses: countFlag('too-many-gloss-senses'),
    transparentCognate: countFlag('transparent-cognate'),
    senseRegisterRisk: countFlag('sense-register-risk'),
  },
};

console.log(`V2-3 Bridge editorial audit: ${summary.total} entries`);
console.log(JSON.stringify(summary, null, 2));

if (hasFlag('--dump')) {
  for (const entry of entries) console.log(`V23_ENTRY\t${JSON.stringify(entry)}`);
}

if (hasFlag('--write-report')) {
  const path = join(root, 'content', 'bridge-editorial-audit.json');
  await writeFile(path, JSON.stringify({ ...summary, entries }, null, 2) + '\n', 'utf8');
  console.log(`Wrote ${path}`);
}
