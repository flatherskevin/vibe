# VIBE

**VIBE** is an **AI-first programming language** designed to make AI agents reliable when modifying software systems.

Most AI agent workflows today rely on **unstructured planning documents** (usually markdown). These plans look good to humans, but they are a poor control surface for AI systems.

They are:

- ambiguous
- hard to validate
- difficult to execute deterministically
- easy for models to drift away from

VIBE solves this by giving AI systems a **structured programming language** to generate instead of unstructured plans.

---

# The Core Idea

Instead of this:

Natural language → Markdown planning docs → AI execution

VIBE introduces a structured intermediate language:

Natural language → **VIBE program** → AI execution → Code changes

The AI writes a **program describing the work**, and that program becomes the execution contract.

---

# Why This Matters

Unstructured plans cause real problems for AI agents:

- hallucinated files
- partially implemented features
- architecture drift
- uncontrolled side effects
- inconsistent execution

These failures happen because the AI is trying to follow **loose natural language instructions** it wrote earlier.

VIBE replaces those instructions with a **formal structure**.

Instead of writing a paragraph describing what to do, the AI writes a **program describing what to do**.

---

# Human Workflow

Humans **do not write VIBE programs manually**.

The intended workflow is:

1. Human describes intent in natural language
2. AI generates a VIBE program
3. AI executes that program to produce targeted output

Example intent:

Add authentication middleware and create integration tests.

The AI then generates a VIBE program describing the work and executes it.

---

# Core Concepts

## VIBE Programs

A VIBE program defines the work to be done.

Programs describe:

- scope
- artifacts
- execution steps
- validation rules

This structure allows the runtime to execute the work deterministically.

---

## Artifacts

Artifacts define **what files or resources are allowed to change**.

This prevents AI agents from modifying unrelated parts of the system.

---

## Apply Steps

Apply steps define the **actions the AI must perform**.

Instead of vague instructions, execution is broken into explicit steps.

---

## Validation

Validation rules verify that the intended outcome was achieved.

Examples include:

- project builds
- tests pass
- services start successfully

If validation fails, execution stops.

---

# Execution Model

VIBE runs in two phases.

## Phase 1 — Planning

The AI generates a VIBE program describing the intended work.

## Phase 2 — Execution

The runtime executes the program step-by-step and applies changes to the system.

This separation dramatically improves reliability.

---

# Why Use VIBE

VIBE helps AI agents behave more like **infrastructure tooling** instead of unpredictable assistants.

Benefits include:

- deterministic execution
- explicit scope
- controlled side effects
- structured reasoning
- improved reliability

---

# Analogy

| System | Purpose |
|------|------|
| Terraform | Infrastructure planning |
| Kubernetes | Container orchestration |
| Makefiles | Build execution |
| **VIBE** | AI action programming |

---

# Long-Term Vision

VIBE is intended to become a **universal execution format for AI agents**.

Potential runtimes include:

- IDE agents
- CI/CD automation
- codebase maintenance agents
- infrastructure automation agents
- autonomous software systems

The goal is simple:

AI agents should not plan complex work in **unstructured prose**.

They should write **programs**.

---

# Project Status

Early experimental specification.

The language is intentionally minimal so that different AI runtimes can implement it.

---

# License

MIT