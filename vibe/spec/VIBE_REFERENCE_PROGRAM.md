# VIBE Reference Program (v1.0)

This document provides a canonical, minimal reference program for VIBE v1.0.

It demonstrates:

- A root project.vibe
- Planning-first workflow
- A strict spec/plan_manifest.json
- Manifest-driven validation commands (no hardcoded npm)

Use this as the template for authoring new `.vibe` programs and as a gold standard for runtime behavior.

---

## 1) Minimal project.vibe (reference)

The root entrypoint imports strict tools, the plan manifest schema, and the strict workflow.

Example structure:

    vibe: 1.0

    meta:
      name: reference_program
      description: Minimal VIBE v1 program that plans, emits a manifest, applies it, and validates.
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
        Build a tiny example project scaffold.
      constraints: |
        - Generate planning docs first.
        - Produce spec/plan_manifest.json before any non-spec changes.
        - Apply only manifest operations.

Notes:

- The runtime should compile/merge imports deterministically.
- The workflow is defined by imported modules.

---

## 2) Example spec/plan_manifest.json (valid)

This is an example manifest that conforms to:

    vibe/stdlib/schemas/plan_manifest.schema.json

Example manifest:

    {
      "meta": {
        "vibe_version": "1.0",
        "program_name": "reference_program",
        "created_at": "2026-03-04T00:00:00Z",
        "mode": "plan_and_apply",
        "agent": {
          "provider": "example",
          "model": "example-model"
        }
      },
      "budgets": {
        "max_steps": 50,
        "max_tool_calls": 500,
        "max_files_changed": 200,
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
          "reason": "Create a simple example artifact",
          "content": "Hello from VIBE v1.\n",
          "ownership": "generated",
          "write_policy": "full_overwrite_allowed",
          "depends_on": [
            "spec/00_overview.md",
            "spec/plan_manifest.json"
          ]
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

---

## 3) Manifest-driven validation commands (portable)

To avoid hardcoding commands like npm test, validation commands should come from the manifest.

Example validator entry:

    {
      "id": "smoke_test",
      "type": "command",
      "config": {
        "cmd": "echo OK"
      }
    }

A runtime can interpret this as:

- run exec.run(cmd)
- require exit_code == 0

---

## 4) Recommended authoring pattern

Follow these guidelines when writing `.vibe` programs:

- Always generate planning docs first (spec/*)
- Always produce spec/plan_manifest.json before APPLY
- Put enforcement logic in JSON schemas and validators
- Prefer patches over full overwrites
- Keep workflow steps small and bounded