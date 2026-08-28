#!/usr/bin/env python3
"""Embed the maintained fullscreen practice assets into app-source.html."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "app-source.html"
CSS_PATH = ROOT / "src" / "practice-screen.css"
JS_PATH = ROOT / "src" / "practice-screen.js"
START = "<!-- ARTIKELWERK_DEDICATED_PRACTICE_SCREEN_START -->"
END = "<!-- ARTIKELWERK_DEDICATED_PRACTICE_SCREEN_END -->"


def add_viewport_fit_cover(source: str) -> str:
    viewport_pattern = re.compile(
        r'(<meta\b[^>]*\bname\s*=\s*["\']viewport["\'][^>]*\bcontent\s*=\s*["\'])([^"\']*)(["\'][^>]*>)',
        flags=re.IGNORECASE,
    )
    match = viewport_pattern.search(source)
    if match:
        content = match.group(2)
        if "viewport-fit" not in content.lower():
            content = content.rstrip(" ,") + ", viewport-fit=cover"
            source = source[: match.start(2)] + content + source[match.end(2) :]
        return source

    head = re.search(r"<head\b[^>]*>", source, flags=re.IGNORECASE)
    if not head:
        raise ValueError("Source has no <head> element")
    meta = '\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
    return source[: head.end()] + meta + source[head.end() :]


def remove_existing_block(source: str) -> str:
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), flags=re.DOTALL)
    return pattern.sub("", source)


def embed(source: str, css: str, javascript: str) -> str:
    if "</script" in javascript.lower():
        raise ValueError("JavaScript asset contains a literal </script sequence")

    block = (
        f"\n{START}\n"
        '<style id="artikelwerk-dedicated-practice-styles">\n'
        f"{css.rstrip()}\n"
        "</style>\n"
        '<script id="artikelwerk-dedicated-practice-controller">\n'
        f"{javascript.rstrip()}\n"
        "</script>\n"
        f"{END}\n"
    )

    body_closings = list(re.finditer(r"</body\s*>", source, flags=re.IGNORECASE))
    if not body_closings:
        raise ValueError("Source has no closing </body> element")
    closing = body_closings[-1]
    return source[: closing.start()] + block + source[closing.start() :]


def main() -> int:
    for path in (SOURCE_PATH, CSS_PATH, JS_PATH):
        if not path.exists():
            raise FileNotFoundError(path)

    source = SOURCE_PATH.read_text(encoding="utf-8")
    css = CSS_PATH.read_text(encoding="utf-8")
    javascript = JS_PATH.read_text(encoding="utf-8")

    source = remove_existing_block(source)
    source = add_viewport_fit_cover(source)
    source = embed(source, css, javascript)
    SOURCE_PATH.write_text(source, encoding="utf-8", newline="\n")

    if source.count(START) != 1 or source.count(END) != 1:
        raise RuntimeError("Practice enhancement markers are not unique")
    print(f"Embedded dedicated practice screen into {SOURCE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
