# VIBE Dependencies (v1)

Dependencies in VIBE v1 express ordering relationships between artifacts and between sections within a document.

Dependencies are a design-time concept. They tell AI planners and human reviewers what must logically come before what. They do not trigger execution or runtime resolution.

---

## 1. Purpose

Dependencies make ordering explicit for:

- AI planners deciding what to write first
- human reviewers understanding document structure
- validation tools checking that referenced content exists
- consumers processing documents in a coherent sequence

Dependencies express logical precedence: "this artifact builds on that one" or "this section assumes that section has been read."

---

## 2. Artifact Dependencies

### 2.1 The `depends_on` Field

Artifacts may declare a `depends_on` field listing paths of other artifacts they build on.

```yaml
artifacts:
  - path: spec/api_design.vibe
    kind: vibe
    description: API design document
    depends_on:
      - spec/architecture.vibe

  - path: spec/data_model.vibe
    kind: vibe
    description: Data model specification
    depends_on:
      - spec/architecture.vibe

  - path: spec/implementation_plan.vibe
    kind: vibe
    description: Implementation plan
    depends_on:
      - spec/api_design.vibe
      - spec/data_model.vibe
```

### 2.2 What Artifact Dependencies Mean

If artifact `A` depends on artifact `B`, this means:

- `B` should be written or reviewed before `A`
- `A` may reference content, decisions, or structure defined in `B`
- a consumer processing artifacts in dependency order will encounter `B` before `A`

Artifact dependencies do not mean:

- `B` must be executed to produce `A`
- `B` must be validated before `A` can be written
- changes to `B` automatically invalidate `A`

### 2.3 Dependency Graph

The set of all artifact dependencies forms a directed acyclic graph (DAG). This graph defines a partial ordering over artifacts.

Any topological sort of the DAG is a valid processing order.

---

## 3. Section Dependencies

### 3.1 The `depends_on` Field for Sections

Sections within a document may declare dependencies on other section IDs in the same document. This expresses content ordering: one section builds on concepts introduced in another.

```yaml
sections:
  - id: requirements_analysis
    type: analysis
    title: Requirements Analysis
    content: |
      Analysis of the core requirements for the authentication system.

  - id: architecture_decisions
    type: decision
    title: Architecture Decisions
    depends_on:
      - requirements_analysis
    content: |
      Based on the requirements analysis, the following architecture
      decisions were made.

  - id: implementation_approach
    type: specification
    title: Implementation Approach
    depends_on:
      - architecture_decisions
    content: |
      Given the architecture decisions, the implementation will follow
      this approach.
```

### 3.2 What Section Dependencies Mean

If section `X` depends on section `Y`, this means:

- `Y` introduces concepts or decisions that `X` builds on
- a reader should read `Y` before `X` for full comprehension
- an AI planner should generate `Y` content before `X` content

Section dependencies are an authoring aid. They help AI systems produce coherent documents where later sections build naturally on earlier ones.

### 3.3 Section Order vs. Section Dependencies

Sections have both a list order (their position in the `sections` array) and optional explicit dependencies.

If no `depends_on` is declared, list order is the implied reading order. When `depends_on` is present, it makes the ordering relationship explicit and machine-verifiable.

Best practice: use `depends_on` when the logical dependency is important and might not be obvious from list position alone.

---

## 4. Cross-Document Dependencies via Imports

Documents that import other `.vibe` files create an implicit dependency on the imported document.

```yaml
imports:
  - vibe/stdlib/quality.vibe
  - spec/shared_context.vibe
```

An import means:

- the imported document's context, quality criteria, or other content is available to this document
- the imported document should be valid before this document references its content
- consumers should process imported documents before the importing document

Cross-document dependencies via imports and artifact-level `depends_on` serve different purposes:

| Mechanism | Scope | Purpose |
|---|---|---|
| `imports` | Document-level | Merge content from another `.vibe` file |
| `depends_on` (artifact) | Artifact-level | Express that one artifact builds on another |

Both create ordering relationships. Imports bring content into scope; artifact dependencies express logical precedence without content merging.

---

## 5. Circular Dependency Detection

### 5.1 Artifact Circular Dependencies

Circular dependencies among artifacts are an error.

Example of an invalid cycle:

```yaml
artifacts:
  - path: spec/api_design.vibe
    depends_on:
      - spec/data_model.vibe

  - path: spec/data_model.vibe
    depends_on:
      - spec/api_design.vibe
```

This is invalid because no topological ordering exists. A consumer or validation tool encountering this cycle MUST report an error.

Recommended error code: `VIBE_CIRCULAR_DEPENDENCY`

### 5.2 Section Circular Dependencies

Circular dependencies among sections within a document are a warning, not an error.

Example:

```yaml
sections:
  - id: api_design
    depends_on:
      - data_model

  - id: data_model
    depends_on:
      - api_design
```

This is a warning because sections exist within a single document and can be read in list order regardless. However, it indicates that the dependency declarations are not accurately representing the authoring order, and the author should revise them.

### 5.3 Import Circular Dependencies

Circular imports (document A imports document B which imports document A) are an error.

See `VIBE_MERGE_SEMANTICS.md` for import resolution rules.

---

## 6. Examples

### 6.1 Artifact Dependency Chain

A feature planning project with a clear dependency chain:

```yaml
artifacts:
  - path: spec/00_overview.vibe
    kind: vibe
    description: Feature overview and goals

  - path: spec/10_architecture.vibe
    kind: vibe
    description: Architecture and design decisions
    depends_on:
      - spec/00_overview.vibe

  - path: spec/20_api_design.vibe
    kind: vibe
    description: API endpoint design
    depends_on:
      - spec/10_architecture.vibe

  - path: spec/30_data_model.vibe
    kind: vibe
    description: Database schema and data model
    depends_on:
      - spec/10_architecture.vibe

  - path: spec/40_implementation_plan.vibe
    kind: vibe
    description: Implementation plan and task breakdown
    depends_on:
      - spec/20_api_design.vibe
      - spec/30_data_model.vibe
```

Dependency graph:

```
00_overview
    |
10_architecture
   / \
20_api   30_data
   \     /
40_implementation
```

Valid processing orders include:

- overview, architecture, api, data, implementation
- overview, architecture, data, api, implementation

### 6.2 Section Dependencies Within a Document

```yaml
sections:
  - id: problem_statement
    type: analysis
    title: Problem Statement
    content: |
      Users cannot reset their passwords without contacting support.

  - id: solution_options
    type: analysis
    title: Solution Options
    depends_on:
      - problem_statement
    content: |
      Three approaches were considered: email-based reset, SMS-based
      reset, and magic link authentication.

  - id: chosen_approach
    type: decision
    title: Chosen Approach
    depends_on:
      - solution_options
    content: |
      Decision: Use email-based password reset with time-limited tokens.
      Rationale: Lowest implementation cost, highest user familiarity.

  - id: implementation_spec
    type: specification
    title: Implementation Specification
    depends_on:
      - chosen_approach
    content: |
      The reset flow requires three new API endpoints and a token
      storage mechanism.
```

### 6.3 Mixed Artifact and Section Dependencies

A document can use both artifact-level and section-level dependencies:

```yaml
artifacts:
  - path: spec/architecture.vibe
    kind: vibe
    description: Architecture document (external dependency)

  - path: spec/auth_feature.vibe
    kind: vibe
    description: This document
    depends_on:
      - spec/architecture.vibe

sections:
  - id: context
    type: analysis
    title: Context
    content: |
      This feature builds on the architecture defined in
      spec/architecture.vibe.

  - id: design
    type: specification
    title: Design
    depends_on:
      - context
    content: |
      The authentication design follows the API gateway pattern
      established in the architecture document.
```

---

## 7. Transitive Dependencies

Dependencies are transitive. If artifact `A` depends on `B` and `B` depends on `C`, then `A` transitively depends on `C`.

Transitive dependencies do not need to be declared explicitly. They are implied by the dependency graph.

Validation tools MAY compute the transitive closure of the dependency graph to:

- verify that all transitive dependencies are satisfiable
- detect long dependency chains that may indicate over-coupling
- report the full set of prerequisites for a given artifact

---

## 8. Validation Rules

### 8.1 Required Checks

A validation tool processing dependencies MUST check:

1. Every `depends_on` path (artifact) or ID (section) references a known target
2. No circular dependencies exist among artifacts
3. No circular imports exist between documents

### 8.2 Recommended Checks

A validation tool SHOULD also check:

1. Section circular dependencies (emit warning)
2. Dependency targets have status `complete` or `draft` (not `abandoned`)
3. Dependency chains are not excessively deep (suggested limit: 10 levels)

---

## 9. Design Philosophy

AI planners and human reviewers both benefit from explicit ordering.

Without dependencies, the ordering of artifacts and sections is implicit -- determined by list position, naming conventions, or tribal knowledge. This is fragile and hard for AI systems to reason about consistently.

Dependencies make ordering a first-class, machine-verifiable property of VIBE documents. They answer the question "what should I read or write first?" without requiring execution machinery.

In VIBE v1, dependencies are a planning tool, not an execution mechanism. They guide the order of thought, not the order of commands.
