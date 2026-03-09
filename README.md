# VIBE

**VIBE is a compiled specification format for AI software work.**

Modern AI workflows generate large amounts of planning artifacts:

- markdown plans
- research documents
- task breakdowns
- architecture notes
- AI conversation outputs
- issue lists
- PRDs

These artifacts are **useful for humans**, but **unreliable as execution contracts** for AI systems.

They are ambiguous, inconsistent, and difficult to validate.

VIBE solves this problem by acting as a **compile target**.

Instead of letting AI systems directly execute markdown plans, those plans are **compiled into `.vibe` files**, which become a **structured contract describing the intended work.**

---

# Core Idea

```
Natural Language
        ↓
Research / Planning Tools
        ↓
Markdown Artifacts
        ↓
AI Compiler
        ↓
.vibe
        ↓
Execution System
```

VIBE does **not** perform planning.

VIBE does **not** perform execution.

VIBE exists as the **normalized interface between them.**

---

# Why VIBE Exists

AI systems are excellent at exploration and planning, but poor at:

- maintaining deterministic structure
- respecting execution scope
- producing stable machine-readable contracts

Markdown plans drift over time and become unreliable.

VIBE introduces a **compiled specification layer** that transforms messy planning artifacts into a **structured, validated contract**.

This allows execution systems to operate with **deterministic inputs**.

---

# What a `.vibe` File Represents

A `.vibe` file is the **compiled representation of intended work**.

It may include:

- metadata
- source artifacts used during compilation
- scoped files and directories
- required outputs
- transformations
- constraints
- validation rules
- execution intent

Execution systems may interpret `.vibe` however they choose.

VIBE simply guarantees that the **intent is normalized and structured.**

---

# Example

Source planning artifacts:

```
docs/plan.md
docs/architecture.md
docs/tasks.md
```

Compiled output:

```
build_feature.vibe
```

Example `.vibe` file:

```yaml
meta:
  name: implement-authentication
  version: 1

sources:
  - docs/plan.md
  - docs/architecture.md
  - docs/tasks.md

scope:
  include:
    - src/auth/**
    - tests/auth/**
  exclude:
    - migrations/**

artifacts:
  outputs:
    - src/auth/service.py
    - src/auth/routes.py
    - tests/auth/test_auth.py

constraints:
  language: python
  framework: fastapi

validation:
  tests_required: true
  lint_required: true
```

---

# Design Principles

### 1. Compile, Don't Plan

Planning should happen in external systems.

VIBE exists only as the **compiled contract**.

---

### 2. Deterministic Structure

`.vibe` files are designed to be:

- machine readable
- schema validated
- predictable for AI systems

---

### 3. Tool-Agnostic

Any system can generate `.vibe`.

Examples:

- research agents
- planning frameworks
- code assistants
- CI pipelines
- IDE tools

---

### 4. Runtime Independence

VIBE does not prescribe execution.

Execution systems may:

- generate code
- apply repository changes
- produce infrastructure
- run validations
- orchestrate pipelines

VIBE simply describes the **compiled intent.**

---

# Typical Workflow

```
1. AI research tool generates planning docs
2. Planning artifacts accumulate (markdown, notes, specs)
3. AI compiler converts artifacts into `.vibe`
4. `.vibe` becomes the contract for the next system
5. downstream system executes the work
```

---

# Why Not Just Use Markdown?

Markdown is great for **humans**, but poor for **machines**.

Problems:

- inconsistent structure
- missing fields
- ambiguous intent
- difficult validation
- scope drift

`.vibe` provides a **strict schema** that AI systems can reliably consume.

---

# Goals of the Project

VIBE aims to become a **universal compiled format for AI work specification.**

Similar to how compilers normalize code before execution, VIBE normalizes **AI-generated work plans** before downstream systems act on them.

---

# Future Tooling

Planned tooling includes:

```
vibe compile
vibe validate
vibe inspect
vibe normalize
```

As well as integrations through:

- MCP servers
- IDE plugins
- AI skills
- CI pipelines

---

# Status

Early specification.

The goal of this repository is to define the **format and philosophy of compiled AI work contracts.**

---

# License

MIT