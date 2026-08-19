#!/usr/bin/env python3
"""Reformat plain interview callouts into conversational, scannable points."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CALLOUT_START = re.compile(r"^> \[!(abstract|note)\](?:[+-])?\s*(.*?)\s*$")
LIST_LINE = re.compile(r"^>\s+(?:[-*+]\s+|\d+[.)]\s+)")
SPECIAL_LINE = re.compile(r"^>\s*(?:```|\| |!\[|\[!|#{1,6}\s)")
SENTENCE_SPLIT = re.compile(r"(?<=[。！？?])\s*|(?<=；)\s*")
ENUM_SPLIT = re.compile(r"(?=(?:第一|第二|第三|第四|第五|首先|其次|再次|最后)[，、：:])")


def callout_blocks(lines: list[str]):
    i = 0
    while i < len(lines):
        match = CALLOUT_START.match(lines[i])
        if not match:
            i += 1
            continue
        j = i + 1
        while j < len(lines) and lines[j].startswith(">"):
            j += 1
        yield i, j, match.group(1), match.group(2)
        i = j


def strip_quote(line: str) -> str:
    if line == ">":
        return ""
    return re.sub(r"^> ?", "", line)


def split_units(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = [part.strip() for part in SENTENCE_SPLIT.split(text) if part.strip()]
    units: list[str] = []
    for part in parts:
        enum_parts = [item.strip() for item in ENUM_SPLIT.split(part) if item.strip()]
        units.extend(enum_parts)
    return units


def choose_lead_and_points(units: list[str]) -> tuple[str, list[str]] | None:
    if len(units) < 2:
        return None

    lead = units[0]
    points = units[1:]

    # A colon often introduces the real list; keep the setup as the lead.
    if "：" in lead or ":" in lead:
        prefix, suffix = re.split(r"[：:]", lead, maxsplit=1)
        if 8 <= len(prefix) <= 55 and suffix.strip():
            lead = prefix.strip() + "："
            points.insert(0, suffix.strip())

    # Merge very short fragments with their successor so bullets remain speakable.
    merged: list[str] = []
    for point in points:
        if merged and len(merged[-1]) < 18:
            merged[-1] = merged[-1].rstrip("；。") + "，" + point
        else:
            merged.append(point)
    points = merged

    if not points:
        return None
    while len(points) > 4:
        pair_index = min(
            range(len(points) - 1), key=lambda i: len(points[i]) + len(points[i + 1])
        )
        points[pair_index : pair_index + 2] = [
            points[pair_index].rstrip("；。") + "；" + points[pair_index + 1]
        ]
    return lead, points


def reformat_block(block: list[str], kind: str) -> list[str]:
    body = block[1:]
    if not body:
        return block
    if any(LIST_LINE.match(line) or SPECIAL_LINE.match(line) for line in body):
        return block

    paragraphs: list[str] = []
    current: list[str] = []
    for line in body:
        plain = strip_quote(line).strip()
        if not plain:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(plain)
    if current:
        paragraphs.append(" ".join(current))

    text = " ".join(paragraphs).strip()
    threshold = 72 if kind == "note" else 110
    if len(re.sub(r"\s+", "", text)) < threshold:
        return block

    chosen = choose_lead_and_points(split_units(text))
    if not chosen:
        return block
    lead, points = chosen
    if len(points) < 2 and len(text) < 150:
        return block

    output = [block[0], f"> {lead}", ">"]
    output.extend(f"> - {point}" for point in points)
    return output


def process_file(path: Path, write: bool) -> tuple[int, int]:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    original = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in original else "\n"
    had_final_newline = original.endswith(("\n", "\r"))
    lines = original.splitlines()
    replacements: list[tuple[int, int, list[str]]] = []
    for start, end, kind, _title in callout_blocks(lines):
        block = lines[start:end]
        updated = reformat_block(block, kind)
        if updated != block:
            replacements.append((start, end, updated))

    for start, end, updated in reversed(replacements):
        lines[start:end] = updated
    rendered = newline.join(lines) + (newline if had_final_newline else "")
    if write and rendered != original:
        path.write_text(rendered, encoding="utf-8-sig" if had_bom else "utf-8", newline="")
    return len(replacements), len(original) - len(rendered)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Markdown file or directory")
    parser.add_argument("--write", action="store_true", help="Write changes in place")
    args = parser.parse_args()
    target = args.path.expanduser().resolve()
    files = [target] if target.is_file() else sorted(target.rglob("*.md"))
    files = [path for path in files if path.suffix.lower() == ".md"]

    changed_files = 0
    changed_blocks = 0
    for path in files:
        blocks, _delta = process_file(path, args.write)
        if blocks:
            changed_files += 1
            changed_blocks += blocks
            print(f"{path}: {blocks} callout(s)")
    print(f"Files scanned: {len(files)}")
    print(f"Files changed: {changed_files}")
    print(f"Callouts changed: {changed_blocks}")
    print("Mode: write" if args.write else "Mode: dry-run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
