# V2-2 — 1,000-Word B2→C1 Bridge Corpus

## Result

- Bridge rows: **1,000**
- Level 1 — Intermediate: **400**
- Level 2 — Upper Intermediate: **350**
- Level 3 — Advanced: **250**
- Source CEFR estimates: **600 B2 / 400 C1**
- Articles: **der 232 / die 647 / das 121**
- Eligible source-corroborated pool before final rank cut: **3,028** nouns (935 B2, 2,093 C1)
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
7. Select 600 high-value B2 nouns: the easier 400 become Intermediate and the stronger 200 enter Upper Intermediate. Add 150 accessible C1 nouns to Upper Intermediate. Advanced contains 250 distinct C1 nouns with frequency rank at least 10,500 plus formal/abstract lexical evidence.

## Source and licensing

- **wordhoard**: https://github.com/natema/wordhoard, release v0.1.0 (2026-07-16); downloaded archive SHA-256 `83837efd46241e7226fc6daaa9d0cc81b57bf746434b8c539049c660d98ba761`. The built dataset is CC-BY-SA-4.0 and combines OpenSubtitles-derived frequency evidence with openly licensed lexical sources. Goethe material is calibration-only and is not redistributed.
- **German Wiktionary extraction**: https://github.com/karoly-varasdi/de-wiktionary-parser, pinned commit `73075bb76c9261c44923f4909858586b261bfd83`; `de_noun_entries_with_translations.zip` Git blob `a56efcb80b64433107ec1f376b933c572f2427c9`. English translations and the second-source grammar check derive from German Wiktionary data.
- The checked-in Bridge corpus, Bridge gloss asset, and Bridge provenance are distributed under **CC-BY-SA-4.0**. The existing Challenge translation asset remains separately licensed as documented in `THIRD_PARTY_NOTICES.md`.

## Frequency-rank ranges

- Level 1: 4,624–7,978
- Level 2: 5,694–11,499
- Level 3: 11,509–17,831

## Largest semantic groups

- bridge-general: 922
- legal: 13
- economy: 12
- technology: 9
- process: 8
- politics: 7
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
- learner_suitability_explicit_noise: 79
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
- Level 2: learner-value 1–30; difficulty 8.68–14.59; CEFR proxy {'B2': 200, 'C1': 150}
- Level 3: learner-value 8–18; difficulty 13.71–20.56; CEFR proxy {'C1': 250}

### Lowest learner-value selections

- **die Hypnose** — hypnosis (value 1, rank 9,596, C1)
- **das Omelett** — omelet; omelette (value 1, rank 9,581, C1)
- **der Erfinder** — inventor (value 1, rank 9,562, C1)
- **der Bankier** — banker (value 1, rank 9,546, C1)
- **der Kritiker** — critic (value 1, rank 9,533, C1)
- **der Verleger** — issuer; publisher (value 1, rank 9,509, C1)
- **die Brautjungfer** — bridesmaid (value 1, rank 9,505, C1)
- **der Wikinger** — viking (value 1, rank 9,502, C1)
- **der Neuling** — newcomer; novice (value 1, rank 9,490, C1)
- **der Verschluss** — closing (value 1, rank 9,479, C1)
- **der Hochverrat** — high treason (value 1, rank 9,441, C1)
- **der Verwalter** — administrator (value 1, rank 9,438, C1)
- **der Dorfbewohner** — villager (value 1, rank 9,437, C1)
- **der Schiedsrichter** — referee; umpire (value 1, rank 9,433, C1)
- **der Waschbär** — Common Raccoon; Northern Raccoon (value 1, rank 9,410, C1)
- **der Pfirsich** — peach (value 1, rank 9,399, C1)
- **das Bataillon** — battalion (value 1, rank 9,396, C1)
- **der Kopfhörer** — headphone (value 1, rank 9,349, C1)
- **die Kaiserin** — empress (value 1, rank 9,344, C1)
- **das Amulett** — amulet (value 1, rank 9,340, C1)
- **das Raubtier** — carnivore; predator (value 1, rank 9,324, C1)
- **der Sündenbock** — scapegoat (value 1, rank 9,321, C1)
- **der Beschuss** — fire; shelling (value 1, rank 9,308, C1)
- **die Kleinstadt** — town; township (value 1, rank 9,297, C1)
- **die Periode** — tide; period (value 1, rank 9,291, C1)
- **die Schwachstelle** — trouble spot; weak point (value 1, rank 9,277, C1)
- **der Elternteil** — parent (value 1, rank 9,267, C1)
- **das Frühjahr** — spring (value 1, rank 9,263, C1)
- **das Abzeichen** — badge (value 1, rank 9,251, C1)
- **die Zeitreise** — time travel (value 1, rank 9,245, C1)
