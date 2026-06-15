import hashlib
import os
import tempfile
from pathlib import Path

# Default base work directory. Two ways to override:
#   1. BOOK_SKILL_WORKDIR env var — pins a fixed directory (legacy behavior;
#      useful in tests and CI). When set, ALL sources write here, so concurrent
#      or back-to-back extractions WILL overwrite each other.
#   2. --workdir <path> CLI flag — same effect, per-invocation.
# When NEITHER is set, main() computes a per-source subdirectory under
# DEFAULT_BASE_WORKDIR so different books no longer clobber each other.
DEFAULT_BASE_WORKDIR = Path(tempfile.gettempdir()) / "book_okf_wiki_work"

OUTPUT_DIR = Path(
    os.environ.get(
        "BOOK_SKILL_WORKDIR",
        str(DEFAULT_BASE_WORKDIR),
    )
)
OUTPUT_TEXT = OUTPUT_DIR / "full_text.txt"
OUTPUT_META = OUTPUT_DIR / "metadata.json"


def per_source_workdir(source_identifier: str) -> Path:
    """Return an isolated work directory keyed by a source identifier.

    Used as the default when neither BOOK_SKILL_WORKDIR nor --workdir is set.
    The identifier is hashed (not used verbatim) so unusual characters in a
    book filename don't produce an invalid path, and two books with the same
    stem but different paths still collide only on content+path hash.
    """
    digest = hashlib.sha1(source_identifier.encode("utf-8")).hexdigest()[:12]
    # Keep a short human-readable prefix when the identifier looks like a path
    stem = Path(source_identifier).stem[:32].replace(" ", "-") or "source"
    return DEFAULT_BASE_WORKDIR / f"{stem}-{digest}"


def env_workdir_pinned() -> bool:
    """True when BOOK_SKILL_WORKDIR is explicitly set (pin-to-one-dir mode)."""
    return bool(os.environ.get("BOOK_SKILL_WORKDIR"))

WORDS_PER_TOKEN = 0.75  # approximate

TEXT_EXTENSIONS = {".txt", ".text", ".md", ".markdown", ".rst", ".adoc", ".asciidoc"}
HTML_EXTENSIONS = {".html", ".htm", ".xhtml"}
CALIBRE_EBOOK_EXTENSIONS = {".mobi", ".azw", ".azw3"}
SUPPORTED_EXTENSIONS = {
    ".pdf", ".epub", ".docx", ".rtf",
    *TEXT_EXTENSIONS,
    *HTML_EXTENSIONS,
    *CALIBRE_EBOOK_EXTENSIONS,
}

PYTHON_DEPENDENCIES = {
    "docling": "docling",
    "PyPDF2": "PyPDF2",
    "pdfminer": "pdfminer.six",
    "ebooklib": "ebooklib",
    "bs4": "beautifulsoup4",
    "docx": "python-docx",
    "striprtf": "striprtf",
}


def supported_formats_message() -> str:
    return ", ".join(sorted(SUPPORTED_EXTENSIONS))
