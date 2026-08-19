---
name: write-interview-notes
description: Create, rewrite, merge, and audit Chinese software-engineering interview notes in Obsidian Markdown using numbered E sections, numbered Q questions, complete blue first-round answers, and optional non-repetitive green deep dives. Use for Java or Agent interview knowledge, resume-based internship and project experience notes, self-introductions, PDF-to-Markdown conversion, old-note consolidation, deduplication, restructuring, completeness upgrades, and accuracy or evidence-boundary reviews.
---

# Write Interview Notes

Produce notes that can be scanned under interview pressure and spoken naturally in a face-to-face conversation without improvising missing logic. Optimize for **clear retrieval, complete first answers, conversational delivery, progressive depth, factual accuracy, and defensible boundaries**.

## Inspect Before Writing

1. Read the complete source materials relevant to the request: resume, PDFs, existing notes, repositories, tests, reports, images, and directory indexes.
2. Treat the user's stated source priority as binding. If none is stated, prefer the newest resume and verified implementation over older notes.
3. Inventory the target directory before changing structure. Preserve unrelated files and existing useful links.
4. Extract claims into three groups:
   - **Verified**: directly supported by source or implementation.
   - **Qualified**: usable only with scope, version, dataset, environment, or ownership limits.
   - **Unsupported**: omit or clearly label as a proposed improvement.
5. Build a topic map before writing. Merge equivalent questions, place each question under its natural category, and remove stale or off-role material.

When a source is a PDF and layout or diagrams matter, use the PDF skill. When experience claims must be checked against code, inspect the relevant implementation and tests rather than trusting names or comments alone.

## Organize The Notes

Use numbered prefixes on folders and files when ordering matters, for example:

```text
01-核心资料/
  01-目录索引.md
  02-实习经历.md
  03-在线学习Agent平台.md
02-后端八股整理/
  01-JAVASE/
    03-集合.md
```

Follow these rules:

- Keep the directory index, experience notes, project notes, and knowledge notes separated by purpose.
- Give each substantial project its own file.
- Use a short, concrete `#` file title.
- Use `## E01. 简短主题` for second-level sections. Number E sections continuously within a file.
- Use `### Q01. 简短问题？` for questions. Restart Q numbering at `Q01` under every E and keep it continuous within that E. A directory index may use Q headings as navigation labels; those labels do not require answer callouts.
- For knowledge notes, one E represents one coherent concept family.
- For internship and project notes, make E01 the overview and normally map each later E to one resume responsibility or one coherent engineering thesis.
- Keep titles short enough to scan. Put detail in the answer, not in the heading.
- Headings must name the concept or question itself. Do not use tutorial-style headings such as “面试里值得分享”, “适合校招生的模板”, “为什么这题加分”, or “怎么回答更稳”.
- Place a question in the file and E section that owns its main concept. Link to related topics instead of duplicating the full answer.
- When a file or E section has a useful technical conclusion that helps answer a broad opening question, place it in a green tip callout instead of an unlabelled blockquote or loose tutorial paragraph:

```markdown
> [!tip] 本节速览
> 用一到三句话直接说清本节最重要的技术主线、判断结论或工程边界。这段话本身也必须能在面试中说出口。
```

- Green is optional. Omit it when it can only say “本节介绍……的定义、原理、场景和边界” or repeat the E/Q title.
- Green must contain subject-specific information. It may summarize the relationship among several questions, establish a decision framework, or state the main engineering boundary, but it must not narrate note structure.
- Keep the overview compact. Detailed lists, comparisons, examples, and implementation explanations still belong under concrete Q headings.

Start from [assets/note-template.md](assets/note-template.md) when creating a new file.

## Write The Blue Direct Answer

Every interview question must have exactly one blue direct-answer callout. With the user's current Obsidian theme, use `note` for blue:

```markdown
> [!note] 可直接回答
> 先用一句话直接回答，再用 2 到 5 个口语化要点展开。
```

The blue direct answer is **not a summary**. Make it self-contained so the candidate can stop after it without leaving the definition, conclusion, causal chain, comparison, or decision framework incomplete. Write for a real conversation, not for a report, textbook, or resume recital.

Write it as follows:

1. Open with one natural sentence that directly answers the question and establishes the main line.
2. Follow with two to five bullet points when the answer has multiple ideas. Each bullet must be a complete phrase or sentence that can be spoken continuously, not a keyword fragment.
3. For experience questions, cover the relevant subset of **business problem -> personal responsibility -> mechanism -> result -> boundary**.
4. Explain why a mechanism exists, not merely which technology was used.
5. Use first-person ownership precisely: distinguish designed, implemented, participated in, modified, and proposed.
6. Bold only retrieval anchors: core concepts, decisive mechanisms, critical numbers, boundaries, and conclusions.
7. Prefer natural spoken Chinese and short clauses. Use transitions such as “我当时主要考虑的是”“具体来说”“这里有两个关键点” only when they sound natural.
8. Avoid stiff phrases such as “我应聘的方向是”, “综上所述”, “其核心在于”, and “我的自我介绍完毕” unless the surrounding conversation genuinely requires them.
9. Remove coaching and scoring meta-language from the answer itself, such as “面试时要说”, “推荐讲法”, “这样很加分”, “候选人常见错误”, and “面试官会觉得”. State the useful conclusion directly.
10. Avoid greetings inside ordinary answers, inflated claims, technology inventories, slogans, unexplained abbreviations, and a chronological reading of the resume.
11. Do not announce the act of answering. Openings such as “如果只抓面试里最常见的”, “我会这样回答”, “这道题主要考察”, “建议按这条线记”, and “一句话面试版” must be rewritten as the actual conclusion.
12. Add a short example when it materially clarifies an abstraction, comparison, execution order, failure mode, or engineering choice. Introduce it naturally with “比如” or “例如”, keep it close to the relevant point, and do not invent project ownership or production data. Skip examples when the definition is already concrete or an example would only repeat the explanation.
13. Match completeness to the question. A definition question normally needs the definition, decisive properties, use case, and boundary; a principle question needs the causal chain and consequence; a comparison question needs shared comparison dimensions, differences, and a selection conclusion; a process question needs the ordered flow, key state changes, and failure point; a design question needs goals, components, main flow, correctness controls, and tradeoffs. Do not treat length alone as completeness.
14. The direct-answer body must contain the answer itself. Placeholders and narration such as “定义”, “从四层说”, “给出一个判断框架”, “可以按下面这条链讲”, “这是高频题”, or “这部分必须答透” are hard errors even when a deep-dive callout follows.
15. Do not move the real first-round answer into the green deep dive. If the direct answer is incomplete and the deep dive contains the missing definition, conclusion, comparison, or main causal chain, merge that material into the direct answer first, then keep only the genuinely deeper layer in green.
16. Use source material such as comprehensive interview notes for **coverage depth**, not as a length quota. A source may place several follow-ups under one large question; preserve equivalent coverage by writing one complete main answer plus distinct follow-ups, not by copying every paragraph into every Q.
17. Treat a main Q followed by several one-line Qs that merely enumerate its points as fragmentation. Merge those points into the main direct answer. Keep a child Q only when an interviewer could ask it independently and its answer contains a complete explanation rather than one bullet fragment.
18. For a substantial main question, normally cover four to six relevant dimensions from: **definition/conclusion, mechanism/process, key differences, use or selection, failure/boundary, example**. Select dimensions by question type; do not force all six into simple factual questions.

Use this default blue pattern for multi-point questions:

```markdown
> [!note] 可直接回答
> 直接给出结论，说明我会从哪几个方面回答。
>
> - **要点一**：用能直接说出口的完整句子解释，不只写关键词。
> - **要点二**：继续补充机制、原因或结果，与上一点自然衔接。
> - **边界或结论**：必要时说明适用条件，避免绝对化。
```

Do not force bullets into a one-sentence answer. Do not split one continuous causal chain into so many bullets that the answer sounds like reading presentation slides.

Simple questions may contain only the blue direct answer.

## Add A Green Deep Dive

Add a green deep-dive callout only when a competent interviewer has a meaningful next layer to ask. With the user's current Obsidian theme, use `abstract` for green:

```markdown
> [!abstract] 深挖补充
> 底层机制、严格边界、失败场景、版本差异、工程取舍、表格、代码或案例。
```

Use blue for one or more of:

- underlying mechanism or execution order;
- concurrency, consistency, transaction, retry, compensation, or recovery;
- strict prerequisites, counterexamples, and failure scenarios;
- version or implementation differences;
- design alternatives and engineering tradeoffs;
- metric definitions, datasets, environments, and reproducibility limits;
- code, SQL, formulas, tables, diagrams, or concrete cases.

Never use green as an overflow area for a long direct answer. Never restate the blue direct answer in more words. Organize a complex green answer by follow-up dimension or execution step, using bullets, numbered flows, tables, or code as appropriate. If removing the blue answer makes green incomprehensible, that is acceptable: green is an expansion of an already complete first answer.

Every sentence in green must also be speakable as a direct response to a follow-up. Remove labels that only coach the candidate, announce difficulty, or praise an answer. Headings inside green may name a mechanism or dimension, but may not be empty labels such as “定义”, “优点”, or “高频追问” without explanatory content.

## Adapt By Note Type

### Knowledge Notes

- Start with the standard answer expected in an interview.
- Cover definition, principle, use case, limits, and comparison where relevant.
- Put exact internals, source-level behavior, version differences, and edge cases in the green deep dive.
- Do not preserve source-document repetition merely because it appeared in different chapters.

### Internship And Project Notes

- Put a complete project or internship introduction in E01.
- Turn each resume responsibility into a later E section, then derive its likely question chain.
- Include questions about context, personal ownership, architecture, execution flow, technology choice, correctness, failure recovery, tests, metrics, limitations, and improvements when relevant.
- Make the first answer reconstruct the real work. Use green for evidence, hard failure modes, strict scope, and alternative designs.
- Do not describe a reference repository or later reproduction as work performed during an internship.
- Do not silently present an improvement proposal as the current implementation. Say **current implementation** and **possible optimization** separately.

For internship notes, enforce this evidence order:

1. **Latest resume** defines the maximum scope that may be claimed as implemented during the internship.
2. **Explicit user confirmation** may clarify what a resume bullet means, but must not be expanded beyond that confirmation.
3. **Reference repositories** may explain implementation details only for a resume-listed responsibility. Repository presence alone never proves the mechanism was used during the internship.
4. Anything outside the first two levels must be omitted from “current implementation”. If useful for a follow-up, label it clearly as **possible optimization**, **alternative design**, or **not used in this project**.

Never claim patterns such as Outbox, transactional messages, distributed transactions, CDC, Saga, or production-grade observability merely because they would improve the design. Include them only when the resume or the user explicitly confirms actual use.

### Self-Introduction

- Use **candidate positioning -> strongest internship evidence -> distinct projects -> engineering preference and role fit**.
- Do not recite courses or a framework inventory already visible on the resume.
- Ensure every paragraph creates a useful follow-up entry point that has supporting notes.
- Keep graduation time and role direction current. Avoid stale school-year labels.

## Integrate And Deduplicate

When merging older notes or PDF content:

1. Preserve the target structure; do not append a source dump to the end.
2. Treat source headings as input topics, not mandatory output boundaries.
3. Merge equivalent questions into the clearest wording and strongest accurate answer.
4. Keep complementary details at their logical position in the blue direct answer or green deep dive.
5. Resolve conflicts using source priority, current version, verified implementation, and interview relevance.
6. Remove obsolete metrics, duplicate definitions, circular cross-references, irrelevant algorithm-role material, and content stored in the wrong category.
7. Use images only when information cannot be represented clearly as text, code, table, or Mermaid. Preserve a source diagram by cropping it into the note assets directory and embedding it near the relevant E/Q; do not screenshot ordinary text or callout styling.

## Protect Accuracy

- Never invent throughput, latency, accuracy, scale, business impact, production use, or personal ownership.
- State the metric name, sample size, workload, environment, and excluded components when needed to prevent overclaiming.
- Distinguish offline replay, unit testing, integration testing, benchmark cores, full-chain testing, and production results.
- If a resume claim and current repository differ, prepare a concise version/scope explanation rather than hiding the difference.
- Keep deterministic business rules, model suggestions, user confirmation, and human approval as separate authorities.
- Correct inaccurate source content. Do not preserve an error for visual consistency.

## Audit Before Finishing

Run [scripts/validate_notes.py](scripts/validate_notes.py) on every changed file or directory:

```powershell
python C:\Users\33769\.codex\skills\write-interview-notes\scripts\validate_notes.py <path>
```

Then manually verify:

1. File and folder order is logical and index links resolve.
2. E numbering is continuous; Q numbering restarts at Q01 under each E and is continuous.
3. Every interview Q has exactly one blue `> [!note] 可直接回答`; navigation Q headings in a directory index are exempt.
4. Every green `> [!abstract] 深挖补充` belongs to the immediately preceding Q and adds a genuinely deeper layer.
5. No duplicate or ambiguous questions remain.
6. Titles are short, clear, and in the correct category.
7. Bold text helps scanning without turning whole paragraphs bold.
8. Code fences, lists, callout indentation, images, and tables render correctly in Obsidian.
9. Claims, metrics, versions, and ownership match the available evidence.
10. The answer is understandable under pressure without relying on improvisation.
11. Multi-point direct answers use conversational bullets; bullets remain complete and speakable rather than becoming outline fragments.
12. Internship implementation claims are traceable to the latest resume or explicit user confirmation; repository-only and idealized mechanisms are absent from current-work wording.
13. Direct answers contain no coaching narration or scoring language; every first sentence can be spoken directly to an interviewer.
14. Useful section overviews use `> [!tip] 本节速览`, contain a concrete technical conclusion, and remain separate from direct-answer and deep-dive semantics; generic previews are absent.
15. Abstract questions include a concise example where it genuinely improves understanding; examples do not fabricate experience, scale, or results.
16. No direct answer is a placeholder, answer-announcement, coaching sentence, or bare keyword. The definition, conclusion, comparison, process, or decision requested by the Q is present in blue itself.
17. Green overview, blue direct answer, and green deep-dive content can all be spoken directly to an interviewer. Callout color expresses depth and function, not whether the text is an answer.
18. A main Q is not followed by several fragment Qs that merely distribute its list items. Equivalent source coverage is consolidated into a complete main answer and genuinely independent follow-ups.

Do not optimize merely for a speaking-time target. Prefer a clear, complete answer; shorten only repetition and low-value detail.
