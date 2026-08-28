#!/usr/bin/env python3
"""Generate the compact English-gloss subset used by Artikelwerk.

The source dictionary is FreeDict deu-eng. Only records for nouns that already
exist in Artikelwerk are selected. The generated JavaScript remains a separate
GPL-3.0-or-later data asset and includes its attribution header.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
BASE64_VALUES = {character: index for index, character in enumerate(BASE64_ALPHABET)}
ARTICLE_GENDER = {"der": "masc", "die": "fem", "das": "neut"}

# These corrections are independently curated for high-frequency polysemous
# words where a dictionary's first record is not the most useful learner gloss.
CURATED_OVERRIDES = {
    "aufwand": "effort; expenditure",
    "erkenntnis": "insight; realization; finding",
    "bilanz": "balance sheet; overall assessment",
    "umfeld": "environment; context",
    "umfang": "scope; extent",
    "anliegen": "concern; request; objective",
    "ansatz": "approach; starting point",
    "ausmass": "extent; scale",
    "anteil": "share; proportion",
    "voraussetzung": "requirement; prerequisite",
    "zusammenhang": "connection; context",
    "massnahme": "measure; action",
    "verfahren": "procedure; process",
    "anspruch": "claim; entitlement; standard",
    "verhalten": "behavior; conduct",
    "wirkung": "effect; impact",
    "eindruck": "impression",
    "ruecksicht": "consideration; regard",
    "schwerpunkt": "focus; priority",
    "nachweis": "proof; evidence",
    "vorhaben": "plan; project",
    "wahrnehmung": "perception",
    "verstaendnis": "understanding",
    "spielraum": "room for maneuver; flexibility",
    "haltung": "attitude; position; posture",
    "aussicht": "prospect; view",
    "zeitraum": "period; time frame",
    "nachfrage": "demand; inquiry",
    "herkunft": "origin; provenance",
    "abweichung": "deviation; discrepancy",
    "vorgabe": "requirement; specification; target",
    "frist": "deadline; time limit",
    "anstieg": "increase; rise",
    "gutachten": "expert report; assessment",
    "stellenwert": "importance; status",
    "gefuege": "structure; framework",
    "vorbehalt": "reservation; condition",
    "resonanz": "response; resonance",
    "tragweite": "implications; scope",
    "entgelt": "payment; remuneration",
    "rueckhalt": "support; backing",
    "auflage": "edition; condition; requirement",
    "belang": "concern; interest; respect",
    "erwerb": "acquisition; gainful employment",
    "kennzahl": "metric; key figure",
    "gefaelle": "gradient; imbalance",
    "leitbild": "guiding principle; mission statement",
    "vorrang": "priority; precedence",
    "mandat": "mandate",
    "aufsicht": "supervision; oversight",
    "ausblick": "outlook; forecast",
    "instanz": "authority; court level; instance",
    "votum": "vote; opinion",
    "rueckschluss": "inference; conclusion",
    "widerspruch": "contradiction; objection",
    "zuspruch": "approval; encouragement; support",
    "gremium": "committee; panel; body",
    "befund": "finding; result; diagnosis",
    "entwurf": "draft; design",
    "narrativ": "narrative",
    "tenor": "overall tone; tenor",
    "pendant": "counterpart",
    "eklat": "scandal; public clash",
    "plaedoyer": "plea; argument in favor",
    "passus": "passage; clause",
    "sog": "pull; suction; draw",
    "zaesur": "watershed; major break",
    "mehrwert": "added value; benefit",
    "primat": "primacy; priority",
    "paradigmenwechsel": "paradigm shift",
    "ausschuss": "committee",
    "befugnis": "authority; power; authorization",
    "erfordernis": "requirement; necessity",
    "vorwand": "pretext; excuse",
    "einbusse": "loss; reduction",
    "versaeumnis": "omission; failure; neglect",
    "wortlaut": "exact wording",
    "sorgfalt": "care; diligence",
    "beduerfnis": "need; desire",
    "vermerk": "note; annotation",
    "stellungnahme": "statement; response; opinion",
    "erzeugnis": "product; manufactured item",
    "hergang": "course of events; sequence",
    "kenntnis": "knowledge; awareness",
    "aergernis": "annoyance; nuisance",
    "anschein": "appearance; impression",
    "gewaehr": "guarantee; assurance",
    "missverstaendnis": "misunderstanding",
    "verbleib": "whereabouts; remaining location",
    "sachlage": "situation; facts of the case",
    "verzeichnis": "directory; index; register",
    "missstand": "abuse; deficiency; unacceptable condition",
    "abhilfe": "remedy; relief",
    "ersuchen": "request; petition",
}

DOMAIN_PREFIX = re.compile(r"^(?:\s*\[[^\]]+\]\s*)+")
ANGLE_TAG = re.compile(r"\s*<[^>]+>")
SQUARE_TAG = re.compile(r"\s*\[[^\]]+\]")
PAREN_PRONUNCIATION = re.compile(r"\s*/[^/]+/\s*")
SPACE = re.compile(r"\s+")


def decode_dict_number(value: str) -> int:
    total = 0
    for character in value.strip():
        total = total * 64 + BASE64_VALUES[character]
    return total


def parse_vocabulary(source: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    for line in source.splitlines():
        stripped = line.strip()
        if not (stripped.startswith('["') and stripped.endswith("],")):
            continue
        try:
            item = json.loads(stripped[:-1])
        except json.JSONDecodeError:
            continue
        if len(item) < 7 or item[2] not in ARTICLE_GENDER:
            continue
        identifier, noun, article, group = item[0], item[1], item[2], item[6]
        if not all(isinstance(value, str) for value in (identifier, noun, article, group)):
            continue
        if identifier in seen:
            raise ValueError(f"Duplicate vocabulary id: {identifier}")
        seen.add(identifier)
        entries.append({"id": identifier, "noun": noun, "article": article, "group": group})
    if len(entries) < 900:
        raise ValueError(f"Expected the complete vocabulary bank; found only {len(entries)} entries")
    return entries


def load_index(index_path: Path) -> dict[str, list[tuple[str, int, int]]]:
    entries: dict[str, list[tuple[str, int, int]]] = defaultdict(list)
    for line in index_path.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        headword, offset_text, length_text = parts[0], parts[-2], parts[-1]
        try:
            offset = decode_dict_number(offset_text)
            length = decode_dict_number(length_text)
        except (KeyError, ValueError):
            continue
        entries[headword.casefold()].append((headword, offset, length))
    return entries


def clean_translation_line(line: str) -> list[str]:
    value = DOMAIN_PREFIX.sub("", line.strip())
    value = ANGLE_TAG.sub("", value)
    value = SQUARE_TAG.sub("", value)
    value = value.replace(" [fig.]", "").replace(" [coll.]", "")
    value = SPACE.sub(" ", value).strip(" .;,–—")
    if not value or value.lower().startswith(("note:", "synonym", "see:")):
        return []

    candidates: list[str] = []
    for part in re.split(r",\s+(?![^()]*\))", value):
        term = SPACE.sub(" ", part).strip(" .;,–—")
        term = re.sub(r"^(?:a|an|the)/", "", term, flags=re.IGNORECASE)
        term = re.sub(r"^(?:a|an|the)\s+", "", term, flags=re.IGNORECASE)
        if not term or len(term) > 74:
            continue
        if any(marker in term for marker in ("\"", "{", "}")):
            continue
        candidates.append(term)
    return candidates


def record_terms(record: str, expected_gender: str) -> tuple[bool, list[str]]:
    lines = [line.rstrip() for line in record.splitlines()]
    if not lines:
        return False, []
    header = PAREN_PRONUNCIATION.sub(" ", lines[0]).casefold()
    is_noun = ", n" in header or " n," in header or "<n" in header
    gender_match = f"<{expected_gender}" in header
    if not is_noun:
        return False, []
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        terms = clean_translation_line(stripped)
        if terms:
            return gender_match, terms
        if stripped.startswith(("Synonym", "see:", "Note:")):
            break
    return gender_match, []


def select_gloss(
    entry: dict[str, str],
    index: dict[str, list[tuple[str, int, int]]],
    dictionary_bytes: bytes,
) -> tuple[str, str]:
    identifier = entry["id"]
    if identifier in CURATED_OVERRIDES:
        return CURATED_OVERRIDES[identifier], "curated"

    records = index.get(entry["noun"].casefold(), [])
    expected_gender = ARTICLE_GENDER[entry["article"]]
    matched: list[str] = []
    unmatched: list[str] = []
    for _, offset, length in records:
        record = dictionary_bytes[offset : offset + length].decode("utf-8", errors="replace")
        gender_match, terms = record_terms(record, expected_gender)
        target = matched if gender_match else unmatched
        target.extend(terms)

    ordered: list[str] = []
    seen: set[str] = set()
    candidates = matched or unmatched
    group = entry["group"].casefold()

    def priority(term: str, position: int) -> tuple[int, int, int]:
        normalized = term.casefold()
        semantic_match = 0 if normalized == group else 1 if group in normalized or normalized in group else 2
        word_count = len(term.split())
        return semantic_match, min(word_count, 5), position

    for _, term in sorted(enumerate(candidates), key=lambda pair: priority(pair[1], pair[0])):
        normalized = re.sub(r"[^a-z0-9]+", "", term.casefold())
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(term)
        if len(ordered) >= 3:
            break

    if ordered:
        return "; ".join(ordered), "dictionary"
    fallback = entry["group"].replace("-", " ").strip() or "meaning unavailable"
    return fallback, "fallback"


def write_javascript(
    output_path: Path,
    translations: dict[str, str],
    fallback_ids: Iterable[str],
    source_version: str,
) -> None:
    fallback_list = sorted(fallback_ids)
    payload = json.dumps(translations, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    fallback_payload = json.dumps(fallback_list, ensure_ascii=False, separators=(",", ":"))
    output = f"""/*
 * Artikelwerk English gloss subset
 * Derived in part from FreeDict deu-eng {source_version}.
 * Dictionary copyright: 1995–2022 Frank Richter; 2020–2022 Einhard Leichtfuß.
 * This data asset is licensed under GPL-3.0-or-later.
 * Source and license details: THIRD_PARTY_NOTICES.md and LICENSES/GPL-3.0.txt
 */
window.ARTIKELWERK_TRANSLATIONS=Object.freeze({payload});
window.ARTIKELWERK_TRANSLATION_FALLBACKS=Object.freeze({fallback_payload});
"""
    output_path.write_text(output, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--version", default="2022.04.21-1")
    args = parser.parse_args()

    vocabulary = parse_vocabulary(args.source.read_text(encoding="utf-8"))
    index = load_index(args.index)
    dictionary_bytes = args.dictionary.read_bytes()

    translations: dict[str, str] = {}
    source_counts = {"curated": 0, "dictionary": 0, "fallback": 0}
    fallback_ids: list[str] = []
    sample_rows: list[str] = []

    for entry in vocabulary:
        gloss, source_kind = select_gloss(entry, index, dictionary_bytes)
        translations[entry["id"]] = gloss
        source_counts[source_kind] += 1
        if source_kind == "fallback":
            fallback_ids.append(entry["id"])
        if len(sample_rows) < 40:
            sample_rows.append(f'{entry["article"]} {entry["noun"]} → {gloss} [{source_kind}]')

    write_javascript(args.output, translations, fallback_ids, args.version)
    report = [
        f"vocabulary_entries={len(vocabulary)}",
        *(f"{key}={value}" for key, value in source_counts.items()),
        f"coverage_exact_or_curated={source_counts['curated'] + source_counts['dictionary']}",
        f"fallback_ids={','.join(fallback_ids)}",
        "",
        "samples:",
        *sample_rows,
    ]
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")

    coverage = (source_counts["curated"] + source_counts["dictionary"]) / len(vocabulary)
    if coverage < 0.90:
        raise SystemExit(f"Dictionary coverage too low: {coverage:.1%}")


if __name__ == "__main__":
    main()
