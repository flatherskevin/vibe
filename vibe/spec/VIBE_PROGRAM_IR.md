# VIBE Program IR (v1.0)

This document defines the canonical compiled representation of a VIBE program after parsing all `.vibe` files, resolving imports, and merging sections.

A VIBE runtime SHOULD compile all source `.vibe` files into a single in-memory Program IR before executing any workflow steps.

The purpose of the Program IR is to make VIBE deterministic across runtimes. Two compliant runtimes should produce materially equivalent Program IRs from the same input files.

---

## 1. Purpose

The Program IR exists to separate:

- source authoring syntax
- merge behavior
- runtime execution behavior

This gives VIBE three important properties:

- deterministic program structure
- easier validation and debugging
- consistent runtime execution across AI systems

The Program IR is not required to be written to disk, but runtimes MAY expose it for debugging or validation.

---

## 2. Canonical Structure

A compiled VIBE program is represented as a single object with the following top-level fields:

- `vibe_version`
- `meta`
- `context`
- `tools`
- `artifacts`
- `workflow`
- `validation`
- `sources`
- `errors`

Example conceptual shape:

    {
      "vibe_version": "1.0",
      "meta": { ... },
      "context": { ... },
      "tools": { ... },
      "artifacts": [ ... ],
      "workflow": { ... },
      "validation": [ ... ],
      "sources": [ ... ],
      "errors": [ ... ]
    }

---

## 3. Field Definitions

## 3.1 `vibe_version`

Required.

String representing the VIBE language version.

For VIBE v1:

    "1.0"

---

## 3.2 `meta`

Required.

Object containing program-level metadata.

Recommended fields:

- `name`
- `description`
- `repo_root`
- `runtime_min`
- `runtime_max`
- `repo_write_scope`
- `exec_allowlist`

Example:

    {
      "name": "example_program",
      "description": "Example VIBE project",
      "repo_root": ".",
      "runtime_min": "1.0",
      "runtime_max": "1.x"
    }

### Meta requirements

- `name` should be stable and human-readable
- `repo_root` should typically be `.`
- version fields should be strings
- unknown meta fields may be preserved by the runtime

---

## 3.3 `context`

Optional.

Object containing problem description, constraints, glossary terms, budgets, or other planning context.

Context is not required to be normalized beyond being stored as key/value pairs.

Values may include:

- strings
- multi-line strings
- JSON-like text blobs
- runtime-specific metadata

Example:

    {
      "problem": "Build a CLI that scaffolds a new project",
      "constraints": "- Planning docs first\n- No uncontrolled writes"
    }

### Context notes

- context is primarily for AI planning
- runtimes may compact or summarize context during execution
- context does not itself authorize side effects

---

## 3.4 `tools`

Optional but strongly recommended.

Object mapping tool names to tool contracts.

Example:

    {
      "fs.read": {
        "schema": {
          "args_schema": { ... },
          "result_schema": { ... },
          "errors_schema": { ... }
        }
      }
    }

### Tool normalization

A runtime SHOULD normalize tool definitions into a consistent structure, even if the source `.vibe` file used a simplified shorthand.

Normalized tool fields:

- `name`
- `args_schema`
- `result_schema`
- `errors_schema`

### Tool semantics

Tools define the only permitted side effects.

The Program IR should preserve tools exactly enough for the runtime to:

- validate tool calls
- validate tool results
- enforce tool allowlists
- enforce tool-truth

---

## 3.5 `artifacts`

Optional but strongly recommended.

Array of artifact definitions.

Each artifact represents a file or managed output in the repository.

Normalized artifact fields:

- `path`
- `kind`
- `source`
- `invariants`
- `ownership`
- `write_policy`
- `depends_on`
- `protected_regions`

Example:

    [
      {
        "path": "spec/00_overview.md",
        "kind": "markdown",
        "ownership": "generated",
        "write_policy": "full_overwrite_allowed",
        "depends_on": []
      }
    ]

### Artifact requirements

- `path` must be unique across the Program IR
- `kind` should describe output type
- `ownership` defaults to `generated` if omitted
- `write_policy` defaults to `patch_preferred` for existing files unless otherwise specified
- `depends_on` defaults to an empty list

### Source normalization

Artifact `source` may be one of:

- `generate`
- `template`
- `copy_from`

Runtimes may normalize source into a shape such as:

    {
      "mode": "generate",
      "content": "..."
    }

---

## 3.6 `workflow`

Required.

Object defining program execution behavior.

Required fields:

- `mode`
- `steps`

Valid `mode` values:

- `plan_only`
- `plan_and_apply`

Example:

    {
      "mode": "plan_and_apply",
      "steps": [ ... ]
    }

---

## 3.7 `workflow.steps`

Array of step objects.

Each step should be normalized into a consistent structure with these fields:

- `id`
- `type`
- `goal`
- `inputs`
- `outputs`
- `gate`
- `retry`
- `tools_allowed`

Example:

    {
      "id": "plan_manifest",
      "type": "plan",
      "goal": "Produce a strict plan manifest",
      "inputs": ["meta", "context", "artifacts"],
      "outputs": "{ ... schema ... }",
      "gate": [ ... ],
      "retry": {
        "max": 2,
        "on_fail": "revise"
      },
      "tools_allowed": ["fs.write"]
    }

### Step requirements

- `id` should be unique
- `type` defaults to `generic` if omitted
- `inputs` defaults to an empty list if omitted
- `tools_allowed` may be inherited or runtime-defined if omitted
- `retry.max` should be an integer
- `retry.on_fail` must be either `revise` or `abort`

---

## 3.8 `validation`

Optional but strongly recommended.

Array of validator objects.

Each validator includes:

- `id`
- `type`
- `config`

Example:

    [
      {
        "id": "manifest_schema_valid",
        "type": "json_schema",
        "config": {
          "instance_path": "spec/plan_manifest.json",
          "schema_path": "vibe/stdlib/schemas/plan_manifest.schema.json"
        }
      }
    ]

### Validation requirements

- validator ids must be unique
- validators should be deterministic
- validators are part of the program contract

---

## 3.9 `sources`

Required.

Array recording source provenance for compilation.

Each source entry should include:

- `path`
- `loaded_at`
- optional `sha256`
- optional `size`
- optional `imported_from`

Example:

    [
      {
        "path": "project.vibe",
        "loaded_at": "2026-03-06T12:00:00Z",
        "sha256": "..."
      }
    ]

### Purpose of `sources`

- debugging
- reproducibility
- auditability
- cache invalidation
- compile diagnostics

---

## 3.10 `errors`

Optional.

Array of compile-time errors encountered during parse or merge.

If compilation succeeds, this should usually be empty or omitted.

Each error should include:

- `code`
- `message`
- optional `path`
- optional `line`
- optional `details`

Example:

    [
      {
        "code": "VIBE_MERGE_CONFLICT",
        "message": "Duplicate artifact path: spec/00_overview.md"
      }
    ]

---

## 4. Merge Rules

When multiple `.vibe` files are imported, they must be merged deterministically.

## 4.1 File load order

Runtimes SHOULD process files in deterministic import order beginning at `project.vibe`.

Recommended order:

- depth-first
- respecting declared import order
- cycle-safe

---

## 4.2 `meta` merge

- keys are merged by name
- conflicting scalar values are compile errors
- identical values are allowed

---

## 4.3 `context` merge

- keys are merged by name
- conflicting scalar values are compile errors unless the runtime supports an explicit override extension
- unknown fields are preserved

---

## 4.4 `tools` merge

- merged by tool name
- duplicate names are compile errors

---

## 4.5 `artifacts` merge

- merged by artifact path
- duplicate paths are compile errors unless an override mechanism is explicitly supported

---

## 4.6 `workflow` merge

- `mode` must agree across definitions
- `steps` are appended in import order

---

## 4.7 `validation` merge

- merged by validator id
- duplicate ids are compile errors

---

## 5. Normalization Rules

A runtime SHOULD normalize missing optional values into explicit defaults.

Recommended defaults:

- `ownership`: `generated`
- `write_policy`: `patch_preferred`
- `depends_on`: `[]`
- `type`: `generic`
- `inputs`: `[]`
- `tools_allowed`: inherited or runtime-defined
- `validation`: `[]`

Normalization improves deterministic execution and validation.

---

## 6. Compile-Time Validation

Before execution, the Program IR SHOULD be validated for structural correctness.

Checks should include:

- required top-level fields present
- unique artifact paths
- unique step ids
- unique validator ids
- valid workflow mode
- valid retry values
- valid ownership and write_policy values
- no unresolved imports
- no import cycles

If compilation fails, execution must not continue.

---

## 7. Runtime Relationship

The Program IR is the bridge between:

- source `.vibe` documents
- runtime planning behavior
- runtime execution behavior

A runtime should never execute directly from loosely parsed source if a normalized Program IR can be created first.

This improves:

- determinism
- debuggability
- portability
- auditability

---

## 8. Optional Debug Artifacts

Runtimes MAY emit compiled representations to disk for debugging.

Recommended paths:

    spec/program_ir.json
    spec/compile_errors.json

These files are optional and should not be required for program correctness.

---

## 9. Compatibility Notes

VIBE v1.0 Program IR is intended to be:

- stable enough for tooling
- simple enough for AI agents to reason about
- explicit enough for runtimes to enforce

Future versions may expand the Program IR, but v1 runtimes should preserve the semantics defined here.

---

## 10. Design Philosophy

The Program IR exists because raw prompt-driven execution is too ambiguous.

VIBE makes AI behavior more reliable by forcing execution through:

- deterministic merge rules
- normalized program structure
- explicit tools
- explicit artifacts
- explicit workflow steps
- explicit validation