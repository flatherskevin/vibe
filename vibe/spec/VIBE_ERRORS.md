# VIBE Error Taxonomy (v1.0)

Standard error codes used by VIBE runtimes.

---

## Parse Errors

VIBE_PARSE_ERROR  
Invalid syntax or indentation.

VIBE_IMPORT_NOT_FOUND  
Import path cannot be resolved.

VIBE_IMPORT_CYCLE  
Import graph contains a cycle.

---

## Merge Errors

VIBE_MERGE_CONFLICT  
Conflicting definitions across modules.

VIBE_INVALID_SCHEMA  
Invalid JSON schema definition.

VIBE_INVALID_PROGRAM  
Compiled program IR violates requirements.

---

## Planning Errors

VIBE_PLAN_OUTPUT_INVALID  
Step output failed schema validation.

VIBE_PLAN_MANIFEST_MISSING  
spec/plan_manifest.json not produced.

VIBE_PLAN_MANIFEST_INVALID  
Manifest failed JSON schema validation.

VIBE_BUDGET_EXCEEDED  
Execution budgets exceeded.

---

## Tool Errors

VIBE_TOOL_NOT_ALLOWED  
Step attempted tool not in allowlist.

VIBE_TOOL_ARGS_INVALID  
Tool arguments invalid.

VIBE_TOOL_RESULT_INVALID  
Tool result failed schema validation.

VIBE_TOOL_FAILURE  
Underlying tool execution failed.

---

## Gate and Validation Errors

VIBE_GATE_FAILURE  
Gate checks failed.

VIBE_VALIDATION_FAILURE  
Validators failed.

---

## Apply Errors

VIBE_OPERATION_NOT_PERMITTED  
Operation violates repo scope.

VIBE_OPERATION_FAILED  
Manifest operation failed.

VIBE_NON_MANIFEST_CHANGE_ATTEMPT  
Attempted modification outside manifest.