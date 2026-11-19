#!/usr/bin/env python3
"""news-image-20261119 -- ship the front page.

The page itself is entry.png, drawn at build time. This program only
carries it to the grader's output directory, refusing anything that is
not exactly the PNG it expects. Standard library only, no network,
deterministic: the same input always writes the same bytes.
"""
import os
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
SOURCE_NAME = "entry.png"


def fail(message):
    print(f"news-image-20261119: {message}", file=sys.stderr)
    return 1


def png_head(data):
    """Read the IHDR chunk: (width, height) or an error string."""
    if len(data) < 33 or data[12:16] != b"IHDR":
        return None, "PNG has no IHDR chunk where it belongs"
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    depth = data[24]
    colour = data[25]
    if not 0 < width <= 1024 or not 0 < height <= 1024:
        return None, f"PNG is {width}x{height}, over the 1024x1024 cap"
    if depth != 8 or colour not in (2, 6):
        return None, f"PNG uses bit depth {depth} colour type {colour}, want 8-bit RGB(A)"
    return (width, height), None


def load_page(repo):
    source = repo / SOURCE_NAME
    if not source.is_file():
        return None, None, f"missing {SOURCE_NAME} beside main.py"
    data = source.read_bytes()
    if len(data) > MAX_BYTES:
        return None, None, f"{SOURCE_NAME} is {len(data)} bytes, over the 1 MiB cap"
    if not data.startswith(PNG_MAGIC):
        return None, None, f"{SOURCE_NAME} is not a PNG file"
    head, problem = png_head(data)
    if problem is not None:
        return None, None, problem
    return data, head, None


def main():
    repo = Path(__file__).resolve().parent
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    data, head, problem = load_page(repo)
    if problem is not None:
        return fail(problem)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / SOURCE_NAME
    target.write_bytes(data)
    if target.read_bytes() != data:
        return fail("the copy does not match the source byte for byte")
    print(f"news-image-20261119: wrote {target} ({len(data)} bytes, "
          f"{head[0]}x{head[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
