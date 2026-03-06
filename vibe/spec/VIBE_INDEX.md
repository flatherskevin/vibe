# VIBE v1 Index

This folder contains the normative specification and guidance documents for VIBE v1.0.

## Normative documents (runtimes MUST follow)

- VIBE_SPEC_v1.md
  - The language overview and core concepts.

- VIBE_RUNTIME_CONTRACT.md
  - Required runtime behaviors: parsing, merge rules, plan/apply, tool-truth, gates, retries, evidence, security.

- VIBE_PROGRAM_IR.md
  - Canonical compiled/merged representation that runtimes should produce deterministically.

- VIBE_ERRORS.md
  - Standard error taxonomy and codes.

- VIBE_SCOPE.md
  - Repository write scope rules and protected region semantics.

## Recommended documents (strongly improves reliability)

- VIBE_STEP_TYPES.md
  - Optional step typing and suggested runtime defaults per type.

- VIBE_DEPENDENCIES.md
  - Optional artifact dependency semantics.

- VIBE_AUTHORING_GUIDE.md
  - Guidance for humans and AIs to author robust `.vibe` programs.

- VIBE_REFERENCE_PROGRAM.md
  - Canonical example program and a valid plan manifest example.

## Completeness checklist (v1.0)

A repo is “VIBE v1 complete” when it includes:

- Root entrypoint: project.vibe
- Plan manifest schema: vibe/stdlib/schemas/plan_manifest.schema.json
- Runtime contract + spec docs in vibe/spec/
- A reference program example: vibe/spec/VIBE_REFERENCE_PROGRAM.md

Optional but useful:

- Gates reference: vibe/stdlib/gates.vibe
- Context budget guidance: vibe/stdlib/context_budget.vibe