#!/usr/bin/env python3
"""Build Artikelwerk's ten deterministic Base64/gzip payload chunks."""

from __future__ import annotations

import base64
import gzip
import hashlib
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "app-source.html"
PAYLOAD_DIR = ROOT / "payload"
REPORT_PATH = ROOT / "payload-build-report.txt"
CHUNK_COUNT = 10


def main() -> int:
    source = SOURCE_PATH.read_bytes()
    if len(source) < 100_000 or b"</html>" not in source.lower():
        raise ValueError("app-source.html is not a complete application source")

    compressed = gzip.compress(source, compresslevel=9, mtime=0)
    encoded = base64.b64encode(compressed).decode("ascii")
    width = math.ceil(len(encoded) / CHUNK_COUNT)

    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
    chunks = [encoded[index * width : (index + 1) * width] for index in range(CHUNK_COUNT)]
    if len(chunks) != CHUNK_COUNT or any(not chunk for chunk in chunks):
        raise RuntimeError("Could not produce ten non-empty payload chunks")

    for index, chunk in enumerate(chunks):
        (PAYLOAD_DIR / f"{index:02d}.txt").write_text(chunk, encoding="ascii", newline="")

    rebuilt = "".join((PAYLOAD_DIR / f"{index:02d}.txt").read_text(encoding="ascii") for index in range(CHUNK_COUNT))
    decoded = gzip.decompress(base64.b64decode(rebuilt, validate=True))
    if decoded != source:
        raise RuntimeError("Payload round-trip does not match app-source.html")

    report = [
        "status=passed",
        f"source_bytes={len(source)}",
        f"compressed_bytes={len(compressed)}",
        f"base64_characters={len(encoded)}",
        f"chunk_count={CHUNK_COUNT}",
        f"smallest_chunk={min(map(len, chunks))}",
        f"largest_chunk={max(map(len, chunks))}",
        f"source_sha256={hashlib.sha256(source).hexdigest()}",
        f"payload_sha256={hashlib.sha256(encoded.encode('ascii')).hexdigest()}",
    ]
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("Built and round-trip verified ten payload chunks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
