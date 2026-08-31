#!/usr/bin/env python3
"""Strict V2-3 replacement proposer.

The V2-2 learner-value heuristic is useful for ranking, but the first V2-3
proposal run proved that it is not an editorial quality gate. This successor
requires an abstract/formal/institutional bridge signal, rejects person labels,
entertainment vocabulary and concrete-prop vocabulary, imposes a learner-value
floor, and blocks known lower-bound/noise terms before proposing anything.

Output remains proposal-only. No candidate is accepted into the release corpus
without explicit editorial review.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter

import generate_bridge_corpus as base
import propose_bridge_replacements as legacy

OUT = legacy.OUT
MIN_LEARNER_VALUE = 6
SHORTLIST_SIZE = 10

# Small project-specific denylist. It deliberately contains only terms surfaced
# by the source/review process; it is not a redistributed external word list.
STRICT_EXCLUDED_NOUNS = {
    "Neger", "Negerin", "Zigeuner", "Zigeunerin",
    "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
    "September", "Oktober", "November", "Dezember",
    "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag",
    "Wanne", "Köter", "Senf", "Sattel", "Speer", "Mühle", "Sperma",
}
STRICT_BLOCKED_GLOSS_TERMS = {
    "negro", "gypsy", "mutt", "cur", "mustard", "saddle", "spear", "javelin", "tub",
    "january", "february", "march", "april", "june", "july", "august", "september",
    "october", "november", "december",
}

# Add missing institutional/abstract concepts that the V2-2 keyword layer did
# not recognize well enough. These are generic semantic categories, not a word list.
EXTRA_ABSTRACT_TERMS = {
    "justice", "judiciary", "jurisdiction", "legislation", "governance", "compliance",
    "accounting", "financing", "funding", "coverage", "insurance", "liability", "ownership",
    "authorization", "authorisation", "approval", "allocation", "coordination", "cooperation",
    "co-ordination", "collaboration", "participation", "representation", "negotiation",
    "assessment", "verification", "monitoring", "supervision", "oversight", "planning",
    "implementation", "enforcement", "provision", "eligibility", "entitlement", "competence",
    "competency", "qualification", "productivity", "efficiency", "stability", "reliability",
    "transparency", "credibility", "legitimacy", "continuity", "compatibility", "feasibility",
}
EXTRA_INSTITUTIONAL_TERMS = {
    "judiciary", "jurisdiction", "legislation", "authority", "administration", "regulator",
    "regulatory", "insurance", "finance", "financial", "fiscal", "taxation", "corporation",
    "employer", "workforce", "ministry", "municipality", "council", "committee", "agency",
    "institution", "association", "federation", "union", "university", "research", "court",
}


def strict_signals(item):
    signals = dict(legacy.signals(item))
    words = legacy.tokens(item["gloss"])
    signals["abstract"] = signals["abstract"] or bool(words & EXTRA_ABSTRACT_TERMS)
    signals["institutional"] = signals["institutional"] or bool(words & EXTRA_INSTITUTIONAL_TERMS)
    return signals


def strict_learner_value(item) -> int:
    # Re-score with the expanded abstract/institutional recognizer while keeping
    # the V2-2 weighting philosophy transparent and deterministic.
    s = strict_signals(item)
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
    first_gloss = legacy.re.sub(r"[^a-z]", "", item["glosses"][0].casefold())
    noun_ascii = legacy.re.sub(r"[^a-z]", "", base.ascii_id(item["noun"]).replace("-", ""))
    score -= 3 if first_gloss and first_gloss == noun_ascii else 0
    if item["group"] == "bridge-general" and not any((s["abstract_suffix"], s["formal_compound"], s["abstract"], s["institutional"])):
        score -= 3
    return int(score)


def strict_difficulty_score(item) -> float:
    s = strict_signals(item)
    return (
        item["frequencyRank"] / 1000
        + min(len(item["noun"]), 24) / 10
        + (1.2 if s["abstract_suffix"] else 0)
        + (0.8 if s["formal_compound"] else 0)
        + (0.7 if s["abstract"] else 0)
    )


def strict_formal_evidence(item) -> bool:
    s = strict_signals(item)
    return bool(s["abstract_suffix"] or s["formal_compound"] or s["abstract"] or s["institutional"])


def strict_reject(item) -> str | None:
    inherited = legacy.hard_reject(item)
    if inherited:
        return inherited
    if item["noun"] in STRICT_EXCLUDED_NOUNS:
        return "v23_explicit_lower_bound_or_noise"
    low_gloss = item["gloss"].casefold()
    if any(term in low_gloss for term in STRICT_BLOCKED_GLOSS_TERMS):
        return "v23_blocked_gloss"
    if ":" in item["gloss"] or "(" in item["gloss"] or ")" in item["gloss"]:
        return "v23_source_annotation_risk"
    s = strict_signals(item)
    if s["person"]:
        return "v23_person_label"
    if s["entertainment"]:
        return "v23_entertainment"
    if s["concrete"]:
        return "v23_concrete_prop"
    if not strict_formal_evidence(item):
        return "v23_missing_bridge_signal"
    if strict_learner_value(item) < MIN_LEARNER_VALUE:
        return "v23_low_learner_value"
    return None


def eligible_for_slot(candidate, level: int, cefr: str) -> bool:
    if candidate["cefrEstimate"] != cefr:
        return False
    if candidate["learnerValue"] < MIN_LEARNER_VALUE:
        return False
    if level == 1:
        return cefr == "B2"
    if level == 2 and cefr == "B2":
        return True
    if level == 2 and cefr == "C1":
        return candidate["frequencyRank"] < legacy.TRANSITION_MAX_FREQUENCY_RANK
    if level == 3:
        return (
            cefr == "C1"
            and candidate["frequencyRank"] >= legacy.ADVANCED_MIN_FREQUENCY_RANK
            and strict_formal_evidence(candidate)
        )
    return False


def candidate_view(item) -> dict:
    s = strict_signals(item)
    return {
        "id": item["id"],
        "noun": item["noun"],
        "article": item["article"],
        "cefrEstimate": item["cefrEstimate"],
        "frequencyRank": item["frequencyRank"],
        "frequencyCount": item["frequencyCount"],
        "gloss": "; ".join(item["glosses"][:2]),
        "group": item["group"],
        "learnerValue": item["learnerValue"],
        "difficultyScore": round(item["difficultyScore"], 3),
        "bridgeSignals": [
            key for key in ("abstract_suffix", "formal_compound", "abstract", "institutional") if s[key]
        ],
    }


def main() -> None:
    rows = legacy.parse_bridge_rows()
    row_by_id = {row[0]: row for row in rows}
    current_ids = set(row_by_id)
    current_nouns = {str(row[1]).casefold() for row in rows}
    decisions = legacy.merged_review_decisions()
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
    strict_rejects = Counter()
    for item in candidates:
        reason = strict_reject(item)
        if reason:
            strict_rejects[reason] += 1
            continue
        curated.append({
            **item,
            "learnerValue": strict_learner_value(item),
            "difficultyScore": strict_difficulty_score(item),
        })

    all_by_id = {item["id"]: item for item in candidates}
    unused = [
        item for item in curated
        if item["id"] not in current_ids and item["noun"].casefold() not in current_nouns
    ]

    slots = []
    bucket_counts = Counter()
    for rejected_id in replacement_ids:
        row = row_by_id.get(rejected_id)
        if row is None:
            base.die(f"Replacement decision references missing Normal id: {rejected_id}")
        level = int(row[3])
        cefr = row[10]["cefrEstimate"]
        source_raw = all_by_id.get(rejected_id)
        source_value = strict_learner_value(source_raw) if source_raw else None
        source_difficulty = strict_difficulty_score(source_raw) if source_raw else None
        slot = {
            "id": rejected_id,
            "noun": row[1],
            "article": row[2],
            "level": level,
            "cefrEstimate": cefr,
            "bucket": legacy.bucket_key(level, cefr),
            "reason": decisions[rejected_id].get("reason"),
            "lowerBound": decisions[rejected_id].get("lowerBound"),
            "lowerBoundEvidenceType": decisions[rejected_id].get("evidenceType"),
            "sourceLearnerValue": source_value,
            "sourceDifficultyScore": round(source_difficulty, 3) if source_difficulty is not None else None,
        }
        slots.append(slot)
        bucket_counts[slot["bucket"]] += 1

    eligible_counts = Counter()
    for slot in slots:
        key = slot["bucket"]
        eligible_counts[key] = sum(1 for item in unused if eligible_for_slot(item, slot["level"], slot["cefrEstimate"]))
    for key, needed in bucket_counts.items():
        if eligible_counts[key] < needed:
            base.die(f"Insufficient strict unused candidate pool for {key}: need {needed}, found {eligible_counts[key]}")

    priority = {"L3-C1": 0, "L2-C1": 1, "L2-B2": 2, "L1-B2": 3}
    reserved: set[str] = set()
    recommendations = {}
    for slot in sorted(slots, key=lambda item: (priority.get(item["bucket"], 9), -(item["sourceDifficultyScore"] or 0), item["id"])):
        eligible = [item for item in unused if eligible_for_slot(item, slot["level"], slot["cefrEstimate"])]
        source_difficulty = slot["sourceDifficultyScore"] if slot["sourceDifficultyScore"] is not None else 0
        eligible.sort(key=lambda item: (
            -item["learnerValue"],
            0 if item["article"] == slot["article"] else 1,
            abs(item["difficultyScore"] - source_difficulty),
            item["frequencyRank"],
            item["noun"].casefold(),
        ))
        recommended = next((item for item in eligible if item["id"] not in reserved), None)
        if recommended is None:
            base.die(f"Could not allocate a unique strict proposal for {slot['id']}")
        reserved.add(recommended["id"])
        alternatives = [item for item in eligible if item["id"] != recommended["id"]][:SHORTLIST_SIZE - 1]
        recommendations[slot["id"]] = {
            "recommended": candidate_view(recommended),
            "alternatives": [candidate_view(item) for item in alternatives],
        }

    current_articles = Counter(row[2] for row in rows)
    removed_articles = Counter(row_by_id[slot["id"]][2] for slot in slots)
    added_articles = Counter(value["recommended"]["article"] for value in recommendations.values())
    post_articles = current_articles - removed_articles + added_articles
    if min(post_articles.values()) < 100:
        base.die(f"Strict replacement proposal would violate article coverage floor: {dict(post_articles)}")

    output = {
        "schema": 2,
        "phase": "V2-3",
        "status": "proposal-only-not-editorially-approved",
        "proposalPolicy": "strict-abstract-formal-institutional",
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
            "minimumLearnerValue": MIN_LEARNER_VALUE,
            "requireNormalSignal": True,
            "rejectConcretePersonEntertainment": True,
            "currentNormalAndChallengeExcluded": True,
            "automaticAcceptance": False,
        },
        "summary": {
            "replacementSlots": len(slots),
            "bucketCounts": dict(sorted(bucket_counts.items())),
            "eligibleUnusedByBucket": dict(sorted(eligible_counts.items())),
            "strictCuratedUnusedPool": len(unused),
            "uniqueRecommendations": len(reserved),
            "currentArticleCounts": dict(current_articles),
            "proposedArticleCounts": dict(post_articles),
            "sourceCandidateRejects": dict(source_reject),
            "strictRejects": dict(strict_rejects),
        },
        "slots": slots,
        "recommendations": recommendations,
    }
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"V2-3 strict replacement proposal passed: {len(slots)} rejected slots, "
        f"{len(reserved)} unique proposals, strict unused pool {len(unused)}, "
        f"buckets {dict(bucket_counts)}."
    )


if __name__ == "__main__":
    main()