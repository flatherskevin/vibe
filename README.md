# VIBE

**VIBE is a structured document format for AI-driven planning.**

A `.vibe.md` file is a markdown document with YAML frontmatter that captures what problem is being solved, what will be built, how decisions were made, and what "done" looks like. VIBE documents are the output of AI planning -- consumed by humans reviewing plans, other AI agents continuing work, and execution tools that need structured instructions.

---

## What VIBE Does

VIBE provides a structured medium for planning:

```
AI system plans
    ↓
.vibe.md document (write)
    ↓
Schema validation (validate)
    ↓
Human/AI review (review)
    ↓
Imported by other plans (import)
```

Instead of ad-hoc markdown, AI systems produce `.vibe.md` documents with typed sections, explicit decisions, and measurable quality criteria.

---

## Document Structure

Every `.vibe.md` file has two parts:

1. **YAML frontmatter** (between `---` delimiters) — `vibe`, `meta`, `imports`
2. **Markdown body** — `## Context`, `## Artifacts`, `## Sections`, `## Decisions`, `## Quality`

| Part | Field | Description |
|------|-------|-------------|
| Frontmatter | `vibe` | Version identifier (required, `"2.0"`) |
| Frontmatter | `meta` | Document metadata: name, author, status, tags |
| Frontmatter | `imports` | List of `.vibe.md` files to import and merge |
| Body | `## Context` | Problem statement, constraints, assumptions (### subheadings) |
| Body | `## Artifacts` | Markdown table of file declarations with acceptance criteria |
| Body | `## Sections` | Typed content blocks with `<!-- id, type -->` metadata |
| Body | `## Decisions` | Architecture Decision Records with bold-label patterns |
| Body | `## Quality` | Markdown table of criteria that define "done" |

---

## Example

```markdown
---
vibe: "2.0"
meta:
  name: auth_redesign
  description: Plan the JWT authentication redesign
  author: claude
  tags: [auth, backend]
  status: draft
imports:
  - vibe/stdlib/quality.vibe.md
---

## Context

### Problem

The current session-based auth doesn't support mobile clients.

### Constraints

- Must be backward compatible with existing web sessions.
- Must support token refresh without re-authentication.

## Artifacts

| Path | Kind | Description | Status | Acceptance Criteria |
|------|------|-------------|--------|---------------------|
| src/auth/jwt_service.py | python | JWT token issuance and validation | planned | Issues access tokens with 15-minute expiry; Validates tokens against signing key |

## Sections

### Current Authentication State
<!-- id: current_state, type: analysis -->

The existing system uses server-side sessions stored in Redis.
Mobile clients cannot maintain session cookies reliably.

### JWT Token Architecture
<!-- id: proposed_design, type: design -->

Replace session-based auth with JWT access/refresh token pair.
Access tokens are short-lived (15 min). Refresh tokens are
long-lived (7 days) and stored in HttpOnly cookies.

## Decisions

### Store refresh tokens in HttpOnly cookies
<!-- id: dec_token_storage, status: proposed -->

**Context:** Refresh tokens need secure client-side storage.

**Options:**

- **local_storage**: Store in localStorage (XSS vulnerable)
- **httponly_cookie**: Store in HttpOnly cookie (CSRF requires mitigation)

**Chosen:** httponly_cookie

**Rationale:** HttpOnly cookies are not accessible to JavaScript, preventing XSS-based token theft. CSRF is mitigated with SameSite=Strict.

**Consequences:**

- Requires CSRF mitigation for cookie-based endpoints
- Mobile clients use Authorization header instead

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_tokens_valid | test | JWT tokens are correctly issued and validated | Access tokens contain user ID, expiry, and valid signature. Expired tokens are rejected |
```

---

## Standard Library

VIBE ships a standard library under `vibe/stdlib/`:

- **quality.vibe.md** -- Reusable quality criteria (import to get standard checks)
- **context_budget.vibe.md** -- Context budgeting guidance for AI planning sessions
- **templates/** -- Document templates for common planning patterns:
  - `overview.vibe.md` -- Project overview
  - `architecture.vibe.md` -- Technical architecture
  - `implementation_plan.vibe.md` -- Implementation planning
  - `risk_assessment.vibe.md` -- Risk analysis
  - `adr_collection.vibe.md` -- Architecture Decision Records

---

## MCP Server

VIBE includes a local MCP server for AI tool integration. The server provides:

- **Tools**: Create sessions, write/read plans, manage sessions
- **Prompts**: System prompt that teaches AI the .vibe.md format
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
- **Imports** -- Compose documents by importing and merging `.vibe.md` files
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
- `VIBE_AUTHORING_GUIDE.md` -- How to write .vibe.md documents
- `VIBE_REFERENCE_DOCUMENT.md` -- Canonical example document
- `VIBE_INTEGRATION_HOOKS.md` -- External tool integration
- `VIBE_MULTI_AUTHOR.md` -- Multi-author collaboration
- `VIBE_MCP_SERVER.md` -- MCP server specification

---

## Repository Structure

```
project.vibe.md                       # Root document
vibe/
  stdlib/                             # Standard library
    quality.vibe.md
    context_budget.vibe.md
    templates/
      overview.vibe.md
      architecture.vibe.md
      implementation_plan.vibe.md
      risk_assessment.vibe.md
      adr_collection.vibe.md
  spec/                               # Specification documents
    VIBE_SPEC_v2.md
    VIBE_CONSUMER_CONTRACT.md
    VIBE_MERGE_SEMANTICS.md
    ...
  schema/                             # JSON Schema
    vibe.schema.json
  templates/                          # Project templates
    new_project.vibe.md
mcp-server/                           # MCP server
  Dockerfile
  docker-compose.yml
  src/
syntaxes/                             # Editor support
  vibe-md.tmLanguage.json
```

---

## Status

VIBE v2 specification. The format is designed for AI-driven planning with structured sections, explicit decisions, and measurable quality criteria.

---

## License

MIT
