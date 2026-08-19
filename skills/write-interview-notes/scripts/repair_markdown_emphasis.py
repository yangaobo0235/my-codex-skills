#!/usr/bin/env python3
"""Repair malformed bold markers left by source conversion."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def marker_count(line: str) -> int:
    return len(re.findall(r"(?<!\\)\*\*", line))


def repair(text: str) -> str:
    source = text.splitlines()
    lines: list[str] = []
    for line in source:
        # A standalone marker was intended to close the previous callout line.
        if line.strip() in {"> - **", "> **"}:
            if lines and marker_count(lines[-1]) % 2:
                lines[-1] += "**"
            continue

        # Conversion occasionally inserted an empty bold opener after a bullet.
        if line.startswith("> - ** **"):
            line = line.replace("> - ** **", "> - **", 1)
        elif line.startswith("> - ** "):
            line = line.replace("> - ** ", "> - ", 1)

        if marker_count(line) % 2:
            line += "**"
        lines.append(line)

    output = "\n".join(lines)
    if text.endswith("\n"):
        output += "\n"
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    files = [args.path] if args.path.is_file() else sorted(args.path.rglob("*.md"))
    changed = 0
    for path in files:
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        output = repair(text)
        encoded = output.encode("utf-8")
        if bom:
            encoded = b"\xef\xbb\xbf" + encoded
        if encoded != raw:
            path.write_bytes(encoded)
            changed += 1
    print(f"Files changed: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
