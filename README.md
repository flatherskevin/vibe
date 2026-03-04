# VIBE

**VIBE** is an AI-first instruction language designed for building and executing structured plans with AI agents.

Instead of writing code directly, you write `.vibe` programs that describe:

- project goals
- required artifacts
- execution workflows
- validation rules
- allowed tools

An AI runtime (Claude, Codex, etc.) interprets these `.vibe` files and executes them deterministically using a **Plan → Apply workflow**.

VIBE acts like **Terraform for AI agents**.

---

# Why VIBE Exists

Modern AI agents are powerful but unreliable when asked to directly modify codebases.

Common problems include:

- hallucinated files
- uncontrolled side effects
- partial implementations
- inconsistent planning

VIBE solves this by introducing:

- strict schemas
- planning artifacts
- tool-only side effects
- deterministic workflows
- validation gates

This creates **repeatable, auditable AI-driven development workflows**.

---

# Core Concepts

## `.vibe` Programs

A VIBE program is a set of `.vibe` files describing a project.

Example layout:

    project.vibe

    vibe/
      stdlib/
      programs/
      spec/

    spec/
      00_overview.md
      10_architecture.md
      20_artifacts.json
      30_workflow.json
      plan_manifest.json

The runtime merges `.vibe` files into a **Program IR** before execution.

---

# Execution Model

VIBE programs run in two phases.

## Phase 1 — PLAN

The AI agent:

1. reads `.vibe` files
2. generates planning artifacts in `/spec`
3. produces a strict `spec/plan_manifest.json`

The manifest lists every change that will occur.

No uncontrolled modifications are allowed.

---

## Phase 2 — APPLY

The runtime:

1. reads the plan manifest
2. executes listed operations
3. uses tools for every side effect
4. validates results

Supported operations include:

    write
    patch
    mkdir
    delete

---

# Example `.vibe` Program

Example root file:

    vibe: 1.0

    meta:
      name: example_project
      description: Example VIBE program
      repo_root: .

    imports:
      - vibe/stdlib/tools_strict.vibe
      - vibe/programs/plans_then_build_strict.vibe

    context:
      problem: |
        Build a simple example project.

      constraints: |
        - Generate planning docs first
        - Produce plan manifest before applying changes

---

# Example Plan Manifest

The plan manifest controls execution.

Example:

    {
      "meta": {
        "vibe_version": "1.0",
        "program_name": "example_project",
        "mode": "plan_and_apply"
      },
      "operations": [
        {
          "op": "mkdir",
          "path": "src",
          "reason": "create source directory"
        },
        {
          "op": "write",
          "path": "src/hello.txt",
          "reason": "example file",
          "content": "Hello VIBE\n"
        }
      ]
    }

The runtime executes **only these operations**.

---

# Tools

Tools define allowed side effects.

Common tools include:

    fs.read
    fs.write
    fs.apply_patch
    fs.list
    exec.run

Tools define schemas including:

- args_schema
- result_schema
- errors_schema

The runtime enforces **tool-truth**:

Agents cannot claim filesystem changes without tool evidence.

---

# Gates

Workflow steps may include gates.

Gates verify conditions before proceeding.

Example gate:

    [
      {
        "type": "file_exists",
        "config": { "path": "spec/plan_manifest.json" }
      }
    ]

Supported gate types include:

- file_exists
- file_tree
- json_schema
- content_rules
- command_success
- diff_budget

---

# Validators

After execution, validators verify correctness.

Common validators include:

    file_tree
    json_schema
    command
    content_rules

If validation fails, the run fails.

---

# Security Model

VIBE runtimes enforce repository safety.

Required protections include:

- no absolute paths
- no path traversal (`..`)
- restricted write scope
- tool-only side effects

Example write scope:

    allowed:
      - src/
      - spec/
      - docs/

    forbidden:
      - .git/
      - node_modules/

---

# Typical Workflow

1. Write a `.vibe` program.

2. Ask an AI agent to run a VIBE runtime.

3. The agent generates planning docs:

    spec/
      00_overview.md
      10_architecture.md
      20_artifacts.json
      30_workflow.json

4. The agent generates:

    spec/plan_manifest.json

5. The runtime applies the manifest operations.

6. Validators confirm success.

---

# Example Prompt for an AI Agent

Example system prompt:

    You are a VIBE runtime.

    1. Parse all .vibe files starting at project.vibe
    2. Compile them into a Program IR
    3. Generate planning documents
    4. Generate spec/plan_manifest.json
    5. Apply operations listed in the manifest
    6. Validate results
    7. Produce spec/runlog_compacted.md

---

# Repository Structure

Recommended structure:

    project.vibe

    vibe/
      stdlib/
      programs/
      spec/

    spec/
      planning documents
      plan_manifest.json

---

# Reference Documents

Specification files are located in:

    vibe/spec/

Important documents include:

- VIBE_SPEC_v1.md
- VIBE_RUNTIME_CONTRACT.md
- VIBE_PROGRAM_IR.md
- VIBE_SCOPE.md
- VIBE_ERRORS.md
- VIBE_REFERENCE_PROGRAM.md

---

# Design Philosophy

VIBE treats AI agents as deterministic executors of structured plans.

Core principles:

- planning before execution
- schema-first validation
- minimal implicit behavior
- tool-driven state changes
- reproducible runs

---

# Future Versions

Possible future improvements include:

- parallel workflows
- remote tool support
- richer dependency graphs
- distributed agent execution
- streaming execution logs

---

# License

Choose any license appropriate for your project.

MIT is recommended for open AI tooling.

---

# Contributing

Contributions are welcome.

Before submitting changes:

- ensure new features are documented in `/vibe/spec`
- maintain backward compatibility with `vibe: 1.0`
- update the reference program if behavior changes