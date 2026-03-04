# VIBE Runtime Contract (v1.0)

This document defines the REQUIRED and RECOMMENDED behaviors for any AI agent or runtime that interprets `.vibe` files.

The goal is to make `.vibe` programs deterministic and portable across different AI models (Claude, Codex, etc.) by enforcing strict execution rules.

---

## Core Principles

A VIBE runtime must enforce the following principles:

- Deterministic parsing and merging of `.vibe` files
- Strict schema validation for structured outputs
- Tool-truth: repository state must come from tool results
- Two-phase execution (PLAN → APPLY)
- Bounded retries and execution budgets
- Evidence-based completion and logging

---

## Program Lifecycle

A VIBE runtime processes programs in five phases.

1. Parse
2. Compile
3. Plan
4. Apply
5. Validate

---

## Phase 1 — Parse

The runtime loads `.vibe` files starting at `project.vibe`.

Requirements:

- Only UTF-8 files are allowed.
- Indentation must use spaces.
- Tabs are invalid.
- Duplicate keys within the same block are errors.

If parsing fails the runtime must return:

VIBE_PARSE_ERROR

---

## Phase 2 — Compile

The runtime resolves imports and merges files into a single **Program IR** as defined in:

VIBE_PROGRAM_IR.md

Compile-time requirements:

- Import paths must resolve.
- Import cycles are forbidden.
- Artifact paths must be unique.
- Tool names must be unique.
- Validator IDs must be unique.

Compile failures must return one of:

VIBE_IMPORT_NOT_FOUND  
VIBE_IMPORT_CYCLE  
VIBE_MERGE_CONFLICT  
VIBE_INVALID_PROGRAM

---

## Phase 3 — Plan

If workflow.mode is:

plan_only  
or  
plan_and_apply

the runtime must first execute the planning phase.

Planning requirements:

- Planning artifacts must be created under `spec/`
- The runtime must produce `spec/plan_manifest.json`
- The manifest must validate against the schema located at:

vibe/stdlib/schemas/plan_manifest.schema.json

Planning may not modify implementation files unless explicitly allowed.

Planning failures must return:

VIBE_PLAN_OUTPUT_INVALID  
VIBE_PLAN_MANIFEST_MISSING  
VIBE_PLAN_MANIFEST_INVALID

---

## Phase 4 — Apply

If workflow.mode is `plan_and_apply`, the runtime executes the plan.

Execution rules:

- Only operations defined in `spec/plan_manifest.json` may modify the repository.
- All side effects must occur through tools.
- The runtime must reject changes outside the manifest.

Allowed operation types may include:

write  
patch  
mkdir  
delete

Apply-phase errors include:

VIBE_OPERATION_NOT_PERMITTED  
VIBE_OPERATION_FAILED  
VIBE_NON_MANIFEST_CHANGE_ATTEMPT

---

## Tool Execution

Tools represent the only permitted side effects.

Each tool may define:

args_schema  
result_schema  
errors_schema

The runtime must:

- Validate tool arguments against args_schema
- Validate tool responses against result_schema
- Return structured errors using errors_schema

If tool validation fails the runtime must return:

VIBE_TOOL_ARGS_INVALID  
VIBE_TOOL_RESULT_INVALID

If a tool execution fails:

VIBE_TOOL_FAILURE

---

## Tool-Truth Policy

AI agents must not invent repository state.

The runtime must enforce:

- File existence claims must come from filesystem tools
- File contents must come from fs.read
- Command success must come from exec.run results

Claims without tool evidence must be rejected.

---

## Gates

Workflow steps may include gate checks.

Gate checks must be executable and machine-verifiable.

Supported gate types include:

file_exists  
file_tree  
json_schema  
content_rules  
command_success  
diff_budget

Example gate logic:

- ensure a file exists
- ensure JSON matches schema
- ensure tests exit with code 0
- ensure patch size stays under diff budget

If gates fail the runtime must return:

VIBE_GATE_FAILURE

---

## Retry Policy

Each step defines retry behavior.

retry.max defines the maximum retries.

retry.on_fail may be:

revise  
abort

Runtime requirements:

- Maximum attempts = retry.max + 1
- Steps must never loop indefinitely

If budgets are exceeded:

VIBE_BUDGET_EXCEEDED

---

## Validation Phase

After APPLY, the runtime runs validators defined in the program.

Typical validators include:

- file_tree
- json_schema
- content_rules
- command

Validators must produce pass/fail results.

If any validator fails:

VIBE_VALIDATION_FAILURE

---

## Execution Logging

The runtime should produce a compact run log.

Recommended file:

spec/runlog_compacted.md

Each step entry should include:

- step id
- attempt number
- tool calls performed
- files changed
- gate results
- remaining tasks

Example entry:

Step: plan_manifest  
Attempt: 1  
Tools: fs.write(spec/plan_manifest.json)  
Files Changed: spec/plan_manifest.json  
Gate Result: PASS

---

## Security Requirements

Runtimes must enforce repository safety.

Required protections:

- Absolute paths are forbidden
- Path traversal ("..") is forbidden
- Writes must respect repo_write_scope rules
- Network access should be disabled unless explicitly allowed

High-risk commands such as destructive shell operations should be blocked unless explicitly permitted.

---

## Completion Criteria

A VIBE program execution is considered successful only if:

- The plan manifest exists and validates
- All manifest operations execute successfully
- All gates pass
- All validators pass

The runtime should return a final execution report summarizing:

- steps executed
- operations applied
- validations run
- evidence of success