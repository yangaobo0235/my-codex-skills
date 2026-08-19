#!/usr/bin/env python3
"""Remove coaching narration and normalize overview callouts in interview notes."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CALLOUT_START = re.compile(r"^> \[!([^\]]+)\](?:[+-])?\s*(.*?)\s*$")
E_HEADING = re.compile(r"^## E\d{2}\.\s+")
Q_HEADING = re.compile(r"^### Q\d{2}\.\s+")
GENERIC_OVERVIEW = re.compile(
    r"^>\s*本节(?:梳理|介绍|覆盖|主要(?:介绍|梳理))"
    r".*(?:定义、原理、使用场景和边界|职责、关键实现、结果和事实边界|"
    r"关键概念、工程取舍和适用边界|能力差异、参数设置和使用边界|"
    r"字段语义、约束设计和版本边界|部署形态、适用场景和治理边界|"
    r"知识管理、检索生成和评测边界|故障分类、定位路径和治理边界|"
    r"裁剪、结构化、持久化和上下文边界|目标、数据来源和风险差异|"
    r"身份、配额、执行环境和数据边界|风险链路、阻断位置和处置边界|"
    r"职责分工、制度约束和持续改进机制)。?$"
)


DIRECT_REPLACEMENTS = {
    "如果只抓面试里最常见、最有代表性的特性，我会这样回答：": "JDK 5 和 JDK 8 中比较有代表性的特性分别是：",
    "如果只抓面试最核心的区别，我会这样总结：": "BIO、NIO 和 AIO 的核心区别在于线程等待方式和完成通知机制。",
    "如果让我概括JVM调优的基本思路，我会分成四步：": "JVM 调优通常分成四步：",
    "如果让我一句话总结：": "三者的关系可以概括为：",
    "所以一句话总结就是：": "简单来说，",
    "所以一句话记忆就是：": "简单来说，",
    "所以一句话记忆：": "简单来说：",
    "一句话总结：": "简单来说：",
    "一句话记忆：": "简单来说：",
    "一句话面试版：": "核心结论是：",
    "面试时一句很好的开场是：": "直接来看结论：",
    "一个面试里很好用的说法是：": "可以这样理解：",
    "可以用这么一段话给面试官讲清楚区别": "两者的区别可以概括为：",
    "这道题必须答得明确。": "这里的边界必须明确：",
    "这是面试里必讲的边界。": "这里有一个必须说明的边界：",
    "这是面试里的一个高频比较题。": "这几个概念可以按职责和使用场景比较。",
    "这是校招面试里的高频追问。": "这个问题主要有以下几个原因。",
    "这部分是面试里的高频追问。": "这部分可以从以下几个层面分析。",
    "这是面试里特别爱考的点。": "这里容易混淆。",
    "这句话在面试里非常好用。": "这条边界很重要。",
    "这部分很适合拿来做工程化加分：": "工程上需要重点记录以下状态：",
    "这是一个很好的加分点。": "这里还有一个重要边界。",
    "这是非常容易加分的一部分。": "这部分需要进一步说明。",
    "面试时只要能举出一两个业务化例子，就很加分。": "例如可以用订单重试、审批超时或工具调用失败说明指标如何落到具体业务。",
}


REGEX_REPLACEMENTS = [
    (re.compile(r"^如果只抓面试里最常见、最有代表性的特性，我会这样回答：$"), "JDK 5 和 JDK 8 中比较有代表性的特性分别是："),
    (re.compile(r"^一句话面试版："), "核心结论是："),
]


def clean_callout_line(line: str) -> str:
    prefix = "> " if line.startswith("> ") else ">" if line.startswith(">") else ""
    text = line[len(prefix):]
    for old, new in DIRECT_REPLACEMENTS.items():
        text = text.replace(old, new)
    for pattern, replacement in REGEX_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    text = re.sub(r"\s{2,}", " ", text)
    text = text.replace("：：", "：").replace("，，", "，")
    text = re.sub(r"^[，；：]\s*", "", text)
    return prefix + text.rstrip()


def normalize_overviews(lines: list[str]) -> tuple[list[str], int]:
    changed = 0
    for i, line in enumerate(lines):
        if line == "> **本节速览**":
            lines[i] = "> [!tip] 本节速览"
            changed += 1

    # Turn plain introductory prose between an E heading and its first Q into a tip callout.
    i = 0
    while i < len(lines):
        if not E_HEADING.match(lines[i]):
            i += 1
            continue
        start = i + 1
        while start < len(lines) and not lines[start].strip():
            start += 1
        if start >= len(lines) or Q_HEADING.match(lines[start]) or CALLOUT_START.match(lines[start]):
            i += 1
            continue
        end = start
        while end < len(lines) and not Q_HEADING.match(lines[end]) and not E_HEADING.match(lines[end]):
            if CALLOUT_START.match(lines[end]):
                break
            end += 1
        body = lines[start:end]
        while body and not body[-1].strip():
            body.pop()
        nonblank_body = [item for item in body if item.strip()]
        if nonblank_body and all(re.match(r"^!\[\[.+\]\]$", item) for item in nonblank_body):
            i = end
            continue
        if body:
            wrapped = ["> [!tip] 本节速览"]
            for item in body:
                wrapped.append(">" if not item.strip() else f"> {item}")
            lines[start:end] = wrapped + [""]
            changed += 1
            i = start + len(wrapped)
        else:
            i += 1
    return lines, changed


def compact_section_overviews(lines: list[str], path: Path) -> tuple[list[str], int]:
    """Remove generic overviews and keep reviewed, topic-specific ones."""
    changed = 0

    # Diagrams are supporting material, not spoken section overviews. Unwrap
    # image-only tips even when the E section intentionally has no Q heading.
    i = 0
    while i < len(lines) - 1:
        if lines[i] == "> [!tip] 本节速览":
            j = i + 1
            body: list[str] = []
            while j < len(lines) and (lines[j].startswith(">") or not lines[j].strip()):
                if lines[j].strip():
                    body.append(lines[j])
                j += 1
            if body and all(re.match(r"^>\s*!\[\[.+\]\]$", line) for line in body):
                replacement = [re.sub(r"^>\s?", "", line) for line in body] + [""]
                lines[i:j] = replacement
                changed += 1
                i += len(replacement)
                continue
        i += 1

    e_positions = [i for i, line in enumerate(lines) if E_HEADING.match(line)]
    for e_index in reversed(range(len(e_positions))):
        start = e_positions[e_index]
        end = e_positions[e_index + 1] if e_index + 1 < len(e_positions) else len(lines)
        first_q = next((i for i in range(start + 1, end) if Q_HEADING.match(lines[i])), None)
        if first_q is None:
            continue

        # A tip inside a concrete Q is answer expansion, not section navigation.
        for i in range(first_q + 1, end):
            if lines[i] == "> [!tip] 本节速览":
                lines[i] = "> [!abstract] 深挖补充"
                changed += 1

        # Preserve an already compact, single overview. This keeps the cleanup
        # idempotent and avoids replacing a reviewed topic-specific summary.
        intro_start = start + 1
        intro = lines[intro_start:first_q]
        tip_positions = [i for i, line in enumerate(intro) if line == "> [!tip] 本节速览"]
        nonblank = [line for line in intro if line.strip()]
        has_generic_overview = any(GENERIC_OVERVIEW.match(line) for line in nonblank)
        image_only_overview = bool(nonblank) and all(
            line == "> [!tip] 本节速览"
            or re.match(r"^>\s*!\[\[.+\]\]$", line)
            for line in nonblank
        )
        if image_only_overview:
            replacement = [
                line[2:] if line.startswith("> ") else line
                for line in nonblank
                if line != "> [!tip] 本节速览"
            ] + [""]
            lines[intro_start:first_q] = replacement
            changed += 1
            continue
        if (
            len(tip_positions) == 1
            and len(nonblank) <= 4
            and all(line.startswith(">") for line in nonblank)
            and not has_generic_overview
        ):
            continue

        # Generic previews add no answer value. Remove malformed, duplicated,
        # or verbose introductions instead of manufacturing a template summary.
        replacement = [""]
        if lines[intro_start:first_q] != replacement:
            lines[intro_start:first_q] = replacement
            changed += 1
    return lines, changed


def clean_file(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    had_trailing_newline = text.endswith("\n")
    lines = text.splitlines()
    lines, overview_changes = normalize_overviews(lines)
    lines, compact_changes = compact_section_overviews(lines, path)
    overview_changes += compact_changes

    callout_changes = 0
    active_answer = False
    for i, line in enumerate(lines):
        match = CALLOUT_START.match(line)
        if match:
            active_answer = match.group(1).lower() in {"abstract", "note"}
            continue
        if active_answer:
            if line.startswith(">") or not line.strip():
                cleaned = clean_callout_line(line) if line.startswith(">") else line
                if cleaned != line:
                    lines[i] = cleaned
                    callout_changes += 1
            else:
                active_answer = False

    output = "\n".join(lines) + ("\n" if had_trailing_newline else "")
    encoded = output.encode("utf-8")
    if has_bom:
        encoded = b"\xef\xbb\xbf" + encoded
    if encoded != raw:
        path.write_bytes(encoded)
    return overview_changes, callout_changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    target = args.path.resolve()
    files = [target] if target.is_file() else sorted(target.rglob("*.md"))
    overview_total = 0
    callout_total = 0
    changed_files = 0
    for path in files:
        before = path.read_bytes()
        overview, callout = clean_file(path)
        if path.read_bytes() != before:
            changed_files += 1
        overview_total += overview
        callout_total += callout
    print(f"Files changed: {changed_files}")
    print(f"Overviews normalized: {overview_total}")
    print(f"Callout lines cleaned: {callout_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
