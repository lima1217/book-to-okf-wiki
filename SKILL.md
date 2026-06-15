---
name: book-to-okf-wiki
description: "Convert books and documents (PDF, EPUB, DOCX, HTML, Markdown, plain text, RTF, MOBI/AZW with Calibre) into self-contained OKF-compatible LLM Wiki knowledge packages, not agent skills. Use when the user wants to turn a book, paper, report, or document folder into a portable Markdown knowledge bundle with index.md, log.md, AGENTS.md, concepts, chapter notes, claims, glossary, citations, and validation so any agent or human can read it as context."
---

# Book-to-OKF-Wiki Converter

Transform a book or document set into a self-contained OKF-compatible LLM Wiki package.

The output is **not** a Codex/Claude/Copilot skill. It is a portable Markdown knowledge bundle that the user can read directly, put in git, zip and share, or attach as context to any agent.

## Output Philosophy

Prefer a knowledge package over a skill when the user wants:

- A durable reading artifact they can browse.
- A source-backed wiki that grows over time.
- A context pack any agent can consume without installing a skill.
- A self-contained directory with navigation, logs, citations, and concept links.

Use LLM Wiki as the workflow: ingest sources, distill concepts, maintain cross-links, preserve learning over time.

Use OKF as the shape: Markdown file tree, `index.md`, `log.md`, YAML frontmatter with non-empty `type`, stable links, citations, and validation.

## Modes

### Full Conversion

Default when the user provides document paths. Extract text, estimate cost, analyze structure, then generate the full OKF wiki package.

### Analyze Only

Use when the user asks to preview, analyze, or extract before generating. Produce a report of structure, concepts, claims, and suggested package layout. Do not write the package.

### Update Existing Wiki

Use when the user points to an existing OKF/LLM Wiki package. Extract the new source, then fold it into existing concepts, chapter notes, citations, indexes, and logs.

## Step 0: Parse Inputs

Accept one or more files, directories, or glob patterns. Supported inputs:

`.pdf`, `.epub`, `.docx`, `.txt`, `.md`, `.markdown`, `.rst`, `.adoc`, `.html`, `.htm`, `.rtf`, `.mobi`, `.azw`, `.azw3`.

If the final argument is not an existing path and looks like a slug, treat it as `PACKAGE_SLUG`. Otherwise derive the slug from the title.

If no valid input is provided, stop with:

```text
book-to-okf-wiki now creates OKF LLM Wiki packages. Provide a supported document path, folder, or glob.
Usage: book-to-okf-wiki <path-or-glob>... [package-slug]
```

## Step 1: Ask Content Type

Ask once before extraction:

```text
这些资料属于哪类？
1. Technical：有代码、表格、公式、图示
2. Text-heavy：主要是文字
3. Not sure：先用通用方式，必要时提醒我
```

Map to `BOOK_TYPE=technical` for option 1, otherwise `BOOK_TYPE=text`.

## Step 2: Extract Source Text

Use this skill's extractor. Prefer `python3`.

For EPUB sources, prefer installing the higher-quality EPUB parser before extraction:

```bash
pip3 install ebooklib beautifulsoup4
```

`ebooklib` understands EPUB metadata, manifest, spine order, and document items. `beautifulsoup4` cleans XHTML/HTML content more reliably. If they are missing, the extractor falls back to stdlib ZIP/HTML parsing, which is acceptable for simple EPUBs but more likely to lose ordering, miss nested chapters, or include navigation noise.

```bash
SCRIPT_PATH=""
for candidate in \
  "$HOME/.agents/skills/book-to-okf-wiki/scripts/extract.py" \
  "$HOME/.copilot/skills/book-to-okf-wiki/scripts/extract.py" \
  "$HOME/.claude/skills/book-to-okf-wiki/scripts/extract.py" \
  ".agents/skills/book-to-okf-wiki/scripts/extract.py" \
  ".github/skills/book-to-okf-wiki/scripts/extract.py" \
  ".claude/skills/book-to-okf-wiki/scripts/extract.py"
do
  if [ -f "$candidate" ]; then
    SCRIPT_PATH="$candidate"
    break
  fi
done

PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" "$SCRIPT_PATH" $INPUT_PATHS --mode <BOOK_TYPE> --install-missing ask
```

This creates:

- `<tempdir>/book_okf_wiki_work/full_text.txt`
- `<tempdir>/book_okf_wiki_work/metadata.json`

Read `metadata.json` before continuing.

For large books over ~50k tokens, do not load `full_text.txt` all at once. Use `rg`, `grep`, `sed`, `wc`, and bounded reads to inspect sections.

## Step 3: Estimate and Confirm

Before generating a package, present:

- Sources detected.
- Approximate pages, words, and tokens.
- Proposed package slug and output directory.
- Files/directories that will be generated.
- Estimated time and token cost.

Ask for confirmation. If the user says “analyze only”, switch to Analyze Only.

## Step 4: Choose Output Location

Default to the current working directory unless the user gave an explicit output path.

Create:

```text
<package-slug>/
├── AGENTS.md
├── index.md
├── log.md
├── sources/
│   ├── index.md
│   ├── log.md
│   └── source-001.md
├── chapters/
│   ├── index.md
│   ├── log.md
│   └── ch01-<slug>.md
├── concepts/
│   ├── index.md
│   ├── log.md
│   └── <concept>.md
├── claims/
│   ├── index.md
│   ├── log.md
│   └── <claim>.md
├── frameworks/
│   ├── index.md
│   ├── log.md
│   └── <framework>.md
├── glossary/
│   ├── index.md
│   ├── log.md
│   └── terms.md
├── questions/
│   ├── index.md
│   ├── log.md
│   └── open-questions.md
└── tools/
    └── validate_okf_wiki.py
```

Use English directory names for portability and stable agent access. Use Chinese content when the user is Chinese or asks in Chinese.

## Step 5: OKF Frontmatter

Every non-reserved Markdown file must start with YAML frontmatter and non-empty `type`.

Reserved files: `index.md`, `log.md`.

Recommended frontmatter:

```yaml
---
type: Concept
title: Example Concept
description: One-sentence summary.
source_refs: [source-001]
chapter_refs: [ch03]
tags: [core, book-title]
status: active
timestamp: 2026-06-15T00:00:00Z
---
```

Common `type` values:

- `AgentGuide`
- `Source`
- `ChapterNote`
- `Concept`
- `Framework`
- `Claim`
- `Glossary`
- `OpenQuestions`

Unknown fields are allowed. Do not reject useful metadata.

## Step 6: Generate Core Files

### `AGENTS.md`

Explain how any agent should use and maintain the package:

- Read root `index.md` first.
- Use directory `index.md` files for navigation.
- Prefer concept/framework/claim pages over raw chapter notes when answering.
- Cite `source_refs`, `chapter_refs`, and citation sections.
- Update `log.md` after meaningful changes.
- Do not treat uncertain notes or open questions as established claims.

### Root `index.md`

Include:

- Book title, author, source list, generated date.
- One-paragraph scope.
- Reading path for humans.
- Context path for agents.
- Links to all directories.
- Top 10 concepts/frameworks.

### Root `log.md`

Record creation and every later update:

```md
# Log

## 2026-06-15

* Initialized package from <sources>.
```

## Step 7: Generate Source Pages

Create one `sources/source-<NNN>.md` per input source.

Include:

- Original filename/path.
- Format.
- Extraction method if known.
- Pages/words/tokens from metadata.
- Any extraction quality warnings.
- Source citation label used throughout the package.

Do not copy long source text into source pages.

## Step 8: Generate Chapter Notes

For each chapter or major section, create `chapters/ch<NN>-<slug>.md`.

Use:

```md
---
type: ChapterNote
title: Ch NN - Title
description: Main point of this chapter.
source_refs: [source-001]
chapter_refs: [chNN]
tags: [chapter]
status: active
timestamp: <ISO time>
---
# Ch NN - Title

## Core Idea

## Key Concepts

## Frameworks Introduced

## Claims

## Examples

## Caveats

## Links

## Citations
```

For technical books, preserve compact code snippets, commands, tables, and API names when they are essential. Avoid long verbatim excerpts.

## Step 9: Generate Concept Pages

Create one page per durable concept in `concepts/`.

Concept pages are the main LLM Wiki layer. They should synthesize across chapters instead of merely summarizing one chapter.

Use:

```md
---
type: Concept
title: <Concept>
description: <What this concept means and why it matters.>
source_refs: [source-001]
chapter_refs: [ch02, ch05]
tags: [concept]
status: active
timestamp: <ISO time>
---
# <Concept>

## Definition

## Why It Matters

## How To Use It

## Related Concepts

## Common Misreadings

## Evidence And Citations
```

Link concepts to chapters, frameworks, and claims with relative Markdown links.

## Step 10: Generate Framework Pages

Create `frameworks/<framework>.md` for named methods, models, taxonomies, processes, checklists, or decision rules.

Use:

```md
---
type: Framework
title: <Framework Name>
description: <When to use this framework.>
source_refs: [source-001]
chapter_refs: [ch04]
tags: [framework]
status: active
timestamp: <ISO time>
---
# <Framework Name>

## Use When

## Steps

## Decision Rules

## Worked Example

## Failure Modes

## Related

## Citations
```

Preserve the author's exact framework names when meaningful.

## Step 11: Generate Claim Pages

Create `claims/<claim>.md` for important factual or argumentative claims.

Claims are useful when the user wants to connect a book to other sources later.

Use:

```md
---
type: Claim
title: <Short claim>
description: <The claim in one sentence.>
source_refs: [source-001]
chapter_refs: [ch06]
tags: [claim]
status: active
timestamp: <ISO time>
---
# <Short Claim>

## Claim

## Support In Source

## Assumptions

## Confidence

## Related Concepts

## Citations
```

Use `confidence` carefully. If the source is unclear, mark the claim as tentative.

## Step 12: Generate Glossary and Questions

`glossary/terms.md` should contain important terms, short definitions, and links to concept pages.

`questions/open-questions.md` should contain:

- Ambiguities in the source.
- Questions to ask when applying the book.
- Concepts that need external validation.
- Potential contradictions.

## Step 13: Update Indexes

Every directory `index.md` should list files with one-line descriptions.

The root `index.md` should include:

- Concept index.
- Framework index.
- Claim index.
- Chapter index.
- Suggested context bundles:
  - “minimal context”: root index + top concepts + glossary.
  - “deep context”: root index + relevant chapters + frameworks + claims.

## Step 14: Validate

Copy or reference `tools/validate_okf_wiki.py` into the generated package, then run:

```bash
python3 tools/validate_okf_wiki.py .
```

Validation must check:

- Root `index.md`, `log.md`, `AGENTS.md` exist.
- Every directory with content has `index.md`.
- Non-reserved `.md` files have YAML frontmatter.
- Frontmatter includes non-empty `type`.
- Internal Markdown links resolve.

Fix errors before reporting completion. Warnings are acceptable only if explained.

## Update Existing Wiki Workflow

When updating an existing package:

1. Read root `AGENTS.md`, `index.md`, and `log.md`.
2. Read relevant directory indexes.
3. Add a new `sources/source-<NNN>.md`.
4. Create new chapter notes for new source sections.
5. Merge durable ideas into existing concept/framework pages instead of duplicating them.
6. Add or revise claims with source references.
7. Update glossary and open questions.
8. Update affected `index.md` files.
9. Append to root `log.md` and affected directory `log.md`.
10. Run validation.

Never silently overwrite existing concept pages. Merge by preserving useful prior content, adding source references, and noting uncertainty when sources disagree.

## Quality Rules

1. Build a wiki, not a summary.
2. Prefer durable concepts and frameworks over chapter-by-chapter recaps.
3. Preserve source traceability with citations and source refs.
4. Avoid long verbatim excerpts.
5. Use dense, readable Markdown for humans.
6. Make navigation obvious for agents.
7. Put uncertainty into `questions/open-questions.md` instead of pretending the book is complete truth.
8. Keep the package self-contained: the core understanding should survive if external URLs disappear, while citations still point outward when available.

## Completion Report

Report:

```text
✅ OKF LLM Wiki package created: <path>

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
- glossary/terms.md

Validation: passed

Use as agent context:
1. Attach the package folder, or
2. Start with index.md + AGENTS.md, then include relevant concept/framework/chapter pages.
```
