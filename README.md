# book-to-okf-wiki

`book-to-okf-wiki` converts books and document collections into **OKF-compatible LLM Wiki knowledge packages**, not installable agent skills.

The output is a portable Markdown knowledge bundle that humans can read and any agent can use as context.

## What It Generates

```text
<package-slug>/
├── AGENTS.md
├── index.md
├── log.md
├── sources/
├── chapters/
├── concepts/
├── claims/
├── frameworks/
├── glossary/
├── questions/
└── tools/validate_okf_wiki.py
```

The package combines two ideas:

- **LLM Wiki workflow**: a durable, cross-linked wiki that compounds as more sources are folded in.
- **OKF shape**: Markdown file tree, `index.md`, `log.md`, YAML frontmatter, non-empty `type`, internal links, citations, and validation.

## Usage

```text
/book-to-okf-wiki <path-to-document-folder-or-glob>... [package-slug]
```

Supported formats: PDF, EPUB, DOCX, TXT, Markdown, reStructuredText, AsciiDoc, HTML, RTF, MOBI/AZW/AZW3.

Examples:

```text
/book-to-okf-wiki ~/books/systems-thinking.pdf systems-thinking-wiki
/book-to-okf-wiki ~/papers/*.pdf ai-agent-research
/book-to-okf-wiki ~/notes/book.md
```

## Validation

Generated packages should pass:

```bash
python3 tools/validate_okf_wiki.py .
```

The validator checks root files, directory indexes, YAML frontmatter, non-empty `type`, and internal Markdown links.

## Extractor

The existing `scripts/extract.py` pipeline is still used to extract text from source formats before wiki generation. Run:

```bash
python3 scripts/extract.py --check
```

to inspect available extraction backends.

For EPUB, install the recommended parser stack for better chapter order and cleaner XHTML extraction:

```bash
pip3 install ebooklib beautifulsoup4
```

Without those packages, the extractor falls back to Python stdlib ZIP/HTML parsing. That fallback is dependency-free, but it is less EPUB-aware than `ebooklib`.
