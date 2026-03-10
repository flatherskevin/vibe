# VIBE Merge Semantics (v2.0)

This document defines how multiple `.vibe` files are combined when imports are resolved.

In v1, this was the Program IR document, which defined a compiled representation for runtime execution. In v2, there is no compilation step and no IR. Merge is a straightforward field-by-field combination of documents.

---

## 1. Import Resolution Algorithm

When a consumer processes a `.vibe` file with an `imports` field, it resolves those imports recursively using a depth-first traversal.

### 1.1 Algorithm

```
function resolve(file_path, visited_set):
    if file_path in visited_set:
        raise IMPORT_CYCLE error identifying the cycle
    visited_set.add(file_path)

    document = parse_yaml(file_path)
    merged = empty_document()

    for import_path in document.imports (or empty list):
        absolute_path = resolve_relative(directory_of(file_path), import_path)
        imported_document = resolve(absolute_path, copy(visited_set))
        merged = merge(merged, imported_document)

    merged = merge(merged, document)
    return merged
```

### 1.2 Processing Order

Imports are processed in declared order, depth-first. For a file with:

```yaml
imports:
  - a.vibe
  - b.vibe
```

Where `a.vibe` imports `c.vibe`, the processing order is:

1. `c.vibe` (imported by a.vibe)
2. `a.vibe`
3. `b.vibe`
4. Root file

Content from earlier files appears first in concatenated arrays. Content from later files (and the root file) takes precedence in override rules.

### 1.3 Path Resolution

Import paths are resolved relative to the directory containing the importing file.

```
project.vibe          (in project root)
  imports: vibe/stdlib/quality.vibe
    -> resolves to: {project_root}/vibe/stdlib/quality.vibe

plans/architecture.vibe
  imports: ../vibe/stdlib/quality.vibe
    -> resolves to: {project_root}/vibe/stdlib/quality.vibe

plans/architecture.vibe
  imports: shared_context.vibe
    -> resolves to: {project_root}/plans/shared_context.vibe
```

Absolute paths (starting with `/`) are forbidden. See `VIBE_CONSUMER_CONTRACT.md` section 7 for security requirements.

---

## 2. Circular Import Detection

Circular imports are detected using a visited set that tracks file paths during recursive resolution.

### 2.1 Detection Method

Before processing a file, the algorithm checks whether the file's canonical path is already in the visited set. If it is, a circular import error is raised.

The visited set is passed by copy (not reference) at each branch of the import tree. This means the same file may be imported by two different branches without triggering a false cycle. Only actual cycles (A imports B imports A) are detected.

### 2.2 Example: Valid Diamond Import

```
root.vibe imports a.vibe and b.vibe
a.vibe imports shared.vibe
b.vibe imports shared.vibe
```

This is valid. `shared.vibe` is loaded twice (once for each branch) but there is no cycle. The merge rules handle deduplication.

### 2.3 Example: Invalid Circular Import

```
root.vibe imports a.vibe
a.vibe imports b.vibe
b.vibe imports a.vibe
```

This is invalid. The visited set at b.vibe already contains a.vibe, so the import of a.vibe raises a cycle error: `a.vibe -> b.vibe -> a.vibe`.

---

## 3. Field Merge Rules

Each top-level field has a specific merge rule. These rules apply when combining an imported document with the importing document.

---

### 3.1 vibe

**Rule: root wins.**

The root file's `vibe` version is the version of the merged document. Imported files may declare different versions (for example, a stdlib file might still say `vibe: 2.0`), but the root file's value is authoritative.

---

### 3.2 meta

**Rule: root wins (no deep merge).**

The `meta` field is replaced entirely, not merged key by key. If the root file declares `meta`, the imported file's `meta` is discarded completely. If the root file does not declare `meta`, the last imported file's `meta` is used.

Rationale: `meta` describes the identity of a document (name, author, status). A merged document has the identity of the root file, not a combination of identities.

---

### 3.3 imports

**Rule: already resolved, not present in merged result.**

The `imports` field is consumed during resolution. It has no meaning in the merged document. Consumers MAY retain imports for provenance tracking but MUST NOT attempt to re-resolve them.

---

### 3.4 context

**Rule: deep merge, root keys override imported keys.**

Context is merged key by key. If both the root and imported file define the same key (e.g., `problem`), the root file's value wins. Keys that exist only in the imported file are preserved in the merged result.

This applies to both well-known keys (`problem`, `constraints`, `assumptions`, `scope`, `glossary`) and freeform keys.

---

### 3.5 artifacts

**Rule: concatenate arrays, deduplicate by `path` (root wins).**

Imported artifacts are listed first, followed by root artifacts. If two artifacts have the same `path` value, the root file's artifact is kept and the imported duplicate is discarded.

---

### 3.6 sections

**Rule: concatenate arrays (root appended after imports).**

Imported sections appear first, root sections appear after. All sections are preserved. No deduplication is performed, even if two sections share the same `id`.

Rationale: sections are content. Discarding imported content silently would lose information. If two sections have the same ID, consumers may warn but should preserve both.

---

### 3.7 decisions

**Rule: concatenate arrays, deduplicate by `id` (root wins).**

Imported decisions are listed first, followed by root decisions. If two decisions have the same `id`, the root file's decision is kept and the imported duplicate is discarded.

---

### 3.8 quality

**Rule: concatenate arrays, deduplicate by `id` (root wins).**

Imported quality criteria are listed first, followed by root criteria. If two criteria have the same `id`, the root file's criterion is kept and the imported duplicate is discarded.

---

## 4. Conflict Resolution

### 4.1 Duplicate IDs

When deduplication applies (artifacts by path, decisions by id, quality by id), the root file's entry wins and the imported entry is discarded. This is deterministic: the root file always has the final say.

For sections, duplicate IDs do not trigger deduplication. Both sections are preserved.

### 4.2 Multiple Imports with Conflicts

When multiple imported files conflict with each other (not with the root), the later import wins. Given:

```yaml
imports:
  - a.vibe    # defines decision dec_01
  - b.vibe    # also defines decision dec_01
```

The decision from `b.vibe` wins over the one from `a.vibe` because `b.vibe` is processed later. If the root file also defines `dec_01`, the root wins over both.

### 4.3 Context Key Conflicts Between Imports

When multiple imported files define the same context key, the later import's value wins. The root file's value (if present) overrides all imports.

---

## 5. Examples

### 5.1 Simple Two-File Merge

**File: vibe/stdlib/quality.vibe**

```yaml
vibe: 2.0

meta:
  name: stdlib_quality
  description: Standard quality criteria

quality:
  - id: q_yaml_valid
    type: test
    description: Document is valid YAML
    criteria: |
      The .vibe file parses without YAML syntax errors.

  - id: q_schema_valid
    type: test
    description: Document validates against v2 schema
    criteria: |
      The .vibe file passes validation against vibe.schema.json.
```

**File: project.vibe (root)**

```yaml
vibe: 2.0

meta:
  name: my_project
  description: My planning document

imports:
  - vibe/stdlib/quality.vibe

context:
  problem: |
    We need to redesign the authentication system.

sections:
  - id: overview
    type: analysis
    title: Project Overview
    content: |
      This document plans the auth system redesign.

quality:
  - id: q_design_complete
    type: review
    description: Design is complete
    criteria: |
      All components are specified.
```

**Merged Result:**

```yaml
vibe: 2.0

meta:
  name: my_project
  description: My planning document

context:
  problem: |
    We need to redesign the authentication system.

sections:
  - id: overview
    type: analysis
    title: Project Overview
    content: |
      This document plans the auth system redesign.

quality:
  # From imported file (appears first)
  - id: q_yaml_valid
    type: test
    description: Document is valid YAML
    criteria: |
      The .vibe file parses without YAML syntax errors.

  - id: q_schema_valid
    type: test
    description: Document validates against v2 schema
    criteria: |
      The .vibe file passes validation against vibe.schema.json.

  # From root file (appended after imports)
  - id: q_design_complete
    type: review
    description: Design is complete
    criteria: |
      All components are specified.
```

Note:

- `meta` comes entirely from the root file (stdlib meta is discarded).
- `context` comes from the root file (stdlib had no context).
- `sections` come from the root file only (stdlib had no sections).
- `quality` is concatenated: stdlib criteria first, root criteria after.

---

### 5.2 Override Example

**File: defaults.vibe**

```yaml
vibe: 2.0

context:
  constraints: |
    - All documents must be valid YAML
    - All documents must declare vibe: 2.0

artifacts:
  - path: docs/overview.md
    kind: markdown
    description: Default overview document
    status: planned

decisions:
  - id: dec_format
    title: Use YAML for all documents
    status: accepted
    rationale: YAML is human-readable and well-tooled.
```

**File: project.vibe (root)**

```yaml
vibe: 2.0

imports:
  - defaults.vibe

context:
  constraints: |
    - Must use TypeScript for all new code
  glossary: |
    - TS: TypeScript

artifacts:
  - path: docs/overview.md
    kind: markdown
    description: Project-specific overview
    status: in_progress

decisions:
  - id: dec_format
    title: Use YAML for all documents (updated)
    status: accepted
    rationale: YAML is human-readable and supports our import system.
    consequences:
      - All .vibe files use YAML syntax
```

**Merged Result:**

```yaml
vibe: 2.0

context:
  constraints: |
    - Must use TypeScript for all new code
  glossary: |
    - TS: TypeScript

artifacts:
  # Root wins for path "docs/overview.md" (dedup by path)
  - path: docs/overview.md
    kind: markdown
    description: Project-specific overview
    status: in_progress

decisions:
  # Root wins for id "dec_format" (dedup by id)
  - id: dec_format
    title: Use YAML for all documents (updated)
    status: accepted
    rationale: YAML is human-readable and supports our import system.
    consequences:
      - All .vibe files use YAML syntax
```

Note:

- `context.constraints` from root overrides the import (root key wins).
- `context.glossary` from root is preserved (only in root).
- `context.constraints` from the import is discarded (root override).
- `artifacts` with matching path: root's version wins.
- `decisions` with matching id: root's version wins.

---

## 6. Relationship to Other Documents

- `VIBE_SPEC_v2.md` -- Core format specification with field definitions.
- `VIBE_CONSUMER_CONTRACT.md` -- Consumer requirements including import resolution rules.
- `VIBE_ERRORS.md` -- Error codes for import resolution and merge failures.
