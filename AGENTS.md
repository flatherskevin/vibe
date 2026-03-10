# AGENTS.md

Instructions for AI agents working in this repository.

---

## Planning Document Format

This project uses **VIBE v1**, a structured document format for AI-driven planning. When planning work in this repository, produce `.vibe.md` files — markdown documents with YAML frontmatter that capture what problem is being solved, what will be built or changed, how it was reasoned about, and what "done" looks like. This applies to **plan mode** output as well — see "Plan Mode Integration" below.

- **Full specification:** `vibe/spec/VIBE_SPEC_v1.md`
- **Authoring guide:** `vibe/spec/VIBE_AUTHORING_GUIDE.md`
- **Root project document:** `project.vibe.md`

---

## Plan Mode Integration

VIBE is a **format**, not a framework. Frameworks (GSD, Superpowers, etc.) define process; VIBE defines output shape. When any tool or framework enters its planning phase, the plan output should be structured as a VIBE v1 document.

### When to produce VIBE documents

- **Plan mode activation** — When a tool enters a read-only planning phase (e.g., Shift+Tab in Claude Code), the plan file content must be valid VIBE v1.
- **Framework plan phases** — When a planning framework (GSD, Superpowers, etc.) produces a plan or design artifact, that artifact uses VIBE format.
- **Writing to a tool's plan file** — When an agent writes to a tool-specific plan file path, the content is VIBE-formatted regardless of the path.

### Tool plan files

Each tool stores plan files in its own location. The content is always VIBE v1:

| Tool | Plan file location | Notes |
|------|-------------------|-------|
| Claude Code | `~/.claude/plans/` or tool-specified path | Plan file path provided by the tool at plan mode entry |
| Cursor | `.cursor/plans/` | Composer plan files |
| Copilot CLI | Tool-managed | Plan content passed back to the tool |
| Windsurf | `.windsurf/plans/` | Cascade plan files |
| Roo Code | Tool-managed | Plan content passed back to the tool |

**Rule:** The tool controls the file path; VIBE controls the file content.

### Planning frameworks

Frameworks define process. VIBE defines the shape of plan outputs within that process:

| Framework | VIBE-formatted outputs | Non-VIBE outputs (framework-specific) |
|-----------|----------------------|--------------------------------------|
| GSD | `{phase}-{N}-PLAN.md` plan files | `PROJECT.md`, `STATE.md`, `CHECKLIST.md` |
| Superpowers | Plan and design phase artifacts | Brainstorm, setup, and retrospective outputs |
| Custom | Any artifact labeled as a plan or design | Framework bookkeeping and state files |

**Rule:** Framework plan/design outputs use VIBE format. Framework bookkeeping files (state tracking, checklists, project metadata) remain in their native format.

### Canonical location vs. tool paths

- **Canonical:** `docs/vibe/<session-id>/` is the authoritative location for planning documents in this repository.
- **Tool paths:** Tool-specific paths (e.g., `~/.claude/plans/`) are working copies. When a plan is finalized, copy or move it to the canonical location.

---

## File Structure

Every `.vibe.md` file must begin with YAML frontmatter containing `vibe: "1.0"` and a `meta` block:

```yaml
---
vibe: "1.0"
meta:
  name: feature_name_plan
  description: "What this document plans or decides"
  session_id: "2026-03-10-a1b2c3"
  created_at: "2026-03-10"
  updated_at: "2026-03-10"
  author: claude
  tags:
    - relevant-tag
  status: draft
imports:
  - ../../../vibe/stdlib/quality.vibe.md
---
```

**Required fields:**
- `vibe` — Must be `"1.0"`
- `meta.name` — snake_case document identifier
- `meta.description` — Human-readable summary
- `meta.status` — One of: `draft`, `review`, `final`

**Recommended fields:**
- `meta.session_id` — Planning session identifier (see convention below)
- `meta.created_at` / `meta.updated_at` — ISO date strings
- `meta.author` — Who created the document
- `meta.tags` — Freeform tags for categorization
- `imports` — Array of `.vibe.md` file paths to import (relative to this file)

---

## Session Directory Convention

Store planning session artifacts under:

```
docs/vibe/<session-id>/
```

**Session ID format:** `{YYYY-MM-DD}-{6-char-hex}` (e.g., `2026-03-10-091131`)

Generate the hex portion randomly at session start. Each session gets its own directory containing all `.vibe.md` files produced during that session.

**Example session structure:**
```
docs/vibe/2026-03-10-091131/
  agents_md_implementation.vibe.md    # Implementation plan
  session_bootstrap_decisions.vibe.md # ADR collection
```

---

## Templates

Start new documents from these templates under `vibe/stdlib/templates/`:

| Template | File | Use When |
|----------|------|----------|
| Overview | `overview.vibe.md` | Framing a problem and high-level approach |
| Architecture | `architecture.vibe.md` | Designing system components and interactions |
| Implementation Plan | `implementation_plan.vibe.md` | Planning step-by-step implementation with artifacts |
| Risk Assessment | `risk_assessment.vibe.md` | Identifying and mitigating risks |
| ADR Collection | `adr_collection.vibe.md` | Recording architectural decisions |

Copy and modify templates rather than importing them directly.

---

## Standard Library

Import shared modules from `vibe/stdlib/`:

| Module | Path | Import When |
|--------|------|-------------|
| Quality | `vibe/stdlib/quality.vibe.md` | Always — provides standard quality criteria (frontmatter validity, schema validation, section typing, etc.) |
| Context Budget | `vibe/stdlib/context_budget.vibe.md` | Long planning sessions — provides context budgeting guidance for AI systems |

Import paths are relative to the importing file. From a session directory:

```yaml
imports:
  - ../../../vibe/stdlib/quality.vibe.md
```

---

## Document Sections

Organize document content using typed sections. Mark each section with an HTML comment declaring its `id` and `type`:

```markdown
### Section Title
<!-- id: section_id, type: analysis -->

Section content here.
```

**Section types:**

| Type | Purpose |
|------|---------|
| `analysis` | Examining current state, research findings, problem investigation |
| `design` | Proposing solutions, architecture, implementation approaches |
| `specification` | Precise definitions of interfaces, data models, contracts |
| `decision` | Inline decision documentation (use top-level `decisions` for full ADRs) |
| `risk` | Risk identification, likelihood, impact, and mitigations |
| `checklist` | Task lists, implementation phases, verification steps |

**Top-level document fields** beyond sections:

- `context` — Problem statement, constraints, assumptions, scope
- `artifacts` — Planned or tracked files with acceptance criteria
- `decisions` — Full Architecture Decision Records with options, rationale, consequences
- `quality` — Criteria defining what "done" looks like

---

## Workflow

Documents follow a three-stage lifecycle:

1. **`draft`** — Initial creation. Content is being written and may be incomplete.
2. **`review`** — Content is complete. Ready for human or AI review.
3. **`final`** — Reviewed and approved. Represents the accepted plan.

Set `meta.status` to `draft` when creating a document. Advance to `review` when all sections have substantive content. Advance to `final` only after review.
