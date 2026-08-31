# Third-party notices

## FreeDict German–English dictionary subset

`translations.js` contains a compact subset derived in part from the FreeDict `deu-eng` dictionary, version `2022.04.21-1`.

Copyright © 1995–2022 Frank Richter and © 2020–2022 Einhard Leichtfuß.

The generated translation data asset is distributed under the GNU General Public License, version 3 or any later version. A copy is included at `LICENSES/GPL-3.0.txt`. The generators, coverage report, and selected output are included in this repository so the data can be inspected and rebuilt.

Curated learner-oriented corrections and transparent compound cues in `scripts/generate_translations.py` and `scripts/generate_translations_v2.py` are original Artikelwerk metadata.

## Normal vocabulary dataset — wordhoard + German Wiktionary

`bridge-corpus.js`, `bridge-translations.js`, and `content/bridge-provenance.json` contain the V2-2 Normal vocabulary dataset. These Normal data assets are distributed under **Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA-4.0)**; a copy is included at `LICENSES/CC-BY-SA-4.0.txt`.

Normal candidate selection, frequency ranks, German noun gender, and German CEFR estimates derive from **wordhoard v0.1.0 (2026-07-16)** by Nathan Mathias, available from `https://github.com/natema/wordhoard`. The pinned release archive has SHA-256 `83837efd46241e7226fc6daaa9d0cc81b57bf746434b8c539049c660d98ba761`. wordhoard combines openly licensed lexical sources with OpenSubtitles-derived frequency evidence; its German CEFR estimates use Goethe A1–B1 material only as upstream calibration and do not redistribute Goethe list content.

Normal English translations and an independent gender/common-noun cross-check derive from **German Wiktionary** through the `de-wiktionary-parser` extraction pinned to commit `73075bb76c9261c44923f4909858586b261bfd83` (`de_noun_entries_with_translations.zip`, Git blob `a56efcb80b64433107ec1f376b933c572f2427c9`). German Wiktionary content is available under CC-BY-SA and GFDL terms; Artikelwerk's Normal data distribution uses CC-BY-SA-4.0.

Artikelwerk modifies and filters the upstream material by removing Challenge overlaps, names/special-name-only entries, ambiguous/multi-gender items, malformed/noisy/basic candidates, and by assigning the final Normal learning tiers. Generated learner examples and article-guidance text are Artikelwerk additions. See `docs/v2-2-bridge-corpus.md` for the full construction method and modification record.

