#!/usr/bin/env python3
"""Generate Artikelwerk's English gloss data with transparent compound cues.

Exact dictionary records and hand-curated learner glosses remain preferred.
When FreeDict has no record for a productive German academic compound, this
module derives a concise English cue from an explicit, reviewable morpheme
lexicon. Derived entries are marked as cues in the UI rather than presented as
independently dictionary-attested translations.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path

import generate_translations as base

DIRECT_DERIVED_GLOSSES = {
    "momentum": "momentum; forward drive",
    "evidenz": "evidence",
    "credo": "credo; guiding principle",
    "zielbild": "target vision; desired future state",
    "investment": "investment",
    "aufkommen": "volume; occurrence; revenue",
    "regelfall": "normal case; standard situation",
    "ausbleiben": "absence; failure to occur",
    "gelingen": "success; successful outcome",
    "zustandekommen": "formation; coming about",
    "fehlanreiz": "perverse incentive; misaligned incentive",
    "grundtenor": "overall tone; underlying message",
    "stellenanteil": "share of a full-time position",
    "beschlusslage": "current state of decisions",
    "forschungsluecke": "research gap",
    "schwerpunktsetzung": "prioritization; setting of priorities",
    "bewertungsmass": "evaluation measure",
    "deutungsangebot": "interpretive account; proposed interpretation",
    "erklaerungsangebot": "explanatory account",
    "kriterienset": "set of criteria",
    "massnahmenset": "set of measures",
    "meinungsbild": "opinion landscape; overall opinion",
    "stimmungsbild": "public mood; overall sentiment",
    "werteverstaendnis": "understanding of values",
    "problemhorizont": "broader problem context",
    "zielrahmen": "target framework",
    "argumentationsgang": "line of argument",
    "geltungsgrund": "basis for validity; basis for applicability",
    "zielbezug": "relation to the objective",
    "zielhorizont": "target horizon",
    "ergebnisoffenheit": "openness to results",
    "erklaerungsleistung": "explanatory power",
    "ermessensausuebung": "exercise of discretion",
    "handlungsempfehlung": "recommendation for action",
    "geltungswirkung": "legal effect; effect of applicability",
    "reichweitenbegrenzung": "limitation of scope",
    "geltungsreichweite": "scope of application",
    "wirksamkeitspruefung": "effectiveness review",
    "anschlusslogik": "follow-on logic",
    "begruendungslinie": "line of reasoning",
    "kontrollgroesse": "control variable",
    "nachweislage": "state of evidence",
    "sachpruefung": "substantive review",
    "aussagepotenzial": "informational value; evidentiary potential",
    "informationsniveau": "level of information",
    "sachargument": "factual argument",
    "analyseraster": "analysis framework",
    "deutungsraster": "interpretation framework",
    "entscheidungsraster": "decision framework",
    "erklaerungsraster": "explanatory framework",
    "vergleichsraster": "comparison framework",
    "entscheidungsverfahren": "decision-making procedure",
    "aussageziel": "communication objective",
}

# German component -> concise English modifier or head. Keys use the same
# ASCII transliteration as Artikelwerk vocabulary IDs.
PARTS = {
    "aenderung": "change",
    "abwaegung": "balancing",
    "analyse": "analysis",
    "anpassung": "adaptation",
    "anforderung": "requirement",
    "anschluss": "follow-on",
    "anwendung": "application",
    "argumentation": "argumentation",
    "aushandlung": "negotiation",
    "ausgang": "initial",
    "aussage": "statement",
    "ausuebung": "exercise",
    "barriere": "barrier",
    "basis": "basis",
    "bedarf": "need",
    "befund": "finding",
    "begrenzung": "limitation",
    "begruendung": "justification",
    "beschluss": "decision",
    "bewertung": "evaluation",
    "beurteilung": "assessment",
    "bezug": "relation",
    "breite": "breadth",
    "daten": "data",
    "defizit": "deficit",
    "design": "design",
    "deutung": "interpretation",
    "dichte": "density",
    "diskussion": "discussion",
    "druck": "pressure",
    "einordnung": "classification",
    "einsatz": "use",
    "entscheidung": "decision",
    "empfehlung": "recommendation",
    "erfolg": "success",
    "ergebnis": "results",
    "erkenntnis": "knowledge",
    "erklaerung": "explanation",
    "ermessen": "discretion",
    "evidenz": "evidence",
    "fehl": "misaligned",
    "feld": "field",
    "forschung": "research",
    "frage": "question",
    "gang": "progression",
    "geltung": "applicability",
    "grund": "basic",
    "grundlage": "basis",
    "grundsatz": "principle",
    "guete": "quality",
    "handlung": "action",
    "horizont": "horizon",
    "impuls": "impetus",
    "information": "information",
    "interesse": "interest",
    "interpretation": "interpretation",
    "instrument": "tool",
    "kausal": "causal",
    "kern": "core",
    "konflikt": "conflict",
    "konzept": "concept",
    "kontroll": "control",
    "koordination": "coordination",
    "koordinierung": "coordination",
    "kriterium": "criterion",
    "kriterien": "criteria",
    "lage": "state",
    "leistung": "power",
    "linie": "line",
    "logik": "logic",
    "loesung": "solution",
    "luecke": "gap",
    "mass": "measure",
    "massnahme": "measure",
    "massnahmen": "measures",
    "massstab": "benchmark",
    "merkmal": "feature",
    "methode": "method",
    "methoden": "methods",
    "mittel": "resources",
    "mix": "mix",
    "modernisierung": "modernization",
    "modell": "model",
    "muster": "pattern",
    "nachweis": "evidence",
    "niveau": "level",
    "norm": "norm",
    "normen": "norms",
    "offenheit": "openness",
    "option": "option",
    "ordnung": "order",
    "orientierung": "guidance",
    "potenzial": "potential",
    "praxis": "practice",
    "prinzip": "principle",
    "problem": "problem",
    "prozess": "process",
    "profil": "profile",
    "pruef": "review",
    "pruefung": "review",
    "qualitaet": "quality",
    "rahmen": "framework",
    "raster": "framework",
    "recht": "legal",
    "referenz": "reference",
    "regel": "rule",
    "regelung": "regulatory",
    "reichweite": "scope",
    "revision": "revision",
    "sach": "factual",
    "schema": "framework",
    "schritt": "step",
    "schwerpunkt": "priority",
    "setzung": "setting",
    "soll": "target",
    "spektrum": "range",
    "spielraum": "scope",
    "stelle": "position",
    "stellen": "positions",
    "steuerung": "governance",
    "stimmung": "sentiment",
    "strategie": "strategy",
    "struktur": "structure",
    "system": "system",
    "szenario": "scenario",
    "tauglichkeit": "suitability",
    "tenor": "overall tone",
    "thema": "topic",
    "themen": "topics",
    "these": "thesis",
    "tiefe": "depth",
    "untersuchung": "study",
    "variante": "variant",
    "verfahren": "procedure",
    "vergleich": "comparison",
    "vermittlungs": "communication",
    "verstaendnis": "understanding",
    "weg": "path",
    "wechsel": "change",
    "wert": "value",
    "werte": "values",
    "wirkung": "impact",
    "wirksamkeit": "effectiveness",
    "ziel": "objective",
    "zugang": "access",
    "zusammenhang": "context",
}

LINKERS = ("", "s", "es", "n", "en", "er")
PART_KEYS = tuple(sorted(PARTS, key=lambda item: (-len(item), item)))


def _score(parts: tuple[str, ...]) -> tuple[int, int, tuple[str, ...]]:
    """Prefer fewer, longer, deterministic component analyses."""
    return (len(parts), -sum(len(part) ** 2 for part in parts), parts)


def segment(identifier: str) -> tuple[str, ...] | None:
    @lru_cache(maxsize=None)
    def solve(position: int) -> tuple[str, ...] | None:
        if position == len(identifier):
            return ()
        candidates: list[tuple[str, ...]] = []
        for part in PART_KEYS:
            if not identifier.startswith(part, position):
                continue
            end = position + len(part)
            for linker in LINKERS:
                next_position = end
                if linker:
                    if not identifier.startswith(linker, end):
                        continue
                    next_position += len(linker)
                remainder = solve(next_position)
                if remainder is not None:
                    candidates.append((part, *remainder))
        return min(candidates, key=_score) if candidates else None

    result = solve(0)
    return result if result and len(result) >= 2 else None


def compose(parts: tuple[str, ...]) -> str:
    english = [PARTS[part] for part in parts]
    head = parts[-1]
    modifier = " ".join(english[:-1]).strip()
    plain = " ".join(english).strip()

    if head == "bedarf":
        return f"need for {modifier}"
    if head == "spielraum":
        return f"scope for {modifier}"
    if head == "grundlage":
        if parts[0] in {"daten", "evidenz", "information", "vergleich"}:
            return f"{modifier} basis"
        return f"basis for {modifier}"
    if head == "tiefe":
        return f"depth of {modifier}"
    if head == "breite":
        return f"breadth of {modifier}"
    if head == "offenheit":
        return f"openness to {modifier}"
    if head == "ausuebung":
        return f"exercise of {modifier}"
    if head == "reichweite":
        return f"scope of {modifier}"
    if head == "frage":
        return f"question of {modifier}"
    if head == "verstaendnis":
        return f"understanding of {modifier}"
    if head == "empfehlung":
        return f"recommendation for {modifier}"
    if head == "bezug":
        return f"relation to {modifier}"
    if head == "lage":
        return f"state of {modifier}"
    if head == "set":
        return f"set of {modifier}"
    if head == "leistung":
        return f"{modifier} power"
    if head == "tauglichkeit":
        return f"{modifier} suitability"
    if head == "begrenzung":
        return f"limitation of {modifier}"
    if head == "potenzial":
        return f"{modifier} potential"
    if head == "ziel":
        return f"{modifier} objective"
    if head == "massstab":
        return f"{modifier} benchmark"
    if head == "raster" or head == "schema":
        return f"{modifier} framework"
    if head == "wirkung" and parts[0] == "geltung":
        return "legal effect; effect of applicability"
    if head == "prinzip" and parts[0] == "geltung":
        return "principle of applicability"
    if head == "modell" and parts[0] == "geltung":
        return "applicability model"
    if head == "grund" and parts[0] == "geltung":
        return "basis for validity; basis for applicability"
    return plain


def select_gloss(
    entry: dict[str, str],
    index: dict[str, list[tuple[str, int, int]]],
    dictionary_bytes: bytes,
) -> tuple[str, str]:
    gloss, source_kind = base.select_gloss(entry, index, dictionary_bytes)
    if source_kind != "fallback":
        return gloss, source_kind

    identifier = entry["id"]
    direct = DIRECT_DERIVED_GLOSSES.get(identifier)
    if direct:
        return direct, "derived"

    parts = segment(identifier)
    if parts:
        return compose(parts), "derived"

    fallback = entry["group"].replace("-", " ").strip() or "meaning unavailable"
    return fallback, "fallback"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--version", default="2022.04.21-1")
    args = parser.parse_args()

    vocabulary = base.parse_vocabulary(args.source.read_text(encoding="utf-8"))
    index = base.load_index(args.index)
    dictionary_bytes = args.dictionary.read_bytes()

    translations: dict[str, str] = {}
    source_counts = {"curated": 0, "dictionary": 0, "derived": 0, "fallback": 0}
    cue_ids: list[str] = []
    fallback_rows: list[str] = []
    derived_rows: list[str] = []

    for entry in vocabulary:
        gloss, source_kind = select_gloss(entry, index, dictionary_bytes)
        translations[entry["id"]] = gloss
        source_counts[source_kind] += 1
        if source_kind in {"derived", "fallback"}:
            cue_ids.append(entry["id"])
        if source_kind == "fallback":
            fallback_rows.append(f'{entry["id"]}\t{entry["article"]} {entry["noun"]}\t{entry["group"]}')
        elif source_kind == "derived":
            derived_rows.append(f'{entry["id"]}\t{entry["article"]} {entry["noun"]}\t{gloss}')

    base.write_javascript(args.output, translations, cue_ids, args.version)

    covered = source_counts["curated"] + source_counts["dictionary"] + source_counts["derived"]
    coverage = covered / len(vocabulary)
    report = [
        f"vocabulary_entries={len(vocabulary)}",
        *(f"{key}={value}" for key, value in source_counts.items()),
        f"coverage_dictionary_curated_or_derived={covered}",
        f"coverage_ratio={coverage:.4f}",
        f"cue_entries={len(cue_ids)}",
        "",
        "fallback_entries:",
        *(fallback_rows or ["none"]),
        "",
        "derived_entries:",
        *derived_rows,
    ]
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")

    if coverage < 0.90:
        raise SystemExit(f"English gloss coverage too low: {coverage:.1%}")
    if source_counts["fallback"] > 25:
        raise SystemExit(f"Too many topic-label fallbacks remain: {source_counts['fallback']}")

    print(
        "English gloss generation passed: "
        f"{covered}/{len(vocabulary)} ({coverage:.1%}) useful translations or transparent cues; "
        f"{source_counts['fallback']} topic-label fallbacks."
    )


if __name__ == "__main__":
    main()
