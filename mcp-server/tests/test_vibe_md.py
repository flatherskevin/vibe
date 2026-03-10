"""Tests for the .vibe.md parser and serializer."""

import pytest

from src.parsing.vibe_md import parse_vibe_md, serialize_vibe_md


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CANONICAL_EXAMPLE = """\
---
vibe: "1.0"
meta:
  name: auth_service_plan
  description: Plan for implementing JWT authentication service
  author: claude
  tags: [authentication, backend]
  status: draft
imports:
  - vibe/stdlib/quality.vibe.md
---

## Context

### Problem

The application needs a stateless authentication system
using JWT tokens for API access control.

### Constraints

- Must use bcrypt for password hashing
- Tokens must expire after 24 hours

### Assumptions

- PostgreSQL is available for user storage

## Artifacts

| Path | Kind | Description | Status | Depends On | Acceptance Criteria |
|------|------|-------------|--------|------------|---------------------|
| src/auth/service.py | python | Core auth service | planned | | Implements login, logout, refresh; Uses bcrypt |
| src/auth/middleware.py | python | Auth middleware | planned | src/auth/service.py | Validates JWT on protected routes |

## Sections

### Authentication Requirements
<!-- id: problem_analysis, type: analysis -->

The API currently has no authentication. All endpoints are publicly accessible.

### Authentication Architecture
<!-- id: system_design, type: design, depends_on: problem_analysis -->

The auth system has three components:
1. Auth service
2. Auth middleware
3. Token store

### Implementation Tasks
<!-- id: implementation_tasks, type: checklist, depends_on: system_design -->

- [ ] Create user model and migration
- [ ] Implement auth service with bcrypt

## Decisions

### Use JWT for stateless authentication
<!-- id: dec_token_format, status: accepted -->

**Context:** Need to choose between session-based and token-based auth.

**Options:**

- **session_based**: Server-side sessions with cookies
- **jwt_based**: Stateless JWT tokens in Authorization header

**Chosen:** jwt_based

**Rationale:** JWT allows stateless verification, better suited for API-first architecture.

**Consequences:**

- Tokens cannot be individually revoked without a blacklist
- Need to manage token expiration and refresh

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_auth_works | test | Auth flow works end-to-end | User can register, login, access protected endpoints |
| q_security | review | Security best practices followed | Passwords hashed with bcrypt, tokens have expiration |
"""


MINIMAL_EXAMPLE = """\
---
vibe: "1.0"
---
"""


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

class TestFrontmatterParsing:
    def test_parses_vibe_version(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        assert data["vibe"] == "1.0"

    def test_parses_meta(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        assert data["meta"]["name"] == "auth_service_plan"
        assert data["meta"]["author"] == "claude"
        assert data["meta"]["status"] == "draft"
        assert data["meta"]["tags"] == ["authentication", "backend"]

    def test_parses_imports(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        assert data["imports"] == ["vibe/stdlib/quality.vibe.md"]

    def test_minimal_document(self):
        data = parse_vibe_md(MINIMAL_EXAMPLE)
        assert data["vibe"] == "1.0"
        assert "meta" not in data
        assert "context" not in data

    def test_no_frontmatter(self):
        data = parse_vibe_md("# Just markdown\n\nNo frontmatter here.")
        assert "vibe" not in data

    def test_vibe_as_number(self):
        """vibe: 1.0 without quotes parses as float -- parser handles both."""
        text = "---\nvibe: 1.0\n---\n"
        data = parse_vibe_md(text)
        assert data["vibe"] == 1.0


# ---------------------------------------------------------------------------
# Context parsing
# ---------------------------------------------------------------------------

class TestContextParsing:
    def test_parses_context_subheadings(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        ctx = data["context"]
        assert "problem" in ctx
        assert "constraints" in ctx
        assert "assumptions" in ctx

    def test_slugifies_heading(self):
        text = """\
---
vibe: "1.0"
---

## Context

### My Custom Key

Some content here.
"""
        data = parse_vibe_md(text)
        assert "my_custom_key" in data["context"]

    def test_context_content_preserved(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        assert "stateless authentication" in data["context"]["problem"]


# ---------------------------------------------------------------------------
# Artifacts table parsing
# ---------------------------------------------------------------------------

class TestArtifactsParsing:
    def test_parses_artifact_rows(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        arts = data["artifacts"]
        assert len(arts) == 2

    def test_artifact_fields(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        a = data["artifacts"][0]
        assert a["path"] == "src/auth/service.py"
        assert a["kind"] == "python"
        assert a["status"] == "planned"

    def test_semicolon_delimited_arrays(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        a0 = data["artifacts"][0]
        assert isinstance(a0["acceptance_criteria"], list)
        assert len(a0["acceptance_criteria"]) == 2

    def test_depends_on_array(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        a1 = data["artifacts"][1]
        assert a1["depends_on"] == ["src/auth/service.py"]

    def test_empty_depends_on_omitted(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        a0 = data["artifacts"][0]
        assert "depends_on" not in a0

    def test_escaped_pipes(self):
        text = """\
---
vibe: "1.0"
---

## Artifacts

| Path | Description |
|------|-------------|
| test.py | Has a \\| pipe in description |
"""
        data = parse_vibe_md(text)
        assert "| pipe" in data["artifacts"][0]["description"]


# ---------------------------------------------------------------------------
# Sections parsing
# ---------------------------------------------------------------------------

class TestSectionsParsing:
    def test_parses_sections(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        assert len(data["sections"]) == 3

    def test_section_id_and_type(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        s0 = data["sections"][0]
        assert s0["id"] == "problem_analysis"
        assert s0["type"] == "analysis"
        assert s0["title"] == "Authentication Requirements"

    def test_section_depends_on(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        s1 = data["sections"][1]
        assert s1["depends_on"] == ["problem_analysis"]

    def test_section_content(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        s0 = data["sections"][0]
        assert "no authentication" in s0["content"]


# ---------------------------------------------------------------------------
# Decisions parsing
# ---------------------------------------------------------------------------

class TestDecisionsParsing:
    def test_parses_decisions(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        assert len(data["decisions"]) == 1

    def test_decision_metadata(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        d = data["decisions"][0]
        assert d["id"] == "dec_token_format"
        assert d["status"] == "accepted"
        assert d["title"] == "Use JWT for stateless authentication"

    def test_decision_context(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        d = data["decisions"][0]
        assert "session-based" in d["context"]

    def test_decision_options(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        d = data["decisions"][0]
        assert len(d["options"]) == 2
        assert d["options"][0]["name"] == "session_based"
        assert d["options"][1]["name"] == "jwt_based"

    def test_decision_chosen_and_rationale(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        d = data["decisions"][0]
        assert d["chosen"] == "jwt_based"
        assert "stateless" in d["rationale"]

    def test_decision_consequences(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        d = data["decisions"][0]
        assert len(d["consequences"]) == 2


# ---------------------------------------------------------------------------
# Quality table parsing
# ---------------------------------------------------------------------------

class TestQualityParsing:
    def test_parses_quality(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        assert len(data["quality"]) == 2

    def test_quality_fields(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        q0 = data["quality"][0]
        assert q0["id"] == "q_auth_works"
        assert q0["type"] == "test"
        assert "end-to-end" in q0["description"]


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_serialize_produces_frontmatter(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        output = serialize_vibe_md(data)
        assert output.startswith("---\n")
        assert '\nvibe: "1.0"\n' in output

    def test_serialize_produces_body_sections(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        output = serialize_vibe_md(data)
        assert "## Context" in output
        assert "## Artifacts" in output
        assert "## Sections" in output
        assert "## Decisions" in output
        assert "## Quality" in output

    def test_serialize_context_headings(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        output = serialize_vibe_md(data)
        assert "### Problem" in output
        assert "### Constraints" in output

    def test_serialize_section_comments(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        output = serialize_vibe_md(data)
        assert "<!-- id: problem_analysis, type: analysis -->" in output

    def test_serialize_decision_bold_labels(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        output = serialize_vibe_md(data)
        assert "**Context:**" in output
        assert "**Chosen:**" in output
        assert "**Rationale:**" in output

    def test_serialize_artifacts_table(self):
        data = parse_vibe_md(CANONICAL_EXAMPLE)
        output = serialize_vibe_md(data)
        assert "| Path |" in output
        assert "src/auth/service.py" in output


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_parse_serialize_parse_stable(self):
        """parse(serialize(parse(text))) == parse(text)"""
        data1 = parse_vibe_md(CANONICAL_EXAMPLE)
        serialized = serialize_vibe_md(data1)
        data2 = parse_vibe_md(serialized)

        # Compare key fields
        assert data1["vibe"] == data2["vibe"]
        assert data1["meta"] == data2["meta"]
        assert data1["imports"] == data2["imports"]
        assert data1["context"] == data2["context"]
        assert len(data1["artifacts"]) == len(data2["artifacts"])
        assert len(data1["sections"]) == len(data2["sections"])
        assert len(data1["decisions"]) == len(data2["decisions"])
        assert len(data1["quality"]) == len(data2["quality"])

        # Check artifact paths preserved
        for a1, a2 in zip(data1["artifacts"], data2["artifacts"]):
            assert a1["path"] == a2["path"]

        # Check section IDs preserved
        for s1, s2 in zip(data1["sections"], data2["sections"]):
            assert s1["id"] == s2["id"]
            assert s1.get("type") == s2.get("type")

        # Check decision IDs preserved
        for d1, d2 in zip(data1["decisions"], data2["decisions"]):
            assert d1["id"] == d2["id"]
            assert d1.get("status") == d2.get("status")
            assert d1.get("chosen") == d2.get("chosen")

    def test_minimal_round_trip(self):
        data1 = parse_vibe_md(MINIMAL_EXAMPLE)
        serialized = serialize_vibe_md(data1)
        data2 = parse_vibe_md(serialized)
        assert data1["vibe"] == data2["vibe"]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_sections(self):
        text = """\
---
vibe: "1.0"
---

## Context

## Sections

## Quality
"""
        data = parse_vibe_md(text)
        assert data["vibe"] == "1.0"
        # Empty sections should result in empty lists/dicts
        assert data.get("sections", []) == []
        assert data.get("quality", []) == []

    def test_missing_optional_fields(self):
        text = """\
---
vibe: "1.0"
---

## Context

### Problem

Just a problem statement.
"""
        data = parse_vibe_md(text)
        assert data["context"]["problem"] == "Just a problem statement."
        assert "artifacts" not in data
        assert "decisions" not in data

    def test_table_with_missing_columns(self):
        text = """\
---
vibe: "1.0"
---

## Artifacts

| Path | Description |
|------|-------------|
| test.py | A test file |
"""
        data = parse_vibe_md(text)
        assert len(data["artifacts"]) == 1
        assert data["artifacts"][0]["path"] == "test.py"
        assert "kind" not in data["artifacts"][0]

    def test_section_without_comment(self):
        text = """\
---
vibe: "1.0"
---

## Sections

### Untitled Section

Some content without an HTML comment.
"""
        data = parse_vibe_md(text)
        assert len(data["sections"]) == 1
        assert data["sections"][0]["title"] == "Untitled Section"
        assert "id" not in data["sections"][0]
