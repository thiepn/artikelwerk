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
const editorialReview = JSON.parse(await read('content', 'bridge-editorial-review.json'));
const lowerBoundReview = JSON.parse(await read('content', 'bridge-b1-lower-bound-review.json'));
const successorReview = JSON.parse(await read('content', 'bridge-replacement-review.json'));
const editorialEntries = editorialReview.entries || {};
const lowerBoundEntries = lowerBoundReview.entries || {};
const successorEntries = successorReview.entries || {};
const reviewIds = new Set([...Object.keys(editorialEntries), ...Object.keys(lowerBoundEntries)]);

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
if (editorialReview.phase !== 'V2-3' || editorialReview.status !== 'in-progress') {
  throw new Error('Bridge editorial review ledger metadata is invalid.');
}
if (lowerBoundReview.phase !== 'V2-3' || lowerBoundReview.status !== 'in-progress') {
  throw new Error('Bridge B1 lower-bound review metadata is invalid.');
}
if (successorReview.phase !== 'V2-3' || successorReview.status !== 'in-progress') {
  throw new Error('Bridge successor review ledger metadata is invalid.');
}
const bridgeIds = new Set(rows.map((row) => row[0]));
for (const id of reviewIds) {
  if (!bridgeIds.has(id)) throw new Error(`Editorial review references unknown Bridge id: ${id}`);
}
for (const id of Object.keys(successorEntries)) {
  if (!bridgeIds.has(id)) throw new Error(`Successor review references unknown Bridge slot: ${id}`);
}

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
  'scout movement', 'decanium', 'article;', '; article',
];
const SENSE_RISK_TERMS = [
  'obsolete', 'archaic', 'dated', 'regional', 'colloquial', 'figurative', 'jocular',
];
const TRANSPARENT_LOAN_SUFFIXES = ['tion', 'ität', 'ismus', 'ik', 'ie'];
const HARD_BLOCKING_FLAGS = [
  'not-release-reviewed',
  'missing-reviewed-sense',
  'missing-gloss-review',
  'missing-example-review',
  'missing-rule-review',
  'missing-level-review',
  'replacement-pending',
  'generic-example',
  'garbage-gloss',
  'source-annotation-in-gloss',
  'too-many-gloss-senses',
  'example-missing-headword',
  'tuple-contract',
];
const SOFT_REVIEW_FLAGS = [
  'generic-rule',
  'generic-taxonomy',
  'transparent-cognate',
  'sense-register-risk',
];

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

function resolvedSuccessor(review) {
  const s = review?.successor;
  if (!s || typeof s !== 'object') return false;
  if (!Array.isArray(review.reviewedSenseIds) || review.reviewedSenseIds.length < 1) return false;
  if (review.b1LowerBoundCheck !== 'no-exact-match') return false;
  return ['gloss', 'example', 'rule', 'level'].every((component) => review.componentReview?.[component] === 'editorial');
}

const entries = rows.map((row) => {
  const [id, noun, article, level, sourceRule, sourceExample, group, coverage, phase, track, evidence] = row;
  const sourceGloss = translations[id] || '';
  const sourceProvenance = runtimeProvenance[id] || formalProvenance.entries?.[id] || {};
  const review = { ...(editorialEntries[id] || {}), ...(lowerBoundEntries[id] || {}) };
  const decision = review.decision || 'unreviewed';
  const replacement = decision === 'replace' ? successorEntries[id] : null;
  const replacementIsResolved = resolvedSuccessor(replacement);
  const successor = replacement?.successor || null;

  const effectiveId = successor ? successor.id : id;
  const effectiveNoun = successor ? successor.noun : noun;
  const effectiveArticle = successor ? successor.article : article;
  const effectiveLevel = successor ? successor.level : level;
  const effectiveCefr = successor ? successor.cefrEstimate : evidence?.cefrEstimate;
  const effectiveFrequencyRank = successor ? successor.frequencyRank : evidence?.frequencyRank;
  const effectiveGroup = successor ? successor.group : group;
  const gloss = successor ? replacement.gloss : (review.gloss ?? sourceGloss);
  const rule = successor ? replacement.rule : (review.rule ?? sourceRule);
  const example = successor ? replacement.example : (review.example ?? sourceExample);
  const reviewedSenseIds = successor ? (replacement.reviewedSenseIds || []) : (review.reviewedSenseIds || []);
  const componentReview = successor ? {
    gloss: replacement.componentReview?.gloss || 'pending',
    example: replacement.componentReview?.example || 'pending',
    rule: replacement.componentReview?.rule || 'pending',
    level: replacement.componentReview?.level || 'pending',
  } : {
    gloss: review.glossReview || 'pending',
    example: review.exampleReview || 'pending',
    rule: review.ruleReview || 'pending',
    level: review.levelReview || 'pending',
  };
  const reviewStatus = replacementIsResolved ? 'release-reviewed' : (review.reviewStatus || null);
  const lowGloss = String(gloss).toLocaleLowerCase('en-US');
  const flags = [];

  if (decision === 'replace' && !replacementIsResolved) flags.push('replacement-pending');

  if (decision !== 'replace' || successor) {
    if (GENERIC_EXAMPLE_FRAGMENTS.some((fragment) => String(example).includes(fragment))) flags.push('generic-example');
    if (String(rule).startsWith('No reliable productive ending rule is strong enough here')) flags.push('generic-rule');
    if (GARBAGE_GLOSS_TERMS.some((term) => lowGloss.includes(term))) flags.push('garbage-gloss');
    if (SENSE_RISK_TERMS.some((term) => lowGloss.includes(term))) flags.push('sense-register-risk');
    if (/\b[A-Za-zÄÖÜäöüß]+:\s/.test(String(gloss))) flags.push('source-annotation-in-gloss');
    if (glossParts(gloss).length > 2) flags.push('too-many-gloss-senses');
    if (isTransparentGloss(effectiveNoun, gloss)) flags.push('transparent-cognate');
    if (effectiveGroup === 'bridge-general') flags.push('generic-taxonomy');
    if (reviewedSenseIds.length < 1) flags.push('missing-reviewed-sense');
    if (componentReview.gloss !== 'editorial') flags.push('missing-gloss-review');
    if (componentReview.example !== 'editorial') flags.push('missing-example-review');
    if (componentReview.rule !== 'editorial') flags.push('missing-rule-review');
    if (componentReview.level !== 'editorial') flags.push('missing-level-review');
    if (!String(example).includes(effectiveNoun)) flags.push('example-missing-headword');
  }

  if (reviewStatus !== 'release-reviewed') flags.push('not-release-reviewed');
  if (coverage !== 'core-expanded' || phase !== 'V2-2' || track !== 'bridge') flags.push('tuple-contract');

  return {
    id: effectiveId,
    sourceSlotId: id,
    noun: effectiveNoun,
    article: effectiveArticle,
    level: effectiveLevel,
    cefrEstimate: effectiveCefr,
    frequencyRank: effectiveFrequencyRank,
    group: effectiveGroup,
    sourceGloss,
    gloss,
    sourceRule,
    rule,
    sourceExample,
    example,
    sourceStatus: sourceProvenance.reviewStatus || null,
    decision,
    decisionReason: review.reason || null,
    lowerBound: review.lowerBound || null,
    lowerBoundEvidenceType: review.evidenceType || null,
    replacementResolved: replacementIsResolved,
    reviewStatus,
    reviewedSenseIds,
    componentReview,
    flags,
  };
});

const countFlag = (flag) => entries.filter((entry) => entry.flags.includes(flag)).length;
const countComponent = (component) => entries.filter((entry) => entry.componentReview[component] === 'editorial').length;
const levelCounts = Object.fromEntries([1, 2, 3].map((entryLevel) => [entryLevel, entries.filter((entry) => entry.level === entryLevel).length]));
const hardBlockers = Object.fromEntries(HARD_BLOCKING_FLAGS.map((flag) => [flag, countFlag(flag)]));
const softSignals = Object.fromEntries(SOFT_REVIEW_FLAGS.map((flag) => [flag, countFlag(flag)]));
const hardBlockerEntries = entries.filter((entry) => entry.flags.some((flag) => HARD_BLOCKING_FLAGS.includes(flag)));
const reviewDecisions = {
  reviewedLedgerEntries: reviewIds.size,
  editorialLedgerEntries: Object.keys(editorialEntries).length,
  lowerBoundLedgerEntries: Object.keys(lowerBoundEntries).length,
  resolvedReplacements: entries.filter((entry) => entry.replacementResolved).length,
  retain: entries.filter((entry) => entry.decision === 'retain').length,
  replace: entries.filter((entry) => entry.decision === 'replace').length,
  unreviewed: entries.filter((entry) => entry.decision === 'unreviewed').length,
};
const componentProgress = {
  glossReviewed: countComponent('gloss'),
  exampleReviewed: countComponent('example'),
  ruleReviewed: countComponent('rule'),
  levelReviewed: countComponent('level'),
  releaseReviewed: entries.filter((entry) => entry.reviewStatus === 'release-reviewed').length,
};
const summary = {
  schema: 5,
  phase: 'V2-3',
  total: entries.length,
  levelCounts,
  releaseReady: hardBlockerEntries.length === 0,
  hardBlockerEntries: hardBlockerEntries.length,
  reviewDecisions,
  componentProgress,
  hardBlockers,
  softSignals,
  flags: {
    notReleaseReviewed: countFlag('not-release-reviewed'),
    missingReviewedSense: countFlag('missing-reviewed-sense'),
    missingGlossReview: countFlag('missing-gloss-review'),
    missingExampleReview: countFlag('missing-example-review'),
    missingRuleReview: countFlag('missing-rule-review'),
    missingLevelReview: countFlag('missing-level-review'),
    replacementPending: countFlag('replacement-pending'),
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

console.log(`V2-3 Bridge editorial audit: ${summary.total} effective entries`);
console.log(JSON.stringify(summary, null, 2));

if (hasFlag('--dump')) {
  for (const entry of entries) console.log(`V23_ENTRY\t${JSON.stringify(entry)}`);
}

if (hasFlag('--write-report')) {
  const path = join(root, 'content', 'bridge-editorial-audit.json');
  await writeFile(path, JSON.stringify({ ...summary, entries }, null, 2) + '\n', 'utf8');
  console.log(`Wrote ${path}`);
}

if (hasFlag('--assert-release') && !summary.releaseReady) {
  const activeBlockers = Object.entries(hardBlockers).filter(([, count]) => count > 0);
  console.error('Bridge release certification FAILED.');
  for (const [flag, count] of activeBlockers) console.error(`  ${flag}: ${count}`);
  console.error(`  affected entries: ${summary.hardBlockerEntries}/${summary.total}`);
  process.exitCode = 1;
} else if (hasFlag('--assert-release')) {
  console.log('Bridge release certification PASSED.');
}
