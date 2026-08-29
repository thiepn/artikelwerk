#!/usr/bin/env python3
"""Learner-value curation layer for the deterministic V2-2 source generator.

Source eligibility (CEFR proxy, frequency, gender corroboration, clean Wiktionary
translation availability, and Challenge de-duplication) comes from
`generate_bridge_corpus.py`. This layer ranks that eligible pool for actual learner
value and separates usefulness from difficulty so subtitle rarity cannot masquerade
as advanced vocabulary.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import generate_bridge_corpus as base

ROOT = Path(__file__).resolve().parents[1]

TOO_BASIC_GLOSS_FRAGMENTS = {
    "birthday party", "valentine's day", "saint valentine", "phone book", "telephone directory",
    "elementary school", "grade school", "primary school", "steering wheel", "sleeping pill",
    "bald head", "handbag", "flashlight", "torch", "elevator", "lift", "bathtub", "tub",
    "jacket", "collar", "lobster", "dinosaur", "cat", "tomcat", "grape", "silverware",
    "silver medal", "radio", "statue", "pirate", "samurai", "hippie", "world war", "birthday",
    "christmas", "easter", "new year's", "march", "april", "january", "february", "june",
    "july", "august", "september", "october", "november", "december", "monday", "tuesday",
    "wednesday", "thursday", "friday", "saturday", "sunday", "grandmother", "grandfather",
    "grandma", "grandpa", "uncle", "aunt", "cousin", "boyfriend", "girlfriend", "husband",
    "wife", "son", "daughter", "brother", "sister", "shirt", "shoe", "sock", "trousers",
    "pants", "skirt", "dress", "hat", "coat", "fork", "spoon", "knife", "plate", "cup",
    "bottle", "chair", "table", "bed", "sofa", "apple", "banana", "orange", "potato",
    "tomato", "bread", "cheese", "beer", "wine", "chicken", "cow", "pig", "mouse",
    "rabbit", "lion", "tiger", "elephant", "monkey", "motorcycle", "bicycle", "bike",
    "taxi", "delivery van", "bus stop", "airport", "vacuum cleaner", "hoover", "evening meal",
    "pancake", "popcorn", "muffin", "doughnut", "donut", "lipstick", "mattress", "earring",
}
EXPLICIT_LOW_VALUE_NOUNS = {
    "Samurai", "Satan", "Dinosaurier", "Valentinstag", "Geburtstagsparty", "Telefonbuch",
    "Grundschule", "Handtasche", "Taschenlampe", "Fahrstuhl", "Hummer", "Hippie", "Weltkrieg",
    "Pirat", "Kater", "März", "Jackett", "Glatze", "Schlaftablette", "Staubsauger", "Abendbrot",
    "Muffin", "Bingo", "Weichei", "Tussi", "Flittchen", "Kacke", "Drecksack", "Mylady",
    "Kurzer", "Yard", "Jean", "Barbie", "Klingone", "Buddha", "Ami", "Speed", "Joint",
    "Donut", "Spaghetti", "Popcorn", "Vati", "Brite", "Italiener", "Mexikaner", "Spanier",
    "Araber", "Lesbe", "Blondine", "Irrer", "Junkie", "Psychopath", "Fee", "Werwolf",
    "Gespenst", "Greif", "Zauberei", "Magier", "Gorilla", "Pinguin", "Truthahn", "Welpe",
    "Schildkröte", "Fledermaus", "Ameise", "Maulwurf", "Falke", "Geier", "Gans", "Schnecke",
}
BLOCKED_GLOSS_TERMS = {
    "bimbo", "dyke", "sissy", "wimp", "shit", "crap", "whore", "junkie", "klingon",
    "daddy", "spaghetti", "pancake", "muffin", "donut", "doughnut", "popcorn",
}

ABSTRACT_SUFFIXES = (
    "ung", "heit", "keit", "schaft", "tion", "sion", "tät", "ität", "ismus", "nis", "tum",
    "anz", "enz", "ik", "ie", "ur", "ment", "logie", "graphie", "barkeit", "lichkeit",
)
FORMAL_COMPOUND_HEADS = (
    "bereich", "bedarf", "grund", "raum", "stand", "punkt", "wert", "anteil", "maß", "mass",
    "plan", "schutz", "system", "verfahren", "prozess", "recht", "pflicht", "zugang", "einsatz",
    "beitrag", "wirkung", "folge", "lage", "frage", "ziel", "mittel", "rahmen", "modell",
    "kriterium", "faktor", "ordnung", "struktur", "strategie", "konzept", "verwaltung",
)
ABSTRACT_GLOSS_TERMS = {
    "ability", "absence", "acceptance", "access", "accountability", "agreement", "analysis",
    "approach", "argument", "assessment", "assumption", "attention", "attitude", "authority",
    "awareness", "behavior", "behaviour", "capacity", "cause", "circumstance", "claim",
    "communication", "condition", "consequence", "consideration", "constraint", "context",
    "contribution", "criterion", "debate", "decision", "deficiency", "demand", "development",
    "difference", "discretion", "distribution", "effect", "equality", "evaluation", "evidence",
    "extent", "factor", "framework", "function", "impact", "implementation", "importance",
    "influence", "intention", "interpretation", "limitation", "majority", "measure", "method",
    "minority", "necessity", "obligation", "opposition", "permission", "policy", "possibility",
    "principle", "probability", "procedure", "process", "proposal", "regulation", "relation",
    "relationship", "requirement", "research", "responsibility", "restriction", "scope", "strategy",
    "structure", "support", "tendency", "transition", "treatment", "uncertainty", "validity",
    "value", "variation", "change", "concept", "knowledge", "meaning", "perception", "reason",
    "relevance", "result", "risk", "role", "standard", "status", "trend", "understanding",
}
INSTITUTIONAL_GLOSS_TERMS = {
    "administration", "agency", "association", "budget", "committee", "conference", "contract",
    "council", "court", "department", "economy", "education", "employment", "enterprise",
    "federation", "government", "institution", "investment", "law", "licence", "license", "market",
    "ministry", "organization", "organisation", "parliament", "profession", "project", "research",
    "senate", "service", "society", "state", "tax", "trade", "university",
}
CONCRETE_GLOSS_TERMS = {
    "animal", "bird", "fish", "dog", "cat", "horse", "cow", "pig", "rabbit", "insect",
    "shirt", "shoe", "sock", "dress", "jacket", "coat", "hat", "bag", "pouch", "bottle",
    "chair", "table", "bed", "door", "window", "room", "house", "car", "truck", "van",
    "motorcycle", "bicycle", "boat", "ship", "weapon", "sword", "dagger", "revolver", "gun",
    "bomb", "torpedo", "food", "bread", "cheese", "meat", "fruit", "vegetable", "dessert",
    "wrist", "ankle", "neck", "chin", "cheek", "finger", "nail", "sleeve", "moustache",
    "puppy", "goose", "turtle", "beetle", "mole", "falcon", "vulture", "snail", "frog",
}
PERSON_GLOSS_TERMS = {
    "actor", "actress", "attacker", "assassin", "bartender", "bishop", "blonde", "butler",
    "captain", "christian", "communist", "creator", "dancer", "dean", "detective", "employee",
    "executioner", "farmer", "gangster", "host", "investigator", "italian", "lawyer", "mexican",
    "murderer", "officer", "pastor", "patriot", "priest", "prisoner", "prophet", "rescuer",
    "sailor", "soldier", "spaniard", "speaker", "technician", "veterinarian", "woman", "man",
}
ENTERTAINMENT_GLOSS_TERMS = {
    "ghost", "werewolf", "witchcraft", "wizardry", "magic", "superhero", "vampire", "zombie",
    "movie", "film star", "tournament", "parade", "cocktail", "bingo", "autograph",
}


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.casefold()))


def contains_fragment(text: str, fragments: set[str]) -> bool:
    low = text.casefold()
    return any(re.search(rf"(?<![a-z]){re.escape(f)}(?![a-z])", low) for f in fragments)


def hard_reject(item) -> str | None:
    if item["noun"] in EXPLICIT_LOW_VALUE_NOUNS:
        return "learner_suitability_explicit_noise"
    if contains_fragment(item["gloss"], TOO_BASIC_GLOSS_FRAGMENTS):
        return "learner_suitability_too_basic"
    if contains_fragment(item["gloss"], BLOCKED_GLOSS_TERMS):
        return "learner_suitability_slang_or_noise"
    return None


def signals(item):
    noun = item["noun"].casefold()
    words = tokens(item["gloss"])
    return {
        "abstract_suffix": noun.endswith(ABSTRACT_SUFFIXES),
        "formal_compound": noun.endswith(FORMAL_COMPOUND_HEADS),
        "abstract": bool(words & ABSTRACT_GLOSS_TERMS),
        "institutional": bool(words & INSTITUTIONAL_GLOSS_TERMS),
        "concrete": bool(words & CONCRETE_GLOSS_TERMS),
        "person": bool(words & PERSON_GLOSS_TERMS),
        "entertainment": bool(words & ENTERTAINMENT_GLOSS_TERMS),
    }


def learner_value(item) -> int:
    s = signals(item)
    score = max(0, 8 - max(0, item["frequencyRank"] - 4500) // 900)
    score += 7 if s["abstract_suffix"] else 0
    score += 5 if s["formal_compound"] else 0
    score += 7 if s["abstract"] else 0
    score += 5 if s["institutional"] else 0
    score += 3 if item["group"] != "bridge-general" else 0
    score += 1 if 7 <= len(item["noun"]) <= 20 else 0
    score -= 6 if s["concrete"] else 0
    score -= 7 if s["person"] else 0
    score -= 8 if s["entertainment"] else 0
    score -= 3 if item["noun"].casefold().endswith(("er", "erin")) and s["person"] else 0
    first_gloss = re.sub(r"[^a-z]", "", item["glosses"][0].casefold())
    noun_ascii = re.sub(r"[^a-z]", "", base.ascii_id(item["noun"]).replace("-", ""))
    score -= 3 if first_gloss and first_gloss == noun_ascii else 0
    if item["group"] == "bridge-general" and not any((s["abstract_suffix"], s["formal_compound"], s["abstract"], s["institutional"])):
        score -= 3
    return int(score)


def difficulty_score(item) -> float:
    s = signals(item)
    return (
        item["frequencyRank"] / 1000
        + min(len(item["noun"]), 24) / 10
        + (1.2 if s["abstract_suffix"] else 0)
        + (0.8 if s["formal_compound"] else 0)
        + (0.7 if s["abstract"] else 0)
    )


def advanced_qualified(item) -> bool:
    if item["cefrEstimate"] != "C1" or item["frequencyRank"] < 10500:
        return False
    s = signals(item)
    return bool(s["abstract_suffix"] or s["formal_compound"] or s["abstract"] or s["institutional"])


def choose(pool, count: int, soft_article_targets: dict[str, int]):
    ranked = sorted(pool, key=lambda x: (-x["learnerValue"], x["frequencyRank"], x["noun"].casefold()))
    chosen, used = [], set()
    # Article targets are soft: take up to the target from each article, never lower
    # the vocabulary bar merely to satisfy a ratio.
    for article, target in soft_article_targets.items():
        for item in [x for x in ranked if x["article"] == article][:target]:
            chosen.append(item)
            used.add(item["id"])
    if len(chosen) > count:
        chosen = sorted(chosen, key=lambda x: (-x["learnerValue"], x["frequencyRank"]))[:count]
        used = {x["id"] for x in chosen}
    for item in ranked:
        if len(chosen) >= count:
            break
        if item["id"] not in used:
            chosen.append(item)
            used.add(item["id"])
    if len(chosen) != count:
        base.die(f"Could not select {count} quality candidates; found {len(chosen)}")
    return chosen


_original_build = base.build_candidates
_original_report = base.write_report
_original_glosses = base.select_glosses


def select_two_glosses(raw):
    return _original_glosses(raw)[:2]


def curated_candidates(wordhoard, translations, challenge_nouns, challenge_ids):
    candidates, reject = _original_build(wordhoard, translations, challenge_nouns, challenge_ids)
    kept = []
    for item in candidates:
        reason = hard_reject(item)
        if reason:
            reject[reason] += 1
            continue
        kept.append({**item, "learnerValue": learner_value(item), "difficultyScore": difficulty_score(item)})
    return kept, reject


def curated_assign_levels(candidates):
    b2 = [c for c in candidates if c["cefrEstimate"] == "B2"]
    c1 = [c for c in candidates if c["cefrEstimate"] == "C1"]
    advanced = [c for c in c1 if advanced_qualified(c)]
    if len(b2) < 750:
        base.die(f"Need at least 750 curated B2 nouns; found {len(b2)}")
    if len(advanced) < 250:
        base.die(f"Need at least 250 formally qualified upper-C1 nouns; found {len(advanced)}")

    b2_selected = choose(b2, 750, {"der": 220, "die": 300, "das": 110})
    b2_selected.sort(key=lambda x: (x["difficultyScore"], -x["learnerValue"], x["frequencyRank"]))
    level1 = [{**x, "level": 1} for x in b2_selected[:400]]
    level2 = [{**x, "level": 2} for x in b2_selected[400:]]

    advanced_selected = choose(advanced, 250, {"der": 35, "die": 90, "das": 25})
    advanced_selected.sort(key=lambda x: (-x["learnerValue"], x["frequencyRank"], x["noun"].casefold()))
    level3 = [{**x, "level": 3} for x in advanced_selected]
    return level1 + level2 + level3, {
        "eligibleB2": len(b2), "eligibleC1": len(c1), "eligibleAdvancedC1": len(advanced),
    }


def curated_report(selected, reject, pool_stats, candidate_count):
    _original_report(selected, reject, pool_stats, candidate_count)
    report_path = ROOT / "docs" / "v2-2-bridge-corpus.md"
    text = report_path.read_text(encoding="utf-8")
    text = text.replace(
        "6. Sort by wordhoard frequency rank. Select the first 750 eligible B2 nouns and first 250 eligible C1 nouns.\n7. Assign the first 400 B2 nouns to Intermediate, the next 350 B2 nouns to Upper Intermediate, and the 250 C1 nouns to Advanced.",
        "6. Rank eligible B2 nouns by learner value: general-use frequency plus abstract/institutional semantics and productive morphology, with penalties for concrete props, person labels, entertainment/slang vocabulary, and transparent loanwords. Article-diversity targets are soft and never override lexical quality.\n7. Select the strongest 750 B2 nouns, then split them by a separate difficulty score into 400 Intermediate and 350 Upper Intermediate nouns. For Advanced, require a C1 source estimate, frequency rank at least 10,500, and formal/abstract lexical evidence; select the strongest 250 by learner value."
    )
    low = sorted(selected, key=lambda x: (x["learnerValue"], -x["frequencyRank"]))[:30]
    text += "\n## Editorial QA\n\n"
    for level in (1, 2, 3):
        items = [x for x in selected if x["level"] == level]
        vals = [x["learnerValue"] for x in items]
        diffs = [x["difficultyScore"] for x in items]
        text += f"- Level {level}: learner-value {min(vals)}–{max(vals)}; difficulty {min(diffs):.2f}–{max(diffs):.2f}\n"
    text += "\n### Lowest learner-value selections\n\n"
    for item in low:
        text += f"- **{item['article']} {item['noun']}** — {item['gloss']} (value {item['learnerValue']}, rank {item['frequencyRank']:,}, {item['cefrEstimate']})\n"
    report_path.write_text(text, encoding="utf-8")

    machine_path = ROOT / "content" / "bridge-corpus-report.json"
    machine = json.loads(machine_path.read_text(encoding="utf-8"))
    machine["learnerValueRanges"] = {
        str(level): [min(x["learnerValue"] for x in selected if x["level"] == level), max(x["learnerValue"] for x in selected if x["level"] == level)]
        for level in (1, 2, 3)
    }
    machine["lowestLearnerValue"] = [
        {k: x[k] for k in ("id", "noun", "article", "level", "cefrEstimate", "frequencyRank", "gloss", "learnerValue")}
        for x in low
    ]
    machine_path.write_text(json.dumps(machine, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


base.select_glosses = select_two_glosses
base.build_candidates = curated_candidates
base.assign_levels = curated_assign_levels
base.write_report = curated_report
base.main()
