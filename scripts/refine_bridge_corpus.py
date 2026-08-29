#!/usr/bin/env python3
"""Learner-value curation layer for Artikelwerk V2-2.

The base generator supplies reproducible source acquisition, B2/C1 frequency
estimates, single-gender corroboration, clean Wiktionary translation availability,
and Challenge de-duplication. This layer ranks the eligible pool for learner value
and separates usefulness from difficulty so subtitle rarity cannot masquerade as
advanced vocabulary.

Final composition:
- Level 1: 400 B2 nouns
- Level 2: 200 stronger B2 + 150 accessible, useful C1 nouns
- Level 3: 250 upper-C1 nouns with formal/abstract lexical evidence
- total: 600 B2 + 400 C1
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import generate_bridge_corpus as base

ROOT = Path(__file__).resolve().parents[1]
ADVANCED_MIN_FREQUENCY_RANK = 10500
TRANSITION_MAX_FREQUENCY_RANK = 14000
TRANSITION_MIN_LEARNER_VALUE = 5

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
    "garlic", "hazelnut", "sparrow", "north", "fur", "pelt", "gin", "jet", "outfit",
    "omelet", "omelette", "peach", "raccoon", "headphone", "bridesmaid", "villager",
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
    "Pisse", "Drive", "Gin", "Jet", "Outfit", "Nord", "Spatz", "Nuss", "Brei",
    "Omelett", "Waschbär", "Pfirsich", "Kopfhörer", "Brautjungfer", "Dorfbewohner", "Zeitreise",
}
BLOCKED_GLOSS_TERMS = {
    "bimbo", "dyke", "sissy", "wimp", "shit", "crap", "piss", "whore", "junkie", "klingon",
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
    "thread", "thorn", "rock", "cave", "silk", "tobacco", "airfield", "backbone", "spine",
}
PERSON_GLOSS_TERMS = {
    "actor", "actress", "attacker", "assassin", "bartender", "bishop", "blonde", "butler",
    "captain", "christian", "communist", "creator", "dancer", "dean", "detective", "employee",
    "executioner", "farmer", "gangster", "host", "investigator", "italian", "lawyer", "mexican",
    "murderer", "officer", "pastor", "patriot", "priest", "prisoner", "prophet", "rescuer",
    "sailor", "soldier", "spaniard", "speaker", "technician", "veterinarian", "woman", "man",
    "rector", "principal", "supervisor", "observer", "boxer", "sultan", "sheik", "sheikh",
    "inventor", "banker", "critic", "publisher", "viking", "referee", "umpire", "empress",
}
ENTERTAINMENT_GLOSS_TERMS = {
    "ghost", "werewolf", "witchcraft", "wizardry", "magic", "superhero", "vampire", "zombie",
    "movie", "film star", "tournament", "parade", "cocktail", "bingo", "autograph", "video game",
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
    score -= 8 if s["concrete"] else 0
    score -= 8 if s["person"] else 0
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


def formal_advanced_evidence(item) -> bool:
    s = signals(item)
    return bool(s["abstract_suffix"] or s["formal_compound"] or s["abstract"] or s["institutional"])


def choose(pool, count: int):
    ranked = sorted(pool, key=lambda x: (-x["learnerValue"], x["frequencyRank"], x["noun"].casefold()))
    if len(ranked) < count:
        base.die(f"Could not select {count} quality candidates; found {len(ranked)}")
    return ranked[:count]


_original_build = base.build_candidates
_original_report = base.write_report
_original_corpus_writer = base.write_corpus
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
    transition = [
        c for c in c1
        if c["frequencyRank"] < TRANSITION_MAX_FREQUENCY_RANK
        and c["learnerValue"] >= TRANSITION_MIN_LEARNER_VALUE
    ]
    advanced_pool = [
        c for c in c1
        if c["frequencyRank"] >= ADVANCED_MIN_FREQUENCY_RANK and formal_advanced_evidence(c)
    ]
    if len(b2) < 600:
        base.die(f"Need at least 600 curated B2 nouns; found {len(b2)}")
    if len(transition) < 150:
        base.die(f"Need at least 150 useful accessible C1 transition nouns; found {len(transition)}")

    b2_selected = choose(b2, 600)
    b2_selected.sort(key=lambda x: (x["difficultyScore"], -x["learnerValue"], x["frequencyRank"]))
    level1 = [{**x, "level": 1} for x in b2_selected[:400]]
    level2_b2 = [{**x, "level": 2} for x in b2_selected[400:]]

    transition_selected = sorted(
        transition,
        key=lambda x: (x["difficultyScore"], -x["learnerValue"], x["frequencyRank"], x["noun"].casefold())
    )[:150]
    transition_ids = {x["id"] for x in transition_selected}
    advanced = [x for x in advanced_pool if x["id"] not in transition_ids]
    if len(advanced) < 250:
        base.die(f"Need at least 250 distinct formally qualified Advanced nouns; found {len(advanced)}")
    level2_c1 = [{**x, "level": 2} for x in transition_selected]
    level3 = [{**x, "level": 3} for x in choose(advanced, 250)]

    return level1 + level2_b2 + level2_c1 + level3, {
        "eligibleB2": len(b2),
        "eligibleC1": len(c1),
        "eligibleTransitionC1": len(transition),
        "eligibleAdvancedC1": len(advanced_pool),
        "advancedMinFrequencyRank": ADVANCED_MIN_FREQUENCY_RANK,
        "transitionMaxFrequencyRank": TRANSITION_MAX_FREQUENCY_RANK,
        "transitionMinLearnerValue": TRANSITION_MIN_LEARNER_VALUE,
    }


def curated_validate(selected, challenge_nouns, challenge_ids):
    if len(selected) != 1000:
        base.die(f"Expected exactly 1000 selected Bridge nouns, found {len(selected)}")
    ids = [x["id"] for x in selected]
    nouns = [x["noun"].casefold() for x in selected]
    if len(set(ids)) != 1000 or len(set(nouns)) != 1000:
        base.die("Bridge IDs/nouns are not unique")
    if set(ids) & challenge_ids or set(nouns) & challenge_nouns:
        base.die("Bridge overlaps Challenge")
    levels = Counter(x["level"] for x in selected)
    cefr = Counter(x["cefrEstimate"] for x in selected)
    if levels != Counter({1: 400, 2: 350, 3: 250}):
        base.die(f"Unexpected Bridge level distribution: {dict(levels)}")
    if cefr != Counter({"B2": 600, "C1": 400}):
        base.die(f"Unexpected Bridge CEFR-estimate distribution: {dict(cefr)}")
    if any(x["cefrEstimate"] != "B2" for x in selected if x["level"] == 1):
        base.die("Bridge Level 1 must remain B2-estimated")
    level2 = [x for x in selected if x["level"] == 2]
    level2_cefr = Counter(x["cefrEstimate"] for x in level2)
    if level2_cefr != Counter({"B2": 200, "C1": 150}):
        base.die(f"Unexpected Level 2 B2/C1 composition: {dict(level2_cefr)}")
    if any(x["learnerValue"] < TRANSITION_MIN_LEARNER_VALUE for x in level2 if x["cefrEstimate"] == "C1"):
        base.die("Bridge C1 transition contains a low learner-value noun")
    if any(x["cefrEstimate"] != "C1" or x["frequencyRank"] < ADVANCED_MIN_FREQUENCY_RANK for x in selected if x["level"] == 3):
        base.die("Bridge Level 3 Advanced source gate failed")
    articles = Counter(x["article"] for x in selected)
    if set(articles) != base.VALID_ARTICLES or min(articles.values()) < 100:
        base.die(f"Article coverage is too narrow after quality selection: {dict(articles)}")


def curated_write_corpus(selected):
    _original_corpus_writer(selected)
    path = ROOT / "bridge-corpus.js"
    text = path.read_text(encoding="utf-8")
    meta = {
        "schema": 1,
        "count": 1000,
        "levelCounts": {"1": 400, "2": 350, "3": 250},
        "cefrEstimateCounts": dict(Counter(x["cefrEstimate"] for x in selected)),
        "wordhoardRelease": base.WORDHOARD_RELEASE,
        "wordhoardSha256": base.WORDHOARD_SHA256,
        "translationSourceCommit": base.WIKT_PARSER_COMMIT,
    }
    text = re.sub(
        r"window\.ARTIKELWERK_BRIDGE_CORPUS_META=Object\.freeze\([^\n]+\);",
        f"window.ARTIKELWERK_BRIDGE_CORPUS_META=Object.freeze({base.compact_json(meta)});",
        text,
    )
    path.write_text(text, encoding="utf-8")


def curated_report(selected, reject, pool_stats, candidate_count):
    _original_report(selected, reject, pool_stats, candidate_count)
    report_path = ROOT / "docs" / "v2-2-bridge-corpus.md"
    text = report_path.read_text(encoding="utf-8")
    text = text.replace("- Source CEFR estimates: **750 B2 / 250 C1**", "- Source CEFR estimates: **600 B2 / 400 C1**")
    text = text.replace(
        "6. Sort by wordhoard frequency rank. Select the first 750 eligible B2 nouns and first 250 eligible C1 nouns.\n7. Assign the first 400 B2 nouns to Intermediate, the next 350 B2 nouns to Upper Intermediate, and the 250 C1 nouns to Advanced.",
        "6. Rank eligible nouns by learner value: general-use frequency plus abstract/institutional semantics and productive morphology, with penalties for concrete props, person labels, entertainment/slang vocabulary, and transparent loanwords. Article balance is measured after selection and never overrides lexical quality.\n7. Select 600 high-value B2 nouns: the easier 400 become Intermediate and the stronger 200 enter Upper Intermediate. Add 150 accessible C1 nouns to Upper Intermediate only if learner value is at least 5 and source frequency rank is below 14,000. Advanced contains 250 distinct C1 nouns with frequency rank at least 10,500 plus formal/abstract lexical evidence."
    )
    low = sorted(selected, key=lambda x: (x["learnerValue"], -x["frequencyRank"]))[:30]
    text += "\n## Editorial QA\n\n"
    for level in (1, 2, 3):
        items = [x for x in selected if x["level"] == level]
        vals = [x["learnerValue"] for x in items]
        diffs = [x["difficultyScore"] for x in items]
        mix = Counter(x["cefrEstimate"] for x in items)
        text += f"- Level {level}: learner-value {min(vals)}–{max(vals)}; difficulty {min(diffs):.2f}–{max(diffs):.2f}; CEFR proxy {dict(mix)}\n"
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
    machine["levelCefrMix"] = {
        str(level): dict(Counter(x["cefrEstimate"] for x in selected if x["level"] == level))
        for level in (1, 2, 3)
    }
    machine["lowestLearnerValue"] = [
        {k: x[k] for k in ("id", "noun", "article", "level", "cefrEstimate", "frequencyRank", "gloss", "learnerValue")}
        for x in low
    ]
    machine_path.write_text(json.dumps(machine, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


base.select_glosses = lambda raw: _original_glosses(raw)[:2]
base.build_candidates = curated_candidates
base.assign_levels = curated_assign_levels
base.validate_selected = curated_validate
base.write_corpus = curated_write_corpus
base.write_report = curated_report
base.main()
