# Artikelwerk content certification — CC2-2026-08-28

Certified on 2026-08-28.

## Runtime policy

Artikelwerk now displays an English gloss only when the corresponding runtime provenance entry is marked `release-reviewed`. Meaning-dependent glosses are additionally gated by explicit reviewed sense IDs. If certified data is missing, the UI displays `English gloss unavailable` rather than falling back to a semantic category label.

## Translation review

- 1,000 / 1,000 vocabulary entries have local runtime glosses.
- 0 topic-label fallbacks remain.
- Existing curated and dictionary-backed glosses retain their source classification.
- Derived compound glosses retain their derived provenance.
- 22 entries received explicit CC2 editorial overrides, including all seven former topic-label fallbacks and awkward compound renderings identified during audit.

## Example certification

All 1,000 source examples plus 2,000 generated context examples are checked deterministically. 66 hard-coded generated-template article occurrences were normalized to the entry-specific `{term_cap}` token so the noun's actual article is always used. CI rejects unresolved tokens and wrong nominative articles immediately before a vocabulary noun.

## Ambiguous gender

The release explicitly verifies:

- `Primat`: current `der` / `das` variant for priority/supremacy.
- `Dossier`: current `das`; masculine `der` is obsolete.
- `Erbe`: `das` for inheritance/legacy; `der` for a male heir.
- `Mangel`: `der` for deficiency/flaw; `die` for the laundry machine.

Authoritative source URLs and access metadata are stored in `content/ambiguous-gender-review.json`.

## Inflection correction

The audited defect `Hinweiss` was corrected to `Hinweises`. Duden gives `der Hinweis; Genitiv: des Hinweises; Plural: die Hinweise`. This targeted external verification is recorded in `content/inflection-review.json`. Structural validation covers the rest of the runtime inflection metadata; a separate exhaustive external dictionary audit is not claimed.

## Device verification

CI exercises the certified runtime at 360×640, 390×844, 412×915, 844×390, 768×1024, and 1440×900. Each profile checks targeted certified glosses, ambiguous-gender detail surfaces, the corrected Hinweis inflection, practice translation rendering, viewport containment, console errors, and external network requests.

These are browser-emulated device profiles. Physical iOS/Android hardware acceptance remains a release-gate item because this environment cannot operate physical devices.
