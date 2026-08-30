#!/usr/bin/env python3
"""Editorial successor for the V2-3 strict Bridge replacement proposer.

The strict selector correctly blocks noisy/basic/concrete source material, but
its generic semantic recognizer rejects many legitimate B2 nouns simply because
their English gloss does not contain one of a small set of abstract keywords.
This wrapper adds an explicit, proposal-only cohort that was manually screened
from the diagnostic near-miss artifact.

Important: membership here does NOT certify a noun for release. It only permits
the noun to appear in the replacement proposal artifact. A corpus replacement
still requires an explicit editorial decision plus the normal V2-3 sense,
example, rule, level, provenance, and release review.
"""
from __future__ import annotations

import propose_bridge_replacements_strict as strict

# Every noun below came from the pinned Wordhoard + Wiktionary candidate pool,
# was unused by Challenge and the current Bridge corpus, and was rejected by the
# strict selector only for v23_missing_bridge_signal. The cohort intentionally
# favors institutional, legal, economic, technical, formal, and abstract usage.
# It does not override inherited hard rejects, explicit lower-bound/noise blocks,
# concrete-prop blocks, entertainment blocks, source-annotation checks, or any
# future stricter rejection reason.
EDITORIALLY_SCREENED_B2_PROPOSALS = {
    "Abdruck",
    "Ansprache",
    "Arrest",
    "Bankrott",
    "Darlehen",
    "Deckname",
    "Einzelhaft",
    "Entzug",
    "Gunst",
    "Impfstoff",
    "Jahrgang",
    "Klischee",
    "Kodex",
    "Konsul",
    "Konzern",
    "Kopfgeld",
    "Kreislauf",
    "Lebensunterhalt",
    "Leichenhalle",
    "Mythos",
    "Obhut",
    "Pakt",
    "Reaktor",
    "Rebellion",
    "Seuche",
    "Stellvertreter",
    "Streitkraft",
    "Stromausfall",
    "Unterbewusstsein",
    "Unheil",
    "Überfall",
    "Vorgänger",
    "Zitat",
}

_original_reject = strict.strict_reject
_original_learner_value = strict.strict_learner_value
_original_formal_evidence = strict.strict_formal_evidence
_original_candidate_view = strict.candidate_view


def editorial_learner_value(item) -> int:
    score = _original_learner_value(item)
    if item["cefrEstimate"] == "B2" and item["noun"] in EDITORIALLY_SCREENED_B2_PROPOSALS:
        # A fixed review bonus makes the manually screened cohort rank alongside
        # the small number of automatically recognized B2 candidates. This is a
        # proposal-ranking signal, not a CEFR claim or release certification.
        score += 7
    return score


def editorial_formal_evidence(item) -> bool:
    return _original_formal_evidence(item) or (
        item["cefrEstimate"] == "B2" and item["noun"] in EDITORIALLY_SCREENED_B2_PROPOSALS
    )


def editorial_reject(item) -> str | None:
    reason = _original_reject(item)
    if (
        reason == "v23_missing_bridge_signal"
        and item["cefrEstimate"] == "B2"
        and item["noun"] in EDITORIALLY_SCREENED_B2_PROPOSALS
        and editorial_learner_value(item) >= strict.MIN_LEARNER_VALUE
    ):
        return None
    return reason


def editorial_candidate_view(item) -> dict:
    view = _original_candidate_view(item)
    if item["cefrEstimate"] == "B2" and item["noun"] in EDITORIALLY_SCREENED_B2_PROPOSALS:
        view["bridgeSignals"] = [*view["bridgeSignals"], "editorial-proposal-screen"]
    return view


# strict.main resolves these names from its module globals at runtime, so the
# wrapper can retain the proven allocation/provenance machinery unchanged.
strict.strict_learner_value = editorial_learner_value
strict.strict_formal_evidence = editorial_formal_evidence
strict.strict_reject = editorial_reject
strict.candidate_view = editorial_candidate_view


if __name__ == "__main__":
    strict.main()
