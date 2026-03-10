# VIBE

**VIBE is a structured document format for AI-driven planning.**

A `.vibe` file is a YAML document that captures what problem is being solved, what will be built, how decisions were made, and what "done" looks like. VIBE documents are the output of AI planning -- consumed by humans reviewing plans, other AI agents continuing work, and execution tools that need structured instructions.

---

## What VIBE Does

VIBE provides a structured medium for planning:

```
AI system plans
    ↓
.vibe document (write)
    ↓
Schema validation (validate)
    ↓
Human/AI review (review)
    ↓
Imported by other plans (import)
```

Instead of ad-hoc markdown, AI systems produce `.vibe` documents with typed sections, explicit decisions, and measurable quality criteria.

---

## Document Structure

Every `.vibe` file starts with a version declaration and uses these top-level fields:

| Field | Description |
|---|---|
| `vibe` | Version identifier (required, `2.0`) |
| `meta` | Document metadata: name, author, status, tags |
| `imports` | List of `.vibe` files to import and merge |
| `context` | Problem statement, constraints, assumptions, scope |
| `artifacts` | File declarations with acceptance criteria |
| `sections` | Typed content blocks (analysis, design, specification, risk, checklist, decision) |
| `decisions` | Architecture Decision Records with options and rationale |
| `quality` | Criteria that define "done" |

---

## Example

```yaml
vibe: 2.0

meta:
  name: auth_redesign
  description: Plan the JWT authentication redesign
  author: claude
  tags:
    - auth
    - backend
  status: draft

imports:
  - vibe/stdlib/quality.vibe

context:
  problem: |
    The current session-based auth doesn't support mobile clients.
  constraints: |
    - Must be backward compatible with existing web sessions.
    - Must support token refresh without re-authentication.

artifacts:
  - path: src/auth/jwt_service.py
    kind: python
    description: JWT token issuance and validation
    status: planned
    acceptance_criteria:
      - Issues access tokens with 15-minute expiry
      - Validates tokens against signing key

sections:
  - id: current_state
    type: analysis
    title: Current Authentication State
    content: |
      The existing system uses server-side sessions stored in Redis.
      Mobile clients cannot maintain session cookies reliably.

  - id: proposed_design
    type: design
    title: JWT Token Architecture
    content: |
      Replace session-based auth with JWT access/refresh token pair.
      Access tokens are short-lived (15 min). Refresh tokens are
      long-lived (7 days) and stored in HttpOnly cookies.

decisions:
  - id: dec_token_storage
    title: Store refresh tokens in HttpOnly cookies
    status: proposed
    context: |
      Refresh tokens need secure client-side storage.
    options:
      - name: local_storage
        description: Store in localStorage (XSS vulnerable)
      - name: httponly_cookie
        description: Store in HttpOnly cookie (CSRF requires mitigation)
    chosen: httponly_cookie
    rationale: |
      HttpOnly cookies are not accessible to JavaScript, preventing
      XSS-based token theft. CSRF is mitigated with SameSite=Strict.
    consequences:
      - Requires CSRF mitigation for cookie-based endpoints
      - Mobile clients use Authorization header instead

quality:
  - id: q_tokens_valid
    type: test
    description: JWT tokens are correctly issued and validated
    criteria: |
      Access tokens contain user ID, expiry, and valid signature.
      Expired tokens are rejected. Invalid signatures are rejected.
```

---

## Standard Library

VIBE ships a standard library under `vibe/stdlib/`:

- **quality.vibe** -- Reusable quality criteria (import to get standard checks)
- **context_budget.vibe** -- Context budgeting guidance for AI planning sessions
- **templates/** -- Document templates for common planning patterns:
  - `overview.vibe` -- Project overview
  - `architecture.vibe` -- Technical architecture
  - `implementation_plan.vibe` -- Implementation planning
  - `risk_assessment.vibe` -- Risk analysis
  - `adr_collection.vibe` -- Architecture Decision Records

---

## MCP Server

VIBE includes a local MCP server for AI tool integration. The server provides:

- **Tools**: Create sessions, write/read plans, manage sessions
- **Prompts**: System prompt that teaches AI the .vibe format
- **Resources**: Spec documents and templates as readable content

Setup:

```bash
cd mcp-server
docker compose up
```

See `vibe/spec/VIBE_MCP_SERVER.md` for the full specification.

---

## Key Concepts

- **Sections** -- Typed content blocks: `analysis`, `design`, `specification`, `decision`, `risk`, `checklist`
- **Decisions** -- First-class Architecture Decision Records with options, rationale, and consequences
- **Quality** -- Criteria that define "done": `review`, `test`, `metric`, `checklist`
- **Imports** -- Compose documents by importing and merging `.vibe` files
- **Sessions** -- Group related planning documents via the MCP server

---

## Specification Documents

The full specification lives under `vibe/spec/`:

**Normative:**
- `VIBE_SPEC_v2.md` -- Core format specification
- `VIBE_CONSUMER_CONTRACT.md` -- Consumer requirements
- `VIBE_MERGE_SEMANTICS.md` -- Import and merge rules
- `VIBE_ERRORS.md` -- Error taxonomy

**Informative:**
- `VIBE_DOCUMENT_TYPES.md` -- Section types and archetypes
- `VIBE_DEPENDENCIES.md` -- Artifact and section dependencies
- `VIBE_AUTHORING_GUIDE.md` -- How to write .vibe documents
- `VIBE_REFERENCE_DOCUMENT.md` -- Canonical example document
- `VIBE_INTEGRATION_HOOKS.md` -- External tool integration
- `VIBE_MULTI_AUTHOR.md` -- Multi-author collaboration
- `VIBE_MCP_SERVER.md` -- MCP server specification

---

## Repository Structure

```
project.vibe                          # Root document
vibe/
  stdlib/                             # Standard library
    quality.vibe
    context_budget.vibe
    templates/
      overview.vibe
      architecture.vibe
      implementation_plan.vibe
      risk_assessment.vibe
      adr_collection.vibe
  spec/                               # Specification documents
    VIBE_SPEC_v2.md
    VIBE_CONSUMER_CONTRACT.md
    VIBE_MERGE_SEMANTICS.md
    ...
  schema/                             # JSON Schema
    vibe.schema.json
  templates/                          # Project templates
    new_project.vibe
mcp-server/                           # MCP server
  Dockerfile
  docker-compose.yml
  src/
syntaxes/                             # Editor support
  vibe.tmLanguage.json
```

---

## Status

VIBE v2 specification. The format is designed for AI-driven planning with structured sections, explicit decisions, and measurable quality criteria.

---

## License

MIT
