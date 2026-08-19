#!/usr/bin/env python3
"""Merge configured fragment Q sections into complete main interview answers."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


E_RE = re.compile(r"^## E(\d{2})\.\s+(.+)$")
Q_RE = re.compile(r"^### Q\d{2}\.\s+(.+)$")
CALLOUT_RE = re.compile(r"^> \[!([^\]]+)\]\s*(.*)$")
META_RE = re.compile(
    r"^(?:如果让你回答|在校招|下面这张表|这几个概念|这是|关键点是|"
    r"不同评测方法没有绝对优劣|Agent评测的另一个关键点)"
)


@dataclass(frozen=True)
class MergeSpec:
    file_suffix: str
    e_number: int
    question: str
    opening: str


SPECS = (
    MergeSpec("02-Agent架构与编排/04-任务拆解与动态规划.md", 1, "Planning 的完整闭环是什么？", "Planning 不是一次性生成步骤，而是一个**目标澄清、计划生成、执行观察、动态调整和结果收口**的闭环。"),
    MergeSpec("02-Agent架构与编排/04-任务拆解与动态规划.md", 3, "Planning 过程要解决哪些问题？", "一套可执行的 Planning 过程至少要解决目标、依赖、校验、执行反馈和重新规划五类问题。"),
    MergeSpec("02-Agent架构与编排/06-多Agent架构.md", 1, "Multi-Agent 应该怎样拆分和协作？", "Multi-Agent 的关键不在于增加角色数量，而在于把**职责边界、通信协议、共享状态、结果归并和故障责任**设计清楚。"),
    MergeSpec("02-Agent架构与编排/06-多Agent架构.md", 4, "为什么优先考虑单 Agent？", "在单 Agent 能完成任务时，我会优先保持单 Agent，因为它在状态、成本、时延和评测上都更简单。"),
    MergeSpec("02-Agent架构与编排/06-多Agent架构.md", 6, "如何判断是否该上 Multi-Agent？", "是否使用 Multi-Agent，要看任务能否自然分工，以及专业化或并行收益能否覆盖通信和治理成本。"),
    MergeSpec("02-Agent架构与编排/07-人工审批与接管.md", 6, "HITL 可以介入哪些位置？", "HITL 不只发生在最终提交前，它可以介入目标澄清、计划确认、高风险动作、异常处理和结果验收等不同阶段。"),
    MergeSpec("02-Agent架构与编排/07-人工审批与接管.md", 9, "如何决定哪些节点需要 HITL？", "是否插入 HITL，主要根据**动作风险、不确定性、失败成本和组织制度**判断，而不是把所有步骤都交给人工审批。"),
    MergeSpec("02-Agent架构与编排/07-人工审批与接管.md", 10, "HITL 如何兼顾安全和用户体验？", "HITL 的目标是拦住高风险和高不确定动作，同时尽量不打断低风险主流程。"),
    MergeSpec("03-工具调用与协议/01-工具调用与Schema.md", 4, "一个稳定的 Tool Schema 应该怎样设计？", "稳定的 Tool Schema 要让模型明确知道**工具做什么、什么时候不能用、参数怎样填写、结果怎样解释**。"),
    MergeSpec("03-工具调用与协议/05-Skills与能力封装.md", 6, "一个 Skill 应该封装哪些内容？", "Skill 不是一段孤立 Prompt，而是一套可复用的任务方法，通常要同时封装任务边界、步骤、工具依赖、输出标准和评测方式。"),
    MergeSpec("03-工具调用与协议/05-Skills与能力封装.md", 11, "Skill 设计需要遵循哪些原则？", "Skill 设计的目标是让一类任务可以稳定复用、独立评测并安全演进，主要遵循以下原则。"),
    MergeSpec("03-工具调用与协议/05-Skills与能力封装.md", 14, "Skill 会带来哪些安全风险？", "Skill 会把指令、脚本、工具和资料组合成可执行能力，因此也可能放大权限、供应链、过时知识和误调用风险。"),
    MergeSpec("05-Memory与状态管理/01-Context-State-Memory边界.md", 9, "成熟的上下文组装包含哪些层？", "成熟的上下文组装会把固定规则、当前任务、历史摘要、外部召回和工具反馈分层管理，而不是把所有文本直接拼在一起。"),
    MergeSpec("05-Memory与状态管理/02-Agent Memory分类与读写.md", 5, "Context、State、Memory 和 RAG 有什么区别？", "Context、State、Memory 和 RAG 都会影响模型当前决策，但它们负责的信息范围和生命周期不同。"),
    MergeSpec("06-Runtime与可靠性/04-Agent Runtime设计.md", 4, "Agent Runtime 负责什么？", "Agent Runtime 是连接模型能力和业务系统的执行层，负责把一次请求从输入接入推进到安全、可恢复、可观测的任务结果。"),
    MergeSpec("07-评测安全与运维/01-Agent评测体系.md", 1, "如何从零设计 Agent 评测流程？", "从零设计 Agent 评测时，我会按**目标与边界、能力拆解、数据集、评测器、基线门禁、反馈闭环**六步推进。"),
    MergeSpec("07-评测安全与运维/01-Agent评测体系.md", 4, "Agent 评测体系的整体框架是什么？", "完整的 Agent 评测体系可以分成任务定义、成功标准、场景集、执行环境、评测器、报告门禁和优化闭环七层。"),
    MergeSpec("07-评测安全与运维/01-Agent评测体系.md", 5, "Agent 评测要覆盖哪些维度？", "Agent 评测不能只看最终答案，还要同时覆盖**结果、过程、效率、安全、稳健性和业务价值**。"),
    MergeSpec("07-评测安全与运维/01-Agent评测体系.md", 6, "Agent 评测单元应该怎样划分？", "Agent 评测要同时覆盖单次响应、单步动作、完整任务以及长期会话或业务结果，不能把所有问题都压缩成一个成功率。"),
    MergeSpec("07-评测安全与运维/01-Agent评测体系.md", 7, "规则、模型和人工评测怎样组合？", "实际系统通常采用**规则评测做底座、模型评测覆盖开放维度、人工评测负责高风险校准和抽检**。"),
    MergeSpec("07-评测安全与运维/03-过程与结果指标.md", 5, "Agent 的过程指标和结果指标有哪些？", "结果指标判断任务最终是否成功，过程指标解释它为什么成功或失败，两者需要成组设计。"),
    MergeSpec("07-评测安全与运维/03-过程与结果指标.md", 6, "过程指标和结果指标如何配对使用？", "结果指标负责发现是否退化，过程指标负责定位退化发生在哪个环节，二者要通过具体故障假设配对。"),
    MergeSpec("07-评测安全与运维/03-过程与结果指标.md", 8, "评测结果需要做哪些统计分析？", "评测结果不能只报一个平均分，还要考虑置信区间、重复运行、场景切片以及统计显著性与业务意义。"),
    MergeSpec("07-评测安全与运维/05-可观测日志与回放.md", 6, "Log、Metric 和 Trace 分别解决什么问题？", "Log、Metric 和 Trace 分别用于保留事件细节、观察整体趋势和还原单次请求的因果链，三者不能互相替代。"),
    MergeSpec("07-评测安全与运维/05-可观测日志与回放.md", 7, "Replay 为什么重要？", "Replay 的价值是利用历史输入、轨迹和环境快照复现问题，并支持版本对比、回归集沉淀和故障演练。"),
    MergeSpec("07-评测安全与运维/05-可观测日志与回放.md", 10, "观测体系如何帮助优化 Agent？", "可观测体系要把异常现象关联到具体步骤、依赖和版本，再转化为流程、路由、安全或成本优化。"),
    MergeSpec("07-评测安全与运维/09-灰度发布与版本回滚.md", 4, "Agent 应该按照什么梯度上线？", "Agent 上线应该从本地验证、离线评测、Shadow 回放、内部灰度、小流量 Canary 逐步扩大到全量，并在每层设置退出条件。"),
    MergeSpec("01-大模型与提示工程/03-上下文窗口与缓存.md", 8, "长上下文应该怎样治理？", "长上下文治理不能依赖无限扩大窗口，而要组合使用检索、结构化组织、摘要压缩和稳定前缀缓存。"),
    MergeSpec("01-大模型与提示工程/05-Prompt工程.md", 1, "Prompt 设计需要遵循哪些原则？", "Prompt 设计的目标是把任务写成可验收、少歧义、可评测的执行契约，而不是堆叠修饰词。"),
    MergeSpec("01-大模型与提示工程/06-Context工程.md", 2, "怎样判断上下文质量？", "上下文质量主要看相关性、权威性、新鲜度、冲突与冗余，以及信息进入模型的时机。"),
    MergeSpec("01-大模型与提示工程/06-Context工程.md", 9, "Context Engineering 有哪些关键手法？", "Context Engineering 的关键是对信息做选择、排序、压缩、标注和清理，让模型在有限预算内看到当前决策所需的最小充分信息。"),
    MergeSpec("01-大模型与提示工程/08-模型选型与路由.md", 5, "常见的模型路由策略有哪些？", "模型路由不是固定选择一个模型，而是根据任务、质量、预算和失败状态，在静态路由、阈值路由、级联、多模型协同与降级之间切换。"),
    MergeSpec("01-大模型与提示工程/08-模型选型与路由.md", 6, "模型选型应该怎样落地？", "模型选型要先定义任务与指标，用强模型建立质量上界，再通过失败分类、向下路由和缓存等手段逐步降低成本。"),
    MergeSpec("02-Agent架构与编排/01-Agent定义与适用边界.md", 2, "哪些系统不能仅凭表面特征称为 Agent？", "是否属于 Agent 不能只看它有没有聊天界面、工具或记忆，而要看系统是否会围绕目标自主选择动作并根据反馈调整。"),
    MergeSpec("02-Agent架构与编排/01-Agent定义与适用边界.md", 10, "Computer Use Agent 如何工作？", "Computer Use Agent 通过视觉或结构化观察理解界面，再循环执行点击、输入和滚动等动作，因此必须同时设计观察、控制和安全边界。"),
    MergeSpec("02-Agent架构与编排/03-ReAct与规划执行.md", 6, "ReAct、Plan-and-Execute 和 CodeAct 如何组合？", "ReAct、Plan-and-Execute 和 CodeAct 不是互斥方案，可以分别承担即时决策、全局规划和精确执行，再按任务特点组合。"),
    MergeSpec("02-Agent架构与编排/05-状态机与终止条件.md", 5, "Agent 状态机需要满足哪些设计原则？", "Agent 状态机要把状态与动作解耦，显式定义转移和不变量，并通过检查点支持挂起与恢复。"),
    MergeSpec("03-工具调用与协议/04-A2A与Agent互操作.md", 4, "为什么不能把另一个 Agent 简单当作 Tool？", "远端 Agent 与普通 Tool 的差别在于它可能异步运行、内部自主规划、维护任务状态并产出 Artifact，而不是同步返回一个函数值。"),
    MergeSpec("03-工具调用与协议/04-A2A与Agent互操作.md", 9, "A2A 协作需要哪些治理机制？", "A2A 协作需要同时治理身份信任、数据最小化、全链路追踪、多租户策略以及失败补偿。"),
    MergeSpec("06-Runtime与可靠性/04-Agent Runtime设计.md", 7, "Model Router 要考虑哪些因素？", "Model Router 不只是按任务选模型，还要综合任务类型、预算与 SLA、工具兼容性和风险等级。"),
    MergeSpec("07-评测安全与运维/06-Prompt注入与工具安全.md", 9, "为什么 Agent 更容易放大提示注入风险？", "Agent 会主动读取外部内容并执行多步动作，还常连接高权限工具，所以不可信指令可能沿执行链被放大。"),
    MergeSpec("07-评测安全与运维/06-Prompt注入与工具安全.md", 12, "多模态 Agent 需要防范哪些安全风险？", "多模态输入会把文件、图片中的隐藏内容、隐私版权和输出副作用一起带入系统，不能只校验文本 Prompt。"),
    MergeSpec("07-评测安全与运维/07-权限审批与审计.md", 2, "Agent 权限模型包含哪些要素？", "Agent 权限判断至少要明确主体、资源、动作和上下文，并在工具执行时重新校验，不能只依赖模型提示。"),
    MergeSpec("07-评测安全与运维/07-权限审批与审计.md", 3, "Agent 治理与合规框架是什么关系？", "合规框架给出风险治理原则和外部要求，企业内部还要把它们落到权限、审批、审计、数据和事件响应流程。"),
    MergeSpec("07-评测安全与运维/07-权限审批与审计.md", 4, "Agent 审批流程如何分级设计？", "Agent 审批应按风险分级：低风险自动放行，高风险强制审批或确认，极高风险采用双人审批或默认禁止。"),
    MergeSpec("07-评测安全与运维/08-成本延迟与稳定性.md", 3, "为什么成本、延迟和稳定性必须一起优化？", "成本、延迟和稳定性相互制约，单独压低任何一个维度都可能牺牲成功率、安全或用户体验。"),
    MergeSpec("07-评测安全与运维/08-成本延迟与稳定性.md", 6, "Agent 推理服务怎样做容量治理？", "推理容量治理要围绕容量指标、自动扩缩、过载保护和容灾展开，既要应对平均流量，也要控制长尾任务。"),
    MergeSpec("07-评测安全与运维/08-成本延迟与稳定性.md", 9, "Agent 稳定性问题通常来自哪里？", "Agent 稳定性问题通常来自模型供应商、外部工具、内部状态、资源瓶颈和控制流缺陷五个层面。"),
    MergeSpec("07-评测安全与运维/09-灰度发布与版本回滚.md", 2, "Agent 系统需要版本化哪些资产？", "Agent 行为由模型、Prompt、工具、知识、治理策略和评测集共同决定，因此这些资产都要独立版本化并能关联到一次运行。"),
)


def strip_quote(line: str) -> str:
    if line == ">":
        return ""
    return re.sub(r"^>\s?", "", line)


def quoted(lines: list[str]) -> list[str]:
    return [">" if not line else f"> {line}" for line in lines]


def extract_callouts(block: list[str]) -> tuple[list[str], list[str]]:
    direct: list[str] = []
    deep: list[str] = []
    current: list[str] | None = None
    for line in block:
        match = CALLOUT_RE.match(line)
        if match:
            kind, title = match.groups()
            if kind == "note" and title == "可直接回答":
                current = direct
            elif kind == "abstract" and title == "深挖补充":
                current = deep
            else:
                current = deep
            continue
        if line.startswith(">") and current is not None:
            current.append(strip_quote(line))
        elif line.strip() and current is not None:
            current.append(line)
    while direct and not direct[-1].strip():
        direct.pop()
    while deep and not deep[-1].strip():
        deep.pop()
    return direct, deep


def compact_body(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def merge_section(section: list[str], spec: MergeSpec) -> list[str]:
    q_positions = [i for i, line in enumerate(section) if Q_RE.match(line)]
    if len(q_positions) < 2:
        return section

    questions: list[tuple[str, list[str], list[str]]] = []
    for index, start in enumerate(q_positions):
        end = q_positions[index + 1] if index + 1 < len(q_positions) else len(section)
        title = Q_RE.match(section[start]).group(1)  # type: ignore[union-attr]
        direct, deep = extract_callouts(section[start + 1 : end])
        questions.append((title, direct, deep))

    answer: list[str] = [spec.opening, ""]
    deep_answer: list[str] = []
    for index, (title, direct, deep) in enumerate(questions):
        plain = "".join(direct).strip()
        if index == 0 and (not plain or META_RE.match(plain)):
            direct = []
        if direct:
            answer.extend([f"**{title}**", ""])
            answer.extend(direct)
            answer.append("")
        if deep:
            deep_answer.extend([f"**{title}**", ""])
            deep_answer.extend(deep)
            deep_answer.append("")

    answer = compact_body(answer)
    deep_answer = compact_body(deep_answer)
    result = section[: q_positions[0]]
    result.extend([f"### Q01. {spec.question}", "", "> [!note] 可直接回答"])
    result.extend(quoted(answer))
    if deep_answer:
        result.extend(["", "> [!abstract] 深挖补充"])
        result.extend(quoted(deep_answer))
    result.append("")
    return result


def process(path: Path, specs: list[MergeSpec]) -> int:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    had_newline = text.endswith("\n")
    lines = text.splitlines()
    changed = 0

    for spec in sorted(specs, key=lambda item: item.e_number, reverse=True):
        starts = [i for i, line in enumerate(lines) if E_RE.match(line)]
        target = next((i for i in starts if int(E_RE.match(lines[i]).group(1)) == spec.e_number), None)  # type: ignore[union-attr]
        if target is None:
            continue
        end = next((i for i in starts if i > target), len(lines))
        merged = merge_section(lines[target:end], spec)
        if merged != lines[target:end]:
            lines[target:end] = merged
            changed += 1

    if changed:
        output = "\n".join(lines) + ("\n" if had_newline else "")
        encoded = output.encode("utf-8")
        path.write_bytes((b"\xef\xbb\xbf" if has_bom else b"") + encoded)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    root = args.path.resolve()
    total = files_changed = 0
    for path in sorted(root.rglob("*.md")):
        normalized = path.as_posix()
        specs = [spec for spec in SPECS if normalized.endswith(spec.file_suffix)]
        if not specs:
            continue
        count = process(path, specs)
        if count:
            files_changed += 1
            total += count
    print(f"Files changed: {files_changed}")
    print(f"Sections merged: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
