# Architecture

Two pieces:

- `scripts/extract.py`: deterministic text and metadata extraction.
- `SKILL.md`: agent instructions for turning extracted text into an OKF v0.2
  LLM Wiki package ([SPEC](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)).

```text
documents
  -> scripts/extract.py --pkg <package-dir>
  -> <package-dir>/sources/full_text-<date>.txt
  -> <package-dir>/sources/metadata.json
  -> agent follows SKILL.md + PACKAGE.md
  -> chapters/, concepts/, frameworks/, claims/, glossary/, questions/
  -> tools/validate_okf_wiki.py
```

## OKF v0.2 contract

Package shape details live in `PACKAGE.md`. The durable producer rules are:

- Root `index.md` declares `okf_version: "0.2"`.
- Concept pages use `generated`, optional `verified` / `stale_after`, and
  `status: draft | stable | deprecated` (not legacy `timestamp` / `active`).
- Provenance is the `sources` family; each entry needs `resource`, and body
  footnotes key to `sources[].id`.
- Intra-package links and path-valued fields use `/`-rooted bundle paths.
- `tools/validate_okf_wiki.py` gates shape + link resolution; v0.1 leftovers and
  missing recommended trust fields warn (strict mode is advisory).

## Rules

- Prefer `--pkg`; temp extraction is not reusable across sessions.
- Anchor citations to dated pinned text via `sources[].id` footnotes.
- Keep generation behavior in `SKILL.md` / `PACKAGE.md`; keep extraction in
  Python.
- Add dependencies only when a format needs them and stdlib fallback is not good
  enough.

## Files

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Full-conversion steps; points at branch/reference files |
| `PACKAGE.md` | OKF v0.2 naming, tree, frontmatter, citations, page contents |
| `DEEP-READ.md` | Deep-read / subsection branch |
| `UPDATE.md` | Update-existing-package branch + v0.1→v0.2 sweep |
| `scripts/extract.py` | Extraction entrypoint |
| `tools/validate_okf_wiki.py` | Validates packages against the v0.2 producer contract |
| `tools/validate_skill.py` | Validates this skill file for supported hosts |
