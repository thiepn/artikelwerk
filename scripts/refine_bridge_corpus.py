#!/usr/bin/env python3
"""Editorial suitability layer for the deterministic V2-2 source generator.

wordhoard's German B2/C1 values are rank-calibrated estimates. This layer prevents
rare-but-basic subtitle nouns from becoming Artikelwerk's "Advanced" vocabulary.
It keeps source verification/gender/translation filtering in generate_bridge_corpus.py
and adds a learner-facing usefulness/basicness screen plus a lexical-complexity gate
for the C1-derived Level 3.
"""
from __future__ import annotations

import re
from collections import Counter

import generate_bridge_corpus as base

# Clear low/intermediate everyday concepts that become artificially "difficult" only
# because a particular lexical item is uncommon in subtitle dialogue. This list is
# English-gloss based so transparent compounds such as Telefonbuch are caught without
# trying to reverse-engineer German compound boundaries.
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

# Proper-name / genre / subtitle artefacts that can survive generic grammatical filters.
NOISY_NOUNS = {
    "Samurai", "Satan", "Dinosaurier", "Valentinstag", "Geburtstagsparty", "Telefonbuch",
    "Grundschule", "Handtasche", "Taschenlampe", "Fahrstuhl", "Hummer", "Hippie",
    "Weltkrieg", "Pirat", "Kater", "März", "Jackett", "Glatze", "Schlaftablette",
}

# Derivational morphology and abstract-domain vocabulary are useful evidence that a
# C1-rank item is genuinely advanced rather than just an uncommon concrete object.
COMPLEX_SUFFIXES = (
    "ung", "heit", "keit", "schaft", "tion", "sion", "tät", "ität", "ismus", "nis",
    "tum", "anz", "enz", "ik", "ie", "ur", "ment", "logie", "graphie", "nahme",
    "wesen", "igkeit", "barkeit", "lichkeit",
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
        # Whole-word-ish matching prevents e.g. cat matching "allocation".
        if re.search(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", gloss):
            return "learner_suitability_too_basic"
    return None


def complexity_score(item) -> int:
    noun = item["noun"].casefold()
    gloss_words = set(re.findall(r"[a-z]+", item["gloss"].casefold()))
    score = 0
    if noun.endswith(COMPLEX_SUFFIXES):
        score += 3
    if len(item["noun"]) >= 9:
        score += 1
    if len(item["noun"]) >= 14:
        score += 1
    if gloss_words & ABSTRACT_GLOSS_TERMS:
        score += 2
    if gloss_words & ROLE_GLOSS_TERMS:
        score -= 2
    if len(item["glosses"]) >= 2:
        score += 1  # polysemy/lexical breadth is often useful at higher levels
    return score


_original_build_candidates = base.build_candidates


def curated_candidates(wordhoard, translations, challenge_nouns, challenge_ids):
    candidates, reject = _original_build_candidates(wordhoard, translations, challenge_nouns, challenge_ids)
    kept = []
    for item in candidates:
        reason = basic_or_noise(item)
        if reason:
            reject[reason] += 1
            continue
        item = {**item, "complexityScore": complexity_score(item)}
        kept.append(item)
    return kept, reject


def curated_assign_levels(candidates):
    b2 = [c for c in candidates if c["cefrEstimate"] == "B2"]
    c1 = [c for c in candidates if c["cefrEstimate"] == "C1"]
    if len(b2) < 750:
        base.die(f"Need at least 750 curated B2 nouns; found {len(b2)}")

    # Advanced must be C1-estimated *and* show additional lexical complexity.
    advanced = [c for c in c1 if c["complexityScore"] >= 2]
    if len(advanced) < 250:
        base.die(f"Need at least 250 lexically complex C1 nouns; found {len(advanced)}")

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
