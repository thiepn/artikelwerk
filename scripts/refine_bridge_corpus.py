#!/usr/bin/env python3
"""Editorial suitability layer for the deterministic V2-2 source generator.

wordhoard's German B2/C1 values are rank-calibrated estimates. This layer prevents
rare-but-basic subtitle nouns from becoming Artikelwerk's "Advanced" vocabulary.
It keeps source verification/gender/translation filtering in generate_bridge_corpus.py
and adds a learner-facing usefulness/basicness screen plus a formal lexical-evidence
gate for the C1-derived Level 3.
"""
from __future__ import annotations

import re
from pathlib import Path

import generate_bridge_corpus as base

TOO_BASIC_GLOSS_FRAGMENTS = {
    "birthday party", "valentine's day", "saint valentine", "phone book", "telephone directory",
    "elementary school", "grade school", "primary school", "steering wheel", "sleeping pill",
    "bald head", "handbag", "flashlight", "torch", "elevator", "lift", "bathtub", "tub",
    "jacket", "collar", "lobster", "dinosaur", "cat", "tomcat", "grape", "silverware",
    "silver medal", "radio", "statue", "pirate", "samurai", "hippie", "satan", "devil",
    "world war", "birthday", "christmas", "easter", "new year's", "march", "april", "january",
    "february", "june", "july", "august", "september", "october", "november", "december",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "grandmother", "grandfather", "grandma", "grandpa", "uncle", "aunt", "cousin",
    "boyfriend", "girlfriend", "husband", "wife", "son", "daughter", "brother", "sister",
    "shirt", "shoe", "sock", "trousers", "pants", "skirt", "dress", "hat", "coat",
    "fork", "spoon", "knife", "plate", "cup", "bottle", "chair", "table", "bed", "sofa",
    "apple", "banana", "orange", "potato", "tomato", "bread", "cheese", "beer", "wine",
    "chicken", "cow", "pig", "mouse", "rabbit", "lion", "tiger", "elephant", "monkey",
    "motorcycle", "bicycle", "bike", "taxi", "van", "delivery van", "bus stop", "airport",
}

# Exact source-frequency artefacts / low-value subtitle items found in rendered audits.
NOISY_NOUNS = {
    "Samurai", "Satan", "Dinosaurier", "Valentinstag", "Geburtstagsparty", "Telefonbuch",
    "Grundschule", "Handtasche", "Taschenlampe", "Fahrstuhl", "Hummer", "Hippie",
    "Weltkrieg", "Pirat", "Kater", "März", "Jackett", "Glatze", "Schlaftablette",
    "Orgasmus", "Araber", "Muffin",
}

# These suffixes are strong evidence of genuinely abstract/formal lexical formation.
# Deliberately omitted: generic -ur/-ie/-ik/-ment, because concrete compounds and
# everyday loans can accidentally end that way (e.g. Spritztour).
STRONG_ADVANCED_SUFFIXES = (
    "ung", "heit", "keit", "schaft", "tion", "sion", "tät", "ität", "ismus", "nis",
    "tum", "anz", "enz", "logie", "graphie", "nahme", "wesen", "igkeit", "barkeit", "lichkeit",
)

ABSTRACT_GLOSS_TERMS = {
    "ability", "access", "acceptance", "agreement", "analysis", "approach", "assessment",
    "assumption", "authority", "behavior", "behaviour", "capacity", "circumstance", "claim",
    "communication", "condition", "consequence", "consideration", "constraint", "context",
    "contribution", "criterion", "debate", "decision", "deficiency", "demand", "development",
    "difference", "discretion", "distribution", "effect", "equality", "evaluation", "evidence",
    "extent", "factor", "framework", "function", "impact", "implementation", "influence",
    "intention", "interpretation", "limitation", "majority", "measure", "method", "minority",
    "obligation", "opposition", "permission", "policy", "principle", "procedure", "process",
    "proposal", "regulation", "relation", "relationship", "requirement", "research",
    "responsibility", "restriction", "scope", "strategy", "structure", "support", "tendency",
    "transition", "treatment", "uncertainty", "validity", "value", "variation",
}
ROLE_GLOSS_TERMS = {
    "pastor", "prophet", "dean", "communist", "priest", "bishop", "king", "queen", "soldier",
    "officer", "captain", "detective", "gangster", "criminal", "prisoner", "detainee",
}


def basic_or_noise(item) -> str | None:
    if item["noun"] in NOISY_NOUNS:
        return "learner_suitability_explicit_noise"
    gloss = item["gloss"].casefold()
    for phrase in TOO_BASIC_GLOSS_FRAGMENTS:
        if re.search(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", gloss):
            return "learner_suitability_too_basic"
    return None


def gloss_words(item) -> set[str]:
    return set(re.findall(r"[a-z]+", item["gloss"].casefold()))


def formal_advanced_evidence(item) -> bool:
    noun = item["noun"].casefold()
    return noun.endswith(STRONG_ADVANCED_SUFFIXES) or bool(gloss_words(item) & ABSTRACT_GLOSS_TERMS)


def complexity_score(item) -> int:
    noun = item["noun"].casefold()
    words = gloss_words(item)
    score = 0
    if noun.endswith(STRONG_ADVANCED_SUFFIXES):
        score += 3
    if len(item["noun"]) >= 10:
        score += 1
    if len(item["noun"]) >= 15:
        score += 1
    if words & ABSTRACT_GLOSS_TERMS:
        score += 3
    if words & ROLE_GLOSS_TERMS:
        score -= 2
    return score


# Keep only the strongest two Wiktionary glosses. This removes obscure third senses
# and old extraction noise without inventing translations.
_original_select_glosses = base.select_glosses
base.select_glosses = lambda raw: _original_select_glosses(raw)[:2]
_original_build_candidates = base.build_candidates


def curated_candidates(wordhoard, translations, challenge_nouns, challenge_ids):
    candidates, reject = _original_build_candidates(wordhoard, translations, challenge_nouns, challenge_ids)
    kept = []
    for item in candidates:
        reason = basic_or_noise(item)
        if reason:
            reject[reason] += 1
            continue
        kept.append({**item, "complexityScore": complexity_score(item)})
    return kept, reject


def curated_assign_levels(candidates):
    b2 = [c for c in candidates if c["cefrEstimate"] == "B2"]
    c1 = [c for c in candidates if c["cefrEstimate"] == "C1"]
    if len(b2) < 750:
        base.die(f"Need at least 750 curated B2 nouns; found {len(b2)}")

    advanced = [
        c for c in c1
        if formal_advanced_evidence(c) and c["complexityScore"] >= 3
    ]
    if len(advanced) < 250:
        base.die(f"Need at least 250 formally advanced C1 nouns; found {len(advanced)}")

    selected = [{**item, "level": 1} for item in b2[:400]]
    selected += [{**item, "level": 2} for item in b2[400:750]]
    selected += [{**item, "level": 3} for item in advanced[:250]]
    return selected, {
        "eligibleB2": len(b2),
        "eligibleC1": len(c1),
        "eligibleAdvancedC1": len(advanced),
    }


base.build_candidates = curated_candidates
base.assign_levels = curated_assign_levels
base.main()

# Clarify the second-stage editorial gate in the generated methodology report.
report_path = Path(base.ROOT) / "docs" / "v2-2-bridge-corpus.md"
report = report_path.read_text(encoding="utf-8")
report = report.replace(
    "5. Exclude names/special-name-only usages, malformed orthography, selected subtitle-noise categories, exact Challenge noun/ID overlaps, and duplicate Bridge nouns/IDs.\n"
    "6. Sort by wordhoard frequency rank. Select the first 750 eligible B2 nouns and first 250 eligible C1 nouns.\n"
    "7. Assign the first 400 B2 nouns to Intermediate, the next 350 B2 nouns to Upper Intermediate, and the 250 C1 nouns to Advanced.",
    "5. Exclude names/special-name-only usages, malformed orthography, selected subtitle-noise/basic-concept categories, exact Challenge noun/ID overlaps, and duplicate Bridge nouns/IDs.\n"
    "6. Keep the B2 pool frequency-led for Intermediate/Upper Intermediate. Limit every gloss to the two strongest clean source translations.\n"
    "7. For Advanced, require a C1 source estimate **plus formal lexical evidence**: strong abstract/derivational morphology or an abstract/formal semantic signal. Rarity, word length, and polysemy alone cannot qualify a noun as Advanced.\n"
    "8. Assign the first 400 curated B2 nouns to Intermediate, the next 350 to Upper Intermediate, and the first 250 formally qualified C1 nouns to Advanced."
)
report_path.write_text(report, encoding="utf-8")
