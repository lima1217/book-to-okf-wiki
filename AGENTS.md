# AGENTS.md

## Cursor Cloud specific instructions

`book-to-okf-wiki` is a **local, offline, stdlib-first Python CLI** (Python 3.9+; the
VM has 3.12). There is **no server, database, or long-running service** — everything
is a one-shot CLI/tool invocation, so there is nothing to "start". The core tool runs
on the standard library alone; optional third-party packages only improve extraction
quality and every format except MOBI/AZW has a stdlib fallback.

The update script installs the dev tools (`pytest`, `ruff`) and the pure-Python
optional extractors. Two extras are intentionally **not** in the update script:
- `poppler-utils` (`pdftotext`) — a system package needing `sudo apt-get install`.
  PDF extraction still works via the `PyPDF2` / `pdfminer.six` fallbacks without it.
- `docling` (technical-PDF mode) and Calibre `ebook-convert` (MOBI/AZW, no fallback) —
  install on demand only if you need those formats.

### Commands (run from repo root)
- Lint (matches CI gate): `python3 -m ruff check --select E9,F --target-version py310 scripts/ tests/`
- Tests: `python3 -m pytest tests/ -q`
- Dependency preflight report: `python3 scripts/extract.py --check`
- Extract a document into a reusable package:
  `python3 scripts/extract.py <path-or-glob>... --mode text --install-missing no --pkg <package-dir>`
- Validate a generated wiki package: `python3 tools/validate_okf_wiki.py [--strict] <package-dir>`
- Validate the skill file: `python3 tools/validate_skill.py SKILL.md`

### Non-obvious gotchas
- `pytest` / `ruff` install to `~/.local/bin`, which is not on `PATH`. Invoke them as
  `python3 -m pytest` / `python3 -m ruff` (as CI effectively does) rather than the bare
  binaries.
- Use `--install-missing no` (or set `BOOK_SKILL_INSTALL_MISSING=no`) for
  non-interactive runs; `ask` mode prompts on a TTY and otherwise silently falls back.
- Every non-reserved `*.md` in a wiki package must have YAML frontmatter with a
  non-empty `type:`. Only `index.md` and `log.md` are exempt; `AGENTS.md` inside a
  generated package is **not** exempt and needs frontmatter to pass the validator.
- The full wiki-generation step (turning extracted `sources/` text into
  `chapters/`, `concepts/`, etc. per `SKILL.md`) is performed by an AI agent, not by
  this repo's code. The repo only provides extraction (`scripts/extract.py`) and
  validation (`tools/`).
