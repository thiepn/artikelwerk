#!/usr/bin/env python3
"""Editorial successor for the V2-3 strict Normal replacement proposer.

The strict selector correctly blocks noisy/basic/concrete source material, but
its generic semantic recognizer rejects many legitimate B2 nouns simply because
their English gloss does not contain one of a small set of abstract keywords.
This wrapper adds explicit, proposal-only cohorts that were manually screened
from the diagnostic near-miss artifact.

Important: membership here does NOT certify a noun for release. It only permits
the noun to appear in the replacement proposal artifact. A corpus replacement
still requires an explicit editorial decision plus the normal V2-3 sense,
example, rule, level, provenance, B1 lower-bound screen, and release review.
"""
from __future__ import annotations

import propose_bridge_replacements_strict as strict

# Every B2 noun below came from the pinned Wordhoard + Wiktionary candidate pool,
# was unused by Challenge and the source Normal corpus, and was rejected by the
# strict selector only for v23_missing_bridge_signal. The cohort intentionally
# favors institutional, legal, economic, technical, formal, and otherwise useful
# upper-intermediate vocabulary. It does not override inherited hard rejects,
# explicit lower-bound/noise blocks, concrete-prop blocks, entertainment blocks,
# source-annotation checks, or any future stricter rejection reason.
EDITORIALLY_SCREENED_B2_PROPOSALS = {
    "Abdruck",
    "Adrenalin",
    "Ansprache",
    "Arrest",
    "Bankrott",
    "Blutprobe",
    "Bonus",
    "Darlehen",
    "Deckname",
    "Einzelhaft",
    "Entzug",
    "Flora",
    "Gehör",
    "Gewässer",
    "Gunst",
    "Hormon",
    "Impfstoff",
    "Investor",
    "Jahrgang",
    "Klischee",
    "Kodex",
    "Konsul",
    "Konzern",
    "Kopfgeld",
    "Kreislauf",
    "Kulisse",
    "Küstenwache",
    "Labyrinth",
    "Lebensunterhalt",
    "Leichenhalle",
    "Legende",
    "Legion",
    "Lobby",
    "Luftwaffe",
    "Märtyrer",
    "Metropolis",
    "Motto",
    "Mythos",
    "Nachtschicht",
    "Obhut",
    "Orbit",
    "Pakt",
    "Portal",
    "Rassist",
    "Razzia",
    "Reaktor",
    "Rebellion",
    "Reflex",
    "Rekrut",
    "Ruine",
    "Säure",
    "Scham",
    "Schwarm",
    "Serum",
    "Server",
    "Seuche",
    "Stadium",
    "Stamm",
    "Stellvertreter",
    "Streitkraft",
    "Stromausfall",
    "Terror",
    "Trauma",
    "Triumph",
    "Umweg",
    "Unheil",
    "Unruhe",
    "Unterbewusstsein",
    "Vorgänger",
    "Überfall",
    "Zitat",
    "Zielscheibe",
}

# Exact-text hits found during the final official B1 lower-bound screen. Keep
# these out of proposal artifacts even when the generic selector would admit
# them. They are not used by the approved final successor mapping.
BLOCKED_EDITORIAL_PROPOSALS = {"Union", "Mitarbeit"}

# These C1 candidates already pass the strict quality selector. Their frequency
# rank sits just beyond the generic Level-2 cutoff, but editorial review judged
# them suitable for the B2→C1 transition tier. As above, this affects proposals
# only; release still requires a complete successor review and clean B1 screen.
EDITORIALLY_SCREENED_C1_TRANSITION_PROPOSALS = {
    "Essenz",
    "Ethik",
    "Luftraum",
    "Tiefpunkt",
    "Vorlage",
    "Widerstand",
    "Zensur",
}

_original_reject = strict.strict_reject
_original_learner_value = strict.strict_learner_value
_original_formal_evidence = strict.strict_formal_evidence
_original_candidate_view = strict.candidate_view
_original_eligible_for_slot = strict.eligible_for_slot


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
    if item["noun"] in BLOCKED_EDITORIAL_PROPOSALS:
        return "v23_explicit_lower_bound_or_noise"
    # The pinned Wiktionary extraction can expose sense/source annotations such
    # as "royal court (of a ruler)". Those are useful extraction metadata but
    # are not clean learner-facing glosses, so exclude the candidate from this
    # proposal-only pool before later proposal validation sees it.
    gloss = item["gloss"]
    if "(" in gloss or ")" in gloss:
        return "v23_source_annotation_risk"
    reason = _original_reject(item)
    if (
        reason == "v23_missing_bridge_signal"
        and item["cefrEstimate"] == "B2"
        and item["noun"] in EDITORIALLY_SCREENED_B2_PROPOSALS
        and editorial_learner_value(item) >= strict.MIN_LEARNER_VALUE
    ):
        return None
    return reason


def editorial_eligible_for_slot(candidate, level: int, cefr: str) -> bool:
    if _original_eligible_for_slot(candidate, level, cefr):
        return True
    return (
        level == 2
        and cefr == "C1"
        and candidate["cefrEstimate"] == "C1"
        and candidate["noun"] in EDITORIALLY_SCREENED_C1_TRANSITION_PROPOSALS
        and candidate["learnerValue"] >= strict.MIN_LEARNER_VALUE
    )


def editorial_candidate_view(item) -> dict:
    view = _original_candidate_view(item)
    if item["cefrEstimate"] == "B2" and item["noun"] in EDITORIALLY_SCREENED_B2_PROPOSALS:
        view["bridgeSignals"] = [*view["bridgeSignals"], "editorial-proposal-screen"]
    if item["cefrEstimate"] == "C1" and item["noun"] in EDITORIALLY_SCREENED_C1_TRANSITION_PROPOSALS:
        view["bridgeSignals"] = [*view["bridgeSignals"], "editorial-c1-transition-screen"]
    return view


# strict.main resolves these names from its module globals at runtime, so the
# wrapper can retain the proven allocation/provenance machinery unchanged.
strict.strict_learner_value = editorial_learner_value
strict.strict_formal_evidence = editorial_formal_evidence
strict.strict_reject = editorial_reject
strict.eligible_for_slot = editorial_eligible_for_slot
strict.candidate_view = editorial_candidate_view


if __name__ == "__main__":
    strict.main()
