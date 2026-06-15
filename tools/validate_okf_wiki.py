#!/usr/bin/env python3
"""Validate a self-contained OKF-compatible LLM Wiki package."""
from __future__ import annotations

import re
import sys
import urllib.parse
from pathlib import Path


RESERVED = {"index.md", "log.md"}
FRONTMATTER_RE = re.compile(r"^---\s*\n(?P<yaml>.*?)\n---\s*\n", re.S)
LINK_RE = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")


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

        if path.name not in RESERVED:
            match = FRONTMATTER_RE.match(text)
            if not match:
                errors.append(f"{path.relative_to(root)}: missing YAML frontmatter")
            else:
                yaml_text = match.group("yaml")
                type_match = re.search(r"^type:\s*(.+?)\s*$", yaml_text, re.M)
                if not type_match or not type_match.group(1).strip():
                    errors.append(f"{path.relative_to(root)}: missing non-empty type")

        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or is_external(target):
                continue
            target = urllib.parse.unquote(target)
            dest = (root / target.lstrip("/")) if target.startswith("/") else (path.parent / target)
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
            dest = (root / target.lstrip("/")) if target.startswith("/") else (src.parent / target)
            if raw_target.endswith("/") or target.endswith("/"):
                dest = dest / "index.md"
            if dest.exists():
                rel = dest.resolve().relative_to(root.resolve()).as_posix()
                inbound.setdefault(rel, set()).add(src.relative_to(root).as_posix())
    return inbound


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
        if not referrers:
            warns.append(f"[orphan] {rel}: no other page links to it — add a link from the relevant index or concept page")

    # 2. Glossary presence.
    glossary = root / "glossary" / "terms.md"
    if not glossary.exists():
        warns.append("[glossary] glossary/terms.md missing — add key terms for agent lookups")
    elif glossary.exists():
        text = glossary.read_text(encoding="utf-8", errors="ignore")
        # count bold term entries
        term_count = len(re.findall(r"^- \*\*", text, re.MULTILINE))
        if term_count == 0:
            warns.append("[glossary] glossary/terms.md is empty — add key terms")

    # 3. Zero-inbound concept/chapter pages (core-thesis reachability hint).
    for rel, referrers in sorted(inbound.items()):
        if rel.startswith(("concepts/", "frameworks/", "claims/")) and not referrers:
            # already reported as orphan; skip duplicate
            continue
    return warns


def main() -> int:
    args = sys.argv[1:]
    strict = "--strict" in args
    # strip flags to find the root path argument
    positional = [a for a in args if not a.startswith("--")]
    root = Path(positional[0]) if positional else Path(".")
    code = validate(root.resolve())
    if strict and code == 0:
        strict_warns = strict_checks(root.resolve())
        if strict_warns:
            print("\nOKF wiki strict-mode notes (advisory, do not affect pass/fail):")
            for w in strict_warns:
                print(f"- {w}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
