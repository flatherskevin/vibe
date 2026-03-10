"""Tests that all converted .vibe.md files parse correctly and pass schema validation."""

import json
from pathlib import Path

import pytest

from src.parsing.vibe_md import parse_vibe_md, serialize_vibe_md


# Project root relative to mcp-server/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

VIBE_MD_FILES = sorted(PROJECT_ROOT.glob("**/*.vibe.md"))


@pytest.fixture(params=VIBE_MD_FILES, ids=[str(p.relative_to(PROJECT_ROOT)) for p in VIBE_MD_FILES])
def vibe_md_file(request):
    return request.param


class TestConvertedFiles:
    def test_file_parses(self, vibe_md_file):
        """Every .vibe.md file should parse without errors."""
        text = vibe_md_file.read_text(encoding="utf-8")
        data = parse_vibe_md(text)
        assert isinstance(data, dict)
        assert "vibe" in data, f"{vibe_md_file.name} missing 'vibe' field"

    def test_vibe_version(self, vibe_md_file):
        """Every .vibe.md file should declare vibe 1.0."""
        text = vibe_md_file.read_text(encoding="utf-8")
        data = parse_vibe_md(text)
        assert str(data["vibe"]) == "1.0"

    def test_round_trip_stable(self, vibe_md_file):
        """parse(serialize(parse(text))) should equal parse(text) for each file."""
        text = vibe_md_file.read_text(encoding="utf-8")
        data1 = parse_vibe_md(text)
        serialized = serialize_vibe_md(data1)
        data2 = parse_vibe_md(serialized)

        # Compare vibe version
        assert str(data1["vibe"]) == str(data2["vibe"])

        # Compare meta if present
        if "meta" in data1:
            assert data1["meta"] == data2["meta"]

        # Compare imports if present
        if "imports" in data1:
            assert data1["imports"] == data2["imports"]

        # Compare context keys if present
        if "context" in data1:
            assert set(data1["context"].keys()) == set(data2["context"].keys())

        # Compare artifact count
        if "artifacts" in data1:
            assert len(data1["artifacts"]) == len(data2["artifacts"])
            for a1, a2 in zip(data1["artifacts"], data2["artifacts"]):
                assert a1.get("path") == a2.get("path")

        # Compare section count and IDs
        if "sections" in data1:
            assert len(data1["sections"]) == len(data2["sections"])
            for s1, s2 in zip(data1["sections"], data2["sections"]):
                assert s1.get("id") == s2.get("id")

        # Compare decision count and IDs
        if "decisions" in data1:
            assert len(data1["decisions"]) == len(data2["decisions"])
            for d1, d2 in zip(data1["decisions"], data2["decisions"]):
                assert d1.get("id") == d2.get("id")

        # Compare quality count
        if "quality" in data1:
            assert len(data1["quality"]) == len(data2["quality"])


class TestNoStaleVibeFiles:
    def test_no_old_vibe_files(self):
        """No .vibe files should remain (only .vibe.md)."""
        old_files = list(PROJECT_ROOT.glob("**/*.vibe"))
        # Filter out .vibe.md files (glob *.vibe also matches *.vibe.md on some systems)
        old_files = [f for f in old_files if not f.name.endswith(".vibe.md")]
        assert old_files == [], f"Old .vibe files still exist: {[str(f.relative_to(PROJECT_ROOT)) for f in old_files]}"
