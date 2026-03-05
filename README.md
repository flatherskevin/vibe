# VIBE

**VIBE** is an **AI instruction language** designed to make AI agents reliable when modifying software systems.

Instead of letting AI freely generate code, VIBE introduces a **structured execution layer** between human intent and AI actions.

The workflow looks like this:

```
Human intent (natural language)
        ↓
AI generates a VIBE plan
        ↓
AI executes the VIBE plan deterministically
```

VIBE acts like **Terraform for AI actions**.

It separates **planning** from **execution**, ensuring that AI systems behave predictably, safely, and repeatably.

---

# The Problem

Modern AI agents are powerful but unreliable when allowed to directly modify codebases or systems.

Common failure modes include:

- hallucinated files
- incomplete implementations
- inconsistent architecture decisions
- uncontrolled side effects
- partially applied changes

These issues occur because most AI workflows combine **planning and execution in a single step**.

---

# The VIBE Solution

VIBE introduces an **intermediate instruction language** that forces AI systems to:

1. **Create a structured plan**
2. **Validate that plan**
3. **Execute the plan deterministically**

Instead of:

```
Human → AI → Code Changes
```

You get:

```
Human → AI → VIBE Plan → AI Execution
```

This dramatically improves reliability.

---

# Human Workflow

Humans **never write VIBE manually**.

The intended workflow is:

```
1. Human describes intent in natural language
2. AI generates a VIBE plan
3. AI validates the plan
4. AI executes the plan
```

Example:

Human prompt:

```
Add authentication middleware to the API server
and create integration tests.
```

AI produces:

```
plan "Add authentication middleware"

artifact "auth_middleware.go"
artifact "auth_test.go"

apply "Create authentication middleware"
apply "Add middleware to router"
apply "Create integration tests"

validate "Tests pass"
validate "Server compiles"
```

The AI then executes the VIBE plan step-by-step.

---

# Why VIBE Exists

VIBE exists to solve three core problems with current AI coding workflows:

### 1. Deterministic Execution

AI must explicitly define what it intends to do before doing it.

### 2. Reduced Hallucination

Files and artifacts must be declared before modification.

### 3. Controlled Side Effects

Execution occurs only within the defined plan.

---

# Core Concepts

## Plan

A **plan** defines the scope of work.

```
plan "Implement OAuth login"
```

All work must occur within a plan.

---

## Artifacts

Artifacts define **files or resources** the plan is allowed to modify.

```
artifact "auth_controller.go"
artifact "auth_routes.go"
artifact "oauth_service.go"
```

Artifacts prevent AI from touching unrelated files.

---

## Apply Steps

Apply steps describe **specific modifications**.

```
apply "Add OAuth login endpoint"
apply "Implement OAuth token exchange"
apply "Register OAuth routes"
```

These are executed sequentially.

---

## Validation Rules

Validation ensures the plan succeeded.

```
validate "Tests pass"
validate "Project builds"
validate "API server starts"
```

If validation fails, execution halts.

---

# Execution Model

The runtime executes VIBE in two phases.

## Phase 1: Planning

AI generates the VIBE plan.

The plan must include:

- declared artifacts
- ordered apply steps
- validation rules

---

## Phase 2: Apply

The runtime executes each step:

```
for step in plan.apply_steps:
    execute(step)
```

After execution:

```
run_validations()
```

---

# Example VIBE File

```
plan "Add request logging middleware"

artifact "middleware/logging.go"
artifact "server/router.go"

apply "Create logging middleware"
apply "Attach middleware to router"

validate "Project builds"
validate "Server starts"
```

---

# Why This Matters

As AI becomes more capable, **direct code generation becomes dangerous at scale**.

VIBE provides a **structured instruction layer** that makes AI systems:

- predictable
- inspectable
- deterministic
- safe to run in production environments

This allows AI agents to operate more like **infrastructure tooling** rather than uncontrolled assistants.

---

# Analogy

| System | Purpose |
|------|------|
| Terraform | Infrastructure planning |
| Kubernetes | Container orchestration |
| Makefiles | Build execution |
| **VIBE** | AI action planning |

---

# Long-Term Vision

VIBE is intended to become a **universal execution format for AI agents**.

Potential runtimes could include:

- IDE agents
- CI/CD agents
- codebase maintenance agents
- infrastructure automation agents
- autonomous software systems

---

# Project Status

Early experimental specification.

The language is intentionally minimal to allow multiple AI runtimes to implement it.

---

# License

MIT