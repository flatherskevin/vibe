---
vibe: "1.0"
meta:
  name: stdlib_context_budget
  description: >
    Context budgeting and compaction guidance for AI systems working with
    VIBE documents. Helps AI maintain reliable planning across long sessions.
  author: vibe
  tags:
    - stdlib
    - context-management
  status: final
---

## Context

### Purpose

VIBE is AI-first. AI systems working with .vibe.md documents across long
planning sessions need explicit context management to remain reliable.
This module provides guidance for managing context windows effectively.

## Sections

### Context Budget Guidance
<!-- id: budget_guidance, type: specification -->

When working with .vibe.md documents in a planning session:

Max tokens per planning step: ~6000 tokens

Persistent documents (keep in context):
- The current .vibe.md document being authored
- Imported .vibe.md documents referenced by the current document
- Relevant spec documents (VIBE_SPEC_v1.md at minimum)

Compactable content (summarize when context is tight):
- Previous planning iterations
- Reviewed and finalized sections
- Resolved decisions

### Compaction Strategy
<!-- id: compaction_strategy, type: design -->

After each meaningful planning step, create a compact summary:
- Current document status (draft/review/final)
- Sections completed vs remaining
- Key decisions made
- Open questions or risks
- Artifacts planned vs created

This summary helps AI systems resume planning after context
compression or across conversation boundaries.

### Session Continuity
<!-- id: session_continuity, type: design -->

When resuming work in a new conversation or after context compression:
1. Read the current .vibe.md document to restore state
2. Check meta.status to understand lifecycle position
3. Review sections for completed vs placeholder content
4. Check decisions for proposed vs accepted status
5. Review quality criteria for pass/fail status

The structured nature of .vibe.md documents makes them self-describing
state snapshots, reducing the need for external state tracking.
