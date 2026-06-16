# book-to-okf-wiki

Convert books and document collections into OKF-compatible LLM Wiki packages.
The output is a portable Markdown folder, not an installable agent skill.

## Inspiration

This project was inspired by [virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill).

## Usage

```text
/book-to-okf-wiki <path-or-glob>... [package-slug]
```

Supported formats: PDF, EPUB, DOCX, TXT, Markdown, reStructuredText, AsciiDoc,
HTML, RTF, MOBI/AZW/AZW3.

Examples:

```text
/book-to-okf-wiki ~/books/systems-thinking.pdf systems-thinking-wiki
/book-to-okf-wiki ~/papers/*.pdf ai-agent-research
```

## Output

```text
<package-slug>/
├── AGENTS.md
├── index.md
├── log.md
├── sources/
├── chapters/
├── concepts/
├── frameworks/
├── claims/
├── glossary/
├── questions/
└── tools/validate_okf_wiki.py
```

The package keeps pinned extracted text in `sources/` when extraction runs with
`--pkg`, so later updates can reuse the same text and stable line references.

## Extractor

```bash
python3 scripts/extract.py <path-or-glob>... --mode text --install-missing ask --pkg <package-dir>
python3 scripts/extract.py --check
```

For better EPUB extraction:

```bash
python3 -m pip install ebooklib beautifulsoup4
```

## Validation

```bash
python3 tools/validate_okf_wiki.py <package-dir>
python3 tools/validate_skill.py SKILL.md
```
