#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import html as html_lib
import io
import json
import re
import urllib.request
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

WORDHOARD_URL = "https://github.com/natema/wordhoard/releases/download/v0.1.0/wordhoard-csv-v0.1.0.zip"
WORDHOARD_SHA256 = "83837efd46241e7226fc6daaa9d0cc81b57bf746434b8c539049c660d98ba761"
WORDHOARD_RELEASE = "v0.1.0 (2026-07-16)"
WORDHOARD_REPO = "https://github.com/natema/wordhoard"

WIKT_PARSER_COMMIT = "73075bb76c9261c44923f4909858586b261bfd83"
WIKT_TRANSLATIONS_URL = (
    "https://raw.githubusercontent.com/karoly-varasdi/de-wiktionary-parser/"
    f"{WIKT_PARSER_COMMIT}/data/de_noun_entries_with_translations.zip"
)
WIKT_TRANSLATIONS_BLOB_SHA = "a56efcb80b64433107ec1f376b933c572f2427c9"
WIKT_REPO = "https://github.com/karoly-varasdi/de-wiktionary-parser"
CC_BY_SA_URL = "https://raw.githubusercontent.com/natema/wordhoard/v0.1.0/LICENSE"

VALID_ARTICLES = {"der", "die", "das"}
ARTICLE_TO_GENDER = {"der": "m", "die": "f", "das": "n"}
GERMAN_WORD_RE = re.compile(r"^[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*$")
ID_RE = re.compile(r"[^a-z0-9]+")

# Subtitle corpora contain names, sexual vocabulary and entertainment-heavy items
# that can be frequency-prominent but are poor fits for a general learner bridge.
EXCLUDED_GLOSSES = {
    "porn", "pornography", "prostitute", "prostitution", "brothel", "penis", "vagina",
    "orgasm", "masturbation", "intercourse", "slut", "whore", "hooker", "stripper",
    "nazi", "nazism", "gestapo", "ss officer", "serial killer",
}
EXCLUDED_NOUNS = {"madam", "madame", "sir", "mister", "miss", "mrs", "mr"}

FEMININE_SUFFIXES = (
    ("ung", "The ending -ung reliably predicts feminine gender."),
    ("heit", "The ending -heit reliably predicts feminine gender."),
    ("keit", "The ending -keit reliably predicts feminine gender."),
    ("schaft", "The ending -schaft reliably predicts feminine gender."),
    ("ion", "Nouns ending in -ion are overwhelmingly feminine in Standard German."),
    ("tät", "Nouns ending in -tät are feminine."),
    ("ik", "Many learned nouns ending in -ik are feminine."),
    ("ie", "Many learned nouns ending in -ie are feminine."),
    ("ur", "Many learned nouns ending in -ur are feminine."),
    ("ei", "The noun-forming ending -ei is feminine."),
    ("anz", "Learned nouns ending in -anz are feminine."),
    ("enz", "Learned nouns ending in -enz are feminine."),
)
NEUTER_SUFFIXES = (
    ("chen", "The diminutive ending -chen reliably predicts neuter gender."),
    ("lein", "The diminutive ending -lein reliably predicts neuter gender."),
    ("um", "Many learned nouns ending in -um are neuter."),
    ("ment", "Many borrowed nouns ending in -ment are neuter; learn this noun with das."),
)
MASCULINE_SUFFIXES = (
    ("ismus", "The ending -ismus reliably predicts masculine gender."),
    ("ling", "The ending -ling strongly predicts masculine gender."),
)

GROUP_KEYWORDS = [
    ("technology", {"software", "computer", "device", "technology", "network", "data", "digital", "machine", "system", "internet"}),
    ("economy", {"economy", "economic", "finance", "financial", "market", "business", "income", "cost", "price", "trade", "revenue", "company"}),
    ("legal", {"law", "legal", "court", "judge", "right", "claim", "offence", "offense", "contract", "regulation"}),
    ("politics", {"political", "politics", "government", "parliament", "election", "policy", "state", "minister"}),
    ("education", {"school", "student", "education", "university", "learning", "teaching", "knowledge", "research", "study"}),
    ("health", {"health", "medical", "medicine", "disease", "illness", "therapy", "treatment", "patient", "symptom"}),
    ("environment", {"environment", "climate", "nature", "ecological", "energy", "emission", "pollution", "resource"}),
    ("communication", {"communication", "message", "statement", "speech", "language", "conversation", "information", "media", "report"}),
    ("society", {"society", "social", "community", "population", "culture", "public", "group", "family"}),
    ("work", {"work", "job", "employment", "profession", "project", "task", "management", "organization", "organisation", "team"}),
    ("emotion", {"feeling", "emotion", "fear", "trust", "hope", "anger", "attitude", "mood"}),
    ("process", {"process", "procedure", "development", "change", "course", "progress", "transition", "operation"}),
    ("structure", {"structure", "framework", "model", "pattern", "form", "composition", "arrangement"}),
]

EXAMPLE_TEMPLATES = [
    "{article_cap} {noun} wurde in diesem Zusammenhang genauer betrachtet.",
    "{article_cap} {noun} wurde im weiteren Verlauf ausdrücklich erwähnt.",
    "{article_cap} {noun} spielte bei der anschließenden Diskussion eine wichtige Rolle.",
    "{article_cap} {noun} wurde bei der weiteren Planung berücksichtigt.",
    "{article_cap} {noun} wurde im Bericht noch einmal genauer beschrieben.",
    "{article_cap} {noun} wurde bei der abschließenden Bewertung einbezogen.",
    "{article_cap} {noun} wurde im Gespräch ausführlicher erläutert.",
    "{article_cap} {noun} wurde im vorliegenden Fall gesondert geprüft.",
]


def die(message: str) -> None:
    raise SystemExit(message)


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Artikelwerk-V2-2/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def ascii_id(noun: str) -> str:
    s = noun.casefold().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return ID_RE.sub("-", s).strip("-")


def parse_challenge(index_text: str):
    rows = []
    for line in index_text.splitlines():
        value = line.strip()
        if not value.startswith('["') or not value.endswith("],"):
            continue
        try:
            row = json.loads(value[:-1])
        except json.JSONDecodeError:
            continue
        if isinstance(row, list) and len(row) >= 7 and row[2] in VALID_ARTICLES and isinstance(row[3], int):
            rows.append(row)
    if len(rows) != 1000:
        die(f"Expected 1000 Challenge rows in index.html, found {len(rows)}")
    return rows


def find_csv_member(zf: zipfile.ZipFile) -> str:
    candidates = [n for n in zf.namelist() if n.lower().endswith("de.csv")]
    if not candidates:
        candidates = [n for n in zf.namelist() if n.lower().endswith(".csv") and "/de" in n.lower()]
    if not candidates:
        die(f"Could not find German CSV in wordhoard archive: {zf.namelist()[:30]}")
    return sorted(candidates, key=len)[0]


def find_json_member(zf: zipfile.ZipFile) -> str:
    candidates = [n for n in zf.namelist() if n.lower().endswith(".json")]
    if not candidates:
        die(f"Could not find JSON in Wiktionary translation archive: {zf.namelist()[:30]}")
    return max(candidates, key=lambda n: zf.getinfo(n).file_size)


def flatten_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for item in node:
            yield from flatten_strings(item)
    elif isinstance(node, dict):
        for value in node.values():
            yield from flatten_strings(value)


def english_translations(entry) -> list[str]:
    found = []
    def walk(node):
        if not isinstance(node, dict):
            return
        translations = node.get("translations")
        if isinstance(translations, dict) and "en" in translations:
            found.extend(flatten_strings(translations["en"]))
        for key, value in node.items():
            if key == "translations":
                continue
            if isinstance(value, dict):
                walk(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        walk(item)
    walk(entry)
    return found


def parser_genders(entry) -> set[str]:
    result = set()
    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "genus":
                    for leaf in flatten_strings(value):
                        if leaf in {"m", "f", "n"}:
                            result.add(leaf)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(entry)
    return result


def has_common_usage(entry) -> bool:
    if not isinstance(entry, dict):
        return True
    usages = [v for k, v in entry.items() if isinstance(k, str) and re.fullmatch(r"u\d+", k) and isinstance(v, dict)]
    if not usages:
        return True
    return any(not u.get("spec_word_type") for u in usages)


def clean_gloss(value: str) -> str | None:
    text = html_lib.unescape(value).strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\[[^\]]*\]", "", text).strip()
    text = re.sub(r"\{[^}]*\}", "", text).strip()
    if not text or len(text) < 2 or len(text) > 70:
        return None
    low = text.casefold()
    if "http://" in low or "https://" in low or "<" in text or ">" in text:
        return None
    if any(ch in text for ch in "ˈˌʁʃʒŋɲɣχʔːˑɛɔəɑøɡ") or "/" in text:
        return None
    if not re.search(r"[A-Za-z]", text):
        return None
    text = re.sub(r"^(?:figuratively|figurative|colloquial|obsolete|archaic|dated):\s*", "", text, flags=re.I)
    return text.strip(" ;,.") or None


def select_glosses(raw: list[str]) -> list[str]:
    result, seen = [], set()
    for value in raw:
        cleaned = clean_gloss(value)
        if not cleaned:
            continue
        low = cleaned.casefold()
        if low in seen or any(term in low for term in EXCLUDED_GLOSSES):
            continue
        seen.add(low)
        result.append(cleaned)
        if len(result) == 3:
            break
    return result


def infer_group(glosses: list[str]) -> str:
    words = set(re.findall(r"[a-z]+", " ".join(glosses).casefold()))
    for group, keywords in GROUP_KEYWORDS:
        if words & keywords:
            return group
    return "bridge-general"


def article_rule(noun: str, article: str) -> str:
    low = noun.casefold()
    patterns = FEMININE_SUFFIXES if article == "die" else NEUTER_SUFFIXES if article == "das" else MASCULINE_SUFFIXES
    for suffix, explanation in patterns:
        if low.endswith(suffix):
            return explanation
    return f"No reliable productive ending rule is strong enough here; learn the noun as {article} {noun}."


def example_for(noun: str, article: str, stable_id: str) -> str:
    template = EXAMPLE_TEMPLATES[hashlib.sha256(stable_id.encode()).digest()[0] % len(EXAMPLE_TEMPLATES)]
    return template.format(article_cap=article.capitalize(), noun=noun)


def load_translation_dictionary(data: bytes):
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        parsed = json.loads(zf.read(find_json_member(zf)).decode("utf-8"))
    if not isinstance(parsed, dict):
        die("Wiktionary translation archive did not contain a headword dictionary")
    by_lower = {}
    for key, entry in parsed.items():
        if not isinstance(key, str) or not key:
            continue
        lower = key.casefold()
        current = by_lower.get(lower)
        if current is None or (key[:1].isupper() and not current[0][:1].isupper()):
            by_lower[lower] = (key, entry)
    return by_lower


def wordhoard_rows(data: bytes):
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        member = find_csv_member(zf)
        text = io.TextIOWrapper(zf.open(member), encoding="utf-8", newline="")
        yield from csv.DictReader(text)


def build_candidates(wordhoard: bytes, translations: dict, challenge_nouns: set[str], challenge_ids: set[str]):
    candidates, reject = [], Counter()
    seen_id, seen_noun = set(), set()
    for row in wordhoard_rows(wordhoard):
        if row.get("pos") != "NOUN":
            continue
        cefr = (row.get("cefr_estimate") or "").upper()
        if cefr not in {"B2", "C1"}:
            continue
        article = (row.get("gender") or "").lower()
        if article not in VALID_ARTICLES:
            reject["missing_or_invalid_gender"] += 1
            continue
        lemma = (row.get("lemma") or "").strip()
        if not lemma or not GERMAN_WORD_RE.fullmatch(lemma):
            reject["invalid_orthography"] += 1
            continue
        lookup = translations.get(lemma.casefold())
        if not lookup:
            reject["no_wiktionary_translation_entry"] += 1
            continue
        noun, entry = lookup
        if not GERMAN_WORD_RE.fullmatch(noun) or not noun[:1].isupper():
            reject["noncanonical_headword"] += 1
            continue
        if noun.casefold() in EXCLUDED_NOUNS:
            reject["blocked_noise"] += 1
            continue
        if not has_common_usage(entry):
            reject["special_name_only"] += 1
            continue
        genders = parser_genders(entry)
        expected = ARTICLE_TO_GENDER[article]
        if genders != {expected}:
            reject["gender_not_single_source_corroborated"] += 1
            continue
        glosses = select_glosses(english_translations(entry))
        if not glosses:
            reject["no_clean_english_gloss"] += 1
            continue
        stable_id = ascii_id(noun)
        normalized_noun = noun.casefold()
        if not stable_id:
            reject["invalid_id"] += 1
            continue
        if normalized_noun in challenge_nouns or stable_id in challenge_ids:
            reject["challenge_overlap"] += 1
            continue
        if normalized_noun in seen_noun or stable_id in seen_id:
            reject["candidate_duplicate"] += 1
            continue
        try:
            rank = int(row.get("frequency_rank") or 0)
            count = int(row.get("frequency_count") or 0)
        except ValueError:
            reject["bad_frequency"] += 1
            continue
        if rank <= 0 or count <= 0:
            reject["bad_frequency"] += 1
            continue
        seen_noun.add(normalized_noun)
        seen_id.add(stable_id)
        candidates.append({
            "id": stable_id, "noun": noun, "article": article,
            "cefrEstimate": cefr, "frequencyRank": rank, "frequencyCount": count,
            "wordhoardNotes": row.get("notes") or "", "glosses": glosses,
            "gloss": "; ".join(glosses), "group": infer_group(glosses),
            "genderEvidence": sorted(genders),
        })
    candidates.sort(key=lambda item: (item["frequencyRank"], item["noun"].casefold()))
    return candidates, reject


def assign_levels(candidates):
    b2 = [c for c in candidates if c["cefrEstimate"] == "B2"]
    c1 = [c for c in candidates if c["cefrEstimate"] == "C1"]
    if len(b2) < 750:
        die(f"Need at least 750 source-corroborated B2 nouns; found {len(b2)}")
    if len(c1) < 250:
        die(f"Need at least 250 source-corroborated C1 nouns; found {len(c1)}")
    selected = [{**item, "level": 1} for item in b2[:400]]
    selected += [{**item, "level": 2} for item in b2[400:750]]
    selected += [{**item, "level": 3} for item in c1[:250]]
    return selected, {"eligibleB2": len(b2), "eligibleC1": len(c1)}


def validate_selected(selected, challenge_nouns, challenge_ids):
    if len(selected) != 1000:
        die(f"Expected exactly 1000 selected Bridge nouns, found {len(selected)}")
    ids = [x["id"] for x in selected]
    nouns = [x["noun"].casefold() for x in selected]
    if len(set(ids)) != 1000 or len(set(nouns)) != 1000:
        die("Bridge IDs/nouns are not unique")
    if set(ids) & challenge_ids or set(nouns) & challenge_nouns:
        die("Bridge overlaps Challenge")
    levels = Counter(x["level"] for x in selected)
    if levels != Counter({1: 400, 2: 350, 3: 250}):
        die(f"Unexpected Bridge level distribution: {dict(levels)}")
    cefr = Counter(x["cefrEstimate"] for x in selected)
    if cefr != Counter({"B2": 750, "C1": 250}):
        die(f"Unexpected Bridge CEFR-estimate distribution: {dict(cefr)}")
    articles = Counter(x["article"] for x in selected)
    if set(articles) != VALID_ARTICLES or min(articles.values()) < 120:
        die(f"Article coverage is too skewed for an article trainer: {dict(articles)}")


def compact_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def write_corpus(selected):
    rows = []
    for item in selected:
        source_meta = {
            "cefrEstimate": item["cefrEstimate"], "frequencyRank": item["frequencyRank"],
            "frequencyCount": item["frequencyCount"], "genderCorroborated": True,
        }
        rows.append([
            item["id"], item["noun"], item["article"], item["level"],
            article_rule(item["noun"], item["article"]),
            example_for(item["noun"], item["article"], item["id"]),
            item["group"], "core-expanded", "V2-2", "bridge", source_meta,
        ])
    meta = {
        "schema": 1, "count": 1000, "levelCounts": {"1": 400, "2": 350, "3": 250},
        "cefrEstimateCounts": {"B2": 750, "C1": 250}, "wordhoardRelease": WORDHOARD_RELEASE,
        "wordhoardSha256": WORDHOARD_SHA256, "translationSourceCommit": WIKT_PARSER_COMMIT,
    }
    content = (
        "/*\n * Artikelwerk V2-2 Bridge corpus — CC-BY-SA-4.0.\n"
        " * Selection/gender/frequency/CEFR-estimate evidence derived from wordhoard v0.1.0.\n"
        " * Gender cross-check and English-translation availability use German Wiktionary-derived data.\n"
        " * See THIRD_PARTY_NOTICES.md and docs/v2-2-bridge-corpus.md.\n */\n"
        f"window.ARTIKELWERK_BRIDGE_CORPUS=Object.freeze({compact_json(rows)});\n"
        f"window.ARTIKELWERK_BRIDGE_CORPUS_META=Object.freeze({compact_json(meta)});\n"
    )
    (ROOT / "bridge-corpus.js").write_text(content, encoding="utf-8")


def provenance_entry(item):
    return {
        "reviewStatus": "source-certified", "sourceKind": "wiktionary-bridge",
        "selectionSource": f"wordhoard {WORDHOARD_RELEASE}",
        "translationSource": f"German Wiktionary extraction pinned via de-wiktionary-parser {WIKT_PARSER_COMMIT}",
        "cefrEstimate": item["cefrEstimate"], "frequencyRank": item["frequencyRank"],
        "frequencyCount": item["frequencyCount"], "wordhoardNotes": item["wordhoardNotes"],
        "genderCorroborated": True, "license": "CC-BY-SA-4.0",
    }


def write_translations(selected):
    translations = {item["id"]: item["gloss"] for item in selected}
    provenance = {item["id"]: provenance_entry(item) for item in selected}
    certification = {
        "schema": 1, "reviewStatus": "source-certified", "count": 1000,
        "license": "CC-BY-SA-4.0", "selectionSource": f"wordhoard {WORDHOARD_RELEASE}",
        "translationSourceCommit": WIKT_PARSER_COMMIT,
    }
    content = (
        "/*\n * Artikelwerk V2-2 Bridge English gloss asset — CC-BY-SA-4.0.\n"
        " * English translations derive from German Wiktionary via the pinned de-wiktionary-parser extraction.\n"
        " * See THIRD_PARTY_NOTICES.md and LICENSES/CC-BY-SA-4.0.txt.\n */\n"
        "(() => {\n"
        f"  const bridgeTranslations=Object.freeze({compact_json(translations)});\n"
        f"  const bridgeProvenance=Object.freeze({compact_json(provenance)});\n"
        "  window.ARTIKELWERK_TRANSLATIONS=Object.freeze({...window.ARTIKELWERK_TRANSLATIONS,...bridgeTranslations});\n"
        "  window.ARTIKELWERK_TRANSLATION_PROVENANCE=Object.freeze({...window.ARTIKELWERK_TRANSLATION_PROVENANCE,...bridgeProvenance});\n"
        f"  window.ARTIKELWERK_BRIDGE_CONTENT_CERTIFICATION=Object.freeze({compact_json(certification)});\n"
        "})();\n"
    )
    (ROOT / "bridge-translations.js").write_text(content, encoding="utf-8")
    payload = {
        "schema": 1, "track": "bridge", "count": 1000,
        "reviewStatus": "source-certified", "license": "CC-BY-SA-4.0", "entries": provenance,
    }
    (ROOT / "content" / "bridge-provenance.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_report(selected, reject, pool_stats, candidate_count):
    articles = Counter(x["article"] for x in selected)
    groups = Counter(x["group"] for x in selected)
    rank_ranges = {}
    for level in (1, 2, 3):
        ranks = [x["frequencyRank"] for x in selected if x["level"] == level]
        rank_ranges[str(level)] = [min(ranks), max(ranks)]
    sample_lines = []
    for level, label in [(1, "Intermediate"), (2, "Upper Intermediate"), (3, "Advanced")]:
        sample_lines.append(f"### Level {level} — {label}")
        for item in [x for x in selected if x["level"] == level][:20]:
            sample_lines.append(
                f"- **{item['article']} {item['noun']}** — {item['gloss']} "
                f"(source estimate {item['cefrEstimate']}, frequency rank {item['frequencyRank']:,})"
            )
        sample_lines.append("")
    report = f"""# V2-2 — 1,000-Word B2→C1 Bridge Corpus

## Result

- Bridge rows: **1,000**
- Level 1 — Intermediate: **400**
- Level 2 — Upper Intermediate: **350**
- Level 3 — Advanced: **250**
- Source CEFR estimates: **750 B2 / 250 C1**
- Articles: **der {articles['der']} / die {articles['die']} / das {articles['das']}**
- Eligible source-corroborated pool before final rank cut: **{candidate_count:,}** nouns ({pool_stats['eligibleB2']:,} B2, {pool_stats['eligibleC1']:,} C1)
- Challenge overlap: **0**

## CEFR interpretation

`B2` and `C1` here are **targeting estimates, not official Goethe B2/C1 list membership**. wordhoard calibrates German frequency ranks against Goethe A1–B1 anchors and extrapolates B2/C1 thresholds from the fitted B1 boundary. Artikelwerk therefore describes this as a B2→C1-targeted Bridge corpus rather than an official CEFR word list.

## Selection method

1. Start from the German dataset in **wordhoard {WORDHOARD_RELEASE}**.
2. Keep common nouns (`NOUN`) whose wordhoard CEFR estimate is B2 or C1 and whose grammatical gender is `der`, `die`, or `das`.
3. Require a matching common-noun entry in the pinned German Wiktionary extraction and require the old Wiktionary grammar data to corroborate **one single gender**. Ambiguous/multi-gender candidates are excluded from this phase rather than silently reduced to one quiz answer.
4. Require at least one clean English Wiktionary translation.
5. Exclude names/special-name-only usages, malformed orthography, selected subtitle-noise categories, exact Challenge noun/ID overlaps, and duplicate Bridge nouns/IDs.
6. Sort by wordhoard frequency rank. Select the first 750 eligible B2 nouns and first 250 eligible C1 nouns.
7. Assign the first 400 B2 nouns to Intermediate, the next 350 B2 nouns to Upper Intermediate, and the 250 C1 nouns to Advanced.

## Source and licensing

- **wordhoard**: {WORDHOARD_REPO}, release {WORDHOARD_RELEASE}; downloaded archive SHA-256 `{WORDHOARD_SHA256}`. The built dataset is CC-BY-SA-4.0 and combines OpenSubtitles-derived frequency evidence with openly licensed lexical sources. Goethe material is calibration-only and is not redistributed.
- **German Wiktionary extraction**: {WIKT_REPO}, pinned commit `{WIKT_PARSER_COMMIT}`; `de_noun_entries_with_translations.zip` Git blob `{WIKT_TRANSLATIONS_BLOB_SHA}`. English translations and the second-source grammar check derive from German Wiktionary data.
- The checked-in Bridge corpus, Bridge gloss asset, and Bridge provenance are distributed under **CC-BY-SA-4.0**. The existing Challenge translation asset remains separately licensed as documented in `THIRD_PARTY_NOTICES.md`.

## Frequency-rank ranges

- Level 1: {rank_ranges['1'][0]:,}–{rank_ranges['1'][1]:,}
- Level 2: {rank_ranges['2'][0]:,}–{rank_ranges['2'][1]:,}
- Level 3: {rank_ranges['3'][0]:,}–{rank_ranges['3'][1]:,}

## Largest semantic groups

""" + "\n".join(f"- {group}: {count}" for group, count in groups.most_common(12)) + "\n\n## Rejection audit\n\n" + "\n".join(f"- {reason}: {count:,}" for reason, count in reject.most_common()) + "\n\n## Corpus sample\n\n" + "\n".join(sample_lines)
    (ROOT / "docs" / "v2-2-bridge-corpus.md").write_text(report, encoding="utf-8")
    machine = {
        "schema": 1, "selected": 1000,
        "levelCounts": dict(Counter(str(x["level"]) for x in selected)),
        "cefrEstimateCounts": dict(Counter(x["cefrEstimate"] for x in selected)),
        "articleCounts": dict(articles), "rankRanges": rank_ranges,
        "eligible": pool_stats, "rejected": dict(reject),
        "sample": [
            {k: item[k] for k in ("id", "noun", "article", "level", "cefrEstimate", "frequencyRank", "frequencyCount", "gloss")}
            for item in selected[:30]
        ],
    }
    (ROOT / "content" / "bridge-corpus-report.json").write_text(
        json.dumps(machine, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_license():
    (ROOT / "LICENSES").mkdir(exist_ok=True)
    (ROOT / "LICENSES" / "CC-BY-SA-4.0.txt").write_bytes(download(CC_BY_SA_URL))


def main():
    challenge = parse_challenge(INDEX.read_text(encoding="utf-8"))
    challenge_ids = {row[0] for row in challenge}
    challenge_nouns = {row[1].casefold() for row in challenge}

    print("Downloading wordhoard release...")
    wordhoard = download(WORDHOARD_URL)
    digest = hashlib.sha256(wordhoard).hexdigest()
    if digest != WORDHOARD_SHA256:
        die(f"wordhoard SHA-256 mismatch: expected {WORDHOARD_SHA256}, got {digest}")

    print("Downloading pinned German Wiktionary extraction...")
    wikt = download(WIKT_TRANSLATIONS_URL)
    blob_sha = git_blob_sha(wikt)
    if blob_sha != WIKT_TRANSLATIONS_BLOB_SHA:
        die(f"Wiktionary extraction Git blob mismatch: expected {WIKT_TRANSLATIONS_BLOB_SHA}, got {blob_sha}")
    translations = load_translation_dictionary(wikt)
    print(f"Loaded {len(translations):,} translation headwords")

    candidates, reject = build_candidates(wordhoard, translations, challenge_nouns, challenge_ids)
    selected, pool_stats = assign_levels(candidates)
    validate_selected(selected, challenge_nouns, challenge_ids)

    write_corpus(selected)
    write_translations(selected)
    write_report(selected, reject, pool_stats, len(candidates))
    write_license()

    articles = Counter(x["article"] for x in selected)
    print(
        "Bridge generation passed: 1000 nouns "
        f"(L1=400, L2=350, L3=250; B2=750, C1=250; "
        f"der={articles['der']}, die={articles['die']}, das={articles['das']})."
    )


if __name__ == "__main__":
    main()
