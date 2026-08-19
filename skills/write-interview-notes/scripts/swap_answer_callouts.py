#!/usr/bin/env python3
"""Swap interview answer callout kinds without changing their bodies."""

from __future__ import annotations

import argparse
from pathlib import Path


OLD_DIRECT = "> [!abstract] 可直接回答"
NEW_DIRECT = "> [!note] 可直接回答"
OLD_DEEP = "> [!note] 深挖补充"
NEW_DEEP = "> [!abstract] 深挖补充"


def markdown_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if target.suffix.lower() == ".md" else []
    return sorted(target.rglob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    target = args.path.resolve()

    changed = direct = deep = 0
    for path in markdown_files(target):
        raw = path.read_bytes()
        has_bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        lines = text.splitlines(keepends=True)
        file_changed = False
        for index, line in enumerate(lines):
            ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            content = line[: -len(ending)] if ending else line
            if content == OLD_DIRECT:
                lines[index] = NEW_DIRECT + ending
                direct += 1
                file_changed = True
            elif content == OLD_DEEP:
                lines[index] = NEW_DEEP + ending
                deep += 1
                file_changed = True
        if file_changed:
            output = "".join(lines).encode("utf-8")
            path.write_bytes((b"\xef\xbb\xbf" if has_bom else b"") + output)
            changed += 1

    print(f"Files changed: {changed}")
    print(f"Direct answers swapped: {direct}")
    print(f"Deep dives swapped: {deep}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
