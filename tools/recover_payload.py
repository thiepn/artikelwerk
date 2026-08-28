#!/usr/bin/env python3
"""Recover Artikelwerk's editable HTML source from its payload archive.

The script is intentionally idempotent:
1. Keep an already valid app-source.html.
2. Decode a valid payload normally.
3. As a one-time compatibility path, repair the historical single missing
   Base64 character in payload/08.txt.
"""

from __future__ import annotations

import base64
import gzip
import multiprocessing as mp
import os
import re
import sys
import zlib
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_DIR = ROOT / "payload"
SOURCE_PATH = ROOT / "app-source.html"
REPORT_PATH = ROOT / "recovery-report.txt"
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

_SEARCH_DATA = ""
_SEARCH_PREFIX_END = 0


def valid_html(text: str) -> bool:
    lower = text.lower()
    return (
        len(text.encode("utf-8")) > 100_000
        and "<html" in lower
        and "</html>" in lower
        and "<body" in lower
        and "</body>" in lower
    )


def payload_parts() -> list[Path]:
    parts = [PAYLOAD_DIR / f"{index:02d}.txt" for index in range(10)]
    missing = [str(path.relative_to(ROOT)) for path in parts if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing payload parts: {', '.join(missing)}")
    return parts


def read_payload() -> tuple[str, list[int]]:
    values = [re.sub(r"\s+", "", path.read_text(encoding="ascii")) for path in payload_parts()]
    offsets: list[int] = []
    cursor = 0
    for value in values:
        offsets.append(cursor)
        cursor += len(value)
    return "".join(values), offsets


def decode_payload(encoded: str) -> str:
    if len(encoded) % 4 == 1:
        raise ValueError("Base64 length is impossible (modulo 4 equals 1)")
    padded = encoded + "=" * ((4 - len(encoded) % 4) % 4)
    compressed = base64.b64decode(padded, validate=True)
    return gzip.decompress(compressed).decode("utf-8")


def write_source(text: str, mode: str, details: Iterable[str] = ()) -> None:
    if not valid_html(text):
        raise ValueError("Recovered source does not look like a complete HTML document")
    SOURCE_PATH.write_text(text, encoding="utf-8", newline="\n")
    report = [
        f"mode={mode}",
        f"source_bytes={len(text.encode('utf-8'))}",
        f"source_characters={len(text)}",
        *details,
    ]
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")


def corrupt_stream_error_offset(encoded: str) -> int:
    """Estimate where the damaged Base64 stream first breaks gzip/deflate."""
    artificial = encoded + "A" * ((4 - len(encoded) % 4) % 4)
    compressed = base64.b64decode(artificial, validate=True)
    inflater = zlib.decompressobj(31)
    offset = 0
    step = 32
    while offset < len(compressed):
        block = compressed[offset : offset + step]
        try:
            inflater.decompress(block)
        except zlib.error:
            return offset + step
        offset += len(block)
    return len(compressed)


def _init_worker(encoded: str, prefix_end: int) -> None:
    global _SEARCH_DATA, _SEARCH_PREFIX_END
    _SEARCH_DATA = encoded
    _SEARCH_PREFIX_END = prefix_end


def _probe_candidate(candidate: tuple[int, str]) -> tuple[int, str, int] | None:
    position, character = candidate
    repaired = _SEARCH_DATA[:position] + character + _SEARCH_DATA[position:_SEARCH_PREFIX_END]
    repaired = repaired[: len(repaired) - (len(repaired) % 4)]
    try:
        compressed = base64.b64decode(repaired, validate=True)
        inflater = zlib.decompressobj(31)
        output = inflater.decompress(compressed)
        return position, character, len(output)
    except (ValueError, base64.binascii.Error, zlib.error):
        return None


def candidate_ranges(start: int, end: int, approximate: int) -> list[tuple[int, int]]:
    windows = [
        (max(start, approximate - 1536), min(end, approximate + 160)),
        (max(start, approximate - 8192), min(end, approximate + 512)),
        (start, end),
    ]
    unique: list[tuple[int, int]] = []
    for window in windows:
        if window[0] < window[1] and window not in unique:
            unique.append(window)
    return unique


def parse_known_repair(encoded: str) -> tuple[int, str] | None:
    """Reuse exact metadata from an earlier diagnostic run when present."""
    for name in ("source-metadata.txt", "recovery-report.txt"):
        path = ROOT / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        patterns = [
            r"(?:insert(?:ion)?[_ -]?(?:position|index|offset)|global[_ -]?(?:position|index|offset))\s*[:=]\s*(\d+).*?(?:inserted?[_ -]?(?:char(?:acter)?)?|character)\s*[:=]\s*['\"]?([A-Za-z0-9+/])",
            r"(?:inserted?[_ -]?(?:char(?:acter)?)?|character)\s*[:=]\s*['\"]?([A-Za-z0-9+/]).*?(?:insert(?:ion)?[_ -]?(?:position|index|offset)|global[_ -]?(?:position|index|offset))\s*[:=]\s*(\d+)",
        ]
        for index, pattern in enumerate(patterns):
            match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            if not match:
                continue
            if index == 0:
                position, character = int(match.group(1)), match.group(2)
            else:
                character, position = match.group(1), int(match.group(2))
            if 0 <= position <= len(encoded) and character in ALPHABET:
                return position, character
    return None


def full_validate(encoded: str, position: int, character: str) -> str | None:
    try:
        text = decode_payload(encoded[:position] + character + encoded[position:])
    except (ValueError, UnicodeDecodeError, gzip.BadGzipFile, EOFError, zlib.error, base64.binascii.Error):
        return None
    return text if valid_html(text) else None


def repair_single_missing_character(encoded: str, offsets: list[int]) -> tuple[str, int, str]:
    known = parse_known_repair(encoded)
    if known:
        position, character = known
        text = full_validate(encoded, position, character)
        if text is not None:
            return text, position, character

    error_byte = corrupt_stream_error_offset(encoded)
    approximate = error_byte * 4 // 3
    chunk_start = offsets[8]
    chunk_end = offsets[9] if len(offsets) > 9 else len(encoded)
    approximate = min(max(approximate, chunk_start), chunk_end)

    for start, end in candidate_ranges(chunk_start, chunk_end, approximate):
        prefix_end = min(len(encoded), max(approximate + 8192, end + 2048))
        jobs = ((position, character) for position in range(start, end + 1) for character in ALPHABET)
        process_count = max(1, min(os.cpu_count() or 2, 8))
        survivors: list[tuple[int, str, int]] = []
        with mp.Pool(processes=process_count, initializer=_init_worker, initargs=(encoded, prefix_end)) as pool:
            for result in pool.imap_unordered(_probe_candidate, jobs, chunksize=256):
                if result is not None:
                    survivors.append(result)

        survivors.sort(key=lambda item: item[2], reverse=True)
        for position, character, _score in survivors[:512]:
            text = full_validate(encoded, position, character)
            if text is not None:
                return text, position, character

    raise RuntimeError("Unable to repair the historical one-character Base64 corruption")


def main() -> int:
    if SOURCE_PATH.exists():
        current = SOURCE_PATH.read_text(encoding="utf-8", errors="strict")
        if valid_html(current):
            write_source(current, "existing-valid-source")
            print(f"Using existing valid source: {SOURCE_PATH}")
            return 0

    encoded, offsets = read_payload()
    try:
        source = decode_payload(encoded)
    except (ValueError, UnicodeDecodeError, gzip.BadGzipFile, EOFError, zlib.error, base64.binascii.Error):
        if len(encoded) % 4 != 1:
            raise
        source, position, character = repair_single_missing_character(encoded, offsets)
        write_source(
            source,
            "single-character-base64-repair",
            (
                f"insert_position={position}",
                f"insert_character={character}",
                f"damaged_chunk=08.txt",
            ),
        )
        print(f"Recovered source by inserting {character!r} at Base64 offset {position}")
        return 0

    write_source(source, "normal-payload-decode")
    print(f"Decoded valid payload into {SOURCE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
