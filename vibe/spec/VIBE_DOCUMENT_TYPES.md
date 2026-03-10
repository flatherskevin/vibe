# VIBE Document Types (v2.0)

This document defines the section types and document archetypes for VIBE v2.

In v1, step types described what a runtime *does* (plan, generate, apply, validate). In v2, section types describe what a section *contains*. Document archetypes provide guidance on how to organize .vibe files for different purposes.

---

## 1. Section Types

Every section in a .vibe file declares a `type` field. VIBE v2.0 defines six section types.

---

### 1.1 analysis

Understanding and investigating a problem space.

Use for: problem decomposition, research findings, competitive analysis, root cause analysis, requirements gathering, current state descriptions, summaries.

Example titles:

- "Problem Space"
- "Current Architecture"
- "User Research Findings"
- "Root Cause Analysis"
- "Requirements Summary"

Example:

```yaml
- id: problem_space
  type: analysis
  title: Problem Space
  content: |
    The current authentication system uses session cookies stored
    in a monolithic database. This creates a single point of failure
    and prevents horizontal scaling of the API layer.
```

---

### 1.2 design

Proposing how something should work.

Use for: architecture proposals, API design, data models, UI layouts, system interactions, integration patterns, component structure.

Example titles:

- "API Design"
- "Data Model"
- "Component Architecture"
- "Integration Pattern"
- "Migration Approach"

Example:

```yaml
- id: api_design
  type: design
  title: Authentication API Design
  content: |
    The new auth system exposes three endpoints:
    - POST /auth/login -> returns JWT access + refresh tokens
    - POST /auth/refresh -> returns new access token
    - POST /auth/logout -> invalidates refresh token

    Tokens are signed with RS256. Access tokens expire in 15 minutes.
    Refresh tokens expire in 7 days and are stored in a Redis allowlist.
```

---

### 1.3 decision

Recording a choice and its rationale.

Use for: inline decision discussion within a broader document, technology selection notes, approach selection with reasoning, trade-off analysis.

For formal Architecture Decision Records with structured options, chosen outcome, and consequences, use the top-level `decisions` field instead. Sections of type `decision` are for lighter-weight inline discussion where full ADR structure is not needed.

Example titles:

- "Database Selection"
- "Auth Strategy"
- "Framework Choice"
- "Build vs Buy"

Example:

```yaml
- id: db_choice
  type: decision
  title: Database Selection
  content: |
    After evaluating PostgreSQL, MongoDB, and DynamoDB against our
    requirements (strong consistency, JSON support, team familiarity),
    we selected PostgreSQL. The team has extensive PostgreSQL experience
    and the JSONB column type provides the document flexibility we need
    without giving up transactional guarantees.
```

---

### 1.4 specification

Defining exact requirements or interfaces.

Use for: field definitions, protocol specs, schema documentation, contract definitions, format specifications, interface agreements.

Example titles:

- "Field Definitions"
- "API Contract"
- "Wire Format"
- "Event Schema"
- "Configuration Reference"

Example:

```yaml
- id: token_spec
  type: specification
  title: JWT Token Specification
  content: |
    Access token payload:
      sub: string    # User ID
      iss: string    # Issuer (service name)
      exp: number    # Expiration (Unix timestamp)
      iat: number    # Issued at (Unix timestamp)
      roles: [string]  # User roles

    Signing: RS256 with 2048-bit RSA key pair.
    Key rotation: Every 90 days via automated rotation.
```

---

### 1.5 risk

Identifying and assessing risks.

Use for: risk registers, threat models, failure modes, mitigation plans, dependency risks, security considerations, operational concerns.

Example titles:

- "Risk Register"
- "Failure Modes"
- "Security Model"
- "Dependency Risks"
- "Operational Concerns"

Example:

```yaml
- id: auth_risks
  type: risk
  title: Authentication Risk Register
  content: |
    R1: Token theft via XSS
      Likelihood: Medium. Impact: High.
      Mitigation: HttpOnly cookies for refresh tokens, short access
      token expiry, Content Security Policy headers.

    R2: Key compromise
      Likelihood: Low. Impact: Critical.
      Mitigation: Keys stored in secrets manager, automated rotation,
      key revocation endpoint.
```

---

### 1.6 checklist

Actionable items to track or verify.

Use for: migration checklists, launch readiness checks, review criteria, testing plans, acceptance checklists, task lists.

Example titles:

- "Migration Checklist"
- "Launch Readiness"
- "Test Plan"
- "Review Criteria"
- "Deployment Steps"

Example:

```yaml
- id: launch_readiness
  type: checklist
  title: Launch Readiness
  content: |
    - [ ] All endpoints return correct status codes
    - [ ] Rate limiting configured (100 req/min per user)
    - [ ] Monitoring dashboards created
    - [ ] Runbook written for token rotation failure
    - [ ] Load test passes at 2x expected traffic
    - [ ] Security review completed and findings addressed
```

---

## 2. Document Archetypes

Document archetypes are recommended patterns for organizing .vibe files. They are guidance for AI systems and human authors, not enforced by the schema.

A .vibe file does not declare its archetype. Archetypes describe common compositions of section types that work well together for particular purposes.

---

### 2.1 Overview

Purpose: High-level understanding of a project or initiative.

Typical sections:

- analysis (problem statement)
- analysis (users and stakeholders)
- design (proposed approach)
- risk (key risks)
- checklist (success criteria)

When to use: Project kickoffs, initiative proposals, feature briefs. Good starting point for any new planning effort.

---

### 2.2 Architecture

Purpose: Technical design for a system or component.

Typical sections:

- analysis (current state)
- design (proposed architecture)
- design (data model)
- design (API design)
- specification (interface definitions)
- risk (technical risks)

When to use: New services, major refactors, system redesigns, integration planning.

---

### 2.3 Implementation Plan

Purpose: Detailed plan for executing a change.

Typical sections:

- analysis (scope and boundaries)
- design (implementation approach)
- specification (artifact details)
- checklist (tasks)
- checklist (verification steps)

Uses the `artifacts` field extensively to list files that will be created or modified.

When to use: Feature implementation, bug fix planning, migration execution.

---

### 2.4 Risk Assessment

Purpose: Comprehensive risk analysis for a project or decision.

Typical sections:

- analysis (context and background)
- risk (identified risks with likelihood and impact)
- risk (mitigation strategies)
- checklist (monitoring and response plan)
- decision (risk acceptance choices)

When to use: Security reviews, dependency audits, pre-launch assessments, compliance checks.

---

### 2.5 ADR Collection

Purpose: Record of architectural decisions for a project or domain.

Typical sections:

- analysis (background context explaining the decision landscape)

Uses the top-level `decisions` field for each Architecture Decision Record, with full structured options, chosen outcome, rationale, and consequences.

When to use: Technology selection, design pattern choices, API versioning strategy, any set of related architectural decisions.

---

## 3. Quality Criteria Types

The `quality` field supports four types of criteria. These parallel section types in that they categorize what kind of verification is expected.

---

### 3.1 review

Human or AI review against stated criteria.

Use for: document completeness, design review, code review standards, architectural fitness.

Example:

```yaml
- id: q_design_reviewed
  type: review
  description: Architecture covers all integration points
  criteria: |
    Every external system dependency has a documented integration
    pattern. No integration is left as "TBD" or "to be determined."
```

---

### 3.2 test

A testable condition. VIBE does not execute tests, but documents what should be tested.

Use for: acceptance tests, integration test criteria, regression checks, functional requirements.

Example:

```yaml
- id: q_auth_works
  type: test
  description: Authentication flow works end-to-end
  criteria: |
    - POST /auth/login with valid credentials returns 200 and a JWT
    - POST /auth/login with invalid credentials returns 401
    - POST /auth/refresh with valid refresh token returns new access token
    - POST /auth/refresh with expired refresh token returns 401
```

---

### 3.3 metric

A measurable quantity with a target value.

Use for: performance targets, coverage goals, SLA requirements, capacity planning.

Example:

```yaml
- id: q_performance
  type: metric
  description: Authentication endpoint meets performance targets
  criteria: |
    - Login response time < 200ms at p95
    - Token refresh response time < 50ms at p95
    - System handles 1000 concurrent login requests
```

---

### 3.4 checklist

A list of items that must all be true.

Use for: launch readiness, compliance requirements, review checklists, sign-off criteria.

Example:

```yaml
- id: q_security_checklist
  type: checklist
  description: Security review requirements met
  criteria: |
    - All endpoints require authentication
    - Rate limiting is configured
    - Secrets are not logged
    - CORS is restricted to known origins
    - Input validation on all user-supplied fields
```

---

## 4. Extensibility Model

The set of section types and quality criteria types is fixed in v2.0.

Six section types: `analysis`, `design`, `decision`, `specification`, `risk`, `checklist`.

Four quality types: `review`, `test`, `metric`, `checklist`.

This set is intentionally small to keep the format learnable by both humans and AI systems. If a section does not fit neatly into one type, use the closest match. The type is guidance for readers, not a constraint on what content may appear.

Custom types are not supported in v2.0. If the community identifies a clear gap, new types can be added in a point release (v2.1, v2.2). Adding a type is backward-compatible because consumers should already handle unknown type values gracefully (treat as generic content).

The schema enforces type values via an enum. Consumers encountering an unrecognized type value (from a newer schema version) should not reject the document. They should process the section or quality criterion normally and treat the type as informational.

---

## 5. Relationship to Other Documents

- `VIBE_SPEC_v2.md` -- Core format specification defining all top-level fields.
- `VIBE_CONSUMER_CONTRACT.md` -- How consumers should parse and interpret these types.
- `VIBE_AUTHORING_GUIDE.md` -- Guidance on choosing section types and structuring documents.
- `VIBE_REFERENCE_DOCUMENT.md` -- Canonical example showing section types in use.
