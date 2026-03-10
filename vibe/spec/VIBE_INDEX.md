# VIBE v1 Index

This folder contains the specification and guidance documents for VIBE v1.

VIBE v1 is a structured YAML document format for AI-driven planning. It defines how planning documents are written, validated, imported, and consumed.

---

## Normative Documents (consumers MUST follow)

- **VIBE_SPEC_v1.md**
  Format overview and core concepts. Defines the `.vibe` file format, top-level fields, section types, and the document model.

- **VIBE_CONSUMER_CONTRACT.md**
  Consumer requirements. Specifies what any tool, agent, or system that reads `.vibe` files must support: parsing, validation, import resolution, and error reporting.

- **VIBE_MERGE_SEMANTICS.md**
  Import and merge rules. Defines how `imports` are resolved, how fields from multiple documents are combined, and how conflicts are handled.

- **VIBE_ERRORS.md**
  Error taxonomy and codes. Defines the standard error codes (`VIBE_INVALID_YAML`, `VIBE_SCHEMA_VALIDATION_FAILED`, `VIBE_CIRCULAR_DEPENDENCY`, etc.) and their semantics.

---

## Informative Documents (strongly recommended)

- **VIBE_DOCUMENT_TYPES.md**
  Section types and archetypes. Describes the standard section types (`analysis`, `specification`, `decision`, `checklist`) and document archetypes (`feature`, `migration`, `investigation`, `bugfix`, `refactor`).

- **VIBE_DEPENDENCIES.md**
  Artifact and section dependencies. Explains how `depends_on` works for artifacts (design-time ordering), sections (content ordering within a document), and cross-document imports. Covers circular dependency detection rules.

- **VIBE_AUTHORING_GUIDE.md**
  Guidance for writing `.vibe` documents. Best practices for humans and AI systems authoring planning documents, including section structure, quality criteria, and common pitfalls.

- **VIBE_REFERENCE_DOCUMENT.md**
  Canonical example document. A complete, annotated `.vibe` document demonstrating all v1 features. Useful for learning, testing, and as a template.

- **VIBE_INTEGRATION_HOOKS.md**
  External tool integration. Patterns for integrating VIBE documents with CI/CD systems, code review tools, project management tools, and other external systems.

- **VIBE_MULTI_AUTHOR.md**
  Multi-author collaboration patterns. Guidance for multiple humans or AI agents working on the same set of `.vibe` documents, including session management, conflict resolution, and review workflows.

- **VIBE_MCP_SERVER.md**
  MCP server specification. Reference for the local Python MCP server that provides tools for creating, reading, validating, and managing `.vibe` planning sessions.

---

## Standard Library (`vibe/stdlib/`)

The standard library provides reusable modules imported by `.vibe` documents.

- **quality.vibe**
  Reusable quality criteria. Defines standard quality types (`test`, `review`, `metric`, `manual`) and provides baseline criteria that documents can import and reference.

- **context_budget.vibe**
  Context management guidance. Defines conventions for managing AI context windows when working with large sets of planning documents, including summarization and compaction strategies.

- **templates/**
  Document archetype templates. Skeleton `.vibe` documents for common planning scenarios:
  - `feature.vibe` -- New feature planning
  - `migration.vibe` -- System migration or upgrade
  - `investigation.vibe` -- Research or spike
  - `bugfix.vibe` -- Bug analysis and fix plan
  - `refactor.vibe` -- Refactoring plan

---

## Completeness Checklist (v1)

A repository is "VIBE v1 complete" when it includes:

**Required:**

- Root document: `project.vibe` with `vibe: 1.0`
- JSON Schema: `vibe/schema/vibe.schema.json`
- Core spec: `vibe/spec/VIBE_SPEC_v1.md`
- Consumer contract: `vibe/spec/VIBE_CONSUMER_CONTRACT.md`
- Merge semantics: `vibe/spec/VIBE_MERGE_SEMANTICS.md`
- Error taxonomy: `vibe/spec/VIBE_ERRORS.md`
- Standard library: `vibe/stdlib/quality.vibe`, `vibe/stdlib/context_budget.vibe`

**Recommended:**

- Document types reference: `vibe/spec/VIBE_DOCUMENT_TYPES.md`
- Dependencies reference: `vibe/spec/VIBE_DEPENDENCIES.md`
- Authoring guide: `vibe/spec/VIBE_AUTHORING_GUIDE.md`
- Reference document: `vibe/spec/VIBE_REFERENCE_DOCUMENT.md`
- Integration hooks: `vibe/spec/VIBE_INTEGRATION_HOOKS.md`
- Multi-author patterns: `vibe/spec/VIBE_MULTI_AUTHOR.md`
- MCP server spec: `vibe/spec/VIBE_MCP_SERVER.md`
- Archetype templates: `vibe/templates/`

**Optional but useful:**

- JSON Schema for `.vibe` files: `vibe/schema/vibe.schema.json`
- Project template: `vibe/templates/new_project.vibe`
- Syntax highlighting: `syntaxes/vibe.tmLanguage.json`
- VS Code settings: `.vscode/settings.json`

