---
vibe: "1.0"
meta:
  name: session_bootstrap_decisions
  description: >
    Architecture decisions made while bootstrapping the AGENTS.md file and
    docs/vibe/ session directory convention.
  session_id: "2026-03-10-091131"
  created_at: "2026-03-10"
  updated_at: "2026-03-10"
  author: claude
  tags:
    - adr
    - decisions
    - bootstrap
  status: draft
---

## Context

### Problem

The VIBE project needs an agent instruction file and a convention for where
planning session artifacts live. Several design choices must be made before
implementation: where to put session documents, whether to create a
tool-specific or tool-agnostic instruction file, and how to structure the
session's own planning documents.

### Scope

This collection covers three decisions made during the planning of AGENTS.md
and the `docs/vibe/` session directory convention.

## Sections

### Background
<!-- id: background, type: analysis -->

The VIBE repository contains the full v1 specification, standard library,
templates, and schema — but no guidance for AI agents entering the repo.
The `project.vibe.md` root document exists and shows conventions, but agents
need explicit instructions to know they should produce `.vibe.md` files and
where to put them.

The VIBE authoring guide suggests a `plans/` directory for project-specific
planning documents, but this convention was designed for feature planning, not
for ephemeral agent session artifacts that include implementation plans, ADRs,
and other planning byproducts.

## Decisions

### Session directory location
<!-- id: dec_001, status: accepted -->

**Context:** Agent planning sessions produce `.vibe.md` files that need a home
in the repository. The location must be discoverable, not conflict with
existing directories, and clearly separate planning documents from the VIBE
spec itself.

**Options:**

- **docs/vibe/**: Uses the standard git `docs/` convention. Separates planning
  documents from the VIBE format specification under `vibe/`. Clear that these
  are documentation artifacts, not part of the spec.
- **sessions/**: Top-level directory dedicated to sessions. Simple and obvious,
  but adds a new top-level directory with no git convention precedent. Could be
  confused with runtime session data.
- **plans/**: Matches the authoring guide's suggested layout. But `plans/` was
  designed for feature planning documents, not session-scoped artifacts. Mixing
  session bootstrap docs with feature plans muddies the directory's purpose.

**Chosen:** docs/vibe/

**Rationale:** `docs/` is a well-established git convention for project
documentation. Nesting under `docs/vibe/` signals that these are VIBE planning
documents without conflicting with the `vibe/` directory that holds the spec,
stdlib, and schema. The `docs/vibe/<session-id>/` structure provides clean
per-session isolation.

**Consequences:**

- Planning documents live under `docs/vibe/`, separate from the spec under `vibe/`
- The `docs/` directory may grow with non-VIBE documentation in the future, which is fine
- Import paths from session docs to stdlib are longer (`../../../vibe/stdlib/...`) but explicit

### Agent instruction file scope
<!-- id: dec_002, status: accepted -->

**Context:** The project needs an instruction file that AI agents read on
entry. The two main conventions are AGENTS.md (tool-agnostic) and CLAUDE.md
(Claude-specific). The choice affects which agents benefit from the instructions.

**Options:**

- **AGENTS.md only**: Tool-agnostic instruction file. Any AI agent (Claude,
  Copilot, Cursor, Windsurf, etc.) can read and follow the instructions. Aligns
  with VIBE's tool-agnostic philosophy.
- **AGENTS.md + CLAUDE.md**: Both a generic file and a Claude-specific file.
  CLAUDE.md could include Claude-specific hints (e.g., tool use patterns,
  context window guidance). More tailored but creates maintenance burden.

**Chosen:** AGENTS.md only

**Rationale:** VIBE is a tool-agnostic document format. The instructions for
producing `.vibe.md` files are the same regardless of which AI agent is doing
the work. Creating a Claude-specific file would contradict VIBE's philosophy
and create a maintenance burden with duplicated content. If Claude-specific
guidance is needed later, it can be added as a separate file without modifying
AGENTS.md.

**Consequences:**

- All AI agents get the same instructions, consistent with VIBE's tool-agnostic design
- No Claude-specific optimizations (acceptable trade-off for consistency)
- If tool-specific guidance is needed later, it can be added without changing AGENTS.md

### Session document structure
<!-- id: dec_003, status: accepted -->

**Context:** This bootstrap session needs to document both its implementation
plan and the decisions made during planning. The question is whether to use
one large document or multiple focused documents.

**Options:**

- **Two focused documents**: An implementation plan and an ADR collection,
  each following its respective template. Aligns with VIBE's composition-over-monoliths
  philosophy. Each document has a clear purpose and follows a specific template.
- **One monolithic document**: A single document containing both the implementation
  plan and decisions. Simpler to manage as one file, but mixes concerns and doesn't
  demonstrate the composition pattern that AGENTS.md will recommend.

**Chosen:** Two focused documents

**Rationale:** VIBE's core philosophy is "composition over monoliths." This
session should demonstrate the pattern it recommends. Two focused documents —
one implementation plan, one ADR collection — each following their respective
stdlib template, shows agents exactly what the convention looks like in practice.
A monolithic document would contradict the advice being codified in AGENTS.md.

**Consequences:**

- Session directory contains two files, each with a clear purpose
- Demonstrates the composition pattern that AGENTS.md will recommend to future agents
- Slightly more files to manage, but each is smaller and more focused
- Future sessions can use this as a reference for how to structure their own artifacts

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_decisions_documented | checklist | All significant decisions are recorded | Three decisions documented: session directory location, instruction file scope, document structure |
| q_options_fair | review | Alternatives are fairly represented | Each decision includes at least two options with honest descriptions; rationale explains trade-offs |
| q_consequences_present | checklist | Every decision lists consequences | All three decisions have a consequences section with at least two items |
| q_template_followed | review | ADR collection follows the adr_collection template | Document structure matches vibe/stdlib/templates/adr_collection.vibe.md |
