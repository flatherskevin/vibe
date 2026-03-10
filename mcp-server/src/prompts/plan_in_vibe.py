"""MCP prompt registration for the plan_in_vibe prompt.

Provides a system prompt with VIBE v2 format specification condensed,
section types, and an example document.
"""

import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


_VIBE_V2_FORMAT_SPEC = """\
# VIBE v2 Format Reference

VIBE v2 is a structured YAML document format for AI-driven planning.
Every .vibe file is valid YAML with the following top-level structure:

## Required Field
- `vibe: 2.0` -- Version declaration (must be first)

## Optional Top-Level Fields

### meta
Document metadata:
- name (string): Document identifier
- description (string): Human-readable purpose
- session_id (string): Links to MCP session ({YYYY-MM-DD}-{6-char-hex})
- created_at, updated_at (string): ISO timestamps
- author (string): Author identifier (claude, human, agent-id)
- tags (array of strings): Freeform categorization
- status (enum): draft | review | final

### imports
Array of .vibe file paths to import and merge.

### context
Problem statement and background:
- problem (string): What problem is being solved
- constraints (string): Boundaries and limitations
- assumptions (string): Assumptions underlying the plan
- scope (string): What is and is not covered
- glossary (string): Term definitions
- Additional freeform keys allowed

### artifacts
Array of artifact declarations:
- path (string): File or directory path
- kind (string): Artifact type (python, typescript, markdown, yaml, etc.)
- description (string): What this artifact is for
- depends_on (array): Artifact paths this depends on
- acceptance_criteria (array): Conditions for completion
- status (enum): planned | in_progress | complete

### sections
Ordered list of document sections:
- id (string, required): Unique section identifier
- type (enum): analysis | design | decision | specification | risk | checklist
- title (string, required): Human-readable heading
- content (string): Section body (multiline YAML string)
- depends_on (array): Section IDs this builds on

### decisions
Architecture Decision Records:
- id (string, required): Unique decision identifier
- title (string, required): One-line summary
- status (enum): proposed | accepted | deprecated | superseded
- context (string): Why this decision is needed
- options (array): Alternatives considered (name + description)
- chosen (string): Name of chosen option
- rationale (string): Why chosen
- consequences (array): What follows from this choice

### quality
Quality criteria defining done:
- id (string, required): Unique criterion identifier
- type (enum): review | test | metric | checklist
- description (string, required): What is being checked
- criteria (string): How to determine pass/fail
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
## Example VIBE v2 Document

```yaml
vibe: 2.0

meta:
  name: auth_service_plan
  description: Plan for implementing JWT authentication service
  author: claude
  tags:
    - authentication
    - backend
  status: draft

context:
  problem: |
    The application needs a stateless authentication system
    using JWT tokens for API access control.

  constraints: |
    - Must use bcrypt for password hashing
    - Tokens must expire after 24 hours
    - Must support token refresh

  assumptions: |
    - PostgreSQL is available for user storage
    - Redis is available for token blacklisting

artifacts:
  - path: src/auth/service.py
    kind: python
    description: Core authentication service
    status: planned
    acceptance_criteria:
      - Implements login, logout, refresh endpoints
      - Uses bcrypt for password hashing
      - Generates valid JWT tokens

  - path: src/auth/middleware.py
    kind: python
    description: Authentication middleware
    depends_on:
      - src/auth/service.py
    status: planned
    acceptance_criteria:
      - Validates JWT tokens on protected routes
      - Returns 401 for invalid/expired tokens

sections:
  - id: problem_analysis
    type: analysis
    title: Authentication Requirements
    content: |
      The API currently has no authentication. All endpoints are
      publicly accessible. We need to add JWT-based auth with
      user registration, login, and token refresh.

  - id: system_design
    type: design
    title: Authentication Architecture
    depends_on:
      - problem_analysis
    content: |
      The auth system will consist of three components:
      1. Auth service: handles credential validation and token generation
      2. Auth middleware: validates tokens on incoming requests
      3. Token store: Redis-backed blacklist for revoked tokens

  - id: implementation_tasks
    type: checklist
    title: Implementation Tasks
    depends_on:
      - system_design
    content: |
      - [ ] Create user model and migration
      - [ ] Implement auth service with bcrypt
      - [ ] Implement JWT token generation
      - [ ] Create auth middleware
      - [ ] Add token refresh endpoint
      - [ ] Write integration tests

decisions:
  - id: dec_token_format
    title: Use JWT for stateless authentication
    status: accepted
    context: |
      Need to choose between session-based and token-based auth.
    options:
      - name: session_based
        description: Server-side sessions with cookies
      - name: jwt_based
        description: Stateless JWT tokens in Authorization header
    chosen: jwt_based
    rationale: |
      JWT allows stateless verification, better suited for API-first
      architecture and horizontal scaling.
    consequences:
      - Tokens cannot be individually revoked without a blacklist
      - Need to manage token expiration and refresh

quality:
  - id: q_auth_works
    type: test
    description: Authentication flow works end-to-end
    criteria: |
      User can register, login, access protected endpoints,
      refresh tokens, and logout successfully.

  - id: q_security
    type: review
    description: Security best practices are followed
    criteria: |
      Passwords are hashed with bcrypt, tokens have expiration,
      sensitive data is not logged.
```
"""


def register_plan_in_vibe_prompt(mcp: FastMCP) -> None:
    """Register the plan_in_vibe prompt with the MCP server."""

    @mcp.prompt()
    async def plan_in_vibe(
        document_type: str = "implementation_plan",
        session_id: str = "",
    ) -> str:
        """Generate a system prompt for creating a VIBE v2 planning document.

        This prompt provides the complete VIBE v2 format specification,
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
                f"to link this document to the active planning session.\n"
            )

        document_type_guidance = _get_document_type_guidance(document_type)

        return (
            f"You are a planning assistant that writes structured VIBE v2 documents.\n\n"
            f"Your task is to create a **{document_type}** document in VIBE v2 format.\n"
            f"{session_note}\n"
            f"{_VIBE_V2_FORMAT_SPEC}\n"
            f"{_SECTION_TYPES}\n"
            f"{document_type_guidance}\n"
            f"{_EXAMPLE_DOCUMENT}\n"
            f"## Instructions\n\n"
            f"1. Write the document as valid YAML with `vibe: 2.0` at the top.\n"
            f"2. Fill in all relevant sections with substantive content -- no placeholders.\n"
            f"3. Use appropriate section types for each section.\n"
            f"4. Include quality criteria that define what 'done' looks like.\n"
            f"5. If artifacts are relevant, declare them with acceptance criteria.\n"
            f"6. If architectural decisions are involved, record them in the decisions array.\n"
            f"7. Output only the YAML content, no surrounding markdown fences.\n"
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
            "- decisions array with key architectural choices\n"
            "- artifacts array with planned components\n"
        ),
        "implementation_plan": (
            "## Document Type: Implementation Plan\n\n"
            "An implementation plan should contain:\n"
            "- analysis section for scope analysis\n"
            "- design section for implementation approach\n"
            "- specification section for artifact specifications\n"
            "- checklist section for implementation tasks\n"
            "- checklist section for verification steps\n"
            "- artifacts array with all planned files\n"
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
            "- decisions array with each architectural decision\n"
            "- Each decision must have context, options, chosen, rationale, "
            "and consequences\n"
        ),
    }

    return guidance_map.get(
        document_type,
        (
            f"## Document Type: {document_type}\n\n"
            f"Create a VIBE v2 document appropriate for the '{document_type}' "
            f"document type. Use section types that best fit the content.\n"
        ),
    )
