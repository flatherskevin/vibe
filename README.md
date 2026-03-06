# VIBE

**VIBE** is an **AI-first instruction language** designed to make AI agents reliable when modifying software systems.

Instead of letting AI freely generate code, VIBE introduces a **structured execution layer** between human intent and AI actions.

The workflow looks like this:

```
Human intent (natural language)
        ↓
AI generates a VIBE program
        ↓
AI produces a structured execution plan
        ↓
AI executes the plan deterministically
```

VIBE acts like **Terraform for AI actions**.

It separates **planning** from **execution**, ensuring that AI systems behave predictably, safely, and repeatably.

---

# The Problem

Modern AI agents are powerful but unreliable when allowed to directly modify codebases or systems.

Common failure modes include:

- hallucinated files
- incomplete implementations
- inconsistent architecture decisions
- uncontrolled side effects
- partially applied changes

These issues occur because most AI workflows combine **planning and execution in a single step**.

---

# The VIBE Solution

VIBE introduces an **intermediate instruction language** that forces AI systems to:

1. **Create a structured plan**
2. **Validate that plan**
3. **Execute the plan deterministically**

Instead of:

```
Human → AI → Code Changes
```

You get:

```
Human → AI → VIBE Program → Plan Manifest → Deterministic Execution
```

This dramatically improves reliability.

---

# Human Workflow

Humans **never write `.vibe` files manually**.

The intended workflow is:

```
1. Human describes intent in natural language
2. AI generates VIBE planning artifacts
3. AI produces a strict plan manifest
4. AI executes the manifest
```

Example prompt:

```
Add authentication middleware to the API server
and create integration tests.
```

The AI generates planning documents and ultimately produces:

```
spec/plan_manifest.json
```

This manifest defines **every repository operation** that will occur.

The runtime executes **only the operations listed in the manifest**.

---

# Core Concepts

## `.vibe` Programs

A VIBE program is a collection of `.vibe` files describing a project.

Example structure:

```
project.vibe

vibe/
  stdlib/
  programs/
  spec/

spec/
  planning documents
  plan_manifest.json
```

The runtime merges `.vibe` files into a **Program IR** before execution.

---

# Execution Model

VIBE programs run in two phases.

## Phase 1 — PLAN

The AI agent:

1. reads `.vibe` files
2. generates planning artifacts in `/spec`
3. produces a strict `spec/plan_manifest.json`

Example planning outputs:

```
spec/
  00_overview.md
  10_architecture.md
  20_artifacts.json
  30_workflow.json
  plan_manifest.json
```

---

## Phase 2 — APPLY

The runtime:

1. reads `spec/plan_manifest.json`
2. executes listed operations
3. uses tools for every side effect
4. validates results

Example operations:

```
write
patch
mkdir
delete
```

Only operations listed in the manifest are allowed.

---

# Tools

Tools define **allowed side effects**.

Example tools:

```
fs.read
fs.write
fs.apply_patch
fs.list
exec.run
```

Tools define schemas including:

- args_schema
- result_schema
- errors_schema

This enforces **tool-truth**.

AI agents cannot claim filesystem changes without tool evidence.

---

# Gates

Workflow steps may include gates.

Gates verify conditions before execution continues.

Example:

```
[
  {
    "type": "file_exists",
    "config": { "path": "spec/plan_manifest.json" }
  }
]
```

Supported gate types include:

- file_exists
- file_tree
- json_schema
- content_rules
- command_success
- diff_budget

---

# Validators

Validators verify correctness after execution.

Examples:

```
file_tree
json_schema
command
content_rules
diff_budget
```

If validation fails, the run fails.

---

# Subagents

VIBE supports **bounded subagents** for complex planning workflows.

Subagents are specialized workers used during the planning phase.

Example roles:

- planner
- researcher
- generator
- validator
- summarizer

Subagents produce **structured handoff artifacts**:

```
spec/subagents/repo_research.json
spec/subagents/artifact_plan.json
spec/subagents/plan_review.json
```

The parent runtime remains responsible for:

- final plan manifest generation
- applying repository changes
- running validators
- enforcing policy

Subagents assist planning but **never bypass the runtime's safety guarantees**.

---

# Example `.vibe` Program

Example root file:

```
vibe: 1.0

imports:
  - vibe/stdlib/tools.vibe
  - vibe/programs/plans_then_build.vibe
```

The imported program defines planning and execution behavior.

---

# Example Plan Manifest

```
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
```

The runtime executes **only these operations**.

---

# Security Model

VIBE runtimes enforce repository safety.

Required protections include:

- no absolute paths
- no path traversal (`..`)
- restricted write scope
- tool-only side effects

Example scope:

```
allowed:
  - src/
  - spec/
  - docs/

forbidden:
  - .git/
  - node_modules/
```

---

# Repository Structure

Recommended structure:

```
project.vibe

vibe/
  stdlib/
    tools.vibe
    validators.vibe
    gates.vibe
    context_budget.vibe
    plan_manifest_schema.vibe

  programs/
    plans_then_build.vibe
    multi_agent_plan_apply.vibe

  spec/
    language specification
```

---

# Reference Documents

Specification files are located in:

```
vibe/spec/
```

Important documents include:

- VIBE_SPEC_v1.md
- VIBE_RUNTIME_CONTRACT.md
- VIBE_PROGRAM_IR.md
- VIBE_SCOPE.md
- VIBE_ERRORS.md
- VIBE_SUBAGENTS.md
- VIBE_REFERENCE_PROGRAM.md

---

# Analogy

| System | Purpose |
|------|------|
| Terraform | Infrastructure planning |
| Kubernetes | Container orchestration |
| Makefiles | Build execution |
| **VIBE** | AI action planning |

---

# Long-Term Vision

VIBE aims to become a **universal execution format for AI agents**.

Possible runtimes include:

- IDE agents
- CI/CD automation
- codebase maintenance agents
- infrastructure automation agents
- autonomous software systems

---

# Project Status

Experimental language specification.

The language is intentionally minimal so multiple AI runtimes can implement it.

---

# License

MIT