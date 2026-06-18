---
name: book-to-okf-wiki
description: "Convert books and document collections into self-contained, source-grounded OKF LLM Wiki packages, not agent skills. Use for a new portable Markdown knowledge base, a deep read added to an existing package, or an existing package updated from new sources."
---

# Book to OKF Wiki

Turn source documents into a self-contained Markdown knowledge package. The
output is not an agent skill; it is a portable OKF-compatible LLM Wiki that a
human can browse and any agent can use as context.

Write package prose in Chinese. Keep the package slug and fixed directory names
in English.

## Language and Naming

- Name the package directory with a lowercase English kebab-case slug, such as
  `systems-thinking-wiki`.
- Keep fixed directory names in English: `sources/`, `chapters/`, `concepts/`,
  `frameworks/`, `claims/`, `glossary/`, `questions/`, and `tools/`.
- Name every human-authored Markdown knowledge page in Chinese. The only
  reserved English Markdown filenames are `index.md`, `log.md`, and
  `AGENTS.md`.
- Write all Markdown prose in Chinese, including those three reserved files.
  Preserve exact source terms, code, commands, API names, citations, YAML keys,
  and fixed `type` values when translation would reduce precision.
- Keep machine-generated support artifacts unchanged, including
  `full_text*.txt`, `metadata.json`, and `validate_okf_wiki.py`.

## Leitworter

Keep these behavior anchors active while working:

- **Source-grounded wiki**: build durable knowledge from pinned evidence, not a
  fluent book report.
- **Concept-first synthesis**: extract concepts, frameworks, and claims before
  chapter recaps.
- **Bidirectional traceability**: every durable idea links back to source lines
  and forward to the pages that use it.
- **Navigation spine**: indexes, logs, and AGENTS.md make the package usable by
  both humans and agents.
- **Uncertainty ledger**: unresolved ambiguity belongs in
  `questions/待解决问题.md`, not hidden in prose.

## Modes

- **Full conversion**: default when the user provides document paths.
- **Analyze only**: when the user asks to preview/analyze/extract before writing.
- **Update existing wiki**: when the user points to an existing package.

## Inputs

Accept files, directories, or globs for:

`.pdf`, `.epub`, `.docx`, `.txt`, `.md`, `.markdown`, `.rst`, `.adoc`, `.html`,
`.htm`, `.rtf`, `.mobi`, `.azw`, `.azw3`.

If the final argument is not an existing path and looks like a slug, use it as
`PACKAGE_SLUG`; otherwise derive the slug from the title.

No valid input:

```text
book-to-okf-wiki creates OKF LLM Wiki packages. Provide a supported document path, folder, or glob.
Usage: book-to-okf-wiki <path-or-glob>... [package-slug]
```

## Classify Once

Before extraction, ask unless the user already supplied an equivalent
classification:

```text
这些资料属于哪类？
1. Technical：有代码、表格、公式、图示
2. Text-heavy：主要是文字
3. Not sure：先用通用方式，必要时提醒我
```

Map option 1 to `BOOK_TYPE=technical`; otherwise use `BOOK_TYPE=text`.

## Extract

Use this skill's extractor with `python3`. For EPUB, install the better parser
stack only if useful:

```bash
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" -m pip install ebooklib beautifulsoup4
```

Run extraction:

```bash
SCRIPT="$HOME/.agents/skills/book-to-okf-wiki/scripts/extract.py"
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" "$SCRIPT" $INPUT_PATHS --mode <BOOK_TYPE> --install-missing ask --pkg <package-dir>
```

If this skill is installed somewhere else, find `scripts/extract.py` with `rg
--files` or `find` and use that path.

Always prefer `--pkg <package-dir>` when generating or updating a wiki. It
writes reusable pinned source text inside the package:

- `sources/full_text-<YYYYMMDD>.txt` or `sources/full_text-<YYYYMMDD>-N.txt`
- `sources/full_text.txt`
- `sources/metadata.json`

Read `sources/metadata.json` before writing notes. Anchor line references to
the dated file, not to the moving `full_text.txt`.

Extraction is complete only when `sources/metadata.json` and the dated pinned
text exist, and their paths, md5, and line count are readable.

For large books, do not load the whole text. Use `rg`, `grep`, `sed`, and `wc`
against the pinned file. EPUB extraction may include:

- `=== EPUB-SECTION <n>: <href> ===` markers
- `chapter_map` in metadata

Use those before guessing chapter boundaries.

If not using `--pkg`, read the workdir from extractor stdout (`Text ->`,
`Meta ->`). Do not assume a fixed temp path.

## Confirm Before Writing

Before creating a new package, show:

- detected sources
- approximate pages, words, tokens
- output directory and package slug
- generated directories/files
- estimated time and token cost

Ask for confirmation. If the user says "analyze only", stop after the analysis
report.

This phase is complete only after the user confirms the displayed scope, or
the analyze-only report has been delivered.

## Package Shape

Create this tree:

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

Reserved English filenames: `index.md`, `log.md`, `AGENTS.md`. All other
human-authored Markdown filenames must be Chinese.

Every other Markdown file starts with YAML frontmatter and a non-empty `type`:

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

## What To Write

- `AGENTS.md`: how agents should read, cite, update logs, and treat uncertainty.
- root `index.md`: title, author, sources, scope, human reading path, agent
  context path, directory links, top concepts/frameworks.
- `sources/来源-<NNN>.md`: original path, format, extraction method, metadata,
  warnings, source citation label, pinned text filename, md5, line count.
- `chapters/第<NN>章-<中文短名>.md`: core idea, key concepts, frameworks, claims,
  examples, caveats, links, citations.
- `concepts/<中文概念>.md`: synthesized durable concepts across chapters.
- `frameworks/<中文框架>.md`: named methods, models, taxonomies, checklists, or
  decision rules.
- `claims/<中文主张>.md`: important factual or argumentative claims with support,
  assumptions, confidence, related concepts, citations.
- `glossary/术语.md`: terms, short definitions, links.
- `questions/待解决问题.md`: ambiguities, application questions,
  contradictions, items needing external validation.

Prefer concept/framework/claim pages over chapter recaps. Preserve essential
technical snippets, commands, tables, API names, and exact framework names.
Avoid long verbatim excerpts.

Writing is complete only when every load-bearing claim is either supported by
dated-file line citations or recorded in `questions/待解决问题.md`, every
created page is reachable from an index, and all human-authored Markdown prose
and non-reserved filenames follow the Chinese-language rule above.

## Deep Read

When the user asks to deep-read a chapter, or a long chapter contains
load-bearing claims, add subsection notes under `chapters/subsections/`:

```text
chapters/subsections/第04章-第01节-<中文短名>.md
```

Subsection notes use `type: ChapterNote`, `tags: [subsection, ch04, ...]`, and
link to previous/next subsection plus the chapter overview. Update:

- chapter overview with a subsection table
- `chapters/index.md`
- `chapters/subsections/index.md`
- relevant concept pages that depend on the subsection
- `chapters/log.md` and `chapters/subsections/log.md`

Core theses must be reachable both ways: from chapter/subsection notes to
concepts, and from concept pages back to the evidence.

## Update Existing Wiki

1. Read root `AGENTS.md`, `index.md`, `log.md`, and relevant directory indexes.
2. Reuse pinned extraction if `sources/metadata.json` md5/line count matches the
   source page. Re-extract with `--pkg` only if missing or mismatched.
3. Add a new `来源-<NNN>.md` only for genuinely new sources.
4. Add new chapter/subsection notes as needed.
5. Merge durable ideas into existing concept/framework/claim pages instead of
   duplicating them.
6. Update glossary, questions, indexes, and logs.
7. Validate.

Never silently overwrite useful existing pages.

## Validate

Copy or reference `tools/validate_okf_wiki.py` into the package, then run:

```bash
python3 tools/validate_okf_wiki.py .
python3 tools/validate_okf_wiki.py --strict .
```

The first command must pass. Strict mode is advisory; fix real gaps it reports.

## Completion Report

```text
OKF LLM Wiki package created: <path>

Sources: <N>
Chapters: <N>
Concepts: <N>
Frameworks: <N>
Claims: <N>

Key files:
- index.md
- AGENTS.md
- concepts/
- frameworks/
- chapters/
- claims/
- glossary/术语.md

Validation: passed
```
