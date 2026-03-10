---
vibe: "2.0"
meta:
  name: agents_md_implementation
  description: >
    Implementation plan for creating AGENTS.md and bootstrapping the
    docs/vibe/ session directory convention with .vibe.md planning documents.
  session_id: "2026-03-10-091131"
  created_at: "2026-03-10"
  updated_at: "2026-03-10"
  author: claude
  tags:
    - implementation
    - agents
    - bootstrap
  status: draft
imports:
  - ../../../vibe/stdlib/quality.vibe.md
---

## Context

### Problem

The VIBE project has no agent instruction file. AI agents entering the
repository have no guidance to produce `.vibe.md` planning documents and no
established convention for where planning artifacts live. Without AGENTS.md,
every agent session starts from scratch — reading the full spec to understand
what VIBE is and how to use it. This wastes context budget and produces
inconsistent output.

### Constraints

- AGENTS.md must be tool-agnostic (not CLAUDE.md) since VIBE targets any AI agent
- AGENTS.md must be self-sufficient: an agent reading only AGENTS.md can produce a valid `.vibe.md` file
- Session directories must use the `{YYYY-MM-DD}-{6-char-hex}` format from the spec
- All `.vibe.md` files must have valid YAML frontmatter with `vibe: "2.0"`
- This session must bootstrap the convention by producing its own `.vibe.md` files first

### Assumptions

- The repository already contains the full VIBE v2 spec, authoring guide, stdlib, and templates
- `project.vibe.md` at the root demonstrates valid frontmatter conventions
- Agents will read AGENTS.md on entry (standard behavior for Claude, Copilot, Cursor, etc.)

### Scope

- In scope: AGENTS.md, CLAUDE.md, session `.vibe.md` files, `docs/vibe/` directory structure, plan mode integration
- Out of scope: Modifying existing spec files, tooling changes, schema updates, other tool instruction files (.cursorrules, etc.)

## Artifacts

| Path | Kind | Description | Status | Depends On | Acceptance Criteria |
|------|------|-------------|--------|------------|---------------------|
| AGENTS.md | markdown | Agent instruction file at project root | planned | | Self-sufficient: agent reading only AGENTS.md can produce valid .vibe.md; references spec and template paths correctly |
| docs/vibe/2026-03-10-091131/agents_md_implementation.vibe.md | vibe | This implementation plan | planned | | Valid frontmatter with vibe: "2.0"; follows implementation_plan template; import path resolves |
| docs/vibe/2026-03-10-091131/session_bootstrap_decisions.vibe.md | vibe | ADR collection for session decisions | planned | | Valid frontmatter with vibe: "2.0"; follows adr_collection template; records 3 decisions with options and rationale |
| CLAUDE.md | markdown | Claude Code plan mode instructions with inline VIBE template | planned | AGENTS.md | Contains valid VIBE v2 inline template; references AGENTS.md; includes MCP server note |
| docs/vibe/2026-03-10-091131/plan_mode_integration_decisions.vibe.md | vibe | ADR collection for plan mode integration decisions | planned | | Valid frontmatter with vibe: "2.0"; records 3 decisions: plan file identity, guidance scope, framework outputs |

## Sections

### Scope Analysis
<!-- id: scope_analysis, type: analysis -->

Three files are created, none modified:

1. **AGENTS.md** (project root) — New file. No existing AGENTS.md or CLAUDE.md to conflict with.
2. **agents_md_implementation.vibe.md** (session dir) — New file in new directory.
3. **session_bootstrap_decisions.vibe.md** (session dir) — New file in same new directory.

Existing files referenced but not modified:
- `vibe/spec/VIBE_SPEC_v2.md` — linked from AGENTS.md
- `vibe/spec/VIBE_AUTHORING_GUIDE.md` — linked from AGENTS.md
- `vibe/stdlib/templates/*` — listed in AGENTS.md
- `vibe/stdlib/quality.vibe.md` — imported by this file
- `project.vibe.md` — referenced as example in AGENTS.md

### Implementation Approach
<!-- id: approach, type: design -->

**Order of operations:**

1. Generate session ID (`2026-03-10-091131`)
2. Create `docs/vibe/2026-03-10-091131/` directory
3. Write this implementation plan (establishes the pattern)
4. Write the ADR collection (records decisions made during planning)
5. Write AGENTS.md (the primary deliverable)

**AGENTS.md design principles:**

- Distill the spec and authoring guide into actionable instructions
- Include a minimal inline `.vibe.md` example so agents don't need to read templates
- Reference templates and spec by path for agents that want full detail
- Cover the `docs/vibe/<session-id>/` convention so future sessions follow it

### AGENTS.md Specification
<!-- id: agents_md_spec, type: specification -->

AGENTS.md contains these sections:

1. **Planning Document Format** — What VIBE is (1-2 sentences), links to spec and authoring guide
2. **File Structure** — Frontmatter requirements (`vibe: "2.0"`, `meta` fields), inline minimal example
3. **Session Directory Convention** — `docs/vibe/<session-id>/` with `{YYYY-MM-DD}-{6-char-hex}` format
4. **Templates** — Table of 5 available templates under `vibe/stdlib/templates/`
5. **Standard Library** — `quality.vibe.md` and `context_budget.vibe.md`, when to import each
6. **Document Sections** — Section types (`analysis`, `design`, `specification`, `decision`, `risk`, `checklist`) and `<!-- id, type -->` convention
7. **Workflow** — `draft` → `review` → `final` lifecycle

### Plan Mode Integration Design
<!-- id: plan_mode_design, type: design -->

**Core principle:** VIBE is a format, not a framework. Tools control file paths; VIBE controls file content. Frameworks define process; VIBE defines output shape.

**AGENTS.md additions:**
- "Plan Mode Integration" section inserted after "Planning Document Format", before "File Structure"
- Tool plan files table mapping tools to their plan file locations
- Planning frameworks table distinguishing VIBE-formatted outputs from framework bookkeeping
- Canonical location vs. tool paths guidance

**CLAUDE.md additions:**
- Plan mode instructions specific to Claude Code
- Inline minimal VIBE v2 template (frontmatter + Context + Sections + Quality)
- MCP server `plan_in_vibe` prompt reference

**Separation of concerns:**
- AGENTS.md: Universal guidance — "plan mode output uses VIBE format", tool table, framework table
- CLAUDE.md: Tool-specific guidance — inline template, Claude Code plan mode conventions
- ADR file: Records the architectural decisions driving this design

### Implementation Tasks
<!-- id: task_checklist, type: checklist -->

- [x] Generate session ID
- [x] Create `docs/vibe/2026-03-10-091131/` directory
- [x] Write `agents_md_implementation.vibe.md` (this file)
- [x] Write `session_bootstrap_decisions.vibe.md`
- [x] Write `AGENTS.md`
- [ ] Add "Plan Mode Integration" section to AGENTS.md
- [ ] Expand CLAUDE.md with plan mode instructions and inline template
- [ ] Write `plan_mode_integration_decisions.vibe.md` ADR
- [ ] Update this file with expanded scope, artifacts, and tasks
- [ ] Verify all files exist at expected paths
- [ ] Verify all `.vibe.md` files have valid YAML frontmatter
- [ ] Verify import paths resolve from session directory
- [ ] Verify AGENTS.md references correct spec and template paths
- [ ] Verify no contradictions between AGENTS.md and CLAUDE.md

### Verification Steps
<!-- id: verification, type: checklist -->

- [ ] `docs/vibe/2026-03-10-091131/agents_md_implementation.vibe.md` exists with `vibe: "2.0"` frontmatter
- [ ] `docs/vibe/2026-03-10-091131/session_bootstrap_decisions.vibe.md` exists with `vibe: "2.0"` frontmatter
- [ ] `AGENTS.md` exists at project root
- [ ] Import `../../../vibe/stdlib/quality.vibe.md` resolves from session directory to existing file
- [ ] AGENTS.md references `vibe/spec/VIBE_SPEC_v2.md` (exists)
- [ ] AGENTS.md references `vibe/spec/VIBE_AUTHORING_GUIDE.md` (exists)
- [ ] AGENTS.md lists all 5 templates under `vibe/stdlib/templates/`
- [ ] An agent reading only AGENTS.md has enough information to produce a valid `.vibe.md` file

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_all_files_created | checklist | All three planned files exist | AGENTS.md at root, both .vibe.md files in session directory |
| q_frontmatter_valid | test | Both .vibe.md files have valid YAML frontmatter | Frontmatter parses as valid YAML with vibe: "2.0" and complete meta block |
| q_imports_resolve | test | Import paths resolve to existing files | ../../../vibe/stdlib/quality.vibe.md from session dir resolves to vibe/stdlib/quality.vibe.md |
| q_agents_md_self_sufficient | review | AGENTS.md is self-sufficient for producing .vibe.md files | An agent reading only AGENTS.md can produce a file with valid frontmatter, typed sections, and quality criteria |
| q_paths_correct | test | All file path references in AGENTS.md are valid | Every spec, template, and stdlib path referenced in AGENTS.md points to an existing file |
