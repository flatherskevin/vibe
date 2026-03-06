# VIBE Runtime Hooks (v1.0)

This document defines optional runtime hook points that allow orchestrators to enforce hard logical guardrails during VIBE execution.

These hooks allow a runtime to intercept execution events and enforce additional policy before continuing.

Hooks are not required for a minimal VIBE runtime, but are strongly recommended for production environments.

---

# Purpose

VIBE uses schemas, validators, and manifests to constrain AI behavior.

Runtime hooks extend this system by allowing orchestrators to enforce additional constraints such as:

- security policies
- diff budgets
- tool allowlists
- resource limits
- audit logging
- external approval systems

Hooks operate outside the language itself and provide **deterministic enforcement points**.

---

# Hook Lifecycle

A VIBE runtime may expose the following lifecycle events:

    on_program_loaded
    on_plan_generated
    on_manifest_validated
    before_operation
    after_operation
    before_validator
    after_validator
    on_run_complete
    on_run_failure

Each hook receives structured data describing the event context.

The runtime may:

- allow execution to continue
- modify metadata
- reject the action

---

# Example Hook Context

Example data passed to a hook:

    {
      "step_id": "apply_operations",
      "operation": {
        "op": "write",
        "path": "src/main.ts"
      },
      "diff_size": 42
    }

The hook may return:

    allow
    reject
    modify

---

# Example Hook Implementations

## Diff Budget Enforcement

A runtime may reject operations that exceed a configured diff budget.

Example logic:

    if diff_size > diff_budget:
        reject("VIBE_BUDGET_EXCEEDED")

---

## Tool Policy Enforcement

Hooks can enforce tool allowlists or deny lists.

Example:

    if tool_name not in allowed_tools:
        reject("VIBE_TOOL_NOT_ALLOWED")

---

## Security Enforcement

Hooks may prevent modifications to sensitive paths.

Example:

    if operation.path starts_with ".git/":
        reject("VIBE_OPERATION_NOT_PERMITTED")

---

# Approval Hooks

Hooks can also integrate with external approval systems.

Example:

    if operation.path matches "production_config":
        require_manual_approval()

This allows VIBE to integrate with:

- CI systems
- deployment pipelines
- security scanners

---

# Logging Hooks

Runtimes may also use hooks for observability.

Example:

    log_event({
        step: step_id,
        operation: operation,
        timestamp: now()
    })

This enables full audit logs of AI-driven changes.

---

# Recommended Usage

Production VIBE runtimes should implement hooks for:

- diff budget enforcement
- tool allowlists
- restricted paths
- audit logging

These hooks ensure that even if an AI agent behaves incorrectly, the runtime can still enforce safe behavior.

---

# Design Philosophy

VIBE treats AI agents as **untrusted planners**.

The runtime is responsible for enforcing deterministic execution.

Hooks provide the final enforcement layer between AI plans and real-world side effects.