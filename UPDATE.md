# Update existing wiki

Load this when the user points at an existing package. Follow naming and
frontmatter in [PACKAGE.md](PACKAGE.md). Preserve useful existing pages; merge
durable ideas into them.

## Steps

1. Read root `AGENTS.md`, `index.md`, `log.md`, and relevant directory indexes.
2. Reuse pinned extraction when `sources/metadata.json` md5/line count matches
   the source page. Re-extract with `--pkg` only when missing or mismatched
   (see Extract in [SKILL.md](SKILL.md)).
3. Add a new `来源-<NNN>.md` only for genuinely new sources.
4. Add chapter/subsection notes as needed (deep-read path:
   [DEEP-READ.md](DEEP-READ.md)).
5. Merge durable ideas into existing concept/framework/claim pages.
6. Update glossary, questions, indexes, and logs.
7. Validate: non-strict `tools/validate_okf_wiki.py` must pass.

Done when: new evidence is merged or cited, indexes/logs reflect the change,
useful pages remain intact, and non-strict validation passes.
