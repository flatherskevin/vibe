# VIBE Reference Program (v1.0)

This document provides a canonical reference program for VIBE v1.0.

Its purpose is to show how a minimal but complete VIBE program should be structured and interpreted.

This reference is useful for:

- runtime implementers
- AI systems authoring `.vibe` files
- users learning the language
- regression testing of VIBE tooling

It demonstrates:

- a root `project.vibe`
- imports
- planning artifacts
- workflow steps
- plan manifest expectations
- validators
- runtime behavior

---

## 1. Goals of the Reference Program

The reference program is intentionally small.

It should demonstrate the following VIBE properties:

- deterministic parse and merge
- planning before execution
- strict plan manifest generation
- manifest-driven apply
- validator-backed completion
- bounded side effects

The reference program is not meant to be feature-complete.

It is meant to be clear, portable, and representative.

---

## 2. Reference Repository Layout

Recommended minimal layout:

    project.vibe

    vibe/
      stdlib/
        tools_strict.vibe
        gates.vibe
        validators_strict.vibe
        plan_manifest_schema.vibe
      programs/
        plans_then_build_strict.vibe
      spec/
        VIBE_SPEC_v1.md
        VIBE_RUNTIME_CONTRACT.md
        VIBE_REFERENCE_PROGRAM.md

    spec/
      00_overview.md
      10_architecture.md
      20_artifacts.json
      30_workflow.json
      plan_manifest.json
      runlog_compacted.md

This structure illustrates both the language and a typical runtime output directory.

---

## 3. Reference `project.vibe`

A minimal root program may look like:

    vibe: 1.0

    meta:
      name: reference_program
      description: Minimal VIBE reference program
      repo_root: .
      runtime_min: 1.0
      runtime_max: 1.x
      repo_write_scope:
        allowed:
          - spec/
          - src/
          - docs/
          - vibe/
        forbidden:
          - .git/
          - node_modules/
          - dist/
          - build/

    imports:
      - vibe/stdlib/tools_strict.vibe
      - vibe/stdlib/gates.vibe
      - vibe/stdlib/plan_manifest_schema.vibe
      - vibe/stdlib/validators_strict.vibe
      - vibe/programs/plans_then_build_strict.vibe

    context:
      problem: |
        Build a small example repository using a planning-first workflow.

      constraints: |
        - Generate planning artifacts first.
        - Produce spec/plan_manifest.json before any non-spec writes.
        - Apply only operations listed in the manifest.
        - Validate all results before marking the run complete.

This root file defines:

- metadata
- imports
- repository scope
- planning constraints

The imported modules supply most of the behavior.

---

## 4. Expected Planning Outputs

In a compliant run, the planning phase should create at least:

    spec/00_overview.md
    spec/10_architecture.md
    spec/20_artifacts.json
    spec/30_workflow.json
    spec/plan_manifest.json

These files form the planning contract for APPLY.

### 4.1 `spec/00_overview.md`

Human-readable overview of:

- project purpose
- users
- success criteria

### 4.2 `spec/10_architecture.md`

High-level architecture and design decisions.

### 4.3 `spec/20_artifacts.json`

Structured artifact manifest describing expected files.

### 4.4 `spec/30_workflow.json`

Structured workflow summary derived from planning.

### 4.5 `spec/plan_manifest.json`

Authoritative operation list for APPLY.

This file is the bridge between planning and execution.

---

## 5. Reference Workflow Behavior

A typical strict workflow contains three major phases inside the overall run:

### 5.1 Plan

Generate structured planning outputs and a valid manifest.

### 5.2 Apply

Read the plan manifest and perform only the operations listed there.

### 5.3 Validate

Run file, schema, and command validators to confirm success.

This maps cleanly onto VIBE’s overall PLAN → APPLY model.

---

## 6. Reference Plan Manifest

A valid minimal `spec/plan_manifest.json` may look like:

    {
      "meta": {
        "vibe_version": "1.0",
        "program_name": "reference_program",
        "created_at": "2026-03-06T00:00:00Z",
        "mode": "plan_and_apply",
        "agent": {
          "provider": "example",
          "model": "example-model"
        }
      },
      "budgets": {
        "max_steps": 50,
        "max_tool_calls": 500,
        "max_files_changed": 50,
        "diff_budget": {
          "max_lines_added": 500,
          "max_lines_removed": 500
        }
      },
      "operations": [
        {
          "op": "mkdir",
          "path": "src",
          "reason": "Create source directory"
        },
        {
          "op": "write",
          "path": "src/hello.txt",
          "reason": "Create example artifact",
          "content": "Hello from VIBE v1.\n",
          "ownership": "generated",
          "write_policy": "full_overwrite_allowed"
        }
      ],
      "validations": [
        {
          "id": "required_plans_exist",
          "type": "file_tree",
          "config": {
            "required": [
              "spec/00_overview.md",
              "spec/10_architecture.md",
              "spec/20_artifacts.json",
              "spec/30_workflow.json",
              "spec/plan_manifest.json"
            ]
          }
        },
        {
          "id": "manifest_schema_valid",
          "type": "json_schema",
          "config": {
            "instance_path": "spec/plan_manifest.json",
            "schema_path": "vibe/stdlib/schemas/plan_manifest.schema.json"
          }
        }
      ]
    }

This example demonstrates:

- manifest metadata
- execution budgets
- operations
- validations

---

## 7. Reference Step Types

A strict reference workflow commonly uses these step types:

- `plan`
- `apply`
- `validate`
- optional `summarize`

Example conceptual sequence:

    1. generate_planning_docs
    2. plan_manifest
    3. apply_operations
    4. validate_from_manifest
    5. summarize_run

This sequence is not mandatory, but it is strongly recommended.

---

## 8. Expected Runtime Guarantees

A compliant runtime running the reference program should guarantee:

- deterministic import resolution
- deterministic merge behavior
- manifest validation before APPLY
- no non-manifest changes during APPLY
- tool-only side effects
- validator-backed completion

It should also enforce:

- path safety
- repo write scope
- tool allowlists
- diff budgets where configured

---

## 9. Expected Runtime Artifacts

A runtime should usually produce:

- planning docs in `spec/`
- `spec/plan_manifest.json`
- `spec/runlog_compacted.md`

The run log should summarize:

- step execution
- tool calls
- file changes
- gate results
- validator results

---

## 10. Minimal Example Run

A minimal successful run looks like this:

### 10.1 Source load

The runtime loads:

- `project.vibe`
- imported stdlib files
- imported workflow modules

### 10.2 Program compile

The runtime merges source files into a normalized Program IR.

### 10.3 Planning

The runtime generates planning docs and writes `spec/plan_manifest.json`.

### 10.4 Manifest validation

The runtime validates the manifest against:

    vibe/stdlib/schemas/plan_manifest.schema.json

### 10.5 Apply

The runtime performs manifest operations only.

### 10.6 Validate

The runtime runs validators from the manifest and/or program.

### 10.7 Completion

The runtime emits `spec/runlog_compacted.md` and marks the run successful.

---

## 11. What This Reference Program Is Meant to Teach

This reference program is meant to teach five core VIBE habits:

### 11.1 Plan first

Do not modify implementation files before planning is complete.

### 11.2 Use manifests as contracts

The plan manifest is not a suggestion. It is the execution contract.

### 11.3 Use schemas and validators

If something matters, make it machine-checkable.

### 11.4 Limit side effects

All repository mutations should be explicit, bounded, and tool-driven.

### 11.5 Prefer deterministic execution over improvisation

VIBE is not designed to maximize model creativity.

It is designed to maximize execution reliability.

---

## 12. Recommended Use in Testing

Runtime implementers should use this reference program for:

- parser tests
- merge tests
- manifest validation tests
- apply enforcement tests
- regression tests

A runtime that cannot execute the reference program correctly is not ready for broader use.

---

## 13. Relationship to Other Spec Documents

This file is a teaching and reference document.

For normative behavior, see:

- `VIBE_SPEC_v1.md`
- `VIBE_RUNTIME_CONTRACT.md`
- `VIBE_PROGRAM_IR.md`
- `VIBE_SCOPE.md`
- `VIBE_ERRORS.md`

For authoring guidance, see:

- `VIBE_AUTHORING_GUIDE.md`

For runtime extensibility, see:

- `VIBE_RUNTIME_HOOKS.md`

---

## 14. Design Philosophy

Every language benefits from a canonical example.

For VIBE, the reference program is especially important because AI systems learn better from:

- concrete structure
- repeated patterns
- explicit examples

A good reference program makes the whole language easier to implement, easier to author, and easier to trust.