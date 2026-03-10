# VIBE Authoring Guide (v2.0)

Guide for writing effective `.vibe` planning documents.

VIBE v2 is a structured YAML document format for AI-driven planning. This guide covers how to write documents that are clear, complete, and useful for both human reviewers and AI systems.

---

## Golden Rules

1. **Start with context.** Define the problem, constraints, and assumptions before writing anything else. Context frames every section, decision, and artifact.

2. **Use the right section type for each piece of content.** Analysis sections analyze. Design sections propose solutions. Specification sections define precise details. Do not mix purposes within a section.

3. **Make decisions explicit.** Use the `decisions` field for every significant choice. Record what options were considered, what was chosen, and why. Do not bury decisions inside section prose.

4. **Define quality criteria.** Every document should answer "what does done look like?" with specific, evaluable criteria in the `quality` field.

5. **Compose via imports.** Do not repeat content across documents. Import shared criteria from the stdlib, and reference prior planning documents rather than copying them.

6. **Track status.** Use `meta.status` to indicate where the document is in its lifecycle: `draft`, `review`, or `final`. Advance status only when the document is ready.

---

## Recommended Project Layout

```
project.vibe                          # Root document (imports stdlib)

vibe/
  stdlib/
    quality.vibe                      # Standard quality criteria
    context_budget.vibe               # Context management for AI
    templates/                        # Starter templates
      overview.vibe
      architecture.vibe
      implementation_plan.vibe
      risk_assessment.vibe
      adr_collection.vibe
  spec/                               # Specification documents
    VIBE_SPEC_v2.md
    VIBE_REFERENCE_DOCUMENT.md
    VIBE_AUTHORING_GUIDE.md
    VIBE_ERRORS.md
    VIBE_MULTI_AUTHOR.md
  schema/
    vibe.schema.json                  # JSON Schema for validation

plans/                                # Project-specific planning documents
  feature_a.vibe
  feature_b.vibe
  q4_initiative.vibe

syntaxes/
  vibe.tmLanguage.json                # Editor syntax highlighting
```

Key conventions:

- `project.vibe` at the root is the entrypoint that imports stdlib modules
- `vibe/` contains the VIBE format itself (stdlib, spec, schema)
- `plans/` (or similar) contains project-specific planning documents
- Templates in `vibe/stdlib/templates/` provide starting points for new documents

---

## Writing Good Sections

Sections are the body of a `.vibe` document. Each section has a `type` that signals its purpose.

### analysis

Use for examining the current state, understanding problems, and gathering evidence.

Good analysis sections:
- Describe the current state with specifics (numbers, examples)
- Identify who is affected and how
- Cite evidence or data that supports conclusions

```yaml
- id: user_research
  type: analysis
  title: User Research Findings
  content: |
    Survey of 200 active users (Feb 2026):
    - 78% want in-app notifications
    - 45% have missed critical billing alerts via email
    - Average email open rate for system notifications: 23%
```

Avoid: Vague statements like "users are unhappy" without specifics.

### design

Use for proposing solutions, architecture, and implementation approaches.

Good design sections:
- Describe what will be built or changed
- Explain the approach at a level sufficient for implementation
- Reference constraints from the context

```yaml
- id: api_design
  type: design
  title: REST API Design
  content: |
    GET /api/v1/notifications
      Query: cursor, limit (default 20, max 100), unread_only
      Response: { items: [...], next_cursor: string | null }

    POST /api/v1/notifications/{id}/read
      Response: 204 No Content
```

Avoid: Design sections that only describe goals without concrete details.

### specification

Use for precise, normative definitions of interfaces, data models, or protocols.

Good specification sections:
- Define exact fields, types, and constraints
- Are precise enough to implement from directly
- Leave no ambiguity about required behavior

```yaml
- id: data_model
  type: specification
  title: Notification Data Model
  content: |
    Table: notifications
      - id: UUID, primary key
      - user_id: UUID, indexed, NOT NULL
      - type: VARCHAR(50), NOT NULL
      - title: VARCHAR(255), NOT NULL
      - body: TEXT
      - created_at: TIMESTAMP WITH TIME ZONE, default NOW()
      - read_at: TIMESTAMP WITH TIME ZONE, nullable
```

Avoid: Vague specifications like "a database table for notifications" without field definitions.

### decision

Use for recording a choice within a section (separate from the top-level `decisions` field which provides full ADR structure). Decision sections are useful for smaller choices that do not warrant a full ADR.

```yaml
- id: auth_approach
  type: decision
  title: WebSocket Authentication
  content: |
    Options: JWT query parameter, first-message JWT, session cookies.
    Chosen: JWT query parameter.
    Rationale: Simplest protocol, short-lived tokens mitigate log exposure.
```

For significant architectural decisions, prefer the top-level `decisions` array which provides full ADR structure with options, chosen, rationale, and consequences.

### risk

Use for identifying threats, their likelihood, impact, and mitigations.

Good risk sections:
- Name specific risks (not generic concerns)
- Rate impact and probability
- Propose concrete mitigations

```yaml
- id: scaling_risks
  type: risk
  title: Scaling Risks
  content: |
    Risk: WebSocket connection limits at ~10K concurrent per server
      Impact: High
      Probability: Medium (expected within 6 months)
      Mitigation: Redis pub/sub for horizontal scaling, connection migration
```

Avoid: Listing risks without mitigations, or vague risks like "it might not scale."

### checklist

Use for ordered task lists, implementation phases, or verification steps.

Good checklist sections:
- Break work into concrete, completable items
- Order items by dependency or phase
- Each item is specific enough to verify completion

```yaml
- id: implementation_plan
  type: checklist
  title: Implementation Phases
  content: |
    Phase 1 - Data layer:
    - [ ] Create notifications table migration
    - [ ] Implement SQLAlchemy models
    - [ ] Write repository layer with pagination

    Phase 2 - API layer:
    - [ ] Implement REST endpoints
    - [ ] Add auth middleware integration
    - [ ] Write integration tests
```

Avoid: Checklists with items like "do the backend work."

---

## Writing Good Decisions

The `decisions` array provides full Architecture Decision Record (ADR) structure. Use it for choices that have lasting architectural impact.

### Context

Explain why the decision is needed. What forces are at play?

Good: "Notification lists grow continuously and users page through recent items. We need a pagination strategy that remains performant at scale."

Bad: "We need to pick a pagination approach."

### Options

List at least two alternatives. Each should be a real option that was genuinely considered.

Good:
```yaml
options:
  - name: offset_pagination
    description: Traditional LIMIT/OFFSET with page numbers
  - name: cursor_pagination
    description: Cursor-based pagination using (created_at, id) composite key
```

Bad: Listing only the chosen option, or including straw-man options that were never realistic.

### Rationale

Explain why the chosen option is the best fit given the context and constraints. Reference specific trade-offs.

Good: "Cursor-based pagination provides O(1) performance at any depth and stable results during insertions, which matters for a continuously growing notification feed."

Bad: "It seemed like the best option."

### Consequences

List what follows from this choice -- both positive and negative.

Good:
```yaml
consequences:
  - Clients must store cursor tokens instead of page numbers
  - Cannot jump to arbitrary pages (acceptable for feeds)
  - Consistent performance regardless of dataset size
```

Bad: Omitting consequences, or listing only positives.

---

## Writing Good Quality Criteria

Quality criteria define what "done" looks like. Every criterion should be specific enough that someone can evaluate it as pass or fail.

### Types

- `test` -- Can be verified by running a test (automated or manual)
- `metric` -- Can be verified by measuring a number against a threshold
- `review` -- Requires human or AI judgment to evaluate
- `checklist` -- Can be verified by checking a list of conditions

### Specific and measurable

Good:
```yaml
- id: q_latency
  type: metric
  description: Notification read latency meets target
  criteria: |
    GET /notifications p99 latency is under 50ms with 10,000
    notifications per user, measured via load test.
```

Bad:
```yaml
- id: q_fast
  type: review
  description: API is fast enough
  criteria: |
    The API should respond quickly.
```

### Evaluable

Every criterion should answer: "How would someone verify this?" If the answer is unclear, the criterion needs to be more specific.

Good criteria patterns:
- "All endpoints return 401 without valid JWT" (testable)
- "Test coverage above 80% for src/notifications/" (measurable)
- "At least one backend engineer has approved the API design" (verifiable review)

Bad criteria patterns:
- "Code quality is high" (what does high mean?)
- "The feature works well" (what counts as well?)
- "Performance is acceptable" (acceptable to whom, by what measure?)

---

## Writing Good Artifacts

Artifacts declare what files will be created or modified. Each artifact should have enough information to be actionable.

### Path and kind

Specify the exact file path and its type:

```yaml
- path: src/notifications/router.py
  kind: python
```

### Acceptance criteria

Define what makes the artifact complete. These should be concrete and verifiable:

```yaml
acceptance_criteria:
  - GET /notifications returns paginated list for authenticated user
  - POST /notifications/{id}/read marks notification as read
  - All endpoints require valid JWT authentication
  - Response shapes match the api_design section specification
```

Avoid vague criteria like "code is well-written" or "feature works correctly."

### Dependencies

Declare which other artifacts this one depends on:

```yaml
depends_on:
  - src/notifications/models.py
  - src/notifications/service.py
```

Dependencies help readers understand build order and help AI systems plan implementation sequence.

### Status

Track artifact progress:

- `planned` -- Not yet created
- `in_progress` -- Work has started
- `complete` -- Artifact exists and meets acceptance criteria

---

## Using Templates

The `vibe/stdlib/templates/` directory provides starter templates for common planning patterns. To use a template:

1. Copy the template file to your plans directory
2. Replace placeholder content (marked with `[brackets]`) with real content
3. Add or remove sections as needed for your specific case
4. Update `meta.name` and `meta.description`

Available templates:

| Template | Purpose |
|---|---|
| `overview.vibe` | High-level project overview with problem analysis and approach |
| `architecture.vibe` | Architecture planning with component design and trade-offs |
| `implementation_plan.vibe` | Detailed implementation plan with phases and artifacts |
| `risk_assessment.vibe` | Risk identification, analysis, and mitigation planning |
| `adr_collection.vibe` | Collection of Architecture Decision Records |

Templates import `vibe/stdlib/quality.vibe` by default. You can add additional imports or remove the default as needed.

---

## Common Pitfalls

### Missing context

Starting with sections or artifacts before defining the problem. Without clear context, sections lack framing and reviewers cannot evaluate whether the plan addresses the right problem.

Fix: Always fill in `context.problem` and `context.constraints` before writing sections.

### Wrong section type

Using `analysis` for what should be `design`, or `design` for what should be `specification`. This muddies the document structure and makes it harder to review.

Fix: Ask "what is this section doing?" -- analyzing the current state, proposing a solution, defining precise details, recording a choice, identifying risks, or listing tasks? Match the type to the answer.

### Buried decisions

Making important choices inside section prose without using the `decisions` array. This makes decisions invisible to reviewers and tools.

Fix: If a section contains "we chose X over Y because Z," extract that into a decision record.

### Vague quality criteria

Criteria like "the feature should work well" or "code quality is high." These cannot be evaluated and provide no definition of done.

Fix: Make every criterion specific enough that someone could mark it pass or fail.

### Monolithic documents

Putting everything for a large initiative into a single `.vibe` file. This makes documents unwieldy and prevents reuse.

Fix: Split large plans into focused documents and compose them via imports.

### Skipping status

Leaving `meta.status` unset or not advancing it through the lifecycle. This makes it unclear whether a document is a rough draft or an approved plan.

Fix: Start every document as `draft`. Move to `review` when content is complete. Move to `final` only after review.

### Duplicating imported content

Copying quality criteria or sections from imported documents instead of using imports. This creates maintenance burden and inconsistency.

Fix: Import shared content from stdlib or shared documents. Only add project-specific criteria in the importing document.

---

## Prompt Template for AI

When asking an AI to create a `.vibe` document:

```
Create a VIBE v2 planning document for [feature/initiative].

Requirements:
- Start with context: problem, constraints, assumptions, scope
- Use typed sections: analysis, design, specification, risk, checklist
- Record architectural decisions with options and rationale
- Define specific, measurable quality criteria
- List all artifacts with acceptance criteria
- Import vibe/stdlib/quality.vibe for standard criteria
- Set meta.status to draft
```
