# VIBE Program IR (v1.0)

This document defines the canonical merged representation of a VIBE program after parsing all `.vibe` files and resolving imports.

A VIBE runtime MUST compile the `.vibe` file set into this Program IR before executing any workflow steps.

The goal of this IR is determinism: different runtimes should produce the same IR from the same inputs.

---

## 1) Canonical Program Object

The Program IR is a single JSON-like object (in memory). It is not required to be written to disk, but runtimes SHOULD support emitting it for debugging.

Program:

- vibe_version: "1.0"
- meta: object
- context: object
- tools: object
- artifacts: array
- workflow: object
- validation: array
- sources: array
- errors: array (optional)

---

## 2) Field Schemas

### meta

Required fields:

- name
- description
- repo_root

Optional fields:

- runtime_min
- runtime_max
- repo_write_scope

### context

Freeform key/value map.

### tools

Map of tool_name -> tool_contract.

### artifacts

Array of artifact objects.

Artifact fields:

- path
- kind
- source
- invariants
- ownership
- write_policy
- depends_on
- protected_regions

### workflow

Object containing:

- mode
- steps

### validation

Array of validator objects.

Each validator has:

- id
- type
- config

---

## 3) Merge Algorithm

Files are loaded in deterministic order.

### meta

Keys merged.
Conflicts are compile errors.

### context

Keys merged.
Conflicts are compile errors.

### tools

Merged by tool name.
Conflicts are compile errors.

### artifacts

Merged by path.
Duplicate paths are compile errors.

### workflow

Steps appended in load order.

### validation

Merged by validator id.
Duplicate ids are compile errors.

---

## 4) Provenance

Runtimes SHOULD track source provenance.

Example structure:

sources:
- path
- sha256
- loaded_at

---

## 5) Compile Time Errors

If compilation fails:

- abort execution
- return structured error codes defined in VIBE_ERRORS.md

---

## 6) Optional Debug Output

Runtimes may emit:

spec/program_ir.json

and

spec/compile_errors.json