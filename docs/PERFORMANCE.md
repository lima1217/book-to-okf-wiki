# Performance

Default to the cheap path:

- Use text mode for prose.
- Use technical mode only when tables, code, formulas, or diagrams matter.
- Use `--pkg` so future sessions reuse pinned text instead of re-extracting.
- For large books, inspect slices with `rg`, `grep`, `sed`, and `wc`; do not
  load the full text into context.

## Tradeoff

`pdftotext` is fast and loses structure. Technical extraction is slower and
worth it only when the structure is useful.

| Source type | Mode |
| --- | --- |
| prose book, essay, notes | `text` |
| code-heavy book | `technical` |
| tables/formulas matter | `technical` |
| unsure | `text`, then re-run technical if structure is missing |

## Check

```bash
python3 scripts/extract.py --check
```
