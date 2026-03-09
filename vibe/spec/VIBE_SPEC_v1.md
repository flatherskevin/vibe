# VIBE Specification v1

VIBE defines a **compiled specification format** for AI software work.

It is designed to transform loosely structured planning artifacts into a **deterministic contract** that downstream systems can interpret.

---

# Compilation Model

```
Planning Artifacts
      ↓
AI Compiler
      ↓
.vibe
      ↓
Consumer System
```

Planning artifacts may include:

- markdown plans
- architecture docs
- research notes
- task lists
- AI transcripts
- PRDs

The compiler normalizes this information into a `.vibe` file.

---

# File Format

`.vibe` files use YAML syntax.

---

# Top Level Fields

```
meta
sources
scope
artifacts
constraints
transforms
validation
handoff
```

---

# meta

General metadata describing the compiled specification.

```yaml
meta:
  name: implement-auth
  version: 1
  description: authentication system implementation
```

---

# sources

Artifacts used during compilation.

```yaml
sources:
  - docs/plan.md
  - docs/architecture.md
  - docs/tasks.md
```

---

# scope

Defines which parts of the repository the compiled specification affects.

```yaml
scope:
  include:
    - src/auth/**
    - tests/auth/**
  exclude:
    - migrations/**
```

---

# artifacts

Expected outputs of the work.

```yaml
artifacts:
  outputs:
    - src/auth/service.py
    - src/auth/routes.py
    - tests/auth/test_auth.py
```

---

# constraints

Rules that guide downstream systems.

```yaml
constraints:
  language: python
  framework: fastapi
  test_framework: pytest
```

---

# transforms

Optional transformations derived during compilation.

```yaml
transforms:
  generate_tests: true
  enforce_type_hints: true
```

---

# validation

Conditions that must hold true after execution.

```yaml
validation:
  tests_required: true
  lint_required: true
```

---

# handoff

Information for downstream systems consuming the compiled specification.

```yaml
handoff:
  target_system: codegen
  expected_branch: feature/auth
```

---

# Philosophy

VIBE is not:

- a planning framework
- an execution runtime
- an agent orchestration system

VIBE is a **compiled specification contract**.

It exists to normalize AI-generated planning artifacts into a structured format that machines can reliably interpret.