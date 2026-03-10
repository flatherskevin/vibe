---
vibe: "1.0"
meta:
  name: "[system_name]_architecture"
  description: "[Technical architecture for a system or component]"
  author: "[claude | human | agent-id]"
  tags:
    - architecture
  status: draft
---

## Context

### Problem

[Describe the technical problem or capability gap this architecture addresses]

### Constraints

[List technical constraints: performance, compatibility, infrastructure, etc.]

### Assumptions

[List technical assumptions: available services, team expertise, etc.]

### Scope

[Define what systems/components are covered]

### Glossary

[Define technical terms specific to this architecture]

## Artifacts

| Path | Kind | Description | Status | Acceptance Criteria |
|------|------|-------------|--------|---------------------|
| [path/to/main/artifact] | [language] | [Primary artifact description] | planned | [Criterion 1]; [Criterion 2] |

## Sections

### Current State
<!-- id: current_state, type: analysis -->

[Describe the current architecture or system state.
What exists today? What are its limitations?]

### Proposed Design
<!-- id: proposed_design, type: design -->

[Describe the target architecture. Include component relationships,
data flow, and integration points.]

### Data Model
<!-- id: data_model, type: design -->

[Define the data structures, schemas, or models.
Include relationships and constraints.]

### API Design
<!-- id: api_design, type: specification -->

[Specify interfaces, endpoints, protocols, or contracts.
Include request/response formats.]

### Technical Risks
<!-- id: technical_risks, type: risk -->

[Identify technical risks: scalability limits, single points of failure,
dependency risks, security considerations.]

## Decisions

### [Primary architectural decision]
<!-- id: dec_primary_approach, status: proposed -->

**Context:** [Why this decision is needed]

**Options:**

- **[option_a]**: [Description of option A]
- **[option_b]**: [Description of option B]

**Chosen:** [chosen_option]

**Rationale:** [Why this option was chosen]

**Consequences:**

- [Consequence 1]

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_design_complete | review | Architecture covers all integration points | Every external dependency and integration point is documented with interface details |
| q_risks_mitigated | review | All identified risks have mitigation strategies | Each risk in the technical risks section has at least one mitigation or acceptance rationale |
