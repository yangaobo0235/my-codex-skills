#!/usr/bin/env python3
"""Validate the structural conventions of Obsidian interview notes."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


E_RE = re.compile(r"^## E(\d{2})\.\s+(.+?)\s*$")
Q_RE = re.compile(r"^### Q(\d{2})\.\s+(.+?)\s*$")
CALLOUT_RE = re.compile(r"^> \[!([^\]]+)\][+-]?\s*(.*?)\s*$")
PLACEHOLDER_ANSWER_RE = re.compile(
    r"^(?:定义|概念|原理|特点|优点|缺点|作用|应用场景|从.{0,8}说[。.]?|"
    r"给出一个.{0,20}|可以按下面.{0,20}|这是.{0,30}(?:题|追问|问题|原则)[。.]?|"
    r"(?:优秀|完整)回答.{0,40}|不需要背.{0,40}|这个问题我一般.{0,40})$"
)
GENERIC_OVERVIEW_RE = re.compile(
    r"^本节(?:梳理|介绍|覆盖|主要).*(?:定义|原理|场景|边界|关键概念|工程取舍|职责|实现|结果)"
)


def markdown_files(target: Path):
    if target.is_file():
        return [target] if target.suffix.lower() == ".md" else []
    return sorted(target.rglob("*.md"))


def validate(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    errors: list[str] = []
    is_index = "目录索引" in path.stem
    e_numbers: list[int] = []
    current_e: int | None = None
    q_numbers: list[int] = []
    current_q_line: int | None = None
    current_q_title = ""
    direct_count = 0
    direct_body: list[str] = []
    collecting_direct = False
    seen_questions: set[str] = set()

    def finish_question() -> None:
        nonlocal direct_count, direct_body, collecting_direct
        if not is_index and current_q_line is not None and direct_count != 1:
            errors.append(
                f"{path}:{current_q_line}: Q '{current_q_title}' has "
                f"{direct_count} blue direct answers; expected exactly 1"
            )
        if not is_index and current_q_line is not None and direct_count == 1:
            plain = "".join(direct_body)
            plain = re.sub(r"[`*_#>|\[\]()]", "", plain).strip()
            if not plain:
                errors.append(f"{path}:{current_q_line}: Q '{current_q_title}' has an empty direct answer")
            elif PLACEHOLDER_ANSWER_RE.fullmatch(plain):
                errors.append(
                    f"{path}:{current_q_line}: Q '{current_q_title}' has a placeholder direct answer: '{plain}'"
                )
        direct_count = 0
        direct_body = []
        collecting_direct = False

    def finish_e() -> None:
        if q_numbers and q_numbers != list(range(1, len(q_numbers) + 1)):
            errors.append(
                f"{path}: E{current_e:02d} Q numbering is {q_numbers}; "
                "expected Q01..Qn"
            )
        q_numbers.clear()

    for number, line in enumerate(lines, 1):
        e_match = E_RE.match(line)
        if e_match:
            finish_question()
            finish_e()
            current_q_line = None
            current_e = int(e_match.group(1))
            e_numbers.append(current_e)
            seen_questions.clear()
            continue

        q_match = Q_RE.match(line)
        if q_match:
            finish_question()
            if current_e is None:
                errors.append(f"{path}:{number}: Q appears before the first E section")
            current_q_line = number
            current_q_title = q_match.group(2).strip()
            direct_count = 0
            direct_body = []
            collecting_direct = False
            q_numbers.append(int(q_match.group(1)))
            normalized = re.sub(r"[\s`*？?，,。.!！：:]", "", current_q_title).lower()
            if normalized in seen_questions:
                errors.append(f"{path}:{number}: duplicate Q title '{current_q_title}'")
            seen_questions.add(normalized)
            continue

        callout_match = CALLOUT_RE.match(line)
        if callout_match:
            kind = callout_match.group(1).lower()
            title = callout_match.group(2)
            if kind == "note" and title == "可直接回答":
                if current_q_line is None:
                    errors.append(f"{path}:{number}: direct answer appears outside a Q")
                direct_count += 1
                collecting_direct = True
            else:
                collecting_direct = False
            if kind == "abstract" and title == "深挖补充" and current_q_line is None:
                errors.append(f"{path}:{number}: green deep dive appears outside a Q")
            if kind == "tip" and title == "本节速览":
                body_index = number
                body: list[str] = []
                while body_index < len(lines) and lines[body_index].startswith(">"):
                    body.append(re.sub(r"^>\s?", "", lines[body_index]))
                    body_index += 1
                plain_overview = "".join(body).strip()
                if not plain_overview or GENERIC_OVERVIEW_RE.match(plain_overview):
                    errors.append(f"{path}:{number}: generic or empty section overview")
            continue

        if collecting_direct:
            if line.startswith(">"):
                direct_body.append(re.sub(r"^>\s?", "", line))
            elif line.strip():
                collecting_direct = False

    finish_question()
    finish_e()

    if e_numbers and e_numbers != list(range(1, len(e_numbers) + 1)):
        errors.append(f"{path}: E numbering is {e_numbers}; expected E01..En")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Markdown file or directory")
    args = parser.parse_args()
    target = args.path.expanduser().resolve()
    if not target.exists():
        print(f"ERROR: path does not exist: {target}", file=sys.stderr)
        return 2

    files = markdown_files(target)
    all_errors = [error for path in files for error in validate(path)]
    print(f"Markdown files checked: {len(files)}")
    print(f"Errors: {len(all_errors)}")
    for error in all_errors:
        print(f"- {error}")
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
