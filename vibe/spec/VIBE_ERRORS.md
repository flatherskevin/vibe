# VIBE Error Taxonomy (v1.0)

This document defines standard error codes for VIBE runtimes.

These codes allow VIBE tooling, orchestrators, and users to reason about failures consistently across implementations.

A compliant runtime SHOULD emit these error codes whenever applicable.

---

## 1. Goals

The VIBE error taxonomy exists to provide:

- deterministic failure categories
- portable runtime behavior
- easier debugging
- machine-readable run diagnostics
- consistent policy enforcement

Errors should be structured whenever possible.

A runtime SHOULD return errors with at least:

- `code`
- `message`

Optional fields:

- `path`
- `line`
- `step_id`
- `details`
- `evidence`

---

## 2. Parse Errors

## `VIBE_PARSE_ERROR`

The runtime could not parse a `.vibe` file.

Examples:

- invalid indentation
- tab characters where not allowed
- malformed key/value syntax
- invalid list syntax
- malformed block scalar usage

Typical response:

    {
      "code": "VIBE_PARSE_ERROR",
      "message": "Invalid indentation in project.vibe",
      "path": "project.vibe",
      "line": 12
    }

---

## 3. Import Errors

## `VIBE_IMPORT_NOT_FOUND`

A referenced import could not be resolved.

Examples:

- missing file
- wrong relative path
- inaccessible imported module

---

## `VIBE_IMPORT_CYCLE`

An import cycle was detected in the program graph.

Examples:

- `project.vibe` imports `a.vibe`
- `a.vibe` imports `b.vibe`
- `b.vibe` imports `a.vibe`

Execution must not continue after an import cycle is detected.

---

## 4. Merge Errors

## `VIBE_MERGE_CONFLICT`

Two or more files declared incompatible values during merge.

Examples:

- duplicate artifact path
- duplicate validator id
- conflicting `meta.name`
- conflicting workflow mode

---

## `VIBE_INVALID_PROGRAM`

The compiled program is structurally invalid.

Examples:

- missing `workflow`
- missing `meta`
- invalid workflow mode
- invalid ownership value
- duplicate step ids after normalization

This is broader than a merge conflict and refers to program invalidity after parse and merge are complete.

---

## 5. Schema Errors

## `VIBE_INVALID_SCHEMA`

A schema declared by the program is itself invalid.

Examples:

- malformed JSON schema
- unsupported schema structure
- invalid schema reference path

This applies to:

- tool schemas
- outputs schemas
- manifest schema references
- validator schemas

---

## 6. Planning Errors

## `VIBE_PLAN_OUTPUT_INVALID`

A planning step emitted output that did not conform to its declared schema.

Examples:

- missing required fields in step outputs
- invalid JSON shape
- extra properties when forbidden

---

## `VIBE_PLAN_MANIFEST_MISSING`

A plan manifest was required but was not produced.

Example:

- workflow mode is `plan_and_apply`
- `spec/plan_manifest.json` does not exist after planning

---

## `VIBE_PLAN_MANIFEST_INVALID`

The plan manifest exists but is invalid.

Examples:

- not parseable as JSON
- fails schema validation
- missing required fields such as `operations`

---

## 7. Budget and Limit Errors

## `VIBE_BUDGET_EXCEEDED`

The runtime exceeded a declared budget.

Examples:

- max steps exceeded
- max tool calls exceeded
- max files changed exceeded
- diff budget exceeded

Optional details may include the specific budget that was violated.

Example:

    {
      "code": "VIBE_BUDGET_EXCEEDED",
      "message": "Diff budget exceeded",
      "details": {
        "max_lines_added": 200,
        "actual_lines_added": 312
      }
    }

---

## 8. Tool Errors

## `VIBE_TOOL_NOT_ALLOWED`

The current step attempted to use a tool that was not allowed.

Examples:

- `exec.run` called in a step with only `fs.write`
- undeclared tool called by the runtime

---

## `VIBE_TOOL_ARGS_INVALID`

A tool call failed argument validation.

Examples:

- missing required `path`
- invalid argument type
- extra unexpected fields

---

## `VIBE_TOOL_RESULT_INVALID`

A tool returned a result that did not match its declared schema.

Examples:

- missing required result fields
- invalid field types
- malformed tool result object

---

## `VIBE_TOOL_FAILURE`

The tool itself failed to execute.

Examples:

- file not found
- patch failed to apply
- command returned infrastructure error
- shell execution unavailable

`VIBE_TOOL_FAILURE` does not necessarily mean the model behaved incorrectly. It may indicate an external execution problem.

---

## 9. Gate Errors

## `VIBE_GATE_FAILURE`

A gate check failed.

Examples:

- required file not found
- command exited non-zero
- JSON schema gate failed
- forbidden pattern found
- diff budget exceeded for step

Gate failures should ideally include:

- which gate failed
- what evidence caused the failure
- which step was affected

---

## 10. Validation Errors

## `VIBE_VALIDATION_FAILURE`

One or more validators failed after planning or apply.

Examples:

- `file_tree` validator failed
- `json_schema` validator failed
- test command failed
- content rules were violated

This error indicates that the program did not satisfy its completion contract.

---

## 11. Apply Errors

## `VIBE_OPERATION_NOT_PERMITTED`

A requested manifest operation violated runtime policy.

Examples:

- write outside allowed scope
- modification of protected artifact
- forbidden path
- blocked command execution

---

## `VIBE_OPERATION_FAILED`

An operation listed in the manifest could not be applied.

Examples:

- patch rejected
- file write failed
- directory create failed
- delete failed

This error means the operation was allowed in principle but failed in execution.

---

## `VIBE_NON_MANIFEST_CHANGE_ATTEMPT`

A runtime or agent attempted to change repository state outside the approved manifest.

Examples:

- direct write not listed in `spec/plan_manifest.json`
- undeclared file modification during apply

This is a serious runtime enforcement failure and should usually abort execution immediately.

---

## 12. Security Errors

A runtime MAY use existing error codes for security failures, but SHOULD prefer the following mapping:

- forbidden path write → `VIBE_OPERATION_NOT_PERMITTED`
- blocked command → `VIBE_OPERATION_NOT_PERMITTED`
- invalid traversal path → `VIBE_OPERATION_NOT_PERMITTED`

A separate security namespace is not required in v1, but runtimes may extend it.

---

## 13. Error Severity

Runtimes MAY annotate errors with severity.

Suggested severities:

- `fatal`
- `error`
- `warning`
- `info`

Recommended defaults:

- parse/import/merge/program/schema errors → `fatal`
- gate/validation/apply/tool errors → `error`
- advisory compaction/logging issues → `warning`

Severity is optional in v1.

---

## 14. Error Reporting Format

Recommended structured format:

    {
      "code": "VIBE_GATE_FAILURE",
      "message": "Required file not found",
      "step_id": "plan_manifest",
      "details": {
        "gate_type": "file_exists",
        "path": "spec/plan_manifest.json"
      },
      "evidence": {
        "tool": "fs.list",
        "result": { ... }
      }
    }

This format is recommended but not strictly required.

---

## 15. Runtime Behavior on Error

Recommended runtime behavior:

- parse/import/merge/program errors:
  - stop immediately
- planning errors:
  - follow retry policy if applicable
- tool/gate/validation errors:
  - follow step retry policy if applicable
- non-manifest or forbidden operations:
  - abort immediately

A runtime SHOULD not continue silently after a fatal error.

---

## 16. Extensibility

Runtimes may define additional custom error codes, but SHOULD preserve all standard VIBE codes.

Custom codes should preferably use a namespaced pattern such as:

    VIBE_VENDOR_CUSTOM_ERROR

This avoids collisions while preserving portability.

---

## 17. Design Philosophy

VIBE errors are intended to make failures:

- explicit
- machine-readable
- actionable
- enforceable

AI systems are often vague when they fail.

VIBE runtimes should not be vague.