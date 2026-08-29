# V2-2 — 1,000-Word B2→C1 Bridge Corpus

## Result

- Bridge rows: **1,000**
- Level 1 — Intermediate: **400**
- Level 2 — Upper Intermediate: **350**
- Level 3 — Advanced: **250**
- Source CEFR estimates: **750 B2 / 250 C1**
- Articles: **der 303 / die 548 / das 149**
- Eligible source-corroborated pool before final rank cut: **3,044** nouns (947 B2, 2,097 C1)
- Challenge overlap: **0**

## CEFR interpretation

`B2` and `C1` here are **targeting estimates, not official Goethe B2/C1 list membership**. wordhoard calibrates German frequency ranks against Goethe A1–B1 anchors and extrapolates B2/C1 thresholds from the fitted B1 boundary. Artikelwerk therefore describes this as a B2→C1-targeted Bridge corpus rather than an official CEFR word list.

## Selection method

1. Start from the German dataset in **wordhoard v0.1.0 (2026-07-16)**.
2. Keep common nouns (`NOUN`) whose wordhoard CEFR estimate is B2 or C1 and whose grammatical gender is `der`, `die`, or `das`.
3. Require a matching common-noun entry in the pinned German Wiktionary extraction and require the old Wiktionary grammar data to corroborate **one single gender**. Ambiguous/multi-gender candidates are excluded from this phase rather than silently reduced to one quiz answer.
4. Require at least one clean English Wiktionary translation.
5. Exclude names/special-name-only usages, malformed orthography, selected subtitle-noise categories, exact Challenge noun/ID overlaps, and duplicate Bridge nouns/IDs.
6. Rank eligible B2 nouns by learner value: general-use frequency plus abstract/institutional semantics and productive morphology, with penalties for concrete props, person labels, entertainment/slang vocabulary, and transparent loanwords. Article-diversity targets are soft and never override lexical quality.
7. Select the strongest 750 B2 nouns, then split them by a separate difficulty score into 400 Intermediate and 350 Upper Intermediate nouns. For Advanced, require a C1 source estimate, frequency rank at least 10,500, and formal/abstract lexical evidence; select the strongest 250 by learner value.

## Source and licensing

- **wordhoard**: https://github.com/natema/wordhoard, release v0.1.0 (2026-07-16); downloaded archive SHA-256 `83837efd46241e7226fc6daaa9d0cc81b57bf746434b8c539049c660d98ba761`. The built dataset is CC-BY-SA-4.0 and combines OpenSubtitles-derived frequency evidence with openly licensed lexical sources. Goethe material is calibration-only and is not redistributed.
- **German Wiktionary extraction**: https://github.com/karoly-varasdi/de-wiktionary-parser, pinned commit `73075bb76c9261c44923f4909858586b261bfd83`; `de_noun_entries_with_translations.zip` Git blob `a56efcb80b64433107ec1f376b933c572f2427c9`. English translations and the second-source grammar check derive from German Wiktionary data.
- The checked-in Bridge corpus, Bridge gloss asset, and Bridge provenance are distributed under **CC-BY-SA-4.0**. The existing Challenge translation asset remains separately licensed as documented in `THIRD_PARTY_NOTICES.md`.

## Frequency-rank ranges

- Level 1: 4,624–7,765
- Level 2: 5,694–9,220
- Level 3: 10,513–18,309

## Largest semantic groups

- bridge-general: 933
- legal: 12
- technology: 10
- economy: 9
- process: 7
- politics: 5
- structure: 5
- communication: 4
- health: 4
- emotion: 3
- education: 3
- society: 3

## Rejection audit

- no_wiktionary_translation_entry: 877
- no_clean_english_gloss: 460
- gender_not_single_source_corroborated: 250
- challenge_overlap: 171
- missing_or_invalid_gender: 89
- learner_suitability_too_basic: 79
- learner_suitability_explicit_noise: 70
- special_name_only: 56
- candidate_duplicate: 11
- invalid_orthography: 2
- learner_suitability_slang_or_noise: 2

## Corpus sample

### Level 1 — Intermediate
- **der Eid** — oath (source estimate B2, frequency rank 4,624)
- **die Bude** — shack (source estimate B2, frequency rank 4,630)
- **der Stab** — staff; rod (source estimate B2, frequency rank 4,719)
- **die Gnade** — mercy (source estimate B2, frequency rank 4,651)
- **die Geste** — gesture; act of friendship (source estimate B2, frequency rank 4,660)
- **der Orden** — order; medal (source estimate B2, frequency rank 4,674)
- **das Moor** — bog; fen (source estimate B2, frequency rank 4,819)
- **der Krach** — crash; noise (source estimate B2, frequency rank 4,753)
- **der Tumor** — tumor; tumour (source estimate B2, frequency rank 4,811)
- **die Mafia** — mafia (source estimate B2, frequency rank 4,827)
- **der Rückzug** — retreat (source estimate B2, frequency rank 4,659)
- **die Masse** — mass; bulk (source estimate B2, frequency rank 4,868)
- **der Gauner** — crook; rogue (source estimate B2, frequency rank 4,818)
- **das Verhör** — examination; interrogation (source estimate B2, frequency rank 4,858)
- **das Fell** — fur; pelt (source estimate B2, frequency rank 5,068)
- **der Klub** — club (source estimate B2, frequency rank 5,074)
- **die Werft** — shipyard; dockyard (source estimate B2, frequency rank 4,976)
- **der Satellit** — satellite (source estimate B2, frequency rank 4,684)
- **der Winkel** — angle; corner (source estimate B2, frequency rank 4,903)
- **die Fahne** — flag (source estimate B2, frequency rank 5,081)

### Level 2 — Upper Intermediate
- **die Ähnlichkeit** — resemblance; similarity (source estimate B2, frequency rank 6,049)
- **die Erlösung** — relief; deliverance (source estimate B2, frequency rank 6,352)
- **die Seide** — silk; dodder (source estimate B2, frequency rank 7,854)
- **die Konzentration** — concentration (source estimate B2, frequency rank 5,858)
- **der Schleier** — veil (source estimate B2, frequency rank 7,567)
- **der Defekt** — defect; fault (source estimate B2, frequency rank 7,768)
- **der Aufenthaltsort** — whereabouts (source estimate B2, frequency rank 6,971)
- **die Chemie** — chemistry; Psychologie: attunement (source estimate B2, frequency rank 6,572)
- **der Absturz** — fall; crash (source estimate B2, frequency rank 7,673)
- **die Ermordung** — assassination; murder (source estimate B2, frequency rank 6,282)
- **das Videospiel** — video game (source estimate B2, frequency rank 7,384)
- **das Kaliber** — calibre; caliber (source estimate B2, frequency rank 7,685)
- **die Stiftung** — endowment; foundation (source estimate B2, frequency rank 6,388)
- **die Hauptrolle** — main role (source estimate B2, frequency rank 6,695)
- **der Hellseher** — seer; clairvoyant (source estimate B2, frequency rank 7,497)
- **die Festnahme** — arrest; apprehension (source estimate B2, frequency rank 7,499)
- **die Philosophie** — philosophy (source estimate B2, frequency rank 6,101)
- **die Mischung** — mix; mixture (source estimate B2, frequency rank 6,409)
- **der Tabak** — tobacco (source estimate B2, frequency rank 7,916)
- **der Kodex** — code; codex (source estimate B2, frequency rank 7,920)

### Level 3 — Advanced
- **die Prozedur** — procedure (source estimate C1, frequency rank 10,768)
- **die Ablösung** — shift change; removal (source estimate C1, frequency rank 17,831)
- **das Einverständnis** — consent; agreement (source estimate C1, frequency rank 11,289)
- **das Anrecht** — claim; entitlement (source estimate C1, frequency rank 16,255)
- **die Unternehmung** — enterprise; company (source estimate C1, frequency rank 17,263)
- **die Wichtigkeit** — importance (source estimate C1, frequency rank 11,872)
- **die Auffassung** — concept; idea (source estimate C1, frequency rank 12,729)
- **die Verwandtschaft** — relationship (source estimate C1, frequency rank 13,317)
- **die Beachtung** — account; attention (source estimate C1, frequency rank 14,020)
- **die Kondition** — condition (source estimate C1, frequency rank 14,036)
- **die Einschränkung** — limitation; constraint (source estimate C1, frequency rank 14,130)
- **die Gleichheit** — equality (source estimate C1, frequency rank 15,768)
- **die Unstimmigkeit** — difference of opinions (source estimate C1, frequency rank 16,130)
- **die Annäherung** — approach; convergence (source estimate C1, frequency rank 16,332)
- **die Ungewissheit** — uncertainty (source estimate C1, frequency rank 16,638)
- **die Verteilung** — distribution (source estimate C1, frequency rank 17,352)
- **die Schweigepflicht** — pledge of secrecy; requirement of confidentiality (source estimate C1, frequency rank 12,258)
- **die Tagesordnung** — agenda (source estimate C1, frequency rank 12,594)
- **die Personalabteilung** — human resources; personnel department (source estimate C1, frequency rank 13,108)
- **die Verordnung** — order; statutory instrument (source estimate C1, frequency rank 14,654)

## Editorial QA

- Level 1: learner-value 1–23; difficulty 4.92–8.35
- Level 2: learner-value 1–30; difficulty 8.35–11.83
- Level 3: learner-value 4–20; difficulty 11.84–20.58

### Lowest learner-value selections

- **der Drive** — tee shot; drive (value 1, rank 8,429, B2)
- **der Dorn** — thorn; awl (value 1, rank 8,424, B2)
- **der Faden** — thread; fathom (value 1, rank 8,405, B2)
- **der Brei** — pap; pudding (value 1, rank 8,404, B2)
- **der Fels** — rock (value 1, rank 8,365, B2)
- **die Höhle** — cave; cavern (value 1, rank 8,298, B2)
- **der Rektor** — rector; principal (value 1, rank 8,297, B2)
- **der Spatz** — sparrow (value 1, rank 8,290, B2)
- **der Nord** — north (value 1, rank 8,273, B2)
- **die Pisse** — piss (value 1, rank 8,244, B2)
- **der Zar** — tsar; czar (value 1, rank 8,226, B2)
- **der Pelz** — fur; pelt (value 1, rank 8,107, B2)
- **der Scanner** — scanner (value 1, rank 7,159, B2)
- **die Massage** — massage (value 1, rank 6,777, B2)
- **der Investor** — investor (value 1, rank 6,582, B2)
- **das Hospital** — hospital (value 1, rank 6,501, B2)
- **das Trauma** — trauma (value 1, rank 6,077, B2)
- **die Suite** — suite (value 1, rank 5,883, B2)
- **der Sultan** — sultan (value 1, rank 5,878, B2)
- **der Boxer** — boxer (value 1, rank 5,760, B2)
- **das Ego** — ego (value 1, rank 5,681, B2)
- **der Gin** — gin (value 1, rank 5,515, B2)
- **der Jet** — jet (value 1, rank 5,480, B2)
- **das Outfit** — outfit (value 1, rank 5,468, B2)
- **der Scheich** — sheik; sheikh (value 2, rank 8,984, B2)
- **der Beobachter** — observer (value 2, rank 8,983, B2)
- **der Aufseher** — supervisor; invigilator (value 2, rank 8,967, B2)
- **der Flugplatz** — airfield (value 2, rank 8,966, B2)
- **der Knoblauch** — garlic (value 2, rank 8,962, B2)
- **das Rückgrat** — backbone; spine (value 2, rank 8,961, B2)
