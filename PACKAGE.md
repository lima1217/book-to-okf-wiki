# Package shape and page contents

Load this when creating or editing wiki pages. Single source for naming, tree,
frontmatter, and what each page holds.

## Naming

- Package directory: lowercase English kebab-case slug (e.g.
  `systems-thinking-wiki`).
- Fixed directories stay English: `sources/`, `chapters/`, `concepts/`,
  `frameworks/`, `claims/`, `glossary/`, `questions/`, `tools/`.
- Reserved English Markdown filenames only: `index.md`, `log.md`, `AGENTS.md`.
- Every other human-authored Markdown filename: Chinese.
- All Markdown prose: Chinese (including the three reserved files). Keep exact
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

Every Markdown file except the three reserved names starts with YAML and a
non-empty `type`:

```yaml
---
type: Concept
title: 示例概念
description: 一句话摘要。
source_refs: [source-001]
chapter_refs: [ch03]
tags: [核心]
status: active
timestamp: 2026-06-15T00:00:00Z
---
```

Useful `type` values: `AgentGuide`, `Source`, `ChapterNote`, `Concept`,
`Framework`, `Claim`, `Glossary`, `OpenQuestions`.

## Pages

- `AGENTS.md` — how agents read, cite, update logs, and treat uncertainty.
- root `index.md` — title, author, sources, scope, human reading path, agent
  context path, directory links, top concepts/frameworks.
- `sources/来源-<NNN>.md` — original path, format, extraction method, metadata,
  warnings, citation label, pinned text filename, md5, line count.
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
