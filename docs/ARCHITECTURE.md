# Architecture

book-to-okf-wiki has two halves: a **deterministic extractor** (Python) and a
**spec-driven generator** (the agent following `SKILL.md`). The extractor turns any
document into clean text + metadata; the agent turns that into an OKF-compatible
LLM Wiki package.

```
            ┌─────────────────────────── EXTRACTOR (Python, deterministic) ──┐
 documents  │  scripts/extract.py  →  extractor/                              │
 (pdf/epub/ │    ├─ utils.py        CLI parse · multi-source resolve · runner │
  docx/...) │    ├─ config.py       supported extensions · paths · deps map   │
     │      │    ├─ dependencies.py optional-dep probing · --check report     │
     ▼      │    └─ parsers/        pdf · epub · docx · html · rtf · calibre · │
 ───────────│                        text  (best tool first, stdlib fallback) │
            │  output → <tempdir>/book_okf_wiki_work/                            │
            │    full_text.txt   (all sources merged, source-marked)          │
            │    metadata.json   (pages, words, tokens, chapters, ToC)        │
            └────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
            ┌─────────────────────────── GENERATOR (agent, follows SKILL.md) ┐
            │  Step 1.5  ask content type → BOOK_TYPE (technical | text)      │
            │  Step 2/2.5 extract · cost estimate · confirm                   │
            │  Step 2.6  REPL-style probing for large books (grep/sed, no     │
            │            full re-reads)                                        │
            │  Step 3    analyze structure (title, author, chapters, ToC)     │
            │  Step 4    choose output package location                         │
            │  Step 8    chapter notes with source references                   │
            │  Step 9    durable concept pages                                  │
            │  Step 10   framework pages                                        │
            │  Step 11   claim pages                                            │
            │  Step 13   indexes + context bundles                              │
            └────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                <package-slug>/  ← portable output folder:
                  AGENTS.md       agent maintenance rules
                  index.md        human + agent navigation
                  log.md          update history
                  sources/        source metadata
                  chapters/       chapter notes
                  concepts/       durable synthesized concepts
                  frameworks/     named methods and decision rules
                  claims/         important source-backed claims
                  glossary/       terms
                  questions/      open questions and uncertainties
```

## Design principles

1. **Extract structure, not summaries** — named frameworks, decision rules,
   anti-patterns; never raw passages.
2. **Compile-time over runtime** — pay navigation/structuring once; at query time
   load only the relevant concept, framework, claim, or chapter. See [PERFORMANCE.md](PERFORMANCE.md).
3. **Agent-readable indexes** — root and directory `index.md` files make context selection cheap.
4. **Source traceability** — concept, framework, and claim pages point back to source and chapter refs.
5. **Graceful degradation** — every format has a stdlib fallback; one bad source is
   skipped, not fatal.

## Key components

| Path | Responsibility |
|------|----------------|
| `scripts/extract.py` | thin entrypoint wrapper |
| `scripts/extractor/utils.py` | CLI parsing, multi-source resolution, chapter/ToC detection, runner |
| `scripts/extractor/parsers/` | one module per format |
| `scripts/extractor/dependencies.py` | optional-dependency probing + `--check` |
| `tools/discovery_tax.py` | legacy measurement helper for token cost comparisons |
| `tools/validate_skill.py` | checks a generated SKILL.md against host rules (`--lens claude|copilot|amp`) |
| `tools/validate_okf_wiki.py` | validates generated OKF wiki packages |
| `SKILL.md` | the generator spec for OKF LLM Wiki packages |

## Extending

- **New format** → add `parsers/<fmt>.py`, register its extension in `config.py`,
  wire dependency probing in `dependencies.py`, branch in `utils.extract_single_file`.
- **New generation behavior** → edit the relevant Step in `SKILL.md`; keep it lean
  and verify with `tools/validate_okf_wiki.py`.
