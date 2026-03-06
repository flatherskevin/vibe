# VIBE Artifact Dependencies (v1.0)

This document defines dependency semantics for VIBE artifacts.

Dependencies are optional in VIBE v1.0, but strongly recommended for non-trivial programs.

They allow runtimes to determine generation order and prevent invalid execution sequences.

---

## 1. Purpose

Artifact dependencies help express that one output requires another output to exist first.

This improves:

- planning order
- execution order
- runtime determinism
- validation correctness
- AI reasoning quality

Dependencies are especially useful when a program generates:

- planning docs
- manifests
- implementation files
- tests
- derived documentation

---

## 2. `depends_on`

Artifacts may declare:

    depends_on:
      - spec/10_architecture.md
      - spec/20_artifacts.json

The `depends_on` field is a list of artifact paths that must be available before generating or applying the dependent artifact.

Example:

    - path: src/main.ts
      kind: typescript
      depends_on:
        - spec/10_architecture.md
        - spec/20_artifacts.json

---

## 3. Dependency Semantics

If artifact `A` depends on artifact `B`, then:

- `B` must exist before `A` is generated or finalized
- `B` should satisfy its own invariants first if the runtime supports staged validation
- the runtime should not generate `A` before prerequisites are satisfied

Dependencies express execution order, not ownership or permission.

---

## 4. Common Dependency Patterns

## 4.1 Planning docs before manifest

Typical planning chain:

- `spec/00_overview.md`
- `spec/10_architecture.md`
- `spec/20_artifacts.json`
- `spec/30_workflow.json`
- `spec/plan_manifest.json`

Example relationships:

- `spec/plan_manifest.json` depends on:
  - `spec/00_overview.md`
  - `spec/10_architecture.md`
  - `spec/20_artifacts.json`
  - `spec/30_workflow.json`

---

## 4.2 Implementation depends on planning

Typical implementation file dependencies:

- source files depend on architecture and artifact manifest
- tests depend on implementation files and architecture docs
- docs may depend on implementation state or planning docs

Example:

    - path: src/main.ts
      depends_on:
        - spec/10_architecture.md
        - spec/20_artifacts.json

    - path: tests/main.test.ts
      depends_on:
        - src/main.ts
        - spec/10_architecture.md

---

## 5. Runtime Ordering

A runtime SHOULD build a dependency graph across artifacts.

Recommended behavior:

1. collect artifact nodes
2. collect dependency edges
3. topologically sort
4. generate/apply in valid order

If no dependencies are declared, runtime may use source order or workflow order.

Dependencies improve precision, but are not required for basic v1 programs.

---

## 6. Missing Dependencies

If an artifact depends on a path that is not defined or not present when required, the runtime should treat this as an execution or planning failure.

Recommended error codes:

- undefined dependency during compile → `VIBE_INVALID_PROGRAM`
- dependency missing during execution → `VIBE_PLAN_OUTPUT_INVALID` or `VIBE_OPERATION_FAILED` depending on phase

The exact error may vary by runtime stage.

---

## 7. Cycles

Dependency cycles are invalid.

Example invalid cycle:

- `src/main.ts` depends on `tests/main.test.ts`
- `tests/main.test.ts` depends on `src/main.ts`

A runtime SHOULD detect cycles before execution.

Recommended error:

    VIBE_INVALID_PROGRAM

---

## 8. Dependency Scope

Dependencies should usually refer to artifacts known to the program.

Recommended scope:

- artifact paths declared in `artifacts`
- runtime-generated planning outputs
- manifest-controlled files

Dependencies should not be used to refer to arbitrary unknown files unless the runtime explicitly supports that model.

---

## 9. Interaction with Workflow Steps

Dependencies do not replace workflow steps.

Instead:

- workflow steps define what happens
- dependencies define ordering constraints among artifacts

For example:

- a `plan` step may produce several planning docs
- dependencies ensure `spec/plan_manifest.json` comes last
- an `apply` step may then materialize implementation artifacts in dependency order

---

## 10. Dependency Validation

A runtime SHOULD validate dependencies before generation.

Recommended checks:

- every dependency path is syntactically valid
- dependency targets are known or resolvable
- no cycles exist
- topological ordering is possible

Optional checks:

- dependency target invariants already satisfied
- dependency target ownership allows required operation

---

## 11. Transitive Dependencies

Runtimes MAY reason about transitive dependencies.

Example:

- `tests/main.test.ts` depends on `src/main.ts`
- `src/main.ts` depends on `spec/10_architecture.md`

This implies `tests/main.test.ts` transitively depends on `spec/10_architecture.md`

A runtime does not need to record transitive dependencies explicitly if topological ordering is already computed.

---

## 12. Recommended Patterns for VIBE Programs

Recommended dependency conventions:

Planning artifacts:

- `spec/10_architecture.md` depends on `spec/00_overview.md`
- `spec/20_artifacts.json` depends on `spec/10_architecture.md`
- `spec/30_workflow.json` depends on `spec/20_artifacts.json`
- `spec/plan_manifest.json` depends on all planning docs

Implementation artifacts:

- source files depend on architecture and artifacts manifest
- test files depend on source files
- generated docs depend on source or planning docs as appropriate

---

## 13. Minimal Example

Example dependency declaration:

    artifacts:
      - path: spec/10_architecture.md
        kind: markdown

      - path: spec/20_artifacts.json
        kind: json
        depends_on:
          - spec/10_architecture.md

      - path: src/main.ts
        kind: typescript
        depends_on:
          - spec/20_artifacts.json

This ensures architecture is defined before artifact planning, and artifact planning is complete before implementation generation.

---

## 14. Design Philosophy

AI agents often struggle with implicit ordering.

Dependencies make ordering explicit.

That makes VIBE programs:

- easier to reason about
- easier to validate
- safer to execute
- more deterministic across runtimes