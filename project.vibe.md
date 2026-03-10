---
vibe: "2.0"
meta:
  name: vibe_project_root
  description: >
    Root VIBE document. Defines the project's standard library imports,
    context, and quality criteria for the VIBE v2 planning document format.
  author: human
  tags:
    - root
    - project
  status: final
imports:
  - vibe/stdlib/quality.vibe.md
  - vibe/stdlib/context_budget.vibe.md
---

## Context

### Problem

VIBE is a structured document format for AI-driven planning. This root
document defines the project's standard library, quality criteria, and
document conventions for all .vibe.md files in the repository.

### Constraints

- All .vibe.md files must have valid YAML frontmatter
- All .vibe.md files must declare vibe: "2.0" in frontmatter
- All .vibe.md files must validate against vibe/schema/vibe.schema.json
- Documents should follow section type conventions
- Imports must not create circular references

### Glossary

- VIBE: Structured planning document format for AI-driven work
- Section: A typed content block within a .vibe.md document
- Decision: An Architecture Decision Record (ADR) within a .vibe.md document
- Quality: Criteria that define when a document or artifact is complete
- MCP: Model Context Protocol for AI tool integration

## Artifacts

| Path | Kind | Description | Status |
|------|------|-------------|--------|
| vibe/spec/VIBE_SPEC_v2.md | markdown | Core language specification | complete |
| vibe/schema/vibe.schema.json | json | JSON Schema for validating .vibe.md files | complete |
| vibe/stdlib/quality.vibe.md | vibe | Standard quality criteria library | complete |
| vibe/stdlib/context_budget.vibe.md | vibe | Context budgeting guidance for AI systems | complete |

## Sections

### Project Overview
<!-- id: project_overview, type: analysis -->

VIBE v2 is a structured markdown document format for AI-driven planning.
A .vibe.md file captures what problem is being solved (context), what
will be built or changed (artifacts), how it was reasoned about
(sections, decisions), and what "done" looks like (quality criteria).

VIBE documents are the output of AI planning, consumed by humans
reviewing plans, other AI agents continuing work, and execution
tools that need structured instructions.

### Document Model
<!-- id: document_model, type: specification -->

The VIBE v2 document lifecycle:

1. Write: AI or human creates a .vibe.md document
2. Validate: Document is checked against the v2 schema
3. Review: Humans or AI review sections, decisions, quality
4. Import: Other documents can import and build on this one

This replaces the v1 execution model (parse -> compile -> plan ->
apply -> validate) with a document-oriented model.

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_project_valid | test | All .vibe.md files in the project are valid v2 format | Every .vibe.md file in the repository has vibe: "2.0" and validates against vibe/schema/vibe.schema.json |
