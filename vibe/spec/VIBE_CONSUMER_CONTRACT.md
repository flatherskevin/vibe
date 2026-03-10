# VIBE Consumer Contract (v1.0)

This document defines the required and recommended behaviors for any system that reads `.vibe.md` files.

This document specifies how consumers -- humans, AI systems, IDEs, CI pipelines, and other tools -- should parse, validate, and interpret VIBE documents.

---

## 1. What Is a Consumer?

A consumer is any system that reads `.vibe.md` files. Consumers do not execute .vibe.md files. They read and interpret them.

Examples of consumers:

- A human reading a .vibe.md file in an editor
- An AI system loading a .vibe.md file to understand a plan
- An execution tool reading artifacts and context to implement a plan
- An IDE providing syntax highlighting and structure preview
- A CI pipeline validating .vibe.md files against the schema
- The VIBE MCP server reading and writing .vibe.md documents

All consumers MUST follow the parsing requirements in this document. Consumers that resolve imports MUST follow the import resolution and merge behavior rules.

---

## 2. Parsing Requirements

### 2.1 YAML Frontmatter

`.vibe.md` files use markdown with YAML frontmatter syntax. Consumers MUST parse the frontmatter as YAML 1.2.

### 2.2 Encoding

All `.vibe.md` files MUST be UTF-8 encoded. Consumers MUST reject files that are not valid UTF-8.

### 2.3 Indentation

Indentation MUST use spaces. Tabs are not permitted. Consumers SHOULD reject files containing tab indentation.

### 2.4 Version Check

Every `.vibe.md` file MUST begin with a `vibe` field at the top level of the YAML frontmatter.

```yaml
vibe: 1.0
```

Consumers MUST check this field before processing. A consumer encountering an unrecognized version SHOULD reject the file or warn that it is an incompatible version.

The `vibe` field accepts both string (`"1.0"`) and number (`1.0`) values. Consumers MUST normalize both representations to the same version identifier.

### 2.5 Duplicate Keys

Duplicate keys within the same YAML mapping are an error. Consumers SHOULD reject files containing duplicate keys.

### 2.6 Parse Errors

If parsing fails, consumers SHOULD provide a clear error message including:

- The file path
- The line number (if available)
- A description of the syntax error

---

## 3. Import Resolution

Consumers that process the `imports` field MUST resolve imports according to these rules.

### 3.1 Path Resolution

Import paths are relative to the directory containing the importing file.

```yaml
# In file: plans/architecture.vibe.md
imports:
  - ../vibe/stdlib/quality.vibe.md    # resolves to vibe/stdlib/quality.vibe.md
  - shared_context.vibe.md            # resolves to plans/shared_context.vibe.md
```

Absolute paths (starting with `/`) are forbidden. See section 7 for security requirements.

### 3.2 Recursive Loading

Imports are resolved recursively and depth-first, respecting declared order.

Algorithm:

```
function resolve(file, visited):
    if file in visited:
        raise circular import error
    visited.add(file)
    document = parse(file)
    for import_path in document.imports:
        resolved_path = resolve_relative(file.directory, import_path)
        imported = resolve(resolved_path, visited)
        document = merge(document, imported)
    return document
```

### 3.3 Circular Import Detection

Consumers MUST detect circular imports and raise an error. Detection uses a visited set that tracks file paths during recursive resolution.

If file A imports file B and file B imports file A, this is a circular import error. The error SHOULD identify the cycle (for example: `A -> B -> A`).

### 3.4 Missing Imports

If an imported file does not exist, consumers SHOULD raise an error. Consumers MAY choose to emit a warning and continue processing without the missing file, but MUST clearly indicate that imports were not fully resolved.

---

## 4. Merge Behavior

When a root .vibe.md file imports other .vibe.md files, the documents are merged field by field. The root file's values take precedence where conflicts occur.

Merge happens after recursive import resolution. The result is a single logical document containing the combined content of all files in the import chain.

### 4.1 vibe

Root file's version wins. Imported files may declare different versions, but the root file's `vibe` value is the version of the merged document.

### 4.2 meta

Root file wins entirely. The `meta` field is not deep-merged. If the root file declares `meta`, the imported file's `meta` is discarded. If the root file does not declare `meta`, the first imported file's `meta` is used.

Rationale: meta describes the document identity. A merged document has the identity of the root file.

### 4.3 imports

The `imports` field is consumed during resolution and is not present in the merged result. Consumers MAY retain the original imports list for provenance tracking, but it has no semantic meaning after resolution.

### 4.4 context

Deep merge. Keys from the root file override keys from imported files. Keys present only in imported files are preserved.

```yaml
# imported file
context:
  problem: "Imported problem statement"
  glossary: "Imported glossary"

# root file
context:
  problem: "Root problem statement"
  constraints: "Root constraints"

# merged result
context:
  problem: "Root problem statement"      # root wins
  glossary: "Imported glossary"          # preserved from import
  constraints: "Root constraints"        # preserved from root
```

Freeform keys (keys not defined in the schema) follow the same rule: root overrides, import-only keys are preserved.

### 4.5 artifacts

Concatenate arrays. If both the root and an imported file declare artifacts, the imported file's artifacts appear first, followed by the root file's artifacts.

Deduplication: if two artifacts share the same `path`, the root file's artifact wins and the imported duplicate is discarded.

### 4.6 sections

Concatenate arrays. Imported sections appear first, root sections are appended after.

No deduplication is performed on sections. If two sections share the same `id`, both are preserved in order. Consumers MAY warn about duplicate section IDs but MUST NOT discard sections silently.

### 4.7 decisions

Concatenate arrays. Imported decisions appear first, root decisions are appended after.

Deduplication: if two decisions share the same `id`, the root file's decision wins and the imported duplicate is discarded.

### 4.8 quality

Concatenate arrays. Imported quality criteria appear first, root criteria are appended after.

Deduplication: if two quality criteria share the same `id`, the root file's criterion wins and the imported duplicate is discarded.

---

## 5. Field Interpretation

Consumers should interpret each top-level field according to its purpose.

### 5.1 vibe

The version identifier. Use this to determine which version of the spec applies.

### 5.2 meta

Document metadata. Consumers use this to identify the document, track its status, filter by tags, and understand authorship.

The `status` field indicates the document's lifecycle position:

- `draft` -- Work in progress. Content may be incomplete or incorrect.
- `review` -- Content is complete and awaiting review.
- `final` -- Content has been reviewed and approved.

Consumers MAY use status to filter or sort documents. Status does not affect parsing or merge behavior.

### 5.3 context

Problem description and planning context. Consumers should treat this as the "why" of the document. The `problem` field is the most important context key.

Context keys like `constraints`, `assumptions`, `scope`, and `glossary` provide additional planning context. Freeform keys are allowed and should be preserved by consumers.

### 5.4 artifacts

Planned or tracked files. Each artifact describes a file that is part of the plan. The `status` field tracks artifact progress: `planned`, `in_progress`, `complete`.

The `acceptance_criteria` array defines what "done" means for the artifact. Consumers should present these criteria alongside the artifact for review.

### 5.5 sections

The body of the document. Sections are ordered and typed. Consumers should present sections in the order they appear. The `type` field indicates what kind of content the section contains. See `VIBE_DOCUMENT_TYPES.md` for type definitions.

The `depends_on` field indicates which other sections this section builds on. This is informational and does not affect merge or ordering.

### 5.6 decisions

Structured Architecture Decision Records. Each decision captures a choice, the alternatives considered, the rationale, and the consequences. Consumers should present decisions with their full structure to support review.

The `status` field tracks the decision lifecycle: `proposed`, `accepted`, `deprecated`, `superseded`.

### 5.7 quality

Criteria that define "done" for the document or its artifacts. Consumers should present quality criteria as a checklist or review guide. See `VIBE_DOCUMENT_TYPES.md` for quality type definitions.

---

## 6. Validation

### 6.1 Schema Validation

VIBE v1 provides a JSON Schema at `vibe/schema/vibe.schema.json`. Consumers SHOULD validate .vibe.md files against this schema.

Schema validation checks:

- Required field `vibe` is present
- Field types are correct (meta is object, sections is array, etc.)
- Enum values are valid (section types, status values, decision status)
- No unknown top-level fields (additionalProperties is false)

### 6.2 Advisory Validation

Schema validation is advisory, not blocking. A .vibe.md file that fails schema validation is still a valid document and MAY still contain useful content.

Consumers SHOULD:

- Report validation errors clearly
- Continue processing the document when possible
- Not silently discard content that fails validation

Consumers MUST NOT:

- Refuse to display a document solely because it fails schema validation
- Silently modify content to pass validation

### 6.3 Structural Validation

Beyond schema validation, consumers MAY perform structural checks:

- Section IDs are unique within the sections array
- Decision IDs are unique within the decisions array
- Quality criterion IDs are unique within the quality array
- Artifact paths are unique within the artifacts array
- Import paths resolve to existing files
- No circular imports exist

These checks are recommended but not required. Consumers SHOULD report structural issues as warnings.

---

## 7. Security

### 7.1 Import Path Safety

Consumers MUST enforce path safety when resolving imports.

Forbidden patterns:

- Absolute paths: `/etc/passwd`, `/home/user/secrets.vibe.md`
- Parent traversal beyond the project root: `../../../../etc/passwd`
- Paths containing null bytes or other control characters

Consumers SHOULD resolve import paths to canonical form and verify they remain within the expected project directory.

### 7.2 Path Traversal

The `..` path component is permitted for navigating within a project (for example, `../vibe/stdlib/quality.vibe.md`). However, consumers MUST ensure that the resolved path does not escape the project root directory.

Consumers SHOULD define a project root (typically the directory containing `project.vibe.md` or the repository root) and reject any import that resolves to a path outside this root.

### 7.3 Content Safety

`.vibe.md` files are data documents, not executable code. Consumers MUST NOT execute any content within a .vibe.md file. String fields may contain code snippets as documentation, but these are for human reading, not execution.

### 7.4 Size Limits

Consumers MAY impose reasonable size limits on .vibe.md files and import chains to prevent resource exhaustion. Recommended limits:

- Individual file size: 1 MB
- Total import chain size: 10 MB
- Import depth: 20 levels

These limits are recommendations. Consumers should document their limits.

---

## 8. Relationship to Other Documents

- `VIBE_SPEC_v1.md` -- Core format specification with field definitions.
- `VIBE_MERGE_SEMANTICS.md` -- Detailed merge rules and examples.
- `VIBE_DOCUMENT_TYPES.md` -- Section type and quality type definitions.
- `VIBE_ERRORS.md` -- Error codes for parse, schema, and import failures.
- `VIBE_INTEGRATION_HOOKS.md` -- How specific consumer types (IDE, CI, MCP) integrate.

