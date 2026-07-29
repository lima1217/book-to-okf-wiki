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
5. Merge durable ideas into existing concept/framework/claim pages. On every
   page you rewrite, refresh `generated.at`, add the new `sources` entry the new
   footnotes cite, and leave `verified` untouched — a rewrite invalidates the old
   confirmation rather than inheriting it.
6. Update glossary, questions, indexes, and logs.
7. Overwrite the package's `tools/validate_okf_wiki.py` with this skill's copy.
   A package carries the validator it was built with, and a pre-v0.2 copy
   rejects the bundle-relative links this skill now writes.
8. Sweep any pre-v0.2 page, including pages this update never touched:
   `timestamp` → `generated`, `source_refs` and a `# 引用` list → `sources` plus
   keyed footnotes, `status: active` → `stable`, relative links → `/`-rooted,
   and `okf_version: "0.2"` on the root `index.md`. Record the sweep in the root
   `log.md`. On an already-migrated package this pass finds nothing.
9. Validate: non-strict must pass.

Done when: new evidence is merged or cited, indexes/logs reflect the change,
useful pages remain intact, validation reports no v0.1 warning, and non-strict
validation passes.
