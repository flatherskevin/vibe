# VIBE Authoring Guide (v1.0)

Guide for writing robust `.vibe` programs.

---

## Golden Rules

1. Generate planning docs first.
2. Always create spec/plan_manifest.json before APPLY.
3. Prefer schemas over natural language.
4. Prefer patches over full overwrites.
5. Use executable gates.
6. Keep steps small.

---

## Recommended Project Layout

project.vibe

vibe/stdlib/  
vibe/spec/  
vibe/programs/

Planning docs:

spec/00_overview.md  
spec/10_architecture.md  
spec/20_artifacts.json  
spec/30_workflow.json  
spec/plan_manifest.json

---

## Writing Good Artifacts

Use strong invariants.

Bad:

"High quality code"

Good:

"Must export function createAgent()"

---

## Writing Good Steps

Each step should have one responsibility.

Examples:

generate_plans  
plan_manifest  
apply_operations  
validate_and_test  
summarize_run

---

## Gates

Prefer structured gates.

Example:

type: json_schema  
config: validate plan_manifest.json

Avoid vague checks.

---

## Plan Manifest Best Practices

A good manifest:

- lists all file operations
- sets budgets
- includes validations
- avoids unnecessary rewrites

---

## Common Pitfalls

Missing schema validation  
No diff budgets  
Too many tools allowed  
Vague gates

---

## Prompt Template for AI

Author a VIBE v1 program.

Requirements:

- generate planning docs
- generate strict plan manifest
- add validators
- use typed gates
- enforce diff budgets