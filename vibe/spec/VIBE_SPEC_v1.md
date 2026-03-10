# VIBE Specification v1

VIBE defines a **structured document format** for AI-driven planning.

A `.vibe.md` file is a markdown document with YAML frontmatter that captures what problem is being solved, what will be built or changed, how it was reasoned about, and what "done" looks like. Documents are the output of AI planning, consumed by humans reviewing plans, other AI agents continuing work, and execution tools that need structured instructions.

---

## Document Model

```
.vibe.md document
    |
Write (AI or human creates document)
    |
Validate (check against v1 schema)
    |
Review (humans or AI review sections, decisions, quality)
    |
Import (other documents can import and build on this one)
```

A `.vibe.md` document may import other `.vibe.md` documents. Imports are merged by simple field concatenation. Imported content is additive: arrays are concatenated, scalars from the importing document take precedence.

VIBE uses a document-oriented model. There is no runtime, no workflow engine, and no apply phase. Documents are the deliverable.

---

## File Format

`.vibe.md` files use markdown with YAML frontmatter syntax.

Every `.vibe.md` file must begin with a version declaration in the frontmatter:

```yaml
vibe: 1.0
```

Files must contain valid YAML frontmatter and should validate against `vibe/schema/vibe.schema.json`.

---

## Top-Level Fields

| Field | Required | Description |
|---|---|---|
| `vibe` | Yes | Version identifier. Must be `1.0`. |
| `meta` | Recommended | Document metadata: name, description, author, status, tags. |
| `imports` | No | Array of `.vibe.md` file paths to import. |
| `context` | No | Problem statement, constraints, assumptions, scope, glossary. |
| `artifacts` | No | Array of planned or tracked file artifacts. |
| `sections` | No | Array of typed content blocks (analysis, design, specification, etc.). |
| `decisions` | No | Array of Architecture Decision Records (ADRs). |
| `quality` | No | Array of quality criteria defining "done". |

---

## vibe

The version field is required at the top level of every `.vibe.md` file.

```yaml
vibe: 1.0
```

The value must be `1.0`.

---

## meta

Document metadata. Recommended for all documents.

```yaml
meta:
  name: auth_system_plan
  description: Planning document for JWT authentication system
  session_id: "2026-03-10-a1b2c3"
  created_at: "2026-03-10"
  updated_at: "2026-03-10"
  author: human
  tags:
    - authentication
    - backend
  status: draft
```

### meta fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Document identifier. Should be snake_case. |
| `description` | string | Human-readable summary of the document's purpose. |
| `session_id` | string | Planning session identifier. Format: `{YYYY-MM-DD}-{6-char-hex}`. |
| `created_at` | string | Date the document was created. |
| `updated_at` | string | Date the document was last modified. |
| `author` | string | Who created the document (e.g. `human`, `claude`, a name). |
| `tags` | [string] | Freeform tags for categorization and filtering. |
| `status` | string | Document lifecycle status. One of: `draft`, `review`, `final`. |

---

## imports

Array of `.vibe.md` file paths. Imported documents are merged into the importing document by concatenating arrays and inheriting fields not already defined.

```yaml
imports:
  - vibe/stdlib/quality.vibe.md
  - vibe/stdlib/context_budget.vibe.md
  - ./shared_context.vibe.md
```

### Import rules

- Paths are relative to the importing file's directory.
- Circular imports are errors. A document must not import itself, and no chain of imports may form a cycle.
- Imported arrays (`artifacts`, `sections`, `decisions`, `quality`) are concatenated with the importing document's arrays.
- Imported scalar fields (`meta`, `context` subfields) are used only when the importing document does not define them.
- This is a simple merge, not a compilation step.

---

## context

Freeform object providing the problem description, constraints, assumptions, scope, glossary, and any other contextual data relevant to the planning effort.

```yaml
context:
  problem: |
    Build a JWT authentication system that supports token refresh,
    role-based access control, and session revocation.

  constraints: |
    - Must use bcrypt for password hashing
    - Tokens must expire after 15 minutes
    - Refresh tokens must expire after 7 days
    - Must not store passwords in plaintext

  assumptions: |
    - PostgreSQL database is already provisioned
    - User registration flow exists
    - HTTPS is enforced at the load balancer

  scope: |
    In scope: auth endpoints, token management, middleware
    Out of scope: user registration, email verification, OAuth providers

  glossary: |
    - JWT: JSON Web Token for stateless authentication
    - RBAC: Role-Based Access Control
    - Refresh token: Long-lived token used to obtain new access tokens
```

### context fields

| Field | Type | Description |
|---|---|---|
| `problem` | string | What is being solved or planned. |
| `constraints` | string | Hard requirements that must be satisfied. |
| `assumptions` | string | Things assumed to be true. |
| `scope` | string | What is in scope and out of scope. |
| `glossary` | string | Term definitions for shared understanding. |

Additional freeform keys are allowed. The `context` object is intentionally flexible to accommodate any planning domain.

---

## artifacts

Array of planned or tracked file artifacts. Each artifact describes a file that will be created, modified, or already exists as part of the planning effort.

```yaml
artifacts:
  - path: src/auth/service.py
    kind: python
    description: Core authentication service with login, logout, refresh
    depends_on:
      - src/auth/models.py
      - src/auth/tokens.py
    acceptance_criteria: |
      - Exports authenticate(), refresh_token(), revoke_session()
      - All functions have type annotations
      - Handles token expiration gracefully
    status: planned

  - path: src/auth/models.py
    kind: python
    description: SQLAlchemy models for User, Session, RefreshToken
    status: in_progress

  - path: docs/auth_api.md
    kind: markdown
    description: API documentation for authentication endpoints
    status: complete
```

### artifact fields

| Field | Type | Required | Description |
|---|---|---|---|
| `path` | string | Yes | File path relative to the repository root. |
| `kind` | string | No | File type (e.g. `python`, `typescript`, `markdown`, `json`, `vibe`). |
| `description` | string | No | What the artifact is and what it does. |
| `depends_on` | [string] | No | Paths of artifacts this one depends on. |
| `acceptance_criteria` | string | No | Conditions that must be true for the artifact to be considered complete. |
| `status` | string | No | One of: `planned`, `in_progress`, `complete`. |

---

## sections

Array of typed content blocks. Sections are the primary way to organize planning analysis, design reasoning, specifications, risks, and checklists within a document.

```yaml
sections:
  - id: threat_model
    type: analysis
    title: Authentication Threat Model
    content: |
      Primary threats to the authentication system:

      1. Credential stuffing: Mitigated by rate limiting and account lockout.
      2. Token theft: Mitigated by short expiration and refresh rotation.
      3. Session fixation: Mitigated by generating new session IDs on login.

  - id: token_design
    type: design
    title: Token Architecture
    content: |
      Access tokens are short-lived JWTs (15 min) containing user ID and roles.
      Refresh tokens are opaque strings stored in the database with a 7-day TTL.
      Token refresh issues a new access token and rotates the refresh token.
    depends_on:
      - threat_model

  - id: api_spec
    type: specification
    title: Authentication API Endpoints
    content: |
      POST /auth/login    - Authenticate with credentials, return token pair
      POST /auth/refresh   - Exchange refresh token for new token pair
      POST /auth/logout    - Revoke current session
      GET  /auth/me        - Return current user info from token

  - id: deployment_checklist
    type: checklist
    title: Pre-Deployment Checklist
    content: |
      - [ ] All endpoints return appropriate HTTP status codes
      - [ ] Rate limiting is configured on /auth/login
      - [ ] Refresh token rotation is tested
      - [ ] Token expiration edge cases are covered
      - [ ] CORS configuration allows only expected origins
```

### section fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Unique identifier within the document. Should be snake_case. |
| `type` | string | No | One of: `analysis`, `design`, `decision`, `specification`, `risk`, `checklist`. |
| `title` | string | No | Human-readable title. |
| `content` | string | No | The section body. Freeform text, typically multi-line. |
| `depends_on` | [string] | No | IDs of sections this one depends on. |

### Section types

| Type | Purpose |
|---|---|
| `analysis` | Problem analysis, research, threat models, investigation results. |
| `design` | Architecture decisions, component design, data flow. |
| `decision` | Inline decision documentation (for simple cases; use `decisions` array for ADRs). |
| `specification` | API specs, interface contracts, data schemas. |
| `risk` | Risk identification, likelihood, mitigation strategies. |
| `checklist` | Task lists, review checklists, verification steps. |

---

## decisions

Array of Architecture Decision Records (ADRs). Decisions capture the reasoning behind significant choices made during planning.

```yaml
decisions:
  - id: token_format
    title: Use JWT for access tokens
    status: accepted
    context: |
      The system needs stateless authentication tokens that can be verified
      without a database lookup on every request.
    options:
      - name: JWT
        description: |
          Signed JSON tokens with embedded claims. Stateless verification.
          Industry standard. Risk of token size growth with many claims.
      - name: Opaque tokens
        description: |
          Random strings requiring database lookup on every request.
          Simpler but adds latency and database dependency.
      - name: Signed cookies
        description: |
          Server-signed cookies with embedded claims. Limited to browser
          clients. Not suitable for mobile or API consumers.
    chosen: JWT
    rationale: |
      JWT provides stateless verification, reducing database load. It is an
      industry standard with mature library support. Token size is manageable
      for our use case (user ID + roles).
    consequences: |
      - Tokens cannot be revoked before expiration without a blacklist
      - Token payload is visible (though signed) to clients
      - Must keep token expiration short to limit exposure window

  - id: password_hashing
    title: Use bcrypt for password hashing
    status: accepted
    context: |
      Passwords must be hashed before storage. The hashing algorithm must
      resist brute-force attacks.
    options:
      - name: bcrypt
        description: Time-tested, configurable work factor, widely supported.
      - name: argon2
        description: Newer, memory-hard, resistant to GPU attacks. Less library support.
    chosen: bcrypt
    rationale: |
      bcrypt is a hard constraint from the project requirements and has
      excellent library support across all target languages.
    consequences: |
      - Must configure work factor appropriately (minimum 12 rounds)
      - Hash verification is intentionally slow (~100ms per check)
```

### decision fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Unique identifier within the document. Should be snake_case. |
| `title` | string | No | Human-readable title of the decision. |
| `status` | string | No | One of: `proposed`, `accepted`, `deprecated`, `superseded`. |
| `context` | string | No | Why the decision is needed. |
| `options` | [object] | No | Array of options considered. Each has `name` (string) and `description` (string). |
| `chosen` | string | No | The name of the chosen option. Must match one of the option names. |
| `rationale` | string | No | Why the chosen option was selected. |
| `consequences` | string | No | Expected outcomes and tradeoffs of the decision. |

---

## quality

Array of quality criteria that define when the planning effort (or its outputs) are considered complete.

```yaml
quality:
  - id: all_endpoints_specified
    type: checklist
    description: Every API endpoint has a specification
    criteria: |
      - POST /auth/login is fully specified
      - POST /auth/refresh is fully specified
      - POST /auth/logout is fully specified
      - GET /auth/me is fully specified

  - id: threat_model_reviewed
    type: review
    description: Threat model has been reviewed by security team
    criteria: |
      A security-focused reviewer has read the threat_model section
      and confirmed that all identified threats have mitigations.

  - id: schema_validation
    type: test
    description: Document validates against v1 schema
    criteria: |
      This .vibe.md file passes validation against vibe/schema/vibe.schema.json.

  - id: token_expiration_tested
    type: metric
    description: Token expiration is within acceptable bounds
    criteria: |
      Access token TTL is between 5 and 30 minutes.
      Refresh token TTL is between 1 and 30 days.
```

### quality fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Unique identifier within the document. Should be snake_case. |
| `type` | string | No | One of: `review`, `test`, `metric`, `checklist`. |
| `description` | string | No | What is being measured or checked. |
| `criteria` | string | No | The specific conditions that must be met. |

### Quality types

| Type | Purpose |
|---|---|
| `review` | Requires human or AI review and judgment. |
| `test` | Can be verified by automated tooling. |
| `metric` | A measurable value that must fall within bounds. |
| `checklist` | A list of items that must all be completed. |

---

## Standard Library

VIBE v1 ships a standard library under `vibe/stdlib/`:

| Module | Purpose |
|---|---|
| `quality.vibe.md` | Reusable quality criteria for common document checks (frontmatter validity, schema validation, metadata completeness, section typing, decision completeness, import resolution). |
| `context_budget.vibe.md` | Context budgeting and compaction guidance for AI systems working with `.vibe.md` documents across long planning sessions. |

### Template library

`vibe/stdlib/templates/` provides document archetype templates:

| Template | Purpose |
|---|---|
| `overview.vibe.md` | Project overview and problem framing. |
| `architecture.vibe.md` | System architecture and component design. |
| `implementation_plan.vibe.md` | Step-by-step implementation plan with artifacts and ordering. |
| `risk_assessment.vibe.md` | Risk identification, analysis, and mitigation planning. |
| `adr_collection.vibe.md` | Collection of Architecture Decision Records. |

Templates are starting points. Copy and modify them rather than importing directly.

---

## Related Documents

### Normative (consumers and tooling MUST follow)

- `VIBE_CONSUMER_CONTRACT.md` -- Required consumer behaviors for tools that read `.vibe.md` documents.
- `VIBE_MERGE_SEMANTICS.md` -- How imports are merged: array concatenation, scalar precedence, conflict rules.
- `VIBE_ERRORS.md` -- Standard error taxonomy for validation and parsing failures.

### Recommended (strongly improves document quality)

- `VIBE_DOCUMENT_TYPES.md` -- Guidance on common document archetypes and when to use each.
- `VIBE_DEPENDENCIES.md` -- Artifact and section dependency semantics.
- `VIBE_AUTHORING_GUIDE.md` -- Guidance for humans and AIs authoring `.vibe.md` documents.
- `VIBE_REFERENCE_DOCUMENT.md` -- Canonical example document demonstrating all v1 features.

### Integration (for tooling and multi-agent workflows)

- `VIBE_INTEGRATION_HOOKS.md` -- How external tools can consume, validate, and act on `.vibe.md` documents.
- `VIBE_MULTI_AUTHOR.md` -- Patterns for multiple humans or AI agents collaborating on a single document.
- `VIBE_MCP_SERVER.md` -- Model Context Protocol server for AI tool integration with `.vibe.md` documents.

---

## Philosophy

VIBE is:

- a **document format** for AI-driven planning
- a **structured alternative to unstructured markdown** for capturing plans, decisions, and quality criteria
- an **import-based composition system** for building on shared context and standards

VIBE is not:

- a runtime or execution engine
- a workflow orchestrator
- a build system or task runner
- a chat protocol or prompt format
- a replacement for version control

### Core beliefs

**Documents are the deliverable.** The output of AI planning is a structured document that humans can review and execution tools can consume. The document is the plan.

**Structured planning is more valuable than unstructured markdown.** Typed sections, explicit decisions, and machine-checkable quality criteria produce plans that are easier to review, easier to continue, and easier to act on.

**AI-first, human-readable.** VIBE documents are designed to be authored by AI systems and reviewed by humans. The format is optimized for AI planning workflows while remaining readable and editable by hand.

**Composition over monoliths.** Small, focused documents that import shared context are more maintainable than large monolithic plans. The import system enables reuse without complexity.

VIBE exists to normalize AI-driven planning into a structured, reviewable, composable format that both humans and machines can reliably work with.
