#!/usr/bin/env python3
"""Static integrity checks for the dedicated Artikelwerk practice screen."""

from __future__ import annotations

import base64
import gzip
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "app-source.html"
INDEX_PATH = ROOT / "index.html"
PAYLOAD_DIR = ROOT / "payload"
REPORT_PATH = ROOT / "practice-screen-verification.txt"
START = "ARTIKELWERK_DEDICATED_PRACTICE_SCREEN_START"
END = "ARTIKELWERK_DEDICATED_PRACTICE_SCREEN_END"


def require(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    checks.append(message)


def main() -> int:
    source_bytes = SOURCE_PATH.read_bytes()
    source = source_bytes.decode("utf-8")
    index = INDEX_PATH.read_text(encoding="utf-8")
    checks: list[str] = []

    require(source.count(START) == 1 and source.count(END) == 1, "single enhancement block", checks)
    require('id="aw-practice-shell"' in source, "fullscreen practice shell exists", checks)
    require('id="aw-practice-launch"' in source or "LAUNCH_ID = 'aw-practice-launch'" in source, "dedicated practice launcher exists", checks)
    require("position: fixed" in source and "height: var(--aw-practice-vh" in source, "fixed dynamic-viewport layout", checks)
    require("overflow: hidden" in source and "overscroll-behavior: none" in source, "outer scrolling disabled", checks)
    require("safe-area-inset-top" in source and "safe-area-inset-bottom" in source, "device safe areas supported", checks)
    require("orientation: landscape" in source and "max-height: 660px" in source, "small-height and landscape layouts", checks)
    require("data-aw-article-choice" in source and "min-height: clamp(58px" in source, "large article tap targets", checks)
    require("English meaning" in source and "Explanation in English" in source, "English support panel", checks)
    require("api.mymemory.translated.net" in source, "German-to-English network fallback", checks)
    require("artikelwerk:english-cache:v1" in source, "translation cache", checks)
    require("translationIndex" in source and "localStorage" in source, "local vocabulary translation lookup", checks)
    require("scrollIntoView" in source and "state.open" in source, "automatic scroll guard", checks)
    require("event.key === 'Escape'" in source and "focusableElements" in source, "keyboard close and focus containment", checks)
    require("viewport-fit=cover" in source, "viewport supports safe-area cover", checks)
    require(source.lower().count("</html>") == 1, "single complete HTML document", checks)

    expected_parts = [f"payload/{number:02d}.txt" for number in range(10)]
    require(all(part in index for part in expected_parts), "loader references all ten payload chunks", checks)
    require("DecompressionStream" in index and "gzip" in index, "loader performs gzip decompression", checks)

    encoded = "".join((PAYLOAD_DIR / f"{number:02d}.txt").read_text(encoding="ascii").strip() for number in range(10))
    require(len(encoded) % 4 == 0, "payload Base64 length is valid", checks)
    decoded = gzip.decompress(base64.b64decode(encoded, validate=True))
    require(decoded == source_bytes, "payload round-trip exactly matches source", checks)

    require(not re.search(r"\ufffd", source), "source contains no replacement characters", checks)
    report = [
        "status=passed",
        f"checks={len(checks)}",
        f"source_bytes={len(source_bytes)}",
        f"source_sha256={hashlib.sha256(source_bytes).hexdigest()}",
        *[f"check_{index + 1}={check}" for index, check in enumerate(checks)],
    ]
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Practice-screen verification passed: {len(checks)} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
