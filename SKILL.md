---
name: book-to-okf-wiki
description: "Source-grounded OKF LLM Wiki from books and document collections. Use when converting sources into a new portable Markdown wiki package, deep-reading a chapter into an existing package, or updating an existing package from new sources."
---

# Book to OKF Wiki

Build a portable Markdown OKF LLM Wiki from pinned source evidence — a
browsable knowledge package any agent can load as context.

## Leitworter

- **Source-grounded wiki** — durable knowledge from pinned evidence.
- **Concept-first synthesis** — concepts, frameworks, and claims before chapter
  recaps.
- **Bidirectional traceability** — every durable idea links back to source lines
  and forward to the pages that use it.
- **Navigation spine** — indexes, logs, and `AGENTS.md` make the package usable
  by humans and agents.
- **Uncertainty ledger** — unresolved ambiguity lives in
  `questions/待解决问题.md`.

## Branches

- **Full conversion** (default when the user provides document paths): steps
  below.
- **Deep read** (user asks to deep-read a chapter, or a long chapter holds
  load-bearing claims): follow [DEEP-READ.md](DEEP-READ.md).
- **Update** (user points at an existing package): follow [UPDATE.md](UPDATE.md).
- **Analyze only** (user asks to preview/analyze before writing): stop after
  Confirm delivers the analysis report.

## Full conversion

### 1. Classify

Ask unless the user already classified:

```text
这些资料属于哪类？
1. Technical：有代码、表格、公式、图示
2. Text-heavy：主要是文字
3. Not sure：先用通用方式，必要时提醒我
```

Map option 1 → `BOOK_TYPE=technical`; otherwise `BOOK_TYPE=text`.

Done when: `BOOK_TYPE` is set.

### 2. Extract

Accept files, directories, or globs:
`.pdf`, `.epub`, `.docx`, `.txt`, `.md`, `.markdown`, `.rst`, `.adoc`, `.html`,
`.htm`, `.rtf`, `.mobi`, `.azw`, `.azw3`.

If the final argument is not an existing path and looks like a slug, use it as
`PACKAGE_SLUG`; otherwise derive the slug from the title.

No valid input:

```text
book-to-okf-wiki creates OKF LLM Wiki packages. Provide a supported document path, folder, or glob.
Usage: book-to-okf-wiki <path-or-glob>... [package-slug]
```

Run with `python3`. Prefer `--pkg <package-dir>` so pinned text lands inside the
package. For EPUB, install `ebooklib beautifulsoup4` only when useful.

```bash
SCRIPT="$HOME/.agents/skills/book-to-okf-wiki/scripts/extract.py"
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" "$SCRIPT" $INPUT_PATHS --mode <BOOK_TYPE> --install-missing ask --pkg <package-dir>
```

If this skill lives elsewhere, locate `scripts/extract.py` with `rg --files` or
`find`. Without `--pkg`, read the workdir from extractor stdout (`Text ->`,
`Meta ->`).

`--pkg` writes:

- `sources/full_text-<YYYYMMDD>.txt` (or `-<N>` suffix)
- `sources/full_text.txt` (moving pointer)
- `sources/metadata.json`

Read `sources/metadata.json` before writing. Anchor citations to the **dated**
file. Query large books with `rg` / `grep` / `sed` / `wc` against that file.
For EPUB, use `=== EPUB-SECTION … ===` markers and `chapter_map` before
guessing chapter boundaries.

Done when: `sources/metadata.json` and the dated pinned text exist, and their
paths, md5, and line count are readable.

### 3. Confirm

Show: detected sources; approximate pages/words/tokens; output directory and
slug; directories/files to create; estimated time and token cost. Ask for
confirmation.

Done when: the user confirms the displayed scope, or the analyze-only report
has been delivered.

### 4. Write

Read [PACKAGE.md](PACKAGE.md) and build the package it specifies.

Done when: every load-bearing claim has a dated-file line citation or an entry
in `questions/待解决问题.md`; every created page is reachable from an index;
naming and prose follow PACKAGE.md.

### 5. Validate

Copy or reference `tools/validate_okf_wiki.py` into the package, then:

```bash
python3 tools/validate_okf_wiki.py .
python3 tools/validate_okf_wiki.py --strict .
```

Non-strict must pass. Strict is advisory — fix real gaps it reports.

Done when: non-strict validation passes.

### 6. Report

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
