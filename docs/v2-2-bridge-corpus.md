# V2-2 — 1,000-Word B2→C1 Bridge Corpus

## Result

- Bridge rows: **1,000**
- Level 1 — Intermediate: **400**
- Level 2 — Upper Intermediate: **350**
- Level 3 — Advanced: **250**
- Source CEFR estimates: **750 B2 / 250 C1**
- Articles: **der 377 / die 465 / das 158**
- Eligible source-corroborated pool before final rank cut: **3,092** nouns (999 B2, 2,093 C1)
- Challenge overlap: **0**

## CEFR interpretation

`B2` and `C1` here are **targeting estimates, not official Goethe B2/C1 list membership**. wordhoard calibrates German frequency ranks against Goethe A1–B1 anchors and extrapolates B2/C1 thresholds from the fitted B1 boundary. Artikelwerk therefore describes this as a B2→C1-targeted Bridge corpus rather than an official CEFR word list.

## Selection method

1. Start from the German dataset in **wordhoard v0.1.0 (2026-07-16)**.
2. Keep common nouns (`NOUN`) whose wordhoard CEFR estimate is B2 or C1 and whose grammatical gender is `der`, `die`, or `das`.
3. Require a matching common-noun entry in the pinned German Wiktionary extraction and require the old Wiktionary grammar data to corroborate **one single gender**. Ambiguous/multi-gender candidates are excluded from this phase rather than silently reduced to one quiz answer.
4. Require at least one clean English Wiktionary translation.
5. Exclude names/special-name-only usages, malformed orthography, selected subtitle-noise categories, exact Challenge noun/ID overlaps, and duplicate Bridge nouns/IDs.
6. Sort by wordhoard frequency rank. Select the first 750 eligible B2 nouns and first 250 eligible C1 nouns.
7. Assign the first 400 B2 nouns to Intermediate, the next 350 B2 nouns to Upper Intermediate, and the 250 C1 nouns to Advanced.

## Source and licensing

- **wordhoard**: https://github.com/natema/wordhoard, release v0.1.0 (2026-07-16); downloaded archive SHA-256 `83837efd46241e7226fc6daaa9d0cc81b57bf746434b8c539049c660d98ba761`. The built dataset is CC-BY-SA-4.0 and combines OpenSubtitles-derived frequency evidence with openly licensed lexical sources. Goethe material is calibration-only and is not redistributed.
- **German Wiktionary extraction**: https://github.com/karoly-varasdi/de-wiktionary-parser, pinned commit `73075bb76c9261c44923f4909858586b261bfd83`; `de_noun_entries_with_translations.zip` Git blob `a56efcb80b64433107ec1f376b933c572f2427c9`. English translations and the second-source grammar check derive from German Wiktionary data.
- The checked-in Bridge corpus, Bridge gloss asset, and Bridge provenance are distributed under **CC-BY-SA-4.0**. The existing Challenge translation asset remains separately licensed as documented in `THIRD_PARTY_NOTICES.md`.

## Frequency-rank ranges

- Level 1: 4,624–6,700
- Level 2: 6,716–8,163
- Level 3: 9,276–12,575

## Largest semantic groups

- bridge-general: 955
- technology: 6
- politics: 6
- process: 6
- economy: 6
- structure: 4
- health: 4
- society: 3
- education: 3
- emotion: 2
- communication: 2
- environment: 1

## Rejection audit

- no_wiktionary_translation_entry: 877
- no_clean_english_gloss: 460
- gender_not_single_source_corroborated: 250
- challenge_overlap: 171
- missing_or_invalid_gender: 89
- learner_suitability_too_basic: 84
- special_name_only: 56
- learner_suitability_explicit_noise: 19
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
- **der Orden** — order; medal; decoration (source estimate B2, frequency rank 4,674)
- **der Satellit** — satellite (source estimate B2, frequency rank 4,684)
- **der Prophet** — prophet (source estimate B2, frequency rank 4,700)
- **die Division** — division (source estimate B2, frequency rank 4,703)
- **der Pastor** — pastor (source estimate B2, frequency rank 4,705)
- **die Datenbank** — data bank; data base; databank (source estimate B2, frequency rank 4,706)
- **der Stab** — staff; rod; bar (source estimate B2, frequency rank 4,719)
- **die Ablenkung** — deflection (source estimate B2, frequency rank 4,751)
- **der Krach** — crash; noise; quarrel (source estimate B2, frequency rank 4,753)
- **die Autopsie** — autopsy (source estimate B2, frequency rank 4,780)
- **die Republik** — republic (source estimate B2, frequency rank 4,782)
- **die Bestellung** — order (source estimate B2, frequency rank 4,802)

### Level 2 — Upper Intermediate
- **die Bemühung** — effort; endeavour (source estimate B2, frequency rank 6,716)
- **der Attentäter** — assassin (source estimate B2, frequency rank 6,717)
- **der Schöpfer** — creator; Maker; dipper (source estimate B2, frequency rank 6,732)
- **das Weltall** — universe (source estimate B2, frequency rank 6,737)
- **die Hypothek** — mortgage (source estimate B2, frequency rank 6,738)
- **die Lobby** — lobby (source estimate B2, frequency rank 6,741)
- **der Orgasmus** — climax (source estimate B2, frequency rank 6,744)
- **der Campus** — campus (source estimate B2, frequency rank 6,748)
- **die Premiere** — première (source estimate B2, frequency rank 6,758)
- **das Tageslicht** — daylight (source estimate B2, frequency rank 6,764)
- **die Massage** — massage (source estimate B2, frequency rank 6,777)
- **die Wahrscheinlichkeit** — probability; chance (source estimate B2, frequency rank 6,785)
- **das Zeitalter** — age; era; epoc (source estimate B2, frequency rank 6,787)
- **der Antrieb** — drive; impetus (source estimate B2, frequency rank 6,789)
- **die Armut** — poverty; lack (source estimate B2, frequency rank 6,791)
- **die Rüstung** — armour; arms; weapons (source estimate B2, frequency rank 6,794)
- **die Eminenz** — eminence (source estimate B2, frequency rank 6,797)
- **der Araber** — Arab; Arabian horse (source estimate B2, frequency rank 6,800)
- **der Muffin** — muffin (source estimate B2, frequency rank 6,807)
- **der Drang** — urge (source estimate B2, frequency rank 6,808)

### Level 3 — Advanced
- **die Strömung** — tide (source estimate C1, frequency rank 9,276)
- **die Schwachstelle** — trouble spot; weak point (source estimate C1, frequency rank 9,277)
- **die Atmung** — respiration (source estimate C1, frequency rank 9,279)
- **die Kleinstadt** — town; township; townikin (source estimate C1, frequency rank 9,297)
- **das Verteidigungsministerium** — Ministry of Defence (source estimate C1, frequency rank 9,298)
- **die Auseinandersetzung** — argument; dispute (source estimate C1, frequency rank 9,311)
- **die Neigung** — inclination; propensity (source estimate C1, frequency rank 9,322)
- **die Skulptur** — sculpture (source estimate C1, frequency rank 9,350)
- **die Freundlichkeit** — affability; attention; cheerfulness (source estimate C1, frequency rank 9,352)
- **die Spritztour** — joyride (source estimate C1, frequency rank 9,419)
- **der Schiedsrichter** — referee; umpire; jury (source estimate C1, frequency rank 9,433)
- **die Chirurgie** — surgery (source estimate C1, frequency rank 9,434)
- **der Heiratsantrag** — marriage proposal (source estimate C1, frequency rank 9,450)
- **die Besorgnis** — concern; worriedness; anxiety (source estimate C1, frequency rank 9,469)
- **die Intuition** — intuition (source estimate C1, frequency rank 9,485)
- **der Terrorismus** — terrorism (source estimate C1, frequency rank 9,486)
- **die Sequenz** — sequence (source estimate C1, frequency rank 9,489)
- **der Staubsauger** — vacuum cleaner; hoover (source estimate C1, frequency rank 9,508)
- **die Offenbarung** — revelation; Revelations; Apocalypse (source estimate C1, frequency rank 9,519)
- **das Abendbrot** — dinner; evening meal; supper (source estimate C1, frequency rank 9,529)
