# Deep read

Load this when the user asks to deep-read a chapter, or a long chapter holds
load-bearing claims. Follow naming and frontmatter in [PACKAGE.md](PACKAGE.md).

## Steps

1. Add subsection notes under `chapters/subsections/`:

   ```text
   chapters/subsections/第04章-第01节-<中文短名>.md
   ```

2. Each subsection note uses `type: ChapterNote`,
   `tags: [subsection, ch04, ...]`, and links to previous/next subsection plus
   the chapter overview.

3. Update all of:
   - chapter overview (subsection table)
   - `chapters/index.md`
   - `chapters/subsections/index.md`
   - concept pages that depend on the subsection
   - `chapters/log.md` and `chapters/subsections/log.md`

4. Validate with the package's `tools/validate_okf_wiki.py` (non-strict must
   pass).

Done when: every core thesis is reachable both ways — chapter/subsection notes
→ concepts, and concept pages → dated-file evidence — and every new page is
indexed.
