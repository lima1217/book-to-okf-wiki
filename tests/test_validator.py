"""
Tests for validate_okf_wiki.py — shape validation + advisory --strict mode.

The shape validator (default mode) gates pass/fail. The --strict mode adds
advisory notes (orphan pages, missing glossary) that must NEVER change the
exit code.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

# Load the validator module from a file path (it's not on a package).
_VALIDATOR_PATH = (
    Path(__file__).resolve().parent.parent / "tools" / "validate_okf_wiki.py"
)
_spec = importlib.util.spec_from_file_location("validate_okf_wiki", _VALIDATOR_PATH)
validate_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_mod)


# ---------------------------------------------------------------------------
# Helpers: build a minimal valid package skeleton in tmp_path.
# ---------------------------------------------------------------------------

def _write_valid_skeleton(root: Path) -> None:
    """Write the minimum files for shape validation to pass."""
    (root / "index.md").write_text("# Root index\n")
    # AGENTS.md is non-reserved, so it needs frontmatter + a non-empty type.
    (root / "AGENTS.md").write_text(
        "---\ntype: AgentGuide\ntitle: Agents\n---\n# Agents\n"
    )
    (root / "log.md").write_text("# Log\n")


def _write_content_page(path: Path, title: str = "Concept", body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"type: Concept\n"
        f"title: {title}\n"
        "---\n"
        f"# {title}\n\n{body}\n"
    )


# ---------------------------------------------------------------------------
# Default mode is unchanged: shape errors fail, no --strict notes appear.
# ---------------------------------------------------------------------------

class TestDefaultModeUnchanged:
    def test_clean_package_passes(self, tmp_path):
        _write_valid_skeleton(tmp_path)
        assert validate_mod.validate(tmp_path) == 0

    def test_missing_agents_fails(self, tmp_path):
        (tmp_path / "index.md").write_text("# idx")
        (tmp_path / "log.md").write_text("# log")
        # AGENTS.md absent
        assert validate_mod.validate(tmp_path) == 1

    def test_missing_frontmatter_fails(self, tmp_path):
        _write_valid_skeleton(tmp_path)
        (tmp_path / "concepts").mkdir()
        (tmp_path / "concepts" / "x.md").write_text("# no frontmatter\n")
        assert validate_mod.validate(tmp_path) == 1


# ---------------------------------------------------------------------------
# --strict mode: advisory notes printed, exit code unchanged.
# ---------------------------------------------------------------------------

class TestStrictOrphan:
    def test_strict_detects_orphan(self, tmp_path):
        _write_valid_skeleton(tmp_path)
        # an orphan content page nothing links to
        _write_content_page(tmp_path / "concepts" / "lone.md", "Lone")
        warns = validate_mod.strict_checks(tmp_path)
        joined = "\n".join(warns)
        assert any("concepts/lone.md" in w and "orphan" in w for w in warns), joined

    def test_strict_no_orphan_when_linked(self, tmp_path):
        _write_valid_skeleton(tmp_path)
        # concept page linked from the root index
        _write_content_page(tmp_path / "concepts" / "linked.md", "Linked")
        (tmp_path / "index.md").write_text(
            "# Root\n\n- [Linked](concepts/linked.md)\n"
        )
        warns = validate_mod.strict_checks(tmp_path)
        assert not any("concepts/linked.md" in w and "orphan" in w for w in warns)


class TestStrictGlossary:
    def test_strict_warns_missing_glossary(self, tmp_path):
        _write_valid_skeleton(tmp_path)
        warns = validate_mod.strict_checks(tmp_path)
        assert any("[glossary]" in w for w in warns), warns

    def test_strict_warns_empty_glossary(self, tmp_path):
        _write_valid_skeleton(tmp_path)
        (tmp_path / "glossary").mkdir()
        (tmp_path / "glossary" / "terms.md").write_text("# Glossary\n\n(no terms yet)\n")
        warns = validate_mod.strict_checks(tmp_path)
        assert any("[glossary]" in w for w in warns), warns

    def test_strict_quiet_when_glossary_populated(self, tmp_path):
        _write_valid_skeleton(tmp_path)
        (tmp_path / "glossary").mkdir()
        (tmp_path / "glossary" / "terms.md").write_text(
            "# Glossary\n\n- **Term** — def\n"
        )
        # link the glossary from index so it isn't reported as an orphan
        (tmp_path / "index.md").write_text(
            "# Root\n\n- [Terms](glossary/terms.md)\n"
        )
        warns = validate_mod.strict_checks(tmp_path)
        assert not any("[glossary]" in w for w in warns), warns


class TestStrictDoesNotAffectExitCode:
    def test_strict_mode_still_returns_zero_on_orphan(self, tmp_path, capsys, monkeypatch):
        _write_valid_skeleton(tmp_path)
        _write_content_page(tmp_path / "concepts" / "lone.md", "Lone")
        monkeypatch.setattr("sys.argv", ["validate_okf_wiki.py", "--strict", str(tmp_path)])
        code = validate_mod.main()
        out = capsys.readouterr().out
        assert code == 0, "strict must never fail the build"
        assert "orphan" in out.lower()
