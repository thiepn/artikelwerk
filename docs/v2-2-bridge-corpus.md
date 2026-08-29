# V2-2 — 1,000-Word B2→C1 Bridge Corpus

## Result

- Bridge rows: **1,000**
- Level 1 — Intermediate: **400**
- Level 2 — Upper Intermediate: **350**
- Level 3 — Advanced: **250**
- Source CEFR estimates: **600 B2 / 400 C1**
- Articles: **der 219 / die 663 / das 118**
- Eligible source-corroborated pool before final rank cut: **3,021** nouns (935 B2, 2,086 C1)
- Challenge overlap: **0**

## CEFR interpretation

`B2` and `C1` here are **targeting estimates, not official Goethe B2/C1 list membership**. wordhoard calibrates German frequency ranks against Goethe A1–B1 anchors and extrapolates B2/C1 thresholds from the fitted B1 boundary. Artikelwerk therefore describes this as a B2→C1-targeted Bridge corpus rather than an official CEFR word list.

## Selection method

1. Start from the German dataset in **wordhoard v0.1.0 (2026-07-16)**.
2. Keep common nouns (`NOUN`) whose wordhoard CEFR estimate is B2 or C1 and whose grammatical gender is `der`, `die`, or `das`.
3. Require a matching common-noun entry in the pinned German Wiktionary extraction and require the old Wiktionary grammar data to corroborate **one single gender**. Ambiguous/multi-gender candidates are excluded from this phase rather than silently reduced to one quiz answer.
4. Require at least one clean English Wiktionary translation.
5. Exclude names/special-name-only usages, malformed orthography, selected subtitle-noise categories, exact Challenge noun/ID overlaps, and duplicate Bridge nouns/IDs.
6. Rank eligible nouns by learner value: general-use frequency plus abstract/institutional semantics and productive morphology, with penalties for concrete props, person labels, entertainment/slang vocabulary, and transparent loanwords. Article balance is measured after selection and never overrides lexical quality.
7. Select 600 high-value B2 nouns: the easier 400 become Intermediate and the stronger 200 enter Upper Intermediate. Add 150 accessible C1 nouns to Upper Intermediate only if learner value is at least 5 and source frequency rank is below 14,000. Advanced contains 250 distinct C1 nouns with frequency rank at least 10,500 plus formal/abstract lexical evidence.

## Source and licensing

- **wordhoard**: https://github.com/natema/wordhoard, release v0.1.0 (2026-07-16); downloaded archive SHA-256 `83837efd46241e7226fc6daaa9d0cc81b57bf746434b8c539049c660d98ba761`. The built dataset is CC-BY-SA-4.0 and combines OpenSubtitles-derived frequency evidence with openly licensed lexical sources. Goethe material is calibration-only and is not redistributed.
- **German Wiktionary extraction**: https://github.com/karoly-varasdi/de-wiktionary-parser, pinned commit `73075bb76c9261c44923f4909858586b261bfd83`; `de_noun_entries_with_translations.zip` Git blob `a56efcb80b64433107ec1f376b933c572f2427c9`. English translations and the second-source grammar check derive from German Wiktionary data.
- The checked-in Bridge corpus, Bridge gloss asset, and Bridge provenance are distributed under **CC-BY-SA-4.0**. The existing Challenge translation asset remains separately licensed as documented in `THIRD_PARTY_NOTICES.md`.

## Frequency-rank ranges

- Level 1: 4,624–7,978
- Level 2: 5,694–13,870
- Level 3: 11,872–18,309

## Largest semantic groups

- bridge-general: 923
- legal: 13
- economy: 12
- technology: 9
- process: 8
- politics: 6
- structure: 5
- communication: 5
- health: 5
- education: 4
- emotion: 3
- society: 3

## Rejection audit

- no_wiktionary_translation_entry: 877
- no_clean_english_gloss: 460
- gender_not_single_source_corroborated: 250
- challenge_overlap: 171
- missing_or_invalid_gender: 89
- learner_suitability_too_basic: 86
- learner_suitability_explicit_noise: 86
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
- **der Klub** — club (source estimate B2, frequency rank 5,074)
- **die Werft** — shipyard; dockyard (source estimate B2, frequency rank 4,976)
- **der Satellit** — satellite (source estimate B2, frequency rank 4,684)
- **der Winkel** — angle; corner (source estimate B2, frequency rank 4,903)
- **die Fahne** — flag (source estimate B2, frequency rank 5,081)
- **die Datenbank** — data bank; data base (source estimate B2, frequency rank 4,706)

### Level 2 — Upper Intermediate
- **die Titelseite** — cover; front page (source estimate B2, frequency rank 7,678)
- **die Berührung** — contact; touch (source estimate B2, frequency rank 6,591)
- **die Staatsanwaltschaft** — prosecution; public prosecutor's office (source estimate B2, frequency rank 5,694)
- **die Rüstung** — armour; arms (source estimate B2, frequency rank 6,794)
- **die Apokalypse** — Apocalypse (source estimate B2, frequency rank 7,695)
- **die Eminenz** — eminence (source estimate B2, frequency rank 6,797)
- **der Grieche** — Greek (source estimate B2, frequency rank 8,006)
- **das Manuskript** — manuscript (source estimate B2, frequency rank 7,707)
- **die Bemühung** — effort; endeavour (source estimate B2, frequency rank 6,716)
- **die Inspiration** — inspiration (source estimate B2, frequency rank 6,418)
- **der Beifall** — applause; clapping (source estimate B2, frequency rank 8,024)
- **die Auszeichnung** — emphasis; distinction (source estimate B2, frequency rank 6,333)
- **die Bestrafung** — punishment; penalisation (source estimate B2, frequency rank 6,542)
- **die Auktion** — auction (source estimate B2, frequency rank 6,842)
- **der Geschäftspartner** — business partner (source estimate B2, frequency rank 7,145)
- **der Behälter** — bin; container (source estimate B2, frequency rank 7,946)
- **die Abwesenheit** — absence; abstraction (source estimate B2, frequency rank 5,748)
- **das Triebwerk** — engine; powerplant (source estimate B2, frequency rank 7,848)
- **das Logbuch** — logbook (source estimate B2, frequency rank 8,051)
- **das Arbeitszimmer** — bureau; home office (source estimate B2, frequency rank 7,456)

### Level 3 — Advanced
- **die Ablösung** — shift change; removal (source estimate C1, frequency rank 17,831)
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
- **die Infrastruktur** — infrastructure (source estimate C1, frequency rank 14,819)
- **die Steuererklärung** — tax declaration (source estimate C1, frequency rank 15,526)

## Editorial QA

- Level 1: learner-value 2–23; difficulty 4.92–8.68; CEFR proxy {'B2': 400}
- Level 2: learner-value 3–30; difficulty 8.68–14.75; CEFR proxy {'B2': 200, 'C1': 150}
- Level 3: learner-value 8–18; difficulty 14.77–21.23; CEFR proxy {'C1': 250}

### Lowest learner-value selections

- **der Teich** — pond; pool (value 2, rank 7,209, B2)
- **das Aspirin** — aspirin; acetylsalicylic acid (value 2, rank 6,228, B2)
- **der Generator** — generator (value 2, rank 6,025, B2)
- **die Website** — website (value 2, rank 5,907, B2)
- **der Astronaut** — astronaut (value 2, rank 5,422, B2)
- **das Echo** — echo (value 2, rank 5,368, B2)
- **der Bunker** — bunker; stash (value 2, rank 5,233, B2)
- **der Frost** — frost; frostiness (value 2, rank 5,117, B2)
- **der Profit** — profit (value 2, rank 5,112, B2)
- **die Mafia** — mafia (value 2, rank 4,827, B2)
- **der Tumor** — tumor; tumour (value 2, rank 4,811, B2)
- **die Ohnmacht** — faint; swoon (value 3, rank 8,099, B2)
- **der Hinterkopf** — occiput (value 3, rank 8,093, B2)
- **die Mithilfe** — assistance (value 3, rank 8,080, B2)
- **der Scheinwerfer** — spotlight; headlight (value 3, rank 8,064, B2)
- **der Körperteil** — body part (value 3, rank 8,053, B2)
- **das Logbuch** — logbook (value 3, rank 8,051, B2)
- **die Schlucht** — gorge; ravine (value 3, rank 8,049, B2)
- **der Vorschuss** — advance (value 3, rank 8,039, B2)
- **der Beifall** — applause; clapping (value 3, rank 8,024, B2)
- **der Grieche** — Greek (value 3, rank 8,006, B2)
- **das Verbrechen** — crime; criminality (value 3, rank 8,004, B2)
- **der Jahrestag** — anniversary (value 3, rank 7,997, B2)
- **der Eintrag** — entry (value 3, rank 7,978, B2)
- **das Kartell** — cartel (value 3, rank 7,977, B2)
- **der Gründer** — founder (value 3, rank 7,967, B2)
- **der Feldwebel** — staff sergeant (value 3, rank 7,965, B2)
- **der Angeber** — showoff; blusterer (value 3, rank 7,954, B2)
- **der Behälter** — bin; container (value 3, rank 7,946, B2)
- **die Sklaverei** — slavery (value 3, rank 7,936, B2)
