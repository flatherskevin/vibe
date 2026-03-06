# VIBE Subagents (v1.0 Optional Extension)

This document defines an optional subagent model for VIBE v1.0.

Subagents are specialized, bounded workers that help a parent VIBE runtime plan, generate, validate, or summarize work without becoming the final authority over repository mutation.

Subagents are an orchestration feature, not a replacement for the core VIBE execution model.

The parent runtime remains responsible for:

- manifest generation
- manifest validation
- scope enforcement
- tool-truth
- gates
- validators
- final APPLY authority

---

## 1. Purpose

Subagents exist to improve execution quality when a single agent is no longer the best abstraction.

They are most useful when work involves:

- heavy parallelization
- more context than one agent should carry
- distinct specialized domains
- too many tools for one agent to manage well
- bounded research or validation tasks that should be isolated

Subagents should not be introduced by default for simple workflows.

For many tasks, a single well-structured VIBE runtime is the better design.

---

## 2. Design Principles

VIBE subagents should follow these principles:

- one subagent, one clear role
- narrow tool access
- narrow context
- structured outputs
- explicit handoff artifacts
- parent runtime keeps final authority

Subagents are intended to improve modularity and context isolation, not to create uncontrolled agent swarms.

---

## 3. Relationship to Core VIBE

Subagents are optional.

A VIBE program does not need subagents to be valid.

If subagents are used:

- PLAN may delegate bounded work to subagents
- APPLY should remain parent-controlled
- validators may optionally use subagents for specialized checks
- parent runtime must still enforce all core runtime guarantees

A subagent must never be allowed to bypass:

- manifest-only apply
- repo_write_scope
- ownership policy
- protected regions
- tool allowlists
- validation requirements

---

## 4. Recommended Subagent Roles

VIBE v1 recommends a small number of standard subagent roles.

### 4.1 planner

Responsible for:

- decomposing work
- proposing artifact sets
- proposing workflow steps
- drafting manifests

Typical outputs:

- planning documents
- structured planning JSON
- manifest draft fragments

### 4.2 researcher

Responsible for:

- gathering bounded contextual information
- reading source materials
- summarizing relevant evidence
- isolating large-context exploration

Typical outputs:

- research summaries
- dependency notes
- structured evidence documents

### 4.3 generator

Responsible for:

- producing draft artifacts
- generating code or docs
- drafting file content from approved specs

Typical outputs:

- generated file drafts
- patch proposals
- structured generation outputs

### 4.4 validator

Responsible for:

- checking specialized correctness conditions
- running domain-specific validation logic
- reviewing outputs before final acceptance

Typical outputs:

- validation summaries
- structured pass/fail evidence
- issue lists

### 4.5 summarizer

Responsible for:

- compacting long execution state
- producing stable handoff artifacts
- reducing context load for parent runtime

Typical outputs:

- run summaries
- compacted state
- artifact digests

These roles are recommendations, not hard requirements.

---

## 5. Subagent Constraints

Every subagent should have explicit constraints.

Recommended fields:

- `id`
- `role`
- `goal`
- `inputs`
- `outputs`
- `tools_allowed`
- `write_scope`
- `budget`
- `handoff_artifact`

Subagents should be narrower than full VIBE programs.

A subagent should not own full runtime policy.

---

## 6. Canonical Subagent Shape

A runtime may normalize subagents into a structure like:

    {
      "id": "architecture_researcher",
      "role": "researcher",
      "goal": "Summarize existing architecture and constraints",
      "inputs": [
        "spec/00_overview.md",
        "src/"
      ],
      "outputs": {
        "type": "object"
      },
      "tools_allowed": [
        "fs.read",
        "fs.list"
      ],
      "write_scope": [
        "spec/"
      ],
      "budget": {
        "max_steps": 5,
        "max_tool_calls": 25
      },
      "handoff_artifact": "spec/subagents/architecture_research.json"
    }

This is a conceptual structure, not a required on-disk format.

---

## 7. Handoff Artifacts

Every subagent should produce a bounded, explicit handoff artifact.

A handoff artifact is the parent runtime’s contract with the subagent.

Examples:

- `spec/subagents/research_summary.md`
- `spec/subagents/artifact_draft.json`
- `spec/subagents/validation_report.json`

Handoff artifacts should be:

- structured where possible
- small enough to reload efficiently
- machine-checkable when important
- traceable to the subagent that produced them

Subagents should not pass authority implicitly through freeform text alone.

---

## 8. Tool Policy

Subagents should have narrower tool access than the parent runtime.

Recommended examples:

- researcher:
  - `fs.read`
  - `fs.list`

- planner:
  - `fs.read`
  - `fs.list`
  - `fs.write` under `spec/`

- generator:
  - `fs.read`
  - `fs.write`
  - `fs.apply_patch`

- validator:
  - `fs.read`
  - `fs.list`
  - `exec.run`

A subagent should not receive tools it does not need.

Tool minimization improves safety and reliability.

---

## 9. Context Isolation

One of the main reasons to use subagents is context isolation.

A subagent should receive only the context needed for its role.

Recommended inputs include:

- a small set of files
- a small set of artifacts
- a compact problem statement
- a bounded tool set
- a clear output schema

Subagents should not inherit the full parent context by default.

This reduces context sprawl and helps preserve parent runtime focus.

---

## 10. Parent Runtime Authority

The parent runtime must remain the final authority.

This means:

- parent decides whether to invoke subagents
- parent decides whether to accept handoff artifacts
- parent decides whether to include subagent outputs in the manifest
- parent alone performs final APPLY or authorizes APPLY
- parent runs final validators and gates

A subagent may advise, draft, or summarize.

A subagent should not have autonomous final merge authority in VIBE v1.

---

## 11. Parallelization

Subagents may be run in parallel when the tasks are independent.

Good candidates for parallelization:

- multiple research tasks
- code generation for independent files
- separate validator passes
- summarization across independent artifact sets

Parallel execution should still preserve:

- deterministic result collection
- bounded budgets
- explicit handoff artifacts
- final parent-controlled merge

Parallelism is optional and runtime-defined.

---

## 12. Budgeting

Each subagent should have explicit execution budgets.

Recommended budget fields:

- `max_steps`
- `max_tool_calls`
- `max_input_files`
- `max_output_size`
- optional token or latency limits

If a subagent exceeds budget, the parent runtime should reject or retry according to policy.

Subagents should not silently continue beyond limits.

---

## 13. Error Handling

Subagent failures should be reported explicitly.

Recommended fields:

- `subagent_id`
- `role`
- `error_code`
- `message`
- `evidence`

Recommended mappings:

- invalid structured output -> `VIBE_PLAN_OUTPUT_INVALID`
- forbidden tool -> `VIBE_TOOL_NOT_ALLOWED`
- invalid handoff artifact -> `VIBE_VALIDATION_FAILURE`
- exceeded budget -> `VIBE_BUDGET_EXCEEDED`

A subagent failure should not automatically corrupt the parent run.

The parent runtime should decide whether to:

- retry
- replace the subagent
- continue without that result
- abort the full run

---

## 14. Recommended Directory Conventions

If a runtime persists subagent artifacts, recommended locations include:

    spec/subagents/
    spec/subagents/<subagent_id>/

Examples:

    spec/subagents/architecture_research.json
    spec/subagents/codegen_backend.patch
    spec/subagents/validator_report.json

These are conventions, not hard requirements.

---

## 15. Suggested VIBE Authoring Pattern

A good VIBE subagent workflow often looks like this:

1. parent runtime plans top-level work
2. parent identifies tasks worth delegation
3. parent invokes one or more specialized subagents
4. subagents produce structured handoff artifacts
5. parent reviews and normalizes outputs
6. parent generates or updates the manifest
7. parent performs final APPLY
8. parent runs final validators

This keeps the orchestration powerful but bounded.

---

## 16. Example Roles in Practice

Example decomposition for a medium-size code task:

- planner
  - produce workflow breakdown and artifact list

- researcher
  - inspect existing repo structure and summarize architecture

- generator
  - draft implementation files and tests

- validator
  - run targeted checks and summarize issues

- summarizer
  - compact results for the parent run log

This is usually enough specialization without overcomplicating the system.

---

## 17. What Not to Do

Avoid these anti-patterns:

- giving every subagent full repo write access
- letting subagents apply manifest operations independently
- creating too many subagent roles for small tasks
- using freeform handoffs with no structure
- allowing subagents to bypass validators or gates
- turning one linear task into a swarm without clear benefit

Subagents should reduce complexity at runtime, not increase it.

---

## 18. Relationship to Runtime Hooks

Subagents work especially well with runtime hooks.

Hooks may be used to enforce:

- subagent tool restrictions
- subagent budget limits
- subagent approval requirements
- subagent-specific logging
- parent-only APPLY enforcement

This makes subagents more usable in production orchestrators.

---

## 19. Compatibility Guidance

VIBE subagents are intentionally compatible with common industry patterns:

- specialized worker agents
- bounded delegation
- context isolation
- structured handoffs
- parent-orchestrated execution

This makes the model easy to map onto real agent systems without forcing a particular vendor runtime.

---

## 20. Design Philosophy

Subagents are useful when they make the system simpler.

They are not useful when they become the system.

In VIBE v1, subagents are best treated as:

- specialized assistants
- bounded workers
- structured contributors

The runtime remains the source of truth.

That keeps VIBE aligned with its core goal:

deterministic, auditable, policy-enforced AI execution.