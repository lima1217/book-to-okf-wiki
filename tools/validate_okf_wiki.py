#!/usr/bin/env python3
"""Validate a self-contained LLM Wiki package targeting OKF v0.2.

Errors cover OKF §11 shape failures (parseable frontmatter, non-empty `type`),
broken intra-package links (producer gate — consumers must tolerate them per
§11), and this package's required root `okf_version: "0.2"` declaration.
Everything else — package conventions and v0.1 leftovers — prints as a warning.
"""
from __future__ import annotations

import posixpath
import re
import sys
import urllib.parse
from pathlib import Path


OKF_VERSION = "0.2"
RESERVED = {"index.md", "log.md"}
STATUS_VALUES = {"draft", "stable", "deprecated"}
FRONTMATTER_RE = re.compile(r"^---\s*\n(?P<yaml>.*?)\n---\s*\n", re.S)
LINK_RE = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]]+)\]")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:", re.M)
SOURCE_ID_RE = re.compile(r"^\s+-\s*(?:\{\s*)?id:\s*([^\s,}]+)", re.M)
LEGACY_CITATIONS_RE = re.compile(r"^#{1,6}\s*(?:引用|Citations)\s*$", re.M)
SOURCE_ENTRY_START_RE = re.compile(r"^\s+-\s+")
SOURCE_RESOURCE_RE = re.compile(r"(?:^|\s)resource\s*:")


def frontmatter_of(text: str) -> str | None:
    match = FRONTMATTER_RE.match(text)
    return match.group("yaml") if match else None


def _sources_entries_missing_resource(yaml_text: str) -> list[str]:
    """Return display labels for sources[] entries that omit resource (§5.1)."""
    lines = yaml_text.splitlines()
    in_sources = False
    entries: list[list[str]] = []
    current: list[str] | None = None

    for line in lines:
        if re.match(r"^sources:\s*(?:\[.*\])?\s*$", line):
            in_sources = True
            current = None
            # Flow form on one line: sources: [{id: x, resource: y}, ...]
            if "[" in line and not SOURCE_RESOURCE_RE.search(line):
                # Only flag when the line clearly carries at least one mapping
                # entry and none of them name resource.
                if "{" in line:
                    return ["(inline sources entry)"]
            continue
        if not in_sources:
            continue
        if line.strip() and not line[0].isspace():
            break
        if SOURCE_ENTRY_START_RE.match(line):
            if current is not None:
                entries.append(current)
            current = [line]
        elif current is not None:
            current.append(line)
    if current is not None:
        entries.append(current)

    missing: list[str] = []
    for entry in entries:
        blob = "\n".join(entry)
        if SOURCE_RESOURCE_RE.search(blob):
            continue
        id_match = re.search(r"\bid:\s*([^\s,}]+)", blob)
        missing.append(id_match.group(1) if id_match else "(unnamed entry)")
    return missing


def check_frontmatter(rel: str, yaml_text: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for one concept document's frontmatter."""
    errors: list[str] = []
    warnings: list[str] = []

    type_match = re.search(r"^type:\s*(.+?)\s*$", yaml_text, re.M)
    if not type_match or not type_match.group(1).strip():
        errors.append(f"{rel}: missing non-empty type")

    status_match = re.search(r"^status:\s*(\S+)\s*$", yaml_text, re.M)
    if status_match and status_match.group(1) not in STATUS_VALUES:
        warnings.append(
            f"{rel}: status '{status_match.group(1)}' is not one of "
            f"{sorted(STATUS_VALUES)} (OKF v0.2 §5.4)"
        )

    has_generated = re.search(r"^generated:", yaml_text, re.M)
    if re.search(r"^timestamp:", yaml_text, re.M) and not has_generated:
        warnings.append(f"{rel}: v0.1 timestamp — replace with generated: {{ by, at }} (§5.2)")
    if re.search(r"^source_refs:", yaml_text, re.M):
        warnings.append(f"{rel}: v0.1 source_refs — replace with the sources family (§5.1)")

    for label in _sources_entries_missing_resource(yaml_text):
        warnings.append(
            f"{rel}: sources[] entry {label} is missing resource "
            "(required within each entry, OKF v0.2 §5.1)"
        )

    return errors, warnings


def is_external(target: str) -> bool:
    return (
        "://" in target
        or target.startswith("#")
        or target.startswith("mailto:")
        or target.startswith("tel:")
    )


def validate(root: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for required in ["index.md", "log.md", "AGENTS.md"]:
        if not (root / required).exists():
            errors.append(f"root missing {required}")

    for directory in sorted(p for p in root.rglob("*") if p.is_dir()):
        rel_parts = directory.relative_to(root).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        md_children = [p for p in directory.glob("*.md") if p.is_file()]
        child_dirs = [p for p in directory.iterdir() if p.is_dir() and not p.name.startswith(".")]
        if (md_children or child_dirs) and not (directory / "index.md").exists():
            warnings.append(f"{directory.relative_to(root)}: missing index.md")

    for path in sorted(root.rglob("*.md")):
        rel_parts = path.relative_to(root).parts
        if any(part.startswith(".") for part in rel_parts):
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")

        rel = str(path.relative_to(root))
        yaml_text = frontmatter_of(text)

        if path.name not in RESERVED:
            if yaml_text is None:
                errors.append(f"{rel}: missing YAML frontmatter")
            else:
                fm_errors, fm_warnings = check_frontmatter(rel, yaml_text)
                errors.extend(fm_errors)
                warnings.extend(fm_warnings)
            if LEGACY_CITATIONS_RE.search(text):
                warnings.append(
                    f"{rel}: v0.1 citations heading — move the list into the sources "
                    "family and cite it with keyed footnotes (§5.1)"
                )
        elif path.name == "index.md":
            is_root_index = path.parent == root
            version_match = (
                re.search(r'^okf_version:\s*["\']?([^"\'\s]+)["\']?\s*$', yaml_text, re.M)
                if yaml_text
                else None
            )
            declares_target = bool(
                version_match and version_match.group(1) == OKF_VERSION
            )
            if is_root_index and not declares_target:
                declared = version_match.group(1) if version_match else None
                if declared is None:
                    errors.append(
                        f'{rel}: root index must declare okf_version: "{OKF_VERSION}" '
                        "(package requirement; OKF §12 makes the field optional)"
                    )
                else:
                    errors.append(
                        f'{rel}: okf_version is "{declared}", expected "{OKF_VERSION}"'
                    )
            elif yaml_text is not None and not (is_root_index and declares_target):
                warnings.append(
                    f"{rel}: index.md carries frontmatter; only the root index may, "
                    "and only okf_version (§8)"
                )

        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or is_external(target):
                continue
            target = urllib.parse.unquote(target)
            if target.startswith("/"):
                dest = root / target.lstrip("/")
            else:
                warnings.append(
                    f"{rel}: relative link -> {raw_target}; this package writes "
                    "bundle-relative links starting with /"
                )
                dest = path.parent / target
            if raw_target.endswith("/") or target.endswith("/"):
                dest = dest / "index.md"
            if not dest.exists():
                errors.append(f"{path.relative_to(root)}: broken link -> {raw_target}")

    if warnings:
        print("OKF wiki warnings:")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("OKF wiki validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OKF wiki validation passed.")
    return 0


def _collect_link_targets(root: Path) -> dict:
    """Map each .md file (relative path str) to the set of files that link to it.

    Used by strict-mode orphan / cross-link checks. Keys are relative POSIX
    paths like 'concepts/free-will.md'; values are sets of referrer paths.
    """
    inbound: dict = {}
    all_md = sorted(p for p in root.rglob("*.md") if not any(
        part.startswith(".") for part in p.relative_to(root).parts
    ))
    # initialize every file with an empty set
    for p in all_md:
        inbound[p.relative_to(root).as_posix()] = set()

    for src in all_md:
        text = src.read_text(encoding="utf-8", errors="ignore")
        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or is_external(target):
                continue
            target = urllib.parse.unquote(target)
            if target.startswith("/"):
                dest = root / target.lstrip("/")
            else:
                dest = src.parent / target
            if raw_target.endswith("/") or target.endswith("/"):
                dest = dest / "index.md"
            if dest.exists():
                rel = posixpath.normpath(dest.relative_to(root).as_posix())
                inbound.setdefault(rel, set()).add(src.relative_to(root).as_posix())
    return inbound


def _find_glossary(root: Path) -> Path | None:
    """Locate the package's glossary page.

    Discovery order:
      1. A glossary/*.md whose YAML frontmatter declares `type: Glossary`.
      2. The canonical filenames the skill documents: glossary/术语.md
         (Chinese, the naming-rule default) then the legacy glossary/terms.md.
    Returns the first match, or None if no glossary exists.
    """
    glossary_dir = root / "glossary"
    if not glossary_dir.is_dir():
        return None
    # 1. Content-based: any glossary/*.md with type: Glossary.
    candidates = sorted(glossary_dir.glob("*.md"))
    for cand in candidates:
        if cand.name in RESERVED:
            continue
        text = cand.read_text(encoding="utf-8", errors="ignore")
        match = FRONTMATTER_RE.match(text)
        if match and re.search(r"^type:\s*Glossary\s*$", match.group("yaml"), re.M):
            return cand
    # 2. Canonical filenames (Chinese default, then legacy English).
    for name in ("术语.md", "terms.md"):
        cand = glossary_dir / name
        if cand.exists():
            return cand
    return None


def strict_checks(root: Path) -> list:
    """Additional quality warnings beyond shape validation.

    These never affect the exit code — they only print guidance, mirroring the
    skill's Quality Rules (durable concepts, traceability, navigation,
    uncertainty separation) which the shape validator can't enforce.
    """
    warns = []
    inbound = _collect_link_targets(root)

    # 1. Orphan pages: a content .md nothing else links to.
    for rel, referrers in sorted(inbound.items()):
        base = rel.rsplit("/", 1)[-1]
        if base in RESERVED:
            continue  # index.md / log.md are reached structurally
        if rel == "AGENTS.md":
            continue  # required at package root; not expected as a linked concept
        if not referrers:
            warns.append(f"[orphan] {rel}: no other page links to it — add a link from the relevant index or concept page")

    # 2. Glossary presence.
    # Discover by content (type: Glossary) first, then by the canonical names
    # the skill allows: the Chinese 术语.md (per the skill's naming rule) and
    # the legacy English terms.md. This avoids a false "missing" warning for
    # packages that correctly follow the Chinese-filename convention.
    glossary = _find_glossary(root)
    if glossary is None:
        warns.append(
            "[glossary] no glossary found — add a glossary/ page (type: Glossary, "
            "e.g. glossary/术语.md) with key terms for agent lookups"
        )
    else:
        text = glossary.read_text(encoding="utf-8", errors="ignore")
        # Count bold term entries in either list form ("- **Term** …") or the
        # table form the skill's examples also use ("| **Term** | …").
        list_terms = len(re.findall(r"^- \*\*", text, re.MULTILINE))
        table_terms = len(re.findall(r"^\|\s*\*\*", text, re.MULTILINE))
        if list_terms + table_terms == 0:
            warns.append(
                f"[glossary] {glossary.relative_to(root)} has no bold term entries "
                "— add key terms (as `- **Term** — def` or `| **Term** | def |`)"
            )

    # 3. Trust and citation signals on content pages.
    for path in sorted(root.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        if path.name in RESERVED:
            continue
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        yaml_text = frontmatter_of(text)
        if yaml_text is None:
            continue  # already an error in shape validation

        if not re.search(r"^generated:", yaml_text, re.M):
            warns.append(
                f"[trust] {rel}: no generated: {{ by, at }} — readers cannot tell who "
                "wrote this or when (§5.2)"
            )

        source_ids = set(SOURCE_ID_RE.findall(yaml_text))
        body = text[len(FRONTMATTER_RE.match(text).group(0)):]
        cited = set(FOOTNOTE_REF_RE.findall(body)) | set(FOOTNOTE_DEF_RE.findall(body))
        for label in sorted(cited - source_ids):
            warns.append(
                f"[citation] {rel}: footnote [^{label}] has no matching sources[].id "
                "— the label is the join key into sources (§5.1)"
            )
    return warns


def main() -> int:
    args = sys.argv[1:]
    strict = "--strict" in args
    # strip flags to find the root path argument
    positional = [a for a in args if not a.startswith("--")]
    root = Path(positional[0]) if positional else Path(".")
    code = validate(root)
    if strict and code == 0:
        strict_warns = strict_checks(root)
        if strict_warns:
            print("\nOKF wiki strict-mode notes (advisory, do not affect pass/fail):")
            for w in strict_warns:
                print(f"- {w}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
