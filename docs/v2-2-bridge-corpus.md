# V2-2 — 1,000-Word B2→C1 Bridge Corpus

## Result

- Bridge rows: **1,000**
- Level 1 — Intermediate: **400**
- Level 2 — Upper Intermediate: **350**
- Level 3 — Advanced: **250**
- Source CEFR estimates: **750 B2 / 250 C1**
- Articles: **der 318 / die 549 / das 133**
- Eligible source-corroborated pool before final rank cut: **3,095** nouns (996 B2, 2,099 C1)
- Challenge overlap: **0**

## CEFR interpretation

`B2` and `C1` here are **targeting estimates, not official Goethe B2/C1 list membership**. wordhoard calibrates German frequency ranks against Goethe A1–B1 anchors and extrapolates B2/C1 thresholds from the fitted B1 boundary. Artikelwerk therefore describes this as a B2→C1-targeted Bridge corpus rather than an official CEFR word list.

## Selection method

1. Start from the German dataset in **wordhoard v0.1.0 (2026-07-16)**.
2. Keep common nouns (`NOUN`) whose wordhoard CEFR estimate is B2 or C1 and whose grammatical gender is `der`, `die`, or `das`.
3. Require a matching common-noun entry in the pinned German Wiktionary extraction and require the old Wiktionary grammar data to corroborate **one single gender**. Ambiguous/multi-gender candidates are excluded from this phase rather than silently reduced to one quiz answer.
4. Require at least one clean English Wiktionary translation.
5. Exclude names/special-name-only usages, malformed orthography, selected subtitle-noise/basic-concept categories, exact Challenge noun/ID overlaps, and duplicate Bridge nouns/IDs.
6. Keep the B2 pool frequency-led for Intermediate/Upper Intermediate. Limit every gloss to the two strongest clean source translations.
7. For Advanced, require a C1 source estimate, frequency rank at least 10,500, and **formal lexical evidence**: strong abstract/derivational morphology or an abstract/formal semantic signal. Rarity, word length, and polysemy alone cannot qualify a noun as Advanced.
8. Assign the first 400 curated B2 nouns to Intermediate, the next 350 to Upper Intermediate, and the first 250 upper-C1 formally qualified nouns to Advanced.

## Source and licensing

- **wordhoard**: https://github.com/natema/wordhoard, release v0.1.0 (2026-07-16); downloaded archive SHA-256 `83837efd46241e7226fc6daaa9d0cc81b57bf746434b8c539049c660d98ba761`. The built dataset is CC-BY-SA-4.0 and combines OpenSubtitles-derived frequency evidence with openly licensed lexical sources. Goethe material is calibration-only and is not redistributed.
- **German Wiktionary extraction**: https://github.com/karoly-varasdi/de-wiktionary-parser, pinned commit `73075bb76c9261c44923f4909858586b261bfd83`; `de_noun_entries_with_translations.zip` Git blob `a56efcb80b64433107ec1f376b933c572f2427c9`. English translations and the second-source grammar check derive from German Wiktionary data.
- The checked-in Bridge corpus, Bridge gloss asset, and Bridge provenance are distributed under **CC-BY-SA-4.0**. The existing Challenge translation asset remains separately licensed as documented in `THIRD_PARTY_NOTICES.md`.

## Frequency-rank ranges

- Level 1: 4,624–6,699
- Level 2: 6,716–8,172
- Level 3: 10,513–17,372

## Largest semantic groups

- bridge-general: 962
- technology: 5
- process: 5
- economy: 5
- emotion: 3
- politics: 3
- structure: 3
- communication: 3
- health: 3
- society: 2
- education: 2
- legal: 2

## Rejection audit

- no_wiktionary_translation_entry: 877
- no_clean_english_gloss: 460
- gender_not_single_source_corroborated: 250
- challenge_overlap: 171
- missing_or_invalid_gender: 89
- learner_suitability_too_basic: 77
- special_name_only: 56
- learner_suitability_explicit_noise: 23
- candidate_duplicate: 11
- invalid_orthography: 2

## Corpus sample

### Level 1 — Intermediate
- **der Eid** — oath (source estimate B2, frequency rank 4,624)
- **die Bude** — shack (source estimate B2, frequency rank 4,630)
- **der Häftling** — detainee; prisoner (source estimate B2, frequency rank 4,636)
- **die Zeitverschwendung** — waste of time (source estimate B2, frequency rank 4,638)
- **die Gnade** — mercy (source estimate B2, frequency rank 4,651)
- **der Rückzug** — retreat (source estimate B2, frequency rank 4,659)
- **die Geste** — gesture; act of friendship (source estimate B2, frequency rank 4,660)
- **die Genehmigung** — approval (source estimate B2, frequency rank 4,668)
- **der Orden** — order; medal (source estimate B2, frequency rank 4,674)
- **der Satellit** — satellite (source estimate B2, frequency rank 4,684)
- **der Prophet** — prophet (source estimate B2, frequency rank 4,700)
- **die Division** — division (source estimate B2, frequency rank 4,703)
- **der Pastor** — pastor (source estimate B2, frequency rank 4,705)
- **die Datenbank** — data bank; data base (source estimate B2, frequency rank 4,706)
- **der Stab** — staff; rod (source estimate B2, frequency rank 4,719)
- **die Ablenkung** — deflection (source estimate B2, frequency rank 4,751)
- **der Krach** — crash; noise (source estimate B2, frequency rank 4,753)
- **die Autopsie** — autopsy (source estimate B2, frequency rank 4,780)
- **die Republik** — republic (source estimate B2, frequency rank 4,782)
- **die Bestellung** — order (source estimate B2, frequency rank 4,802)

### Level 2 — Upper Intermediate
- **die Bemühung** — effort; endeavour (source estimate B2, frequency rank 6,716)
- **der Attentäter** — assassin (source estimate B2, frequency rank 6,717)
- **der Schöpfer** — creator; Maker (source estimate B2, frequency rank 6,732)
- **das Weltall** — universe (source estimate B2, frequency rank 6,737)
- **die Hypothek** — mortgage (source estimate B2, frequency rank 6,738)
- **die Lobby** — lobby (source estimate B2, frequency rank 6,741)
- **der Campus** — campus (source estimate B2, frequency rank 6,748)
- **die Premiere** — première (source estimate B2, frequency rank 6,758)
- **das Tageslicht** — daylight (source estimate B2, frequency rank 6,764)
- **die Massage** — massage (source estimate B2, frequency rank 6,777)
- **die Wahrscheinlichkeit** — probability; chance (source estimate B2, frequency rank 6,785)
- **das Zeitalter** — age; era (source estimate B2, frequency rank 6,787)
- **der Antrieb** — drive; impetus (source estimate B2, frequency rank 6,789)
- **die Armut** — poverty; lack (source estimate B2, frequency rank 6,791)
- **die Rüstung** — armour; arms (source estimate B2, frequency rank 6,794)
- **die Eminenz** — eminence (source estimate B2, frequency rank 6,797)
- **der Drang** — urge (source estimate B2, frequency rank 6,808)
- **die Blondine** — blonde (source estimate B2, frequency rank 6,814)
- **der Zins** — interest (source estimate B2, frequency rank 6,825)
- **der Zauberspruch** — incantation; spell (source estimate B2, frequency rank 6,826)

### Level 3 — Advanced
- **die Selbstverteidigung** — self-defence (source estimate C1, frequency rank 10,513)
- **die Lungenentzündung** — pneumonia (source estimate C1, frequency rank 10,551)
- **die Übernahme** — takeover; appropriation (source estimate C1, frequency rank 10,590)
- **die Präsenz** — presence (source estimate C1, frequency rank 10,636)
- **die Sensation** — sensation (source estimate C1, frequency rank 10,686)
- **die Prozedur** — procedure (source estimate C1, frequency rank 10,768)
- **die Zündung** — ignition; firing (source estimate C1, frequency rank 10,777)
- **die Begabung** — gift; flair (source estimate C1, frequency rank 10,784)
- **die Brandstiftung** — arson (source estimate C1, frequency rank 10,856)
- **die Kapitulation** — capitulation; surrender (source estimate C1, frequency rank 10,920)
- **die Prellung** — bruise (source estimate C1, frequency rank 10,924)
- **die Anspielung** — allusion; insinuation (source estimate C1, frequency rank 10,954)
- **die Arroganz** — arrogance (source estimate C1, frequency rank 10,957)
- **die Eroberung** — conquest (source estimate C1, frequency rank 10,968)
- **die Audienz** — audience (source estimate C1, frequency rank 11,074)
- **die Zärtlichkeit** — tenderness; caresses (source estimate C1, frequency rank 11,101)
- **die Bewunderung** — admiration (source estimate C1, frequency rank 11,108)
- **die Kanalisation** — sewage system (source estimate C1, frequency rank 11,123)
- **die Barmherzigkeit** — mercy; tenderheartedness (source estimate C1, frequency rank 11,125)
- **die Verachtung** — contempt (source estimate C1, frequency rank 11,126)
