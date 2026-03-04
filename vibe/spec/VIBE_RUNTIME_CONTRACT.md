# VIBE Runtime Contract (v1.0)

This document defines the REQUIRED and RECOMMENDED behaviors for any AI agent or harness that interprets `.vibe` files.

Goal: Make `.vibe` programs reliable across different models (Claude, Codex, etc.) by enforcing:
- deterministic parsing/merging
- strict structured outputs
- tool-truth (no imaginary side effects)
- gated execution
- bounded retries
- evidence-based completion

---

## 1) Definitions

- **Program**: The merged result of all imported `.vibe` files starting from `project.vibe`.
- **PLAN phase**: Produces planning docs and `spec/plan_manifest.json`. NO repository mutations except writing planning artifacts explicitly allowed for planning output.
- **APPLY phase**: Executes operations listed in `spec/plan_manifest.json` using tools only.
- **Tool-truth**: If a claim depends on repository state or command output, it must be backed by tool results.

---

## 2) Deterministic Parse and Merge (REQUIRED)

### 2.1 Parse rules
The runtime MUST:
- Parse only the restricted VIBE-Doc subset used in this repo.
- Reject tabs, invalid indentation, and duplicate keys within the same map level.
- Treat unknown top-level keys as an error unless explicitly configured to allow extensions.

### 2.2 Import resolution
- Imports MUST be resolved as relative paths from the importing file’s directory.
- Imports MUST be loaded in listed order.
- Cycles MUST be detected and rejected.

### 2.3 Merge rules (normative)
When merging modules into the program:
- `meta`: merge keys; conflicting scalar values are an error
- `context`: merge keys; later imports may add keys; conflicting scalars are an error
- `tools`: merge by tool name; conflicts are an error
- `artifacts`: merge by `path`; conflicts are an error unless `override: true` is supported and set
- `workflow.steps`: appended in import order
- `validation`: merge by validator `id`; conflicts are an error

---

## 3) Structured Outputs (REQUIRED)

Whenever a workflow step defines `outputs` as a JSON schema, the runtime MUST:
- Require the model to emit an output that validates against the schema
- Reject extra keys if `additionalProperties: false` is present
- If invalid:
  - apply the step retry policy (revise/abort)
  - include validation errors back to the model (as plain text) so it can correct

The runtime SHOULD prefer model APIs that support strict structured outputs when available.

---

## 4) Two-Phase Execution: PLAN → APPLY (REQUIRED)

### 4.1 PLAN phase
In PLAN phase, the runtime MUST:
1. Parse/merge the program
2. Produce planning artifacts under `spec/` as defined by `artifacts`
3. Produce `spec/plan_manifest.json` that validates against:
   - `vibe/stdlib/schemas/plan_manifest.schema.json`
4. Validate plan manifest schema compliance before moving on

In PLAN phase, the runtime MUST NOT:
- Modify non-spec artifacts (implementation files) unless the workflow step explicitly allows it and the program intends it.
- Claim to have changed repo state without tool calls.

### 4.2 APPLY phase
In APPLY phase, the runtime MUST:
1. Load `spec/plan_manifest.json`
2. Execute ONLY the operations listed in `plan_manifest.operations`
3. Use tools for every side effect (write/patch/mkdir/delete/commands)
4. Collect evidence from tools (results, exit codes, diffs)
5. Run validations defined in `plan_manifest.validations` and/or `validation:` blocks
6. Produce a final execution report

The runtime MUST NOT:
- Perform operations not listed in the manifest
- Expand scope without regenerating the manifest (unless explicitly configured)

---

## 5) Tool Interface and Tool-Truth (REQUIRED)

### 5.1 Tool contracts
For each tool:
- validate args against `args_schema` (if present)
- validate results against `result_schema` (if present)
- on tool error, produce an error object matching `errors_schema` (if present)

### 5.2 Tool-truth policy
The runtime MUST enforce:
- The agent may only claim a file exists, contains content, or has changed if it has read it via tools or written/patched it via tools.
- The agent may only claim a command succeeded if it has tool evidence from `exec.run` with `exit_code: 0`.

If a step output includes statements about state, the runtime SHOULD attach a short list of tool evidence references in the run log.

---

## 6) Gates: Executable Checks (REQUIRED)

A step’s `gate` is expected to be either:
- a JSON array of gate checks (preferred), or
- a legacy natural-language string (discouraged)

### 6.1 Gate checks format (preferred)
Gate checks MUST follow:

```json
[
  { "type": "file_exists", "config": { "path": "spec/plan_manifest.json" } },
  { "type": "json_schema", "config": { "instance_path": "spec/plan_manifest.json", "schema_path": "..." } }
]