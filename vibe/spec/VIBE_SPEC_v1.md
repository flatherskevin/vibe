# VIBE Language Specification v1.0

VIBE is a declarative, AI-first language whose primary runtime is an AI agent harness.

A VIBE program is a set of `.vibe` files that define:
- meta: project metadata
- imports: module graph
- context: problem statement + constraints + glossary
- tools: tool schemas (side effects must occur ONLY via tools)
- artifacts: required repo files + invariants
- workflow: steps, gates, retries, tool allowlists
- validation: validators to prove correctness

## 1. Files and Program Structure

- All source files end with `.vibe`.
- Program root MUST include `project.vibe`.
- Additional `.vibe` files MAY exist in any directory.

### 1.1 Imports
- `imports` is a list of relative file paths to `.vibe` modules.
- Import order matters: later imports append workflow steps.

### 1.2 Merge Rules (Normative)
When multiple files define the same keys:
- meta: merged; conflicting scalar keys are an error
- tools: merged by tool name; conflicts are an error
- artifacts: merged by path; conflicts are an error unless explicitly overridden
- workflow.steps: appended in import order
- validation: merged; conflicting validator ids are an error

## 2. Syntax (VIBE