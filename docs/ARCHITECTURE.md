# Architecture

Two pieces:

- `scripts/extract.py`: deterministic text and metadata extraction.
- `SKILL.md`: agent instructions for turning extracted text into an OKF LLM
  Wiki package.

```text
documents
  -> scripts/extract.py --pkg <package-dir>
  -> <package-dir>/sources/full_text-<date>.txt
  -> <package-dir>/sources/metadata.json
  -> agent follows SKILL.md
  -> chapters/, concepts/, frameworks/, claims/, glossary/, questions/
  -> tools/validate_okf_wiki.py
```

## Rules

- Prefer `--pkg`; temp extraction is not reusable across sessions.
- Anchor citations and line references to the dated pinned text file.
- Keep generation behavior in `SKILL.md`; keep extraction behavior in Python.
- Add dependencies only when a format needs them and stdlib fallback is not good
  enough.

## Files

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Full-conversion steps; points at branch/reference files |
| `PACKAGE.md` | Naming, tree, frontmatter, page contents |
| `DEEP-READ.md` | Deep-read / subsection branch |
| `UPDATE.md` | Update-existing-package branch |
| `scripts/extract.py` | Extraction entrypoint |
| `tools/validate_okf_wiki.py` | Validates generated packages |
| `tools/validate_skill.py` | Validates this skill file for supported hosts |
