#!/usr/bin/env python3
"""Generate reproducible, proposal-only successors for V2-3 Bridge removals.

This script does not mutate the checked-in Bridge corpus. It rebuilds the eligible
source pool from the same pinned Wordhoard and German-Wiktionary inputs used by
V2-2, removes every currently installed Bridge noun, preserves each rejected
slot's Level/CEFR contract, and emits unique recommended successors plus
alternatives for editorial review.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import generate_bridge_corpus as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content" / "bridge-replacement-candidates.json"
ADVANCED_MIN_FREQUENCY_RANK = 10500
TRANSITION_MAX_FREQUENCY_RANK = 14000
TRANSITION_MIN_LEARNER_VALUE = 5
SHORTLIST_SIZE = 8

TOO_BASIC_GLOSS_FRAGMENTS = {
    "birthday party", "valentine's day", "phone book", "telephone directory", "elementary school",
    "grade school", "primary school", "steering wheel", "sleeping pill", "bald head", "handbag",
    "flashlight", "torch", "elevator", "lift", "bathtub", "jacket", "collar", "lobster",
    "dinosaur", "cat", "tomcat", "grape", "silverware", "silver medal", "radio", "statue",
    "pirate", "samurai", "hippie", "birthday", "christmas", "easter", "monday", "tuesday",
    "wednesday", "thursday", "friday", "saturday", "sunday", "grandmother", "grandfather",
    "grandma", "grandpa", "uncle", "aunt", "cousin", "boyfriend", "girlfriend", "husband",
    "wife", "son", "daughter", "brother", "sister", "shirt", "shoe", "sock", "trousers",
    "pants", "skirt", "dress", "hat", "coat", "fork", "spoon", "knife", "plate", "cup",
    "bottle", "chair", "table", "bed", "sofa", "apple", "banana", "orange", "potato",
    "tomato", "bread", "cheese", "beer", "wine", "chicken", "cow", "pig", "mouse",
    "rabbit", "lion", "tiger", "elephant", "monkey", "motorcycle", "bicycle", "bike",
    "taxi", "delivery van", "bus stop", "airport", "vacuum cleaner", "hoover", "evening meal",
    "pancake", "popcorn", "muffin", "doughnut", "donut", "lipstick", "mattress", "earring",
    "garlic", "hazelnut", "sparrow", "fur", "pelt", "gin", "jet", "outfit", "omelet",
    "omelette", "peach", "raccoon", "headphone", "bridesmaid", "villager",
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
    "Pisse", "Drive", "Gin", "Jet", "Outfit", "Nord", "Spatz", "Nuss", "Brei", "Omelett",
    "Waschbär", "Pfirsich", "Kopfhörer", "Brautjungfer", "Dorfbewohner", "Zeitreise",
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
    return any(re.search(rf"(?<![a-z]){re.escape(fragment)}(?![a-z])", low) for fragment in fragments)


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


def parse_bridge_rows() -> list[list]:
    text = (ROOT / "bridge-corpus.js").read_text(encoding="utf-8")
    marker = "window.ARTIKELWERK_BRIDGE_CORPUS=Object.freeze("
    start = text.find(marker)
    if start < 0:
        base.die("Could not locate Bridge corpus payload")
    start += len(marker)
    end = text.find(");\nwindow.ARTIKELWERK_BRIDGE_CORPUS_META", start)
    if end < 0:
        base.die("Could not locate Bridge corpus payload terminator")
    rows = json.loads(text[start:end])
    if not isinstance(rows, list) or len(rows) != 1000:
        base.die(f"Expected 1000 Bridge rows, found {len(rows) if isinstance(rows, list) else 'invalid'}")
    return rows


def merged_review_decisions() -> dict[str, dict]:
    editorial = json.loads((ROOT / "content" / "bridge-editorial-review.json").read_text(encoding="utf-8"))
    lower = json.loads((ROOT / "content" / "bridge-b1-lower-bound-review.json").read_text(encoding="utf-8"))
    merged = {key: dict(value) for key, value in editorial.get("entries", {}).items()}
    for key, value in lower.get("entries", {}).items():
        merged[key] = {**merged.get(key, {}), **value}
    return merged


def bucket_key(level: int, cefr: str) -> str:
    return f"L{level}-{cefr}"


def eligible_for_slot(candidate, level: int, cefr: str) -> bool:
    if candidate["cefrEstimate"] != cefr:
        return False
    if level == 1:
        return cefr == "B2"
    if level == 2 and cefr == "B2":
        return True
    if level == 2 and cefr == "C1":
        return candidate["frequencyRank"] < TRANSITION_MAX_FREQUENCY_RANK and candidate["learnerValue"] >= TRANSITION_MIN_LEARNER_VALUE
    if level == 3:
        return cefr == "C1" and candidate["frequencyRank"] >= ADVANCED_MIN_FREQUENCY_RANK and formal_advanced_evidence(candidate)
    return False


def candidate_view(item) -> dict:
    return {
        "id": item["id"],
        "noun": item["noun"],
        "article": item["article"],
        "cefrEstimate": item["cefrEstimate"],
        "frequencyRank": item["frequencyRank"],
        "frequencyCount": item["frequencyCount"],
        "gloss": item["gloss"],
        "group": item["group"],
        "learnerValue": item["learnerValue"],
        "difficultyScore": round(item["difficultyScore"], 3),
        "formalAdvancedEvidence": formal_advanced_evidence(item),
    }


def main() -> None:
    rows = parse_bridge_rows()
    row_by_id = {row[0]: row for row in rows}
    current_ids = set(row_by_id)
    current_nouns = {str(row[1]).casefold() for row in rows}
    decisions = merged_review_decisions()
    replacement_ids = sorted(key for key, value in decisions.items() if value.get("decision") == "replace")
    if not replacement_ids:
        base.die("No V2-3 replacement decisions found")

    challenge = base.parse_challenge(base.INDEX.read_text(encoding="utf-8"))
    challenge_ids = {row[0] for row in challenge}
    challenge_nouns = {row[1].casefold() for row in challenge}

    print("Downloading pinned Wordhoard source...")
    wordhoard = base.download(base.WORDHOARD_URL)
    digest = hashlib.sha256(wordhoard).hexdigest()
    if digest != base.WORDHOARD_SHA256:
        base.die(f"wordhoard SHA-256 mismatch: expected {base.WORDHOARD_SHA256}, got {digest}")

    print("Downloading pinned German Wiktionary extraction...")
    wikt = base.download(base.WIKT_TRANSLATIONS_URL)
    blob_sha = base.git_blob_sha(wikt)
    if blob_sha != base.WIKT_TRANSLATIONS_BLOB_SHA:
        base.die(f"Wiktionary extraction Git blob mismatch: expected {base.WIKT_TRANSLATIONS_BLOB_SHA}, got {blob_sha}")
    translations = base.load_translation_dictionary(wikt)

    candidates, source_reject = base.build_candidates(wordhoard, translations, challenge_nouns, challenge_ids)
    curated = []
    curation_reject = Counter()
    for item in candidates:
        reason = hard_reject(item)
        if reason:
            curation_reject[reason] += 1
            continue
        curated.append({**item, "learnerValue": learner_value(item), "difficultyScore": difficulty_score(item)})

    all_by_id = {item["id"]: item for item in curated}
    unused = [
        item for item in curated
        if item["id"] not in current_ids and item["noun"].casefold() not in current_nouns
    ]

    slots = []
    bucket_counts = Counter()
    for rejected_id in replacement_ids:
        row = row_by_id.get(rejected_id)
        if row is None:
            base.die(f"Replacement decision references missing Bridge id: {rejected_id}")
        level = int(row[3])
        cefr = row[10]["cefrEstimate"]
        source_item = all_by_id.get(rejected_id)
        slot = {
            "id": rejected_id,
            "noun": row[1],
            "article": row[2],
            "level": level,
            "cefrEstimate": cefr,
            "bucket": bucket_key(level, cefr),
            "reason": decisions[rejected_id].get("reason"),
            "lowerBound": decisions[rejected_id].get("lowerBound"),
            "lowerBoundEvidenceType": decisions[rejected_id].get("evidenceType"),
            "sourceLearnerValue": source_item["learnerValue"] if source_item else None,
            "sourceDifficultyScore": round(source_item["difficultyScore"], 3) if source_item else None,
        }
        slots.append(slot)
        bucket_counts[slot["bucket"]] += 1

    eligible_counts = Counter()
    for slot in slots:
        key = slot["bucket"]
        eligible_counts[key] = sum(1 for item in unused if eligible_for_slot(item, slot["level"], slot["cefrEstimate"]))
    for key, needed in bucket_counts.items():
        if eligible_counts[key] < needed:
            base.die(f"Insufficient unused candidate pool for {key}: need {needed}, found {eligible_counts[key]}")

    priority = {"L3-C1": 0, "L2-C1": 1, "L2-B2": 2, "L1-B2": 3}
    reserved: set[str] = set()
    recommendations = {}
    for slot in sorted(slots, key=lambda item: (priority.get(item["bucket"], 9), -(item["sourceDifficultyScore"] or 0), item["id"])):
        eligible = [item for item in unused if eligible_for_slot(item, slot["level"], slot["cefrEstimate"])]
        source_value = slot["sourceLearnerValue"] if slot["sourceLearnerValue"] is not None else TRANSITION_MIN_LEARNER_VALUE
        source_difficulty = slot["sourceDifficultyScore"] if slot["sourceDifficultyScore"] is not None else 0
        eligible.sort(key=lambda item: (
            0 if item["learnerValue"] >= source_value else 1,
            -item["learnerValue"],
            abs(item["difficultyScore"] - source_difficulty),
            item["frequencyRank"],
            item["noun"].casefold(),
        ))
        shortlist = eligible[:SHORTLIST_SIZE]
        recommended = next((item for item in eligible if item["id"] not in reserved), None)
        if recommended is None:
            base.die(f"Could not allocate a unique proposal for {slot['id']}")
        reserved.add(recommended["id"])
        recommendations[slot["id"]] = {
            "recommended": candidate_view(recommended),
            "alternatives": [candidate_view(item) for item in shortlist if item["id"] != recommended["id"]][:SHORTLIST_SIZE - 1],
        }

    output = {
        "schema": 1,
        "phase": "V2-3",
        "status": "proposal-only-not-editorially-approved",
        "sourcePins": {
            "wordhoardRelease": base.WORDHOARD_RELEASE,
            "wordhoardSha256": base.WORDHOARD_SHA256,
            "wiktionaryParserCommit": base.WIKT_PARSER_COMMIT,
            "wiktionaryBlobSha": base.WIKT_TRANSLATIONS_BLOB_SHA,
        },
        "constraints": {
            "preserveLevelCounts": {"1": 400, "2": 350, "3": 250},
            "preserveCefrCounts": {"B2": 600, "C1": 400},
            "preserveLevel2CefrMix": {"B2": 200, "C1": 150},
            "advancedMinFrequencyRank": ADVANCED_MIN_FREQUENCY_RANK,
            "transitionMaxFrequencyRank": TRANSITION_MAX_FREQUENCY_RANK,
            "transitionMinLearnerValue": TRANSITION_MIN_LEARNER_VALUE,
            "currentBridgeAndChallengeExcluded": True,
            "automaticAcceptance": False,
        },
        "summary": {
            "replacementSlots": len(slots),
            "bucketCounts": dict(sorted(bucket_counts.items())),
            "eligibleUnusedByBucket": dict(sorted(eligible_counts.items())),
            "curatedUnusedPool": len(unused),
            "uniqueRecommendations": len(reserved),
            "sourceCandidateRejects": dict(source_reject),
            "curationRejects": dict(curation_reject),
        },
        "slots": slots,
        "recommendations": recommendations,
    }
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"V2-3 replacement proposal passed: {len(slots)} rejected slots, "
        f"{len(reserved)} unique source-certified successor proposals, buckets {dict(bucket_counts)}."
    )


if __name__ == "__main__":
    main()
