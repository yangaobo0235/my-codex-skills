---
name: write-engineering-resume
description: Rewrite software project descriptions and responsibility bullets into concise, natural, evidence-backed engineering narratives. Use when drafting or revising technical resumes, especially when bullets must communicate architecture, mechanisms, boundaries, failure handling, metrics, character budgets, or fixed-length subtitles without sounding like a technology list or a mechanical STAR template.
---

# Write Engineering Resume

Turn verified engineering work into compact design narratives. Preserve technical truth and make every bullet an independent interview entry point.

## Workflow

1. Establish the candidate's positioning and the distinct problem solved by each project.
2. Inspect source code, tests, benchmark reports, or user-provided evidence before choosing claims and metrics.
3. Assign exactly one capability thesis to each bullet. Write a short title that names that thesis.
4. Build the sentence as a causal engineering chain: design object and goal -> core mechanism -> boundary, recovery, or correctness guarantee -> verified result.
5. Remove details that do not strengthen the thesis. Move useful secondary material to another bullet or interview notes.
6. Check title length, character budget, factual scope, terminology, and overlap across bullets.

## Narrative Pattern

Prefer this flexible pattern instead of mechanically labeling STAR elements:

`**Capability title:** Design or build X; use A and B to implement Y, add C to control a boundary or failure mode, and achieve or support Z.`

Not every bullet needs a metric. Use one only when its dataset, workload, environment, and measurement scope are defensible. A concrete correctness guarantee or supported scenario can be a stronger ending than a weak number.

Write naturally:

- Start with a decisive verb such as design, divide, build, introduce, persist, constrain, or evaluate.
- Name the engineering object early: boundary, workflow, state machine, retrieval chain, tool policy, or consistency mechanism.
- Embed technologies where they explain how the design works; never lead with a stack inventory.
- Include the hard part: authority ownership, state transition, idempotency, retry, recovery, validation, degradation, or audit evidence.
- End on impact, coverage, quality, or the undesirable outcome prevented.

## Bullet Boundaries

Give each bullet one thesis, not one technology. Multiple components are allowed only when they form one causal chain and invite one family of interview questions.

Split or refocus a bullet when:

- its title needs two unrelated nouns joined by "and";
- deleting half the sentence leaves the same conclusion intact;
- it mixes unrelated topics such as authentication, concurrency, and retrieval;
- the likely follow-up questions require separate system explanations.

Keep a multi-stage chain together when every stage is necessary to explain one outcome, such as stock warmup -> atomic reservation -> asynchronous order creation -> failure compensation.

## Project Description

Use the description to establish origin, evolution, system boundary, and problem statement. Do not repeat all responsibilities or list the complete stack.

When a project evolved, state the chronology explicitly. For example, say that an existing Java business platform was extended with a Python Agent runtime rather than implying a greenfield dual-language architecture.

For multiple projects, give each a non-overlapping thesis. Make their relationship clear as progression, contrast, or complementary coverage.

## Constraint Handling

- Treat a requested title length as exact. Count visible Chinese characters and Latin tokens according to the user's stated convention; if unspecified, count each displayed character and exclude Markdown markers and the trailing colon.
- Treat a character limit as a hard ceiling unless the user explicitly calls it approximate. Count the final visible bullet, including the title, punctuation, Latin letters, digits, and spaces.
- Preserve standard technical names such as `requestId`, `Last-Event-ID`, `Recall@6`, and product names.
- Prefer one semicolon or two compact clauses over many comma-separated fragments.
- Avoid inflated ownership verbs when evidence only shows participation or implementation.

## Evidence Rules

- Never invent scale, accuracy, latency, concurrency, business impact, or production use.
- Distinguish offline retrieval replay, routing evaluation, integration testing, and end-to-end production results.
- Use the newest defensible metric when old resume claims conflict with current repository evidence.
- Retain scope qualifiers when they prevent overclaiming.
- Do not call synthetic or frozen evaluation cases real production traffic.

## Quality Check

Before returning the draft, verify:

1. One bullet proves one capability thesis.
2. The first clause tells the reader what was designed, not merely which library was used.
3. Technologies form a coherent execution chain.
4. At least one non-happy-path concern appears where relevant.
5. Every number is traceable and accurately scoped.
6. Bullets within and across projects do not compete for the same story.
7. Titles follow one grammatical style and meet the requested length.
8. Every bullet meets the character budget after formatting is removed.

## Common Failures

Avoid:

- technology inventories disguised as responsibilities;
- generic claims such as "improved efficiency" without mechanism or evidence;
- one bullet combining several independent resume highlights;
- repeating the project description in the first bullet;
- forcing a metric into every bullet;
- dense abbreviations that save characters but make the sentence unnatural;
- presenting an Agent suggestion as authoritative business truth when deterministic services own the decision.
