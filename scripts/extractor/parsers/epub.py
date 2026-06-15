from __future__ import annotations

import posixpath
import re
import zipfile
from extractor.parsers.html import _HTMLTextExtractor


def _section_marker(index: int, href: str) -> str:
    """Boundary marker injected before each EPUB spine item's text.

    Lets downstream consumers (the wiki generator, or `grep`/`sed`) locate
    chapter/section spans in the flattened text without re-parsing the EPUB.
    Format: ``=== EPUB-SECTION <n>: <href> ===``
    """
    return f"\n=== EPUB-SECTION {index}: {href} ===\n"


def extract_with_ebooklib(epub_path: str) -> str | None:
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup

        book = epub.read_epub(epub_path)
        parts = []
        section_index = 0
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            href = getattr(item, "get_name", lambda: "")() or ""
            section_index += 1
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text(separator="\n")
            parts.append(_section_marker(section_index, href) + text)
        return "\n\n".join(parts)
    except ImportError:
        return None
    except Exception:
        return None


def _find_opf_path(zf: zipfile.ZipFile) -> str | None:
    """Locate the OPF package document inside an EPUB archive.

    First tries ``META-INF/container.xml`` (the spec-defined entry point),
    then falls back to scanning the archive for any ``.opf`` file.
    """
    # Spec-defined: read container.xml for the rootfile path
    try:
        container = zf.read("META-INF/container.xml").decode("utf-8", errors="replace")
        match = re.search(r'full-path=["\']([^"\']+\.opf)["\']', container)
        if match:
            return match.group(1)
    except (KeyError, Exception):
        pass

    # Fallback: glob for any .opf file
    opf_files = [n for n in zf.namelist() if n.endswith(".opf")]
    return opf_files[0] if opf_files else None


def extract_with_zipfile(epub_path: str) -> str | None:
    """stdlib-only EPUB extractor: unzip → parse HTML files."""
    try:
        with zipfile.ZipFile(epub_path) as zf:
            names = zf.namelist()

            # Locate OPF and determine its directory for resolving relative hrefs
            opf_path = _find_opf_path(zf)
            opf_dir = posixpath.dirname(opf_path) if opf_path else ""

            # Read OPF spine to get reading order, fall back to sorted xhtml files
            spine_order: list[str] = []
            if opf_path:
                opf_text = zf.read(opf_path).decode("utf-8", errors="replace")
                raw_hrefs = re.findall(r'href=["\']([^"\']+\.(?:xhtml|html))["\']', opf_text)
                # Resolve hrefs relative to the OPF directory
                for href in raw_hrefs:
                    resolved = posixpath.normpath(posixpath.join(opf_dir, href)) if opf_dir else href
                    spine_order.append(resolved)

            html_files = spine_order or sorted(
                n for n in names if n.endswith((".html", ".xhtml"))
            )
            if not html_files:
                return None

            parts = []
            section_index = 0
            for name in html_files:
                try:
                    raw = zf.read(name).decode("utf-8", errors="replace")
                    parser = _HTMLTextExtractor()
                    parser.feed(raw)
                    section_index += 1
                    parts.append(_section_marker(section_index, name) + parser.get_text())
                except Exception:
                    continue
            return "\n\n".join(parts) if parts else None
    except Exception:
        return None


def count_epub_chapters(epub_path: str) -> int:
    """Count spine items (approximate chapter count) without dependencies."""
    try:
        with zipfile.ZipFile(epub_path) as zf:
            opf_path = _find_opf_path(zf)
            if not opf_path:
                return 0
            opf_text = zf.read(opf_path).decode("utf-8", errors="replace")
            return len(re.findall(r'<itemref\b', opf_text))
    except Exception:
        return 0

