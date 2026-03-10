# VIBE Multi-Author Patterns (v1.0)

This document defines patterns for multiple authors collaborating on `.vibe` planning documents.

VIBE v1 documents are authored by humans, AI systems, or both. This document covers how to identify authors, collaborate within and across sessions, manage document lifecycle, and resolve conflicts.

---

## 1. Author Identification

Every `.vibe` document has an optional `meta.author` field that identifies who created or last meaningfully edited the document.

### Author values

```yaml
meta:
  author: claude          # Authored by Claude
  author: human           # Authored by a human
  author: gpt-4           # Authored by a specific AI model
  author: agent-review-01 # Authored by a named agent instance
```

Author values are freeform strings. Recommended conventions:

| Value | Meaning |
|---|---|
| `human` | A human author (individual not specified) |
| `claude` | Anthropic's Claude |
| `human:jane` | A specific human author |
| `claude:session-abc` | Claude in a specific session |
| Any string | Any identified agent or author |

### When to set author

- Set `meta.author` when creating a new document
- Update `meta.author` when a different author makes substantive changes
- For documents with multiple significant contributors, use `meta.author` for the most recent substantive author and note prior authors in a section

### Author vs. editor

The `meta.author` field identifies the primary author, not every editor. Minor edits (typo fixes, formatting) do not require updating the author field. Substantive changes (new sections, revised decisions, changed artifacts) should update the author.

---

## 2. Session Collaboration

Multiple authors can collaborate on `.vibe` documents within a single MCP session.

### Single-session workflow

In a single session, collaboration typically follows this pattern:

1. **Human initiates**: Human describes the problem and constraints
2. **AI drafts**: AI creates an initial `.vibe` document with `meta.status: draft`
3. **Human reviews**: Human reviews sections, decisions, and quality criteria
4. **AI revises**: AI updates the document based on feedback
5. **Human approves**: Human moves `meta.status` to `review` or `final`

### Session identification

Documents created in an MCP session can reference their session via `meta.session_id`:

```yaml
meta:
  session_id: 2026-03-10-a1b2c3
```

The session ID format is `{YYYY-MM-DD}-{6-char-hex}`. This enables cross-session references and traceability.

### Collaborative sections

When multiple authors contribute to the same document in a session, each can own specific sections:

```yaml
sections:
  - id: problem_analysis
    type: analysis
    title: Problem Analysis
    content: |
      [Written by human - domain expertise]

  - id: technical_design
    type: design
    title: Technical Design
    content: |
      [Written by AI - based on problem analysis]

  - id: risk_assessment
    type: risk
    title: Risk Assessment
    content: |
      [Written by AI, reviewed and amended by human]
```

There is no formal per-section author field. If tracking section authorship is important, note it in the section content or maintain a separate tracking document.

---

## 3. Cross-Session Building

VIBE documents can build on work from prior sessions by importing documents from those sessions.

### Importing prior session work

```yaml
imports:
  - sessions/2026-03-08-f4e5d6/api_design.vibe
  - sessions/2026-03-09-a1b2c3/risk_review.vibe
```

### Session directory convention

When an MCP server persists session artifacts, the recommended layout is:

```
sessions/
  2026-03-08-f4e5d6/
    api_design.vibe
    architecture.vibe
  2026-03-09-a1b2c3/
    risk_review.vibe
    updated_plan.vibe
```

### Building on prior plans

A common cross-session pattern:

1. **Session 1**: AI creates initial planning document (draft)
2. **Between sessions**: Human reviews the document offline
3. **Session 2**: AI imports the prior document, addresses feedback, creates updated version
4. **Session 3**: AI imports the updated document, adds implementation details, finalizes

Each session builds on prior work via imports rather than editing prior session files in place. This preserves the history of planning iterations.

### Referencing without importing

Sometimes a document should reference prior work without merging its fields. Use context to reference prior sessions:

```yaml
context:
  prior_work: |
    This plan builds on the API design from session 2026-03-08-f4e5d6.
    Key decisions from that session:
    - Cursor-based pagination (accepted)
    - PostgreSQL + Redis storage (accepted)
    See sessions/2026-03-08-f4e5d6/api_design.vibe for details.
```

---

## 4. Review Workflows

The `meta.status` lifecycle provides a lightweight review workflow for multi-author documents.

### Draft to review

The primary author (human or AI) creates the document and works on it until all sections have substantive content. Then the author moves status to `review`:

```yaml
meta:
  status: review
```

At `review` status:
- All sections should have real content (no placeholders)
- All decisions should have context, options, chosen, and rationale
- All quality criteria should be defined
- All artifacts should have acceptance criteria

### Review process

During review, reviewers (human or AI) evaluate:

1. **Context**: Is the problem clearly defined? Are constraints complete?
2. **Sections**: Is the analysis sound? Is the design feasible?
3. **Decisions**: Were the right options considered? Is the rationale solid?
4. **Quality**: Are criteria specific and measurable?
5. **Artifacts**: Are acceptance criteria complete and verifiable?

Review feedback can be:
- Inline edits to the document (move back to `draft` if substantive)
- Comments in a separate review document
- Verbal discussion in a session

### Review to final

After review is complete and any revisions are made:

```yaml
meta:
  status: final
```

A `final` document represents an approved plan. Changes to a final document should move it back to `draft` and go through review again.

### Multi-reviewer pattern

For documents requiring multiple reviewers:

```yaml
quality:
  - id: q_backend_review
    type: review
    description: Backend team has reviewed technical design
    criteria: |
      At least one backend engineer has reviewed the design and
      specification sections and confirmed feasibility.

  - id: q_product_review
    type: review
    description: Product owner has reviewed scope and priorities
    criteria: |
      Product owner has confirmed the scope section accurately
      reflects priorities and the checklist ordering is correct.
```

Using quality criteria to track review approvals makes the review state explicit and machine-readable.

---

## 5. Conflict Resolution

When two authors edit the same document, conflicts can arise. VIBE v1 handles conflicts at two levels: document-level and field-level.

### Document-level conflicts

If two authors create separate versions of the same document (e.g., both editing `plans/feature_a.vibe` independently), the conflict must be resolved manually. VIBE does not define automatic document merge -- this is a version control concern (git merge, etc.).

Recommended approach:
- Use branches for independent editing
- Review diffs before merging
- The most recent `meta.updated_at` indicates the latest version

### Field-level merge conflicts

When importing multiple documents that declare overlapping fields, VIBE validation will report `MERGE_DUPLICATE_ID` or `MERGE_DUPLICATE_PATH` errors.

Resolution strategies:

**Rename IDs**: If two imported documents both have a section with `id: overview`, rename one:

```yaml
# In the importing document, one author renames their section
- id: auth_overview      # Was: overview
  type: analysis
  title: Auth System Overview
```

**Split documents**: If two documents have too many ID conflicts, they may be trying to cover the same scope. Consolidate into one document or clearly delineate scope boundaries.

**Namespace IDs**: Use prefixes to avoid collisions across documents:

```yaml
# Document A uses auth_ prefix
- id: auth_design
- id: auth_risks

# Document B uses billing_ prefix
- id: billing_design
- id: billing_risks
```

### Decision conflicts

If two authors propose conflicting decisions (e.g., one chooses PostgreSQL, another chooses DynamoDB for the same concern):

1. Both decisions should be recorded with `status: proposed`
2. Create a new decision that resolves the conflict with `status: accepted`
3. Mark the losing decision as `status: superseded`

```yaml
decisions:
  - id: d_storage_v1
    title: Use DynamoDB for notifications
    status: superseded
    context: |
      Initially proposed by author A before PostgreSQL constraints were known.
    # ... options, rationale ...

  - id: d_storage_v2
    title: Use PostgreSQL with Redis caching for notifications
    status: accepted
    context: |
      Supersedes d_storage_v1. After reviewing infrastructure constraints,
      PostgreSQL + Redis is the better fit.
    # ... options, rationale ...
```

---

## 6. Best Practices for Collaborative Planning

### Clear ownership per section

When multiple authors contribute to one document, assign clear ownership of sections. One author should be responsible for each section's content, even if others provide input.

### Use decisions for disagreements

When authors disagree, do not resolve the disagreement in prose. Create a decision record with both positions as options, and record the resolution with rationale. This makes the disagreement and its resolution visible and reviewable.

### Keep documents focused

A document with too many authors often means the scope is too broad. Split large planning efforts into focused documents with clear owners, and compose them via imports.

### Track status honestly

Do not mark a document as `review` if sections still have placeholder content. Do not mark it as `final` if decisions are still `proposed`. Status should reflect reality, not aspiration.

### Use quality criteria for review gates

Define quality criteria that capture review requirements:

```yaml
quality:
  - id: q_security_review
    type: review
    description: Security team has reviewed the authentication design
    criteria: |
      A security engineer has reviewed the auth_decision section and
      confirmed the WebSocket authentication approach is acceptable.
```

This makes review requirements explicit and trackable.

### Prefer new documents over heavy edits

When building on prior work across sessions, prefer creating a new document that imports the prior one rather than heavily editing the original. This preserves the planning history and makes it clear what changed between iterations.

```yaml
# plans/notifications_v2.vibe (new document)
imports:
  - plans/notifications_v1.vibe    # Prior iteration

context:
  problem: |
    Revised plan based on review feedback from the notifications_v1 plan.
    Key changes: switched to cursor pagination, added WebSocket design.
```

### Document your collaboration model

For teams with established collaboration patterns, create a project-level document that describes the workflow:

```yaml
# plans/collaboration.vibe
vibe: 1.0

meta:
  name: collaboration_model
  description: How our team uses VIBE for collaborative planning
  status: final

sections:
  - id: workflow
    type: specification
    title: Collaboration Workflow
    content: |
      1. Product owner creates context (problem, constraints, scope)
      2. AI drafts initial plan with sections and decisions
      3. Tech lead reviews design and specification sections
      4. Security reviews auth and risk sections
      5. Product owner confirms scope and priorities
      6. AI incorporates feedback and moves to final
```
