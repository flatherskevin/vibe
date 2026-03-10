# VIBE Reference Document (v2.0)

This document provides a canonical reference for VIBE v2 planning documents.

VIBE v2 is a structured YAML document format for AI-driven planning. A `.vibe` file captures what problem is being solved, what will be built, how decisions were made, and what "done" looks like. It is not an execution format.

This reference is useful for:

- AI systems authoring `.vibe` documents
- humans reviewing or writing plans
- tooling implementers (validators, MCP servers, editors)
- users learning the format

---

## 1. Purpose

The reference document demonstrates a realistic planning document that uses all v2 features:

- version declaration
- document metadata with author, status, and tags
- imports for composition
- context (problem, constraints, assumptions, scope, glossary)
- artifacts with acceptance criteria and status
- typed sections (analysis, design, decision, specification, risk, checklist)
- architecture decision records
- quality criteria
- document lifecycle (draft, review, final)

The reference is intentionally complete, not minimal. It shows how all features work together in a realistic planning scenario.

---

## 2. Reference Repository Layout (v2)

Recommended layout for a VIBE v2 project:

```
project.vibe                          # Root document

vibe/
  stdlib/
    quality.vibe                      # Standard quality criteria
    context_budget.vibe               # Context management guidance
    templates/
      overview.vibe                   # Project overview template
      architecture.vibe               # Architecture planning template
      implementation_plan.vibe        # Implementation plan template
      risk_assessment.vibe            # Risk assessment template
      adr_collection.vibe             # ADR collection template
  spec/
    VIBE_SPEC_v2.md                   # Core specification
    VIBE_REFERENCE_DOCUMENT.md        # This file
    VIBE_AUTHORING_GUIDE.md           # Authoring guidance
    VIBE_ERRORS.md                    # Error taxonomy
    VIBE_MULTI_AUTHOR.md              # Multi-author patterns
    VIBE_INDEX.md                     # Document index
  schema/
    vibe.schema.json                  # JSON Schema for .vibe files

syntaxes/
  vibe.tmLanguage.json                # Syntax highlighting
```

Key differences from v1 layout:

- No `tools.vibe`, `gates.vibe`, or `plan_manifest_schema.vibe` (execution concepts removed)
- `quality.vibe` replaces `validators.vibe` as the primary stdlib import
- `templates/` directory provides starter documents for common planning patterns
- No `spec/` output directory (no plan manifest, no runlog)

---

## 3. Reference `.vibe` Document

The following is a complete, realistic planning document for an API feature. It demonstrates all v2 fields.

```yaml
vibe: 2.0

meta:
  name: user_notifications_api
  description: >
    Planning document for the user notifications API. Covers design,
    implementation approach, and quality criteria for the notifications
    feature across REST endpoints, event processing, and storage.
  session_id: 2026-03-10-a1b2c3
  created_at: 2026-03-10
  updated_at: 2026-03-10
  author: claude
  tags:
    - api
    - notifications
    - backend
  status: review

imports:
  - vibe/stdlib/quality.vibe
  - vibe/stdlib/context_budget.vibe

context:
  problem: |
    Users have no way to receive notifications about events relevant to
    their account (team invitations, billing alerts, deployment status).
    Currently, all communication happens via email, which has poor
    engagement rates and no in-app presence.

  constraints: |
    - Must integrate with existing auth middleware (JWT-based)
    - Must support real-time delivery via WebSocket and polling fallback
    - Must not exceed 50ms p99 latency for notification reads
    - Must store notifications for at least 90 days
    - Must support at least 10,000 notifications per user

  assumptions: |
    - PostgreSQL is the primary data store (existing infrastructure)
    - Redis is available for caching and pub/sub
    - The frontend team will consume the API (not building the UI here)
    - Event producers already emit structured events to an internal bus

  scope: |
    In scope:
    - REST API for CRUD operations on notifications
    - WebSocket endpoint for real-time delivery
    - Event consumer for notification generation
    - Storage schema and indexing

    Out of scope:
    - Frontend UI components
    - Email/SMS delivery channels
    - Notification preferences UI (API only)

  glossary: |
    - Notification: A structured message delivered to a user about an event
    - Event: An internal system occurrence that may trigger notifications
    - Channel: A delivery mechanism (in-app, WebSocket, polling)
    - Read receipt: Acknowledgment that a user has seen a notification

artifacts:
  - path: src/notifications/router.py
    kind: python
    description: FastAPI router with notification CRUD endpoints
    depends_on:
      - src/notifications/models.py
      - src/notifications/service.py
    acceptance_criteria:
      - GET /notifications returns paginated list for authenticated user
      - POST /notifications/{id}/read marks notification as read
      - DELETE /notifications/{id} soft-deletes a notification
      - All endpoints require valid JWT authentication
    status: planned

  - path: src/notifications/models.py
    kind: python
    description: SQLAlchemy models for notifications and read receipts
    acceptance_criteria:
      - Notification model with id, user_id, type, title, body, created_at, read_at
      - Composite index on (user_id, created_at) for efficient listing
      - Soft delete via deleted_at column
    status: planned

  - path: src/notifications/service.py
    kind: python
    description: Business logic for notification operations
    depends_on:
      - src/notifications/models.py
    acceptance_criteria:
      - create_notification() generates and persists a notification
      - list_notifications() returns paginated results with cursor-based pagination
      - mark_read() updates read_at timestamp
      - Integrates with Redis pub/sub for real-time delivery
    status: planned

  - path: src/notifications/consumer.py
    kind: python
    description: Event consumer that generates notifications from system events
    depends_on:
      - src/notifications/service.py
    acceptance_criteria:
      - Subscribes to internal event bus
      - Maps event types to notification templates
      - Handles duplicate events idempotently
    status: planned

  - path: src/notifications/ws.py
    kind: python
    description: WebSocket endpoint for real-time notification delivery
    depends_on:
      - src/notifications/service.py
    acceptance_criteria:
      - Authenticated WebSocket connection per user
      - Delivers new notifications in real time via Redis pub/sub
      - Graceful disconnect handling
    status: planned

  - path: tests/test_notifications.py
    kind: python
    description: Test suite for notification endpoints and service
    depends_on:
      - src/notifications/router.py
      - src/notifications/service.py
    acceptance_criteria:
      - Unit tests for service layer
      - Integration tests for API endpoints
      - Test coverage above 80%
    status: planned

sections:
  - id: problem_analysis
    type: analysis
    title: Problem Analysis
    content: |
      Current state: Users receive account notifications exclusively via
      email. Email open rates average 23%, and critical alerts (billing
      failures, security events) are frequently missed.

      User research shows 78% of surveyed users want in-app notifications.
      The top requested notification types are:
      1. Team invitations and membership changes
      2. Billing alerts (payment failures, plan changes)
      3. Deployment status updates
      4. Security events (new login, password change)

      The existing event bus already emits structured events for all of
      these categories. The primary gap is the notification layer itself.

  - id: api_design
    type: design
    title: API Design
    content: |
      REST endpoints:

      GET /api/v1/notifications
        Query params: cursor, limit (default 20, max 100), unread_only
        Response: { items: [...], next_cursor: string | null }

      GET /api/v1/notifications/unread-count
        Response: { count: number }

      POST /api/v1/notifications/{id}/read
        Response: 204 No Content

      POST /api/v1/notifications/read-all
        Response: 204 No Content

      DELETE /api/v1/notifications/{id}
        Response: 204 No Content (soft delete)

      WebSocket endpoint:

      WS /api/v1/notifications/ws
        Auth: JWT token as query parameter or first message
        Messages: JSON notification objects pushed on creation

  - id: data_model_spec
    type: specification
    title: Data Model Specification
    content: |
      Table: notifications
        - id: UUID, primary key
        - user_id: UUID, indexed, foreign key to users
        - type: VARCHAR(50), notification category
        - title: VARCHAR(255)
        - body: TEXT
        - metadata: JSONB, additional structured data
        - created_at: TIMESTAMP WITH TIME ZONE, indexed
        - read_at: TIMESTAMP WITH TIME ZONE, nullable
        - deleted_at: TIMESTAMP WITH TIME ZONE, nullable

      Indexes:
        - (user_id, created_at DESC) for listing
        - (user_id, read_at) partial index WHERE read_at IS NULL for unread count

      Retention: Rows older than 90 days are archived via pg_cron job.

  - id: auth_decision
    type: decision
    title: Authentication Approach for WebSocket
    content: |
      WebSocket connections need authentication but cannot use standard
      HTTP headers after the initial handshake.

      Options considered:
      1. JWT as query parameter during handshake
      2. JWT sent as first WebSocket message after connection
      3. Session cookie-based authentication

      Decision: Option 1 (JWT as query parameter). While query parameters
      can appear in server logs, the token is short-lived (15 min) and
      the alternative (first-message auth) adds protocol complexity.
      Cookie-based auth was rejected because the API is consumed by
      multiple clients including mobile apps.

  - id: scaling_risks
    type: risk
    title: Scaling Risks
    content: |
      Risk 1: WebSocket connection limits
        Impact: High
        Probability: Medium
        Mitigation: Use Redis pub/sub to decouple WebSocket servers
        from notification producers. Horizontal scaling via sticky
        sessions or connection migration.

      Risk 2: Notification table growth
        Impact: Medium
        Probability: High
        Mitigation: 90-day retention policy with archival. Cursor-based
        pagination avoids offset performance degradation.

      Risk 3: Event bus consumer lag
        Impact: Medium
        Probability: Low
        Mitigation: Consumer group with multiple workers. Dead letter
        queue for failed processing. Idempotent handling.

  - id: implementation_checklist
    type: checklist
    title: Implementation Checklist
    content: |
      Phase 1 - Data layer:
      - [ ] Create notifications table migration
      - [ ] Implement SQLAlchemy models
      - [ ] Write repository layer with pagination

      Phase 2 - Service layer:
      - [ ] Implement notification service
      - [ ] Integrate Redis pub/sub for real-time
      - [ ] Build event consumer

      Phase 3 - API layer:
      - [ ] Implement REST endpoints
      - [ ] Implement WebSocket endpoint
      - [ ] Add authentication middleware integration

      Phase 4 - Testing:
      - [ ] Unit tests for service layer
      - [ ] Integration tests for endpoints
      - [ ] Load test for p99 latency target

decisions:
  - id: d_pagination_strategy
    title: Use cursor-based pagination instead of offset pagination
    status: accepted
    context: |
      Notification lists grow continuously and users typically read recent
      items. Offset-based pagination degrades with large offsets and is
      unstable when new items are inserted during paging.
    options:
      - name: offset_pagination
        description: Traditional LIMIT/OFFSET pagination
      - name: cursor_pagination
        description: Cursor-based pagination using created_at + id
      - name: keyset_pagination
        description: Keyset pagination using composite key
    chosen: cursor_pagination
    rationale: |
      Cursor-based pagination provides stable results regardless of
      insertions, O(1) performance regardless of page depth, and is the
      standard for real-time feed APIs. The cursor encodes (created_at, id)
      for deterministic ordering.
    consequences:
      - Clients must store cursor tokens instead of page numbers
      - Cannot jump to arbitrary pages (acceptable for notification feeds)
      - Consistent performance at any depth in the notification list

  - id: d_storage_backend
    title: Use PostgreSQL with Redis caching for notifications
    status: accepted
    context: |
      Need a storage backend that supports structured queries, pagination,
      and high read throughput for notification lists.
    options:
      - name: postgresql_only
        description: PostgreSQL for storage and queries, no caching
      - name: postgresql_redis
        description: PostgreSQL for persistence, Redis for caching and pub/sub
      - name: dynamodb
        description: DynamoDB for storage with built-in scaling
    chosen: postgresql_redis
    rationale: |
      PostgreSQL is already in use and provides strong query capabilities.
      Redis adds caching for unread counts (frequently accessed) and
      pub/sub for real-time WebSocket delivery. DynamoDB was rejected to
      avoid introducing a new data store and losing relational query power.
    consequences:
      - Two systems to maintain (PostgreSQL + Redis)
      - Cache invalidation needed for unread counts
      - Redis pub/sub provides simple real-time delivery path

quality:
  - id: q_latency
    type: metric
    description: Notification read latency meets target
    criteria: |
      GET /notifications p99 latency is under 50ms with 10,000
      notifications per user, measured via load test.

  - id: q_coverage
    type: metric
    description: Test coverage meets minimum threshold
    criteria: |
      Test suite covers at least 80% of lines in src/notifications/.

  - id: q_api_contract
    type: test
    description: API endpoints match specification
    criteria: |
      All endpoints listed in the api_design section exist, accept the
      documented parameters, and return the documented response shapes.

  - id: q_auth_enforced
    type: test
    description: All endpoints require authentication
    criteria: |
      Every endpoint returns 401 when called without a valid JWT.
      WebSocket connections are rejected without valid token.

  - id: q_idempotent
    type: test
    description: Event consumer handles duplicates
    criteria: |
      Processing the same event twice does not create duplicate
      notifications. Verified via integration test.

  - id: q_review_complete
    type: review
    description: Design review completed
    criteria: |
      At least one backend engineer and one frontend consumer have
      reviewed the API design section and approved the interface.
```

---

## 4. Import Example

VIBE v2 documents compose via imports. When a document imports another, the imported fields are merged into the importing document.

### Simple import

A planning document imports standard quality criteria:

```yaml
vibe: 2.0

meta:
  name: my_feature_plan
  status: draft

imports:
  - vibe/stdlib/quality.vibe
```

After import resolution, the document has access to all `stdlib_*` quality criteria defined in `quality.vibe`, merged into its own quality array.

### Multi-document composition

A large initiative might be split across documents:

```yaml
# initiative_plan.vibe
vibe: 2.0

meta:
  name: q4_initiative
  description: Q4 platform initiative planning
  status: draft

imports:
  - vibe/stdlib/quality.vibe
  - plans/auth_redesign.vibe
  - plans/notifications_api.vibe
  - plans/billing_migration.vibe

context:
  problem: |
    Q4 initiative covering three workstreams that share
    infrastructure and timeline dependencies.

sections:
  - id: timeline
    type: specification
    title: Cross-Workstream Timeline
    content: |
      Week 1-2: Auth redesign (unblocks notifications)
      Week 2-4: Notifications API (depends on auth)
      Week 3-6: Billing migration (independent)
```

Each imported document contributes its own sections, decisions, artifacts, and quality criteria. IDs must be unique across the merged result.

### Importing from prior sessions

Documents from prior MCP sessions can be imported by path:

```yaml
imports:
  - sessions/2026-03-08-f4e5d6/api_design.vibe
  - sessions/2026-03-09-a1b2c3/risk_review.vibe
```

This enables building on prior planning work across sessions.

---

## 5. Document Lifecycle

Every VIBE v2 document has a `meta.status` field that tracks its position in the authoring lifecycle.

### draft

The document is being actively written. Content may be incomplete or contain placeholders. Sections, decisions, and quality criteria may be missing or partial.

```yaml
meta:
  status: draft
```

In draft status:
- Sections may have placeholder content
- Decisions may have status `proposed` (not yet accepted)
- Quality criteria are defined but not yet evaluated
- Artifacts may have status `planned`

### review

The document is structurally complete and ready for review by humans or other agents. All sections should have substantive content.

```yaml
meta:
  status: review
```

In review status:
- All sections should have real content (no placeholders)
- Decisions should have options, a chosen option, and rationale
- Quality criteria should be evaluable
- Artifacts should have acceptance criteria defined

### final

The document has been reviewed and accepted. It represents an approved plan.

```yaml
meta:
  status: final
```

In final status:
- Content should not change without moving back to draft
- Decisions should have status `accepted`
- The document can be safely imported by other documents
- Quality criteria represent the accepted definition of done

### Lifecycle transitions

```
draft --> review --> final
  ^         |
  +---------+
  (revisions needed)
```

A document may move back from `review` to `draft` if revisions are needed. Moving from `final` back to `draft` indicates a significant change and should be noted in the context or a new decision.

---

## 6. What This Reference Teaches

This reference demonstrates five core VIBE v2 practices:

### 6.1 Context first

Start every document with a clear problem statement, constraints, and assumptions. Context frames everything that follows.

### 6.2 Typed sections for structured thinking

Use section types (analysis, design, specification, risk, checklist) to organize content by purpose. This makes documents scannable and helps AI systems produce appropriate content for each section type.

### 6.3 Explicit decisions

Record decisions as first-class objects with context, options, rationale, and consequences. This makes reasoning transparent and reviewable.

### 6.4 Measurable quality

Define quality criteria that are specific enough to evaluate. Vague criteria like "high quality code" are not useful. Criteria like "p99 latency under 50ms" are.

### 6.5 Composition over repetition

Import shared criteria and build on prior documents rather than copying content. Imports make documents modular and maintainable.

---

## 7. Relationship to Other Spec Documents

This file is a teaching and reference document.

For the normative specification, see:

- `VIBE_SPEC_v2.md` -- Core language specification

For authoring guidance, see:

- `VIBE_AUTHORING_GUIDE.md` -- How to write good .vibe documents

For validation and errors, see:

- `VIBE_ERRORS.md` -- Document validation error taxonomy

For multi-author workflows, see:

- `VIBE_MULTI_AUTHOR.md` -- Collaborative planning patterns
