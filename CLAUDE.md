# CLAUDE.md

Follow the instructions in `AGENTS.md` strictly.

---

## Plan Mode

When in plan mode (activated via Shift+Tab or mode toggle), the plan file content must be valid VIBE v2. The tool provides the plan file path; you provide VIBE-formatted content.

Use this minimal template for plan mode output:

```yaml
---
vibe: "2.0"
meta:
  name: plan_name_here
  description: "One-line description of what this plan covers"
  author: claude
  status: draft
---
```

### Required structure

After the frontmatter, include these sections:

1. **Context** — Problem statement and constraints

```markdown
## Context

### Problem
[What needs to be done and why]

### Constraints
[Key constraints: compatibility, scope limits, dependencies]
```

2. **Sections** — Scope analysis, approach design, and task checklist

```markdown
## Sections

### Scope Analysis
<!-- id: scope_analysis, type: analysis -->
[What files/systems are affected]

### Approach
<!-- id: approach, type: design -->
[How the implementation will proceed]

### Tasks
<!-- id: tasks, type: checklist -->
- [ ] Task 1
- [ ] Task 2
```

3. **Quality** — Criteria defining what "done" looks like

```markdown
## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_1 | test | [What is verified] | [How it is verified] |
```

### MCP server

When the VIBE MCP server is connected, the `plan_in_vibe` prompt provides richer guidance including stdlib imports and template selection. Use it when available for complex plans.
