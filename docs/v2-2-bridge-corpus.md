# V2-2 — 1,000-Word B2→C1 Bridge Corpus

## Result

- Bridge rows: **1,000**
- Level 1 — Intermediate: **400**
- Level 2 — Upper Intermediate: **350**
- Level 3 — Advanced: **250**
- Source CEFR estimates: **750 B2 / 250 C1**
- Articles: **der 418 / die 408 / das 174**
- Eligible source-corroborated pool before final rank cut: **3,195** nouns (1,036 B2, 2,159 C1)
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

- Level 1: 4,624–6,614
- Level 2: 6,616–8,039
- Level 3: 9,245–10,222

## Largest semantic groups

- bridge-general: 963
- technology: 5
- process: 5
- politics: 4
- economy: 4
- education: 4
- structure: 3
- legal: 3
- emotion: 2
- environment: 2
- society: 2
- health: 2

## Rejection audit

- no_wiktionary_translation_entry: 877
- no_clean_english_gloss: 460
- gender_not_single_source_corroborated: 250
- challenge_overlap: 171
- missing_or_invalid_gender: 89
- special_name_only: 56
- candidate_duplicate: 11
- invalid_orthography: 2

## Corpus sample

### Level 1 — Intermediate
- **der Eid** — oath (source estimate B2, frequency rank 4,624)
- **das Funkgerät** — radio (source estimate B2, frequency rank 4,625)
- **die Bude** — shack (source estimate B2, frequency rank 4,630)
- **der Häftling** — detainee; prisoner (source estimate B2, frequency rank 4,636)
- **die Zeitverschwendung** — waste of time (source estimate B2, frequency rank 4,638)
- **die Gnade** — mercy (source estimate B2, frequency rank 4,651)
- **der Weltkrieg** — world war (source estimate B2, frequency rank 4,653)
- **der Pirat** — pirate (source estimate B2, frequency rank 4,656)
- **der Rückzug** — retreat (source estimate B2, frequency rank 4,659)
- **die Geste** — gesture; act of friendship (source estimate B2, frequency rank 4,660)
- **die Genehmigung** — approval (source estimate B2, frequency rank 4,668)
- **der Orden** — order; medal; decoration (source estimate B2, frequency rank 4,674)
- **die Statue** — statue (source estimate B2, frequency rank 4,681)
- **der Satellit** — satellite (source estimate B2, frequency rank 4,684)
- **der Kater** — cat; tomcat; tom (source estimate B2, frequency rank 4,692)
- **der Prophet** — prophet (source estimate B2, frequency rank 4,700)
- **die Division** — division (source estimate B2, frequency rank 4,703)
- **der Pastor** — pastor (source estimate B2, frequency rank 4,705)
- **die Datenbank** — data bank; data base; databank (source estimate B2, frequency rank 4,706)
- **der Stab** — staff; rod; bar (source estimate B2, frequency rank 4,719)

### Level 2 — Upper Intermediate
- **der Dinosaurier** — dinosaur; dino; dinosaurus (source estimate B2, frequency rank 6,616)
- **der Dekan** — dean (source estimate B2, frequency rank 6,618)
- **die Kuppel** — dome (source estimate B2, frequency rank 6,626)
- **die Provinz** — province (source estimate B2, frequency rank 6,627)
- **die Bindung** — relationship; tie; attachment (source estimate B2, frequency rank 6,628)
- **der Krüppel** — cripple (source estimate B2, frequency rank 6,632)
- **der Treibstoff** — fuel (source estimate B2, frequency rank 6,635)
- **die Quarantäne** — quarantine (source estimate B2, frequency rank 6,646)
- **der Kommunist** — communist (source estimate B2, frequency rank 6,647)
- **der Gemahl** — spouse; husband (source estimate B2, frequency rank 6,650)
- **der Sturz** — fall; collapse; drop (source estimate B2, frequency rank 6,652)
- **das Gewebe** — fabric; tissue (source estimate B2, frequency rank 6,653)
- **die Nachforschung** — inquiry (source estimate B2, frequency rank 6,654)
- **das Portal** — portal; gantry (source estimate B2, frequency rank 6,655)
- **der Hummer** — lobster (source estimate B2, frequency rank 6,659)
- **die Wanne** — tub (source estimate B2, frequency rank 6,671)
- **die Taschenlampe** — flashlight; torch (source estimate B2, frequency rank 6,672)
- **der Lieferwagen** — van; box van; delivery van (source estimate B2, frequency rank 6,678)
- **der Kragen** — collar (source estimate B2, frequency rank 6,686)
- **der Valentinstag** — Valentine's Day; Saint Valentine's Day (source estimate B2, frequency rank 6,690)

### Level 3 — Advanced
- **die Zeitreise** — time travel (source estimate C1, frequency rank 9,245)
- **das Abzeichen** — badge (source estimate C1, frequency rank 9,251)
- **die Schlaftablette** — sleeping pill (source estimate C1, frequency rank 9,252)
- **das Lenkrad** — steering wheel (source estimate C1, frequency rank 9,258)
- **das Frühjahr** — spring (source estimate C1, frequency rank 9,263)
- **die Grundschule** — elementary school; grade school; primary school (source estimate C1, frequency rank 9,265)
- **die Glatze** — bald head; skinhead (source estimate C1, frequency rank 9,266)
- **der Elternteil** — parent (source estimate C1, frequency rank 9,267)
- **die Geburtstagsparty** — birthday party (source estimate C1, frequency rank 9,274)
- **das Telefonbuch** — directory; phone book; telephone directory (source estimate C1, frequency rank 9,275)
- **die Strömung** — tide (source estimate C1, frequency rank 9,276)
- **die Schwachstelle** — trouble spot; weak point (source estimate C1, frequency rank 9,277)
- **der Hippie** — hippie (source estimate C1, frequency rank 9,278)
- **die Atmung** — respiration (source estimate C1, frequency rank 9,279)
- **die Periode** — tide; period (source estimate C1, frequency rank 9,291)
- **die Kleinstadt** — town; township; townikin (source estimate C1, frequency rank 9,297)
- **das Verteidigungsministerium** — Ministry of Defence (source estimate C1, frequency rank 9,298)
- **der Beschuss** — fire; shelling; bombardment (source estimate C1, frequency rank 9,308)
- **das Jackett** — jacket (source estimate C1, frequency rank 9,309)
- **die Traube** — grape; raceme (source estimate C1, frequency rank 9,310)
