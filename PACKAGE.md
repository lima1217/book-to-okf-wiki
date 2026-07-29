# Package shape and page contents

Load this when creating or editing wiki pages. Single source for naming, tree,
frontmatter, and what each page holds. The package targets **OKF v0.2**.

## Naming

- Package directory: lowercase English kebab-case slug (e.g.
  `systems-thinking-wiki`).
- Fixed directories stay English: `sources/`, `chapters/`, `concepts/`,
  `frameworks/`, `claims/`, `glossary/`, `questions/`, `tools/`.
- English Markdown filenames: `index.md`, `log.md`, `AGENTS.md`.
- Every other human-authored Markdown filename: Chinese.
- All Markdown prose: Chinese (including those three). Keep exact
  source terms, code, commands, API names, citations, YAML keys, and fixed
  `type` values when translation would reduce precision.
- Leave machine artifacts unchanged: `full_text*.txt`, `metadata.json`,
  `validate_okf_wiki.py`.

## Tree

```text
<package-slug>/
├── AGENTS.md
├── index.md
├── log.md
├── sources/
│   ├── index.md
│   ├── log.md
│   └── 来源-001.md
├── chapters/
│   ├── index.md
│   ├── log.md
│   └── 第01章-<中文短名>.md
├── concepts/
├── frameworks/
├── claims/
├── glossary/
│   └── 术语.md
├── questions/
│   └── 待解决问题.md
└── tools/
    └── validate_okf_wiki.py
```

Every directory with Markdown content needs `index.md`; meaningful directories
also get `log.md`.

## Frontmatter

Every Markdown file except `index.md` and `log.md` starts with YAML and a
non-empty `type` — that includes `AGENTS.md`. Only `type` is required; the rest
is recommended.

```yaml
---
type: Concept
title: 示例概念
description: 一句话摘要。
tags: [核心]
status: stable
generated: { by: cursor/claude-opus-4, at: 2026-06-15T00:00:00Z }
sources:
  - id: src-001
    resource: /sources/full_text-20260615.txt
    title: 《示例书名》第 3 章
    last_modified: 2026-06-15
chapter_refs: [ch03]
---
```

Useful `type` values: `AgentGuide`, `Source`, `ChapterNote`, `Concept`,
`Framework`, `Claim`, `Glossary`, `OpenQuestions`.

- `status`: `draft` | `stable` | `deprecated`. Absent means `stable`. Use
  `draft` for pages still missing evidence.
- `generated`: `{ by, at }` records who wrote the current content. `by` follows
  the actor convention — `<tool>/<model>` for an agent, `human:<name>` for a
  person, `process:<name>` for automation. `at` is ISO 8601.
- `verified`: `{ by, at }`, or a list of them, only when someone actually
  confirmed the page against its sources. A human verifier lifts the page to the
  human-reviewed trust tier, so never write one on the agent's own behalf.
- `stale_after`: optional `YYYY-MM-DD` after which the page needs rechecking.
- `sources`: what the page derives from. `resource` is required per entry and
  points at the dated pinned text file, a `来源-<NNN>.md` page, or an external
  URL. `id` is the stable key body footnotes cite. Add `author` and
  `last_modified` when the source carries them.
- `chapter_refs` is a package extension for filtering by chapter; cross-page
  relationships still travel as markdown links.

## Links

Links between pages, and every path-valued frontmatter field, start with `/`
and resolve from the package root:

```markdown
见[系统结构](/concepts/系统结构.md)。
```

The string is the same wherever it is written, so a paragraph can be moved
between directories — a subsection page one level deeper, a durable idea merged
into another page — without recomputing `../`. It also makes every reference to
a page greppable as one literal, which is what a rename relies on.

## Citations

Attribute a claim with a markdown footnote whose label is a `sources[].id`, and
carry the pinned-text line range in the footnote text:

```markdown
系统的行为由结构决定，而非由事件决定。[^src-001]

[^src-001]: 《示例书名》第 3 章，full_text-20260615.txt L1204-L1231
```

The label is the join key into `sources`, so it survives the list being
reordered — which agents do on every rewrite. A page whose claims cite nothing
belongs in `questions/待解决问题.md` instead.

## Index and log files

`index.md` and `log.md` carry no frontmatter, with one exception: the root
`index.md` declares `okf_version: "0.2"`.

```markdown
---
okf_version: "0.2"
---
```

`log.md` groups entries under ISO 8601 `## YYYY-MM-DD` headings, newest first,
each line opening with `**新增**` / `**更新**` / `**废弃**`.

## Pages

- `AGENTS.md` — how agents read, link, cite, update logs, and treat uncertainty.
- root `index.md` — title, author, sources, scope, human reading path, agent
  context path, directory links, top concepts/frameworks.
- `sources/来源-<NNN>.md` — original path, format, extraction method, metadata,
  warnings, the `sources[].id` other pages cite it by, pinned text filename,
  md5, line count.
- `chapters/第<NN>章-<中文短名>.md` — core idea, key concepts, frameworks,
  claims, examples, caveats, links, citations.
- `concepts/<中文概念>.md` — durable concepts synthesized across chapters.
- `frameworks/<中文框架>.md` — named methods, models, taxonomies, checklists,
  decision rules.
- `claims/<中文主张>.md` — factual or argumentative claims with support,
  assumptions, confidence, related concepts, citations.
- `glossary/术语.md` — terms, short definitions, links.
- `questions/待解决问题.md` — ambiguities, application questions,
  contradictions, items needing external validation.
