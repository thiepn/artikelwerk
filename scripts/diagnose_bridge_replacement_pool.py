#!/usr/bin/env python3
"""Diagnose V2-3 strict replacement-pool scarcity without changing corpus content.

This script intentionally shares the strict selector's source pins and scoring,
but it never proposes or accepts replacements. It exports enough evidence to
explain why a Level/CEFR bucket is under-supplied before editorial thresholds
are changed.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import generate_bridge_corpus as base
import propose_bridge_replacements as legacy
import propose_bridge_replacements_strict as strict

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content" / "bridge-replacement-pool-diagnostic.json"
# Keep the artifact exhaustive for the undersupplied B2 pool. Console output is
# still capped below so CI logs remain readable.
TOP_NEAR_MISSES = 500
LOG_NEAR_MISSES = 80


def compact(item: dict, reject_reason: str | None = None) -> dict:
    signals = strict.strict_signals(item)
    return {
        "id": item["id"],
        "noun": item["noun"],
        "article": item["article"],
        "cefrEstimate": item["cefrEstimate"],
        "frequencyRank": item["frequencyRank"],
        "frequencyCount": item["frequencyCount"],
        "gloss": "; ".join(item["glosses"][:2]),
        "group": item["group"],
        "strictLearnerValue": strict.strict_learner_value(item),
        "difficultyScore": round(strict.strict_difficulty_score(item), 3),
        "signals": {key: bool(value) for key, value in signals.items()},
        "rejectReason": reject_reason,
    }


def main() -> None:
    rows = legacy.parse_bridge_rows()
    current_ids = {row[0] for row in rows}
    current_nouns = {str(row[1]).casefold() for row in rows}
    decisions = legacy.merged_review_decisions()
    replacement_ids = {key for key, value in decisions.items() if value.get("decision") == "replace"}

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

    candidates, source_rejects = base.build_candidates(wordhoard, translations, challenge_nouns, challenge_ids)
    unused = [
        item for item in candidates
        if item["id"] not in current_ids and item["noun"].casefold() not in current_nouns
    ]

    accepted = []
    rejected = []
    reject_counts = Counter()
    cefr_unused = Counter(item["cefrEstimate"] for item in unused)
    accepted_by_cefr = Counter()
    rejected_by_cefr_reason: dict[str, Counter] = defaultdict(Counter)

    for item in unused:
        reason = strict.strict_reject(item)
        if reason is None:
            accepted.append(item)
            accepted_by_cefr[item["cefrEstimate"]] += 1
        else:
            rejected.append((item, reason))
            reject_counts[reason] += 1
            rejected_by_cefr_reason[item["cefrEstimate"]][reason] += 1

    accepted.sort(key=lambda item: (-strict.strict_learner_value(item), item["frequencyRank"], item["noun"].casefold()))
    rejected.sort(key=lambda pair: (-strict.strict_learner_value(pair[0]), pair[0]["frequencyRank"], pair[0]["noun"].casefold()))

    b2_accepted = [item for item in accepted if item["cefrEstimate"] == "B2"]
    b2_rejected = [(item, reason) for item, reason in rejected if item["cefrEstimate"] == "B2"]
    c1_accepted = [item for item in accepted if item["cefrEstimate"] == "C1"]

    bucket_needs = Counter()
    row_by_id = {row[0]: row for row in rows}
    for replacement_id in replacement_ids:
        row = row_by_id[replacement_id]
        bucket_needs[legacy.bucket_key(int(row[3]), row[10]["cefrEstimate"])] += 1

    report = {
        "schema": 1,
        "phase": "V2-3",
        "purpose": "strict replacement pool scarcity diagnosis",
        "sourcePins": {
            "wordhoardRelease": base.WORDHOARD_RELEASE,
            "wordhoardSha256": base.WORDHOARD_SHA256,
            "wiktionaryParserCommit": base.WIKT_PARSER_COMMIT,
            "wiktionaryBlobSha": base.WIKT_TRANSLATIONS_BLOB_SHA,
        },
        "summary": {
            "replacementSlots": len(replacement_ids),
            "bucketNeeds": dict(sorted(bucket_needs.items())),
            "unusedSourceCandidates": len(unused),
            "unusedByCefr": dict(sorted(cefr_unused.items())),
            "strictAcceptedUnused": len(accepted),
            "strictAcceptedByCefr": dict(sorted(accepted_by_cefr.items())),
            "strictRejectCounts": dict(sorted(reject_counts.items())),
            "strictRejectsByCefr": {
                cefr: dict(sorted(counts.items())) for cefr, counts in sorted(rejected_by_cefr_reason.items())
            },
            "sourceCandidateRejects": dict(source_rejects),
        },
        "acceptedB2": [compact(item) for item in b2_accepted],
        "acceptedC1Top": [compact(item) for item in c1_accepted[:TOP_NEAR_MISSES]],
        "b2NearMisses": [compact(item, reason) for item, reason in b2_rejected[:TOP_NEAR_MISSES]],
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        "V2-3 strict pool diagnostic: "
        f"unused={len(unused)}, accepted={len(accepted)}, B2 accepted={len(b2_accepted)}, "
        f"C1 accepted={len(c1_accepted)}, bucket needs={dict(bucket_needs)}"
    )
    print(f"V2-3 strict reject counts: {dict(reject_counts)}")
    for item in b2_accepted:
        print("V23_B2_ACCEPT\t" + json.dumps(compact(item), ensure_ascii=False, sort_keys=True))
    for item, reason in b2_rejected[:LOG_NEAR_MISSES]:
        print("V23_B2_NEAR_MISS\t" + json.dumps(compact(item, reason), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
