import hashlib
import os
import tempfile
from datetime import date
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
    digest = hashlib.sha1(source_identifier.encode("utf-8"), usedforsecurity=False).hexdigest()[:12]
    # Keep a short human-readable prefix when the identifier looks like a path
    stem = Path(source_identifier).stem[:32].replace(" ", "-") or "source"
    return DEFAULT_BASE_WORKDIR / f"{stem}-{digest}"


def env_workdir_pinned() -> bool:
    """True when BOOK_SKILL_WORKDIR is explicitly set (pin-to-one-dir mode)."""
    return bool(os.environ.get("BOOK_SKILL_WORKDIR"))


def pkg_sources_dir(pkg_dir: Path) -> Path:
    """Return the ``sources/`` directory inside an OKF wiki package.

    Does NOT create it — callers (main) mkdir on demand. Centralized here so the
    package-extraction layout is defined in one place.
    """
    return Path(pkg_dir) / "sources"


def today_version() -> str:
    """Return a YYYYMMDD version stamp for the current date."""
    return date.today().strftime("%Y%m%d")


def versioned_text_paths(sources_dir: Path, version: str) -> tuple[Path, Path, Path]:
    """Resolve package-extraction output paths for a given version stamp.

    Returns ``(versioned_text, stable_text, meta)``:

    - ``versioned_text``: ``sources/full_text-<version>.txt`` (or
      ``...-2.txt`` / ``...-3.txt`` if that day's file already exists) — the
      pinned, line-number-anchored extraction for this run. Deep-read line refs
      and source-page provenance point here. Old versioned files are NOT
      overwritten or deleted by re-extraction (callers/users prune manually),
      preserving history.
    - ``stable_text``: ``sources/full_text.txt`` — always the latest extraction's
      copy, so "just read the current full text" keeps working without knowing
      the version. (A copy, not a symlink, so it behaves identically across
      macOS/Linux/Windows and needs no special permissions.)
    - ``meta``: ``sources/metadata.json`` — overwritten each run with the latest
      metadata, which itself carries ``extraction_version`` / ``full_text_md5`` /
      ``full_text_lines`` so any reader can tell which versioned file it describes.
    """
    sources_dir = Path(sources_dir)
    versioned_text = sources_dir / f"full_text-{version}.txt"
    if versioned_text.exists():
        counter = 2
        while True:
            candidate = sources_dir / f"full_text-{version}-{counter}.txt"
            if not candidate.exists():
                versioned_text = candidate
                break
            counter += 1
    return (
        versioned_text,
        sources_dir / "full_text.txt",
        sources_dir / "metadata.json",
    )

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
