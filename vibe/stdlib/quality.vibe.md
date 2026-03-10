---
vibe: "1.0"
meta:
  name: stdlib_quality
  description: >
    Reusable quality criteria library for VIBE v1 documents. Import this
    file and reference these criteria in your document's quality section.
  author: vibe
  tags:
    - stdlib
    - quality
  status: final
---

## Context

### Purpose

This module provides standard quality criteria that any .vibe.md document
can import. Criteria IDs are prefixed with stdlib_ to avoid collisions
with document-specific criteria.

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| stdlib_yaml_valid | test | Document frontmatter is valid YAML | The .vibe.md file's frontmatter parses without YAML syntax errors |
| stdlib_schema_valid | test | Document validates against v1 schema | The .vibe.md file passes validation against vibe/schema/vibe.schema.json |
| stdlib_version_present | test | Document declares vibe version 1.0 | The frontmatter vibe field is present and set to "1.0" |
| stdlib_meta_complete | checklist | Document metadata is complete | meta.name is present and non-empty; meta.description is present and non-empty; meta.status is one of: draft, review, final |
| stdlib_context_present | review | Document has meaningful context | The Context section includes at least a Problem heading that clearly describes what is being planned or solved |
| stdlib_sections_complete | review | All sections have substantive content | No section has empty or placeholder-only content. Each section provides meaningful information relevant to its type |
| stdlib_sections_typed | checklist | All sections declare a valid type | Every section has a type in its <!-- --> comment set to one of: analysis, design, decision, specification, risk, checklist |
| stdlib_decisions_complete | review | Decisions include rationale and consequences | Every decision includes context, at least two options, a chosen option, rationale, and at least one consequence |
| stdlib_artifacts_exist | checklist | All planned artifacts have been created | Every artifact listed in the Artifacts table exists at its specified path |
| stdlib_artifacts_accepted | review | Artifacts meet their acceptance criteria | Every artifact with acceptance criteria has been reviewed and all criteria are satisfied |
| stdlib_imports_resolve | test | All imports resolve to existing files | Every path in the imports array points to an existing .vibe.md file. No circular imports exist |
| stdlib_ids_unique | test | All IDs are unique within their scope | Section IDs are unique; Decision IDs are unique; Quality IDs are unique; Artifact paths are unique |
| stdlib_no_v1_fields | test | Document contains no v1-only fields | The document does not contain any of: tools, workflow, validation, sources, scope, constraints, transforms, handoff |
