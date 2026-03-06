# VIBE Language Specification v1.0

VIBE is a declarative, AI-first language whose primary runtime is an AI agent harness.

A VIBE program is a set of `.vibe` files that define:

- meta: project metadata
- imports: module graph
- context: problem statement + constraints + glossary
- tools: tool schemas (side effects must occur only via tools)
- artifacts: required repo files + invariants
- workflow: steps, gates, retries, tool allowlists
- validation: validators to prove correctness

---

## 1. Files and Program Structure

- All source files end with `.vibe`.
- A program root must include `project.vibe`.
- Additional `.vibe` files may exist in any directory.

### 1.1 Imports

- `imports` is a list of relative file paths to `.vibe` modules.
- Import order matters.
- Imports are merged into a single program before execution.

### 1.2 Merge Rules (Normative)

When multiple files define the same sections:

- `meta`: merged; conflicting scalar keys are an error
- `context`: merged; conflicting scalar keys are an error
- `tools`: merged by tool name; conflicts are an error
- `artifacts`: merged by path; conflicts are an error unless explicitly overridden
- `workflow.steps`: appended in import order
- `validation`: merged by validator id; conflicts are an error

---

## 2. Syntax

VIBE uses a restricted, YAML-like syntax designed to be easy for both humans and AI agents to write and parse.

### 2.1 Syntax Rules

- UTF-8 encoded text
- Spaces only for indentation
- Tabs are invalid
- Keys use `key: value`
- Lists use `- item`
- Multi-line blocks use `|`
- Comments begin with `#`

### 2.2 Required Root Version

Every `.vibe` file must begin with:

    vibe: 1.0

---

## 3. Core Sections

A `.vibe` file may contain the following top-level sections:

- `meta`
- `imports`
- `context`
- `tools`
- `artifacts`
- `workflow`
- `validation`

### 3.1 meta

The `meta` section defines program metadata.

Common fields:

- `name`
- `description`
- `repo_root`
- `runtime_min`
- `runtime_max`
- `repo_write_scope`

Example:

    meta:
      name: example_project
      description: Example VIBE program
      repo_root: .

### 3.2 imports

The `imports` section lists additional `.vibe` modules.

Example:

    imports:
      - vibe/stdlib/tools_strict.vibe
      - vibe/programs/plans_then_build_strict.vibe

### 3.3 context

The `context` section provides problem description, constraints, glossary terms, or other planning context.

Example:

    context:
      problem: |
        Build a simple CLI tool.

      constraints: |
        - Generate planning docs first
        - Use strict plan manifests

### 3.4 tools

The `tools` section defines tool contracts used by the runtime.

A tool may define:

- `args_schema`
- `result_schema`
- `errors_schema`

Example:

    tools:
      fs.write:
        schema:
          args_schema:
            type: object

### 3.5 artifacts

The `artifacts` section defines files the program expects to create, modify, or manage.

Artifact fields may include:

- `path`
- `kind`
- `source`
- `invariants`
- `ownership`
- `write_policy`
- `depends_on`

Example:

    artifacts:
      - path: spec/00_overview.md
        kind: markdown
        ownership: generated

### 3.6 workflow

The `workflow` section defines execution behavior.

Fields include:

- `mode`
- `steps`

Valid modes:

- `plan_only`
- `plan_and_apply`

### 3.7 validation

The `validation` section defines validators used to prove correctness.

Validator fields:

- `id`
- `type`
- `config`

---

## 4. Artifacts

Artifacts represent the files or structured outputs managed by a VIBE program.

Each artifact should define:

- a unique `path`
- a `kind`
- an ownership policy
- optional invariants

### 4.1 Ownership

Supported ownership values:

- `generated`
- `managed`
- `protected`

Definitions:

- `generated`: runtime may overwrite
- `managed`: runtime may patch while preserving protected regions
- `protected`: runtime must not modify

### 4.2 Write Policy

Supported write policy values:

- `patch_preferred`
- `full_overwrite_allowed`

### 4.3 Dependencies

Artifacts may define:

    depends_on:
      - spec/10_architecture.md
      - spec/20_artifacts.json

This helps runtimes determine generation order.

---

## 5. Workflow Semantics

A workflow is a sequence of steps that the runtime executes.

Each step may define:

- `id`
- `type`
- `goal`
- `inputs`
- `outputs`
- `gate`
- `retry`
- `tools_allowed`

### 5.1 Step Types

Recommended step types include:

- `plan`
- `generate`
- `apply`
- `validate`
- `summarize`
- `refactor`
- `generic`

### 5.2 Retry Policy

Each step may include:

    retry:
      max: 2
      on_fail: revise

Supported `on_fail` values:

- `revise`
- `abort`

### 5.3 Gates

Gates are machine-verifiable checks that must pass before continuing.

Supported gate types include:

- `file_exists`
- `file_tree`
- `json_schema`
- `content_rules`
- `command_success`
- `diff_budget`

Example:

    gate:
      - type: file_exists
        config:
          path: spec/plan_manifest.json

---

## 6. Two-Phase Execution Model

VIBE uses a two-phase execution model.

### 6.1 PLAN

In the planning phase, the runtime:

1. parses and merges the program
2. generates planning artifacts under `spec/`
3. produces `spec/plan_manifest.json`

The plan manifest must be validated before execution can continue.

### 6.2 APPLY

In the apply phase, the runtime:

1. reads `spec/plan_manifest.json`
2. executes only operations listed in the manifest
3. performs all side effects through tools
4. runs validations

This separation reduces uncontrolled AI behavior and improves auditability.

---

## 7. Plan Manifest

The plan manifest is the authoritative execution contract between planning and application.

Location:

    spec/plan_manifest.json

The manifest should include:

- metadata
- execution budgets
- operations
- validations

The manifest must validate against:

    vibe/stdlib/schemas/plan_manifest.schema.json

---

## 8. Validators

Validators prove correctness after planning and/or execution.

Common validator types include:

- `file_tree`
- `json_schema`
- `command`
- `content_rules`
- `diff_budget`

Validators are considered part of the program contract.

If validators fail, the run fails.

---

## 9. Tool-Truth

VIBE runtimes must enforce tool-truth.

This means:

- file existence claims must come from filesystem tools
- file contents must come from `fs.read`
- command success must come from `exec.run`
- side effects must come from tools, never from model claims

Agents must not invent repository state.

---

## 10. Security and Scope

VIBE runtimes must enforce repository safety.

Required protections:

- no absolute paths
- no `..` traversal
- write access restricted by `repo_write_scope`
- tool-only side effects

Example:

    repo_write_scope:
      allowed:
        - src/
        - spec/
        - docs/
      forbidden:
        - .git/
        - node_modules/

---

## 11. Runtime Outputs

A runtime should typically generate:

- planning artifacts in `spec/`
- `spec/plan_manifest.json`
- `spec/runlog_compacted.md`

The run log should record:

- steps executed
- tools called
- files modified
- gate results
- validation results

---

## 12. Compatibility

VIBE v1.0 is designed to work well with:

- Claude-based runtimes
- Codex-style runtimes
- OpenAI tool-calling runtimes
- custom agent orchestrators

The language is AI-first, but intentionally constrained so that runtimes can enforce deterministic behavior.

---

## 13. Reference Documents

Additional specification documents are located in:

    vibe/spec/

Important companion docs include:

- `VIBE_RUNTIME_CONTRACT.md`
- `VIBE_PROGRAM_IR.md`
- `VIBE_SCOPE.md`
- `VIBE_ERRORS.md`
- `VIBE_STEP_TYPES.md`
- `VIBE_DEPENDENCIES.md`
- `VIBE_AUTHORING_GUIDE.md`
- `VIBE_REFERENCE_PROGRAM.md`
- `VIBE_RUNTIME_HOOKS.md`
- `VIBE_INDEX.md`

---

## 14. Design Philosophy

VIBE treats AI agents as structured plan executors, not freeform improvisers.

Core principles:

- planning before execution
- schema-first validation
- deterministic runtime behavior
- tool-driven side effects
- auditable results

The goal is not to make AI more creative.

The goal is to make AI execution more reliable.