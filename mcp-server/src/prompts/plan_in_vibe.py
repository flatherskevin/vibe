"""MCP prompt registration for the plan_in_vibe prompt.

Provides a system prompt with VIBE v1 .vibe.md format specification,
section types, and an example document.
"""

import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


_VIBE_V1_FORMAT_SPEC = """\
# VIBE v1 Format Reference

VIBE v1 is a structured markdown document format for AI-driven planning.
Every .vibe.md file has two parts:

1. **YAML frontmatter** (between `---` delimiters) containing `vibe`, `meta`, and `imports`
2. **Markdown body** containing `## Context`, `## Artifacts`, `## Sections`, `## Decisions`, `## Quality`

## Frontmatter (YAML between --- delimiters)

### Required
- `vibe: "1.0"` -- Version declaration (quoted to avoid numeric coercion)

### Optional
- `meta` -- Document metadata:
  - name (string): Document identifier
  - description (string): Human-readable purpose
  - session_id (string): Links to MCP session ({YYYY-MM-DD}-{6-char-hex})
  - created_at, updated_at (string): ISO timestamps
  - author (string): Author identifier (claude, human, agent-id)
  - tags (array of strings): Freeform categorization
  - status (enum): draft | review | final
- `imports` -- Array of .vibe.md file paths to import and merge

## Markdown Body

### ## Context
Each `### Heading` becomes a context key (slugified: lowercase, spaces to underscores).
Freeform keys supported. Common keys: problem, constraints, assumptions, scope, glossary.

### ## Artifacts
Markdown table with columns: Path (required), Kind, Description, Status, Depends On, Acceptance Criteria.
Arrays in cells use semicolons as delimiters.

### ## Sections
Each `### Heading` is a section. HTML comment immediately after heading carries metadata:
`<!-- id: section_id, type: analysis, depends_on: other_id -->`
Types: analysis | design | decision | specification | risk | checklist

### ## Decisions
Each `### Heading` is a decision title. HTML comment: `<!-- id: dec_id, status: accepted -->`
Body uses bold-label patterns:
- **Context:** Why this decision is needed
- **Options:** List of `- **name**: description`
- **Chosen:** Name of chosen option
- **Rationale:** Why chosen
- **Consequences:** Bullet list

### ## Quality
Markdown table with columns: ID (required), Description (required), Type, Criteria.
"""

_SECTION_TYPES = """\
## Section Types

| Type | Purpose |
|------|---------|
| analysis | Examine the problem space, current state, stakeholders |
| design | Describe the proposed solution, architecture, patterns |
| decision | Record a specific decision with context and rationale |
| specification | Define interfaces, contracts, schemas, formats |
| risk | Identify risks, impacts, mitigations |
| checklist | Ordered list of tasks or verification steps |
"""

_EXAMPLE_DOCUMENT = """\
## Example VIBE v1 Document

```markdown
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
- Must support token refresh

### Assumptions

- PostgreSQL is available for user storage
- Redis is available for token blacklisting

## Artifacts

| Path | Kind | Description | Status | Depends On | Acceptance Criteria |
|------|------|-------------|--------|------------|---------------------|
| src/auth/service.py | python | Core authentication service | planned | | Implements login, logout, refresh; Uses bcrypt; Generates valid JWT |
| src/auth/middleware.py | python | Authentication middleware | planned | src/auth/service.py | Validates JWT on protected routes; Returns 401 for invalid/expired |

## Sections

### Authentication Requirements
<!-- id: problem_analysis, type: analysis -->

The API currently has no authentication. All endpoints are
publicly accessible. We need to add JWT-based auth with
user registration, login, and token refresh.

### Authentication Architecture
<!-- id: system_design, type: design, depends_on: problem_analysis -->

The auth system will consist of three components:
1. Auth service: handles credential validation and token generation
2. Auth middleware: validates tokens on incoming requests
3. Token store: Redis-backed blacklist for revoked tokens

### Implementation Tasks
<!-- id: implementation_tasks, type: checklist, depends_on: system_design -->

- [ ] Create user model and migration
- [ ] Implement auth service with bcrypt
- [ ] Implement JWT token generation
- [ ] Create auth middleware
- [ ] Add token refresh endpoint
- [ ] Write integration tests

## Decisions

### Use JWT for stateless authentication
<!-- id: dec_token_format, status: accepted -->

**Context:** Need to choose between session-based and token-based auth.

**Options:**

- **session_based**: Server-side sessions with cookies
- **jwt_based**: Stateless JWT tokens in Authorization header

**Chosen:** jwt_based

**Rationale:** JWT allows stateless verification, better suited for API-first architecture and horizontal scaling.

**Consequences:**

- Tokens cannot be individually revoked without a blacklist
- Need to manage token expiration and refresh

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_auth_works | test | Authentication flow works end-to-end | User can register, login, access protected endpoints, refresh tokens, and logout |
| q_security | review | Security best practices are followed | Passwords hashed with bcrypt, tokens have expiration, sensitive data not logged |
```
"""


def register_plan_in_vibe_prompt(mcp: FastMCP) -> None:
    """Register the plan_in_vibe prompt with the MCP server."""

    @mcp.prompt()
    async def plan_in_vibe(
        document_type: str = "implementation_plan",
        session_id: str = "",
    ) -> str:
        """Generate a system prompt for creating a VIBE v1 planning document.

        This prompt provides the complete VIBE v1 .vibe.md format specification,
        section type reference, and an example document to guide AI-driven
        plan authoring.

        Args:
            document_type: The type of document to create. One of:
                overview, architecture, implementation_plan,
                risk_assessment, adr_collection.
            session_id: Optional session ID to include in the document metadata.
        """
        session_note = ""
        if session_id:
            session_note = (
                f"\n\nInclude `session_id: {session_id}` in the meta section "
                f"of the YAML frontmatter to link this document to the active planning session.\n"
            )

        document_type_guidance = _get_document_type_guidance(document_type)

        return (
            f"You are a planning assistant that writes structured VIBE v1 documents.\n\n"
            f"Your task is to create a **{document_type}** document in VIBE v1 .vibe.md format.\n"
            f"{session_note}\n"
            f"{_VIBE_V1_FORMAT_SPEC}\n"
            f"{_SECTION_TYPES}\n"
            f"{document_type_guidance}\n"
            f"{_EXAMPLE_DOCUMENT}\n"
            f"## Instructions\n\n"
            f"1. Write as a .vibe.md file with YAML frontmatter (between --- delimiters) "
            f"containing `vibe: \"1.0\"`, `meta`, and optionally `imports`.\n"
            f"2. Fill in all relevant body sections (Context, Artifacts, Sections, Decisions, Quality) "
            f"with substantive content -- no placeholders.\n"
            f"3. Use appropriate section types in <!-- --> comments for each section.\n"
            f"4. Include quality criteria that define what 'done' looks like.\n"
            f"5. If artifacts are relevant, declare them in the Artifacts table.\n"
            f"6. If architectural decisions are involved, record them under ## Decisions.\n"
            f"7. Output the complete .vibe.md content.\n"
        )


def _get_document_type_guidance(document_type: str) -> str:
    """Return guidance specific to the requested document type."""
    guidance_map = {
        "overview": (
            "## Document Type: Overview\n\n"
            "An overview document should contain:\n"
            "- analysis section for the problem space\n"
            "- analysis section for users and stakeholders\n"
            "- design section for the proposed approach\n"
            "- risk section for key risks\n"
            "- checklist section for success criteria\n"
        ),
        "architecture": (
            "## Document Type: Architecture\n\n"
            "An architecture document should contain:\n"
            "- analysis section for current state\n"
            "- design section for proposed design\n"
            "- design section for data model\n"
            "- specification section for API design\n"
            "- risk section for technical risks\n"
            "- decisions with key architectural choices\n"
            "- artifacts table with planned components\n"
        ),
        "implementation_plan": (
            "## Document Type: Implementation Plan\n\n"
            "An implementation plan should contain:\n"
            "- analysis section for scope analysis\n"
            "- design section for implementation approach\n"
            "- specification section for artifact specifications\n"
            "- checklist section for implementation tasks\n"
            "- checklist section for verification steps\n"
            "- artifacts table with all planned files\n"
        ),
        "risk_assessment": (
            "## Document Type: Risk Assessment\n\n"
            "A risk assessment should contain:\n"
            "- analysis section for risk context\n"
            "- risk section for identified risks (with likelihood and impact)\n"
            "- risk section for mitigation strategies\n"
            "- checklist section for monitoring plan\n"
            "- decision section for risk acceptance\n"
        ),
        "adr_collection": (
            "## Document Type: ADR Collection\n\n"
            "An ADR collection should contain:\n"
            "- analysis section for background context\n"
            "- decisions with each architectural decision\n"
            "- Each decision must have context, options, chosen, rationale, "
            "and consequences\n"
        ),
    }

    return guidance_map.get(
        document_type,
        (
            f"## Document Type: {document_type}\n\n"
            f"Create a VIBE v1 document appropriate for the '{document_type}' "
            f"document type. Use section types that best fit the content.\n"
        ),
    )
