# VIBE Error Taxonomy (v2.0)

This document defines standard error codes for VIBE v2 document validation.

VIBE v2 is a document format, not an execution format. Errors in v2 relate to document parsing, schema validation, import resolution, field merging, and MCP server operations -- not runtime execution.

These codes allow VIBE tooling, validators, MCP servers, and editors to report problems consistently.

---

## 1. Error Format

Every VIBE error should include at minimum:

| Field | Required | Description |
|---|---|---|
| `code` | Yes | Error code (e.g. `PARSE_INVALID_YAML`) |
| `message` | Yes | Human-readable description |
| `severity` | Yes | `fatal`, `error`, or `warning` |

Optional fields for additional context:

| Field | Description |
|---|---|
| `path` | File path where the error occurred |
| `line` | Line number in the file |
| `field` | YAML field path (e.g. `meta.status`, `sections[2].type`) |
| `details` | Structured object with additional information |

Example structured error:

```json
{
  "code": "SCHEMA_INVALID_FIELD",
  "message": "Invalid section type 'summary' at sections[2].type",
  "severity": "error",
  "path": "plans/feature_a.vibe",
  "line": 45,
  "field": "sections[2].type",
  "details": {
    "value": "summary",
    "allowed": ["analysis", "design", "decision", "specification", "risk", "checklist"]
  }
}
```

---

## 2. Severity Levels

### fatal

The document cannot be processed further. Parsing or import resolution failed at a level that prevents any meaningful validation.

Default for: `PARSE_*` errors, `IMPORT_CYCLE`.

### error

The document has a structural or content problem that must be fixed. The document is parseable but does not conform to the v2 schema or has merge conflicts.

Default for: `SCHEMA_*` errors, `IMPORT_NOT_FOUND`, `MERGE_*` errors, most `MCP_*` errors.

### warning

The document is valid but has a potential issue worth noting. Warnings do not prevent the document from being used.

Default for: Advisory issues such as empty sections, missing optional fields, or unused imports.

---

## 3. PARSE_* -- YAML Parsing Failures

Errors that occur when the `.vibe` file cannot be parsed as valid YAML.

---

### PARSE_INVALID_YAML

The file contains invalid YAML syntax.

Severity: `fatal`

Causes:
- Invalid indentation
- Malformed key-value syntax
- Unclosed quotes or block scalars
- Tab characters where spaces are expected
- Invalid list syntax

Example:

```json
{
  "code": "PARSE_INVALID_YAML",
  "message": "Invalid YAML: unexpected end of stream at line 24",
  "severity": "fatal",
  "path": "plans/feature_a.vibe",
  "line": 24
}
```

---

### PARSE_ENCODING_ERROR

The file is not valid UTF-8 or contains unsupported encoding.

Severity: `fatal`

Causes:
- Binary content in a `.vibe` file
- Non-UTF-8 encoding (Latin-1, UTF-16 without BOM detection)
- Null bytes in the file

Example:

```json
{
  "code": "PARSE_ENCODING_ERROR",
  "message": "File is not valid UTF-8 encoding",
  "severity": "fatal",
  "path": "plans/feature_a.vibe"
}
```

---

## 4. SCHEMA_* -- Schema Validation Failures

Errors that occur when a parsed YAML document does not conform to the VIBE v2 schema (`vibe/schema/vibe.schema.json`).

---

### SCHEMA_MISSING_VERSION

The required `vibe` version field is missing from the document.

Severity: `error`

Every `.vibe` file must have a top-level `vibe` field. Without it, the file cannot be identified as a VIBE document.

Example:

```json
{
  "code": "SCHEMA_MISSING_VERSION",
  "message": "Missing required field: vibe",
  "severity": "error",
  "path": "plans/feature_a.vibe"
}
```

---

### SCHEMA_INVALID_FIELD

A field value does not match its schema definition.

Severity: `error`

Causes:
- Wrong type (string where array expected, etc.)
- Value not in allowed enum
- Missing required subfields
- Pattern mismatch (e.g. `session_id` format)

Example:

```json
{
  "code": "SCHEMA_INVALID_FIELD",
  "message": "Invalid value for meta.status: 'active' is not one of [draft, review, final]",
  "severity": "error",
  "path": "plans/feature_a.vibe",
  "field": "meta.status",
  "details": {
    "value": "active",
    "allowed": ["draft", "review", "final"]
  }
}
```

---

### SCHEMA_UNKNOWN_TYPE

A section, quality criterion, or other typed field uses a type value not defined in the schema.

Severity: `error`

Causes:
- Misspelled section type (e.g. `analaysis` instead of `analysis`)
- Using v1 types not present in v2
- Custom types not supported by the schema

Example:

```json
{
  "code": "SCHEMA_UNKNOWN_TYPE",
  "message": "Unknown section type 'summary' at sections[3].type",
  "severity": "error",
  "path": "plans/feature_a.vibe",
  "field": "sections[3].type",
  "details": {
    "value": "summary",
    "allowed_section_types": ["analysis", "design", "decision", "specification", "risk", "checklist"],
    "allowed_quality_types": ["review", "test", "metric", "checklist"],
    "allowed_decision_statuses": ["proposed", "accepted", "deprecated", "superseded"]
  }
}
```

---

### SCHEMA_INVALID_STATUS

A status field has a value not in the allowed set for its context.

Severity: `error`

This applies to:
- `meta.status` (must be `draft`, `review`, or `final`)
- `decisions[].status` (must be `proposed`, `accepted`, `deprecated`, or `superseded`)
- `artifacts[].status` (must be `planned`, `in_progress`, or `complete`)

Example:

```json
{
  "code": "SCHEMA_INVALID_STATUS",
  "message": "Invalid artifact status 'done' at artifacts[1].status",
  "severity": "error",
  "path": "plans/feature_a.vibe",
  "field": "artifacts[1].status",
  "details": {
    "value": "done",
    "allowed": ["planned", "in_progress", "complete"]
  }
}
```

---

## 5. IMPORT_* -- Import Resolution Failures

Errors that occur when resolving the `imports` array.

---

### IMPORT_NOT_FOUND

A referenced import file does not exist.

Severity: `error`

Causes:
- Typo in the import path
- File was moved or deleted
- Wrong relative path

Example:

```json
{
  "code": "IMPORT_NOT_FOUND",
  "message": "Import not found: vibe/stdlib/quality_criteria.vibe",
  "severity": "error",
  "path": "plans/feature_a.vibe",
  "field": "imports[0]",
  "details": {
    "import_path": "vibe/stdlib/quality_criteria.vibe",
    "searched_from": "plans/feature_a.vibe"
  }
}
```

---

### IMPORT_CYCLE

A circular import was detected in the import graph.

Severity: `fatal`

Import cycles make merge resolution impossible. If A imports B and B imports A (directly or transitively), the cycle must be broken before the document can be processed.

Example:

```json
{
  "code": "IMPORT_CYCLE",
  "message": "Circular import detected: a.vibe -> b.vibe -> a.vibe",
  "severity": "fatal",
  "details": {
    "cycle": ["a.vibe", "b.vibe", "a.vibe"]
  }
}
```

---

### IMPORT_INVALID_PATH

An import path is syntactically invalid.

Severity: `error`

Causes:
- Path traversal outside repository root (`../../../etc/passwd`)
- Absolute paths where relative paths are expected
- Non-`.vibe` file extension
- Empty string

Example:

```json
{
  "code": "IMPORT_INVALID_PATH",
  "message": "Import path must be relative and end with .vibe: /etc/config.yaml",
  "severity": "error",
  "path": "plans/feature_a.vibe",
  "field": "imports[2]",
  "details": {
    "import_path": "/etc/config.yaml"
  }
}
```

---

## 6. MERGE_* -- Field Merge Conflicts

Errors that occur when merging fields from imported documents.

---

### MERGE_DUPLICATE_ID

Two or more elements across imported documents share the same ID within the same array scope.

Severity: `error`

This applies to:
- Section IDs (must be unique across merged `sections` array)
- Decision IDs (must be unique across merged `decisions` array)
- Quality criterion IDs (must be unique across merged `quality` array)

Example:

```json
{
  "code": "MERGE_DUPLICATE_ID",
  "message": "Duplicate section ID 'overview' found in plans/feature_a.vibe and vibe/stdlib/templates/overview.vibe",
  "severity": "error",
  "details": {
    "id": "overview",
    "scope": "sections",
    "sources": [
      "plans/feature_a.vibe",
      "vibe/stdlib/templates/overview.vibe"
    ]
  }
}
```

---

### MERGE_DUPLICATE_PATH

Two or more artifacts across imported documents declare the same file path.

Severity: `error`

Artifact paths must be unique across the merged document. If two imported files both declare an artifact at the same path, the conflict must be resolved manually.

Example:

```json
{
  "code": "MERGE_DUPLICATE_PATH",
  "message": "Duplicate artifact path 'src/auth/service.py' found in plans/auth.vibe and plans/feature_a.vibe",
  "severity": "error",
  "details": {
    "path": "src/auth/service.py",
    "scope": "artifacts",
    "sources": [
      "plans/auth.vibe",
      "plans/feature_a.vibe"
    ]
  }
}
```

---

## 7. MCP_* -- MCP Server Errors

Errors that occur when a VIBE MCP server processes requests for `.vibe` documents.

---

### MCP_SESSION_NOT_FOUND

A referenced MCP session ID does not exist or has expired.

Severity: `error`

Causes:
- Importing from a session that no longer exists
- Mistyped session ID
- Session data has been cleaned up

Example:

```json
{
  "code": "MCP_SESSION_NOT_FOUND",
  "message": "MCP session not found: 2026-03-08-f4e5d6",
  "severity": "error",
  "details": {
    "session_id": "2026-03-08-f4e5d6"
  }
}
```

---

### MCP_FILE_NOT_FOUND

The MCP server could not locate a requested `.vibe` file.

Severity: `error`

Causes:
- File does not exist at the specified path
- File was deleted after being referenced
- Incorrect path provided to the MCP tool

Example:

```json
{
  "code": "MCP_FILE_NOT_FOUND",
  "message": "File not found: plans/feature_a.vibe",
  "severity": "error",
  "details": {
    "path": "plans/feature_a.vibe"
  }
}
```

---

### MCP_INVALID_YAML

The MCP server received or read content that is not valid YAML.

Severity: `error`

This is the MCP-layer equivalent of `PARSE_INVALID_YAML`. It is emitted when the MCP server itself detects the parsing failure (as opposed to an external validator).

Example:

```json
{
  "code": "MCP_INVALID_YAML",
  "message": "Content provided to write_vibe is not valid YAML",
  "severity": "error",
  "details": {
    "tool": "write_vibe",
    "parse_error": "unexpected end of stream at line 12"
  }
}
```

---

### MCP_FILESYSTEM_ERROR

The MCP server encountered a filesystem error while reading or writing a `.vibe` file.

Severity: `error`

Causes:
- Permission denied
- Disk full
- Path too long
- Read-only filesystem

Example:

```json
{
  "code": "MCP_FILESYSTEM_ERROR",
  "message": "Permission denied writing to plans/feature_a.vibe",
  "severity": "error",
  "details": {
    "operation": "write",
    "path": "plans/feature_a.vibe",
    "os_error": "EACCES: permission denied"
  }
}
```

---

## 8. Error Reporting Best Practices

### Report all errors, not just the first

When validating a document, collect all errors and report them together. Stopping at the first error forces repeated validation cycles.

### Include file path and line number when available

Location information dramatically reduces debugging time. YAML parsers typically provide line numbers for syntax errors. Schema validators can map field paths back to approximate line numbers.

### Use structured errors for tooling

Emit errors as structured JSON when consumed by tools, editors, or MCP servers. Use human-readable messages when displayed to users.

### Map errors to editor diagnostics

For VS Code and similar editors, VIBE errors map to diagnostics:

| Severity | Editor Diagnostic |
|---|---|
| `fatal` | Error (red) |
| `error` | Error (red) |
| `warning` | Warning (yellow) |

---

## 9. Relationship to v1 Errors

VIBE v2 removes the following v1 error categories that related to runtime execution:

- `VIBE_PLAN_OUTPUT_INVALID` (no plan phase)
- `VIBE_PLAN_MANIFEST_MISSING` (no manifests)
- `VIBE_PLAN_MANIFEST_INVALID` (no manifests)
- `VIBE_BUDGET_EXCEEDED` (no execution budgets)
- `VIBE_TOOL_NOT_ALLOWED` (no tool definitions)
- `VIBE_TOOL_ARGS_INVALID` (no tool definitions)
- `VIBE_TOOL_RESULT_INVALID` (no tool definitions)
- `VIBE_TOOL_FAILURE` (no tool execution)
- `VIBE_GATE_FAILURE` (no gates)
- `VIBE_VALIDATION_FAILURE` (no runtime validators)
- `VIBE_OPERATION_NOT_PERMITTED` (no apply phase)
- `VIBE_OPERATION_FAILED` (no apply phase)
- `VIBE_NON_MANIFEST_CHANGE_ATTEMPT` (no manifest enforcement)

VIBE v2 errors focus exclusively on document validity: can this `.vibe` file be parsed, does it conform to the schema, do its imports resolve, and do its fields merge cleanly?
