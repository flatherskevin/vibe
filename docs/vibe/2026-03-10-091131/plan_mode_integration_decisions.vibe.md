---
vibe: "2.0"
meta:
  name: plan_mode_integration_decisions
  description: >
    Architecture decisions for integrating VIBE v2 as the format layer for
    plan mode output across AI tools and planning frameworks.
  session_id: "2026-03-10-091131"
  created_at: "2026-03-10"
  updated_at: "2026-03-10"
  author: claude
  tags:
    - adr
    - decisions
    - plan-mode
  status: draft
imports:
  - ../../../vibe/stdlib/quality.vibe.md
---

## Context

### Problem

AI tools (Claude Code, Cursor, Copilot CLI, Windsurf, Roo Code) each have a
"plan mode" — a read-only planning phase where the agent designs an approach
before implementing. Planning frameworks (GSD, Superpowers) also produce plan
artifacts during their planning phases. Currently, plan mode output is ad-hoc
markdown with no consistent structure. VIBE v2 exists as a structured planning
format but is not connected to plan mode in any tool or framework.

### Scope

This collection covers three decisions about how VIBE integrates with plan mode:
the relationship between VIBE documents and plan files, where universal vs.
tool-specific guidance lives, and which framework outputs use VIBE format.

## Sections

### Background
<!-- id: background, type: analysis -->

AGENTS.md already instructs agents to produce `.vibe.md` files for planning
work, but does not mention plan mode — the specific phase tools enter when
designing an approach before implementation. The gap means agents in plan mode
produce unstructured markdown instead of VIBE documents.

The key insight is that VIBE is a format, not a framework. Frameworks define
process (what phases to go through, what questions to ask); VIBE defines output
shape (frontmatter, typed sections, quality criteria). This distinction
determines how VIBE relates to both tools and frameworks.

## Decisions

### VIBE document IS the plan file
<!-- id: dec_001, status: accepted -->

**Context:** When a tool enters plan mode, it provides a plan file path (e.g.,
`~/.claude/plans/plan.md`). The question is whether the VIBE document should be
written directly to this path or maintained as a separate artifact alongside it.

**Options:**

- **plan_file_is_vibe**: Write VIBE-formatted content directly to the tool's
  plan file path. The plan file IS the VIBE document. No separate artifact, no
  copying, no synchronization. The tool controls the path; VIBE controls the
  content.
- **separate_artifacts**: Write VIBE documents to `docs/vibe/` and maintain a
  separate plan file for the tool. Keeps VIBE artifacts in the canonical
  location but requires synchronization between two files with the same content.

**Chosen:** plan_file_is_vibe

**Rationale:** Plan mode is about producing a plan, and VIBE is about
structuring plans. Writing VIBE content directly to the plan file eliminates
duplication and synchronization overhead. The tool already reads the plan file
to present the plan to the user — making that file VIBE-formatted gives it
structure without adding complexity. The canonical `docs/vibe/` location is
for finalized plans, not working drafts.

**Consequences:**

- Plan files are immediately useful as structured VIBE documents
- No synchronization needed between tool paths and canonical paths
- Finalized plans can be copied to `docs/vibe/<session-id>/` when the session ends
- Tools that don't support YAML frontmatter may need adaptation (none known currently)

### Universal guidance in AGENTS.md, tool-specific in CLAUDE.md
<!-- id: dec_002, status: accepted -->

**Context:** Plan mode integration guidance needs to live somewhere agents will
read it. The question is whether to put everything in AGENTS.md (tool-agnostic)
or split between AGENTS.md and tool-specific files like CLAUDE.md.

**Options:**

- **agents_md_only**: Put all plan mode guidance in AGENTS.md, including
  tool-specific details. Keeps everything in one place but mixes universal
  format guidance with tool-specific paths and behaviors.
- **split_by_scope**: Put universal guidance (what VIBE format is, when to use
  it, framework integration rules) in AGENTS.md. Put tool-specific guidance
  (inline template, plan file conventions for this tool) in the tool's
  instruction file (CLAUDE.md for Claude Code). Matches the existing pattern
  where AGENTS.md is tool-agnostic.

**Chosen:** split_by_scope

**Rationale:** AGENTS.md established in the bootstrap session that it is
tool-agnostic. Adding Claude-specific inline templates or plan file paths would
contradict that design decision. The split keeps AGENTS.md clean: it says "plan
mode output uses VIBE format" and provides the tool plan files table. CLAUDE.md
then provides the concrete inline template a Claude agent can copy when entering
plan mode. Other tools can have their own instruction files (.cursorrules, etc.)
with their own inline templates.

**Consequences:**

- AGENTS.md remains tool-agnostic and reusable across all AI tools
- CLAUDE.md grows from 1 line to ~35 lines, but all additions are Claude-specific
- Other tool instruction files can be created independently without modifying AGENTS.md
- Agents that only read AGENTS.md still know to use VIBE format; they just don't get the inline template shortcut

### Framework plan outputs use VIBE; framework bookkeeping does not
<!-- id: dec_003, status: accepted -->

**Context:** Planning frameworks like GSD and Superpowers produce multiple file
types: plan/design artifacts and bookkeeping files (project state, checklists,
configuration). The question is which of these should use VIBE format.

**Options:**

- **all_framework_outputs**: Every file a framework produces uses VIBE format.
  Maximizes consistency but forces VIBE structure onto files designed for
  different purposes (e.g., GSD's STATE.md is a key-value state tracker, not
  a planning document).
- **plan_outputs_only**: Framework plan and design artifacts use VIBE format.
  Framework bookkeeping files (STATE.md, PROJECT.md, CHECKLIST.md) stay in
  their native format. Respects that VIBE is a planning format, not a universal
  document format.

**Chosen:** plan_outputs_only

**Rationale:** VIBE is designed for planning documents — artifacts that capture
what problem is being solved, how it was reasoned about, and what "done" looks
like. Framework bookkeeping files serve a different purpose: they track state,
configuration, and progress. Forcing VIBE structure onto a state tracker like
GSD's STATE.md would add overhead without benefit. The clear rule is: if the
artifact is a plan or design document, use VIBE; if it's operational
bookkeeping, use the framework's native format.

**Consequences:**

- GSD's `{phase}-{N}-PLAN.md` files use VIBE; `STATE.md` and `PROJECT.md` do not
- Superpowers plan/design outputs use VIBE; brainstorm and setup outputs do not
- Clear boundary: agents can determine format by artifact type, not by framework
- Frameworks don't need to be modified — only their plan output format changes

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_decisions_documented | checklist | All three decisions are recorded | Three decisions documented: plan file identity, guidance scope split, framework output boundary |
| q_options_fair | review | Alternatives are fairly represented | Each decision includes two options with honest descriptions; rationale explains trade-offs |
| q_consequences_present | checklist | Every decision lists consequences | All three decisions have a consequences section with at least three items |
| q_consistent_with_agents_md | review | Decisions align with AGENTS.md content | Plan Mode Integration section in AGENTS.md reflects decisions made here |
