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


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    return validate(root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
