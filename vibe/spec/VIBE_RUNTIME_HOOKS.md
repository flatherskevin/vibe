# VIBE Runtime Hooks (v1.0)

This document defines optional runtime hook points for VIBE runtimes.

Runtime hooks allow orchestrators, execution engines, and policy layers to enforce additional constraints at deterministic points during execution.

Hooks are not required for a minimal VIBE runtime, but they are strongly recommended for production-grade systems.

They are especially useful for:

- hard logical enforcement
- security policy integration
- external approvals
- audit logging
- cost and resource control
- orchestration interoperability

---

## 1. Purpose

VIBE already defines:

- program structure
- plan manifests
- tool schemas
- gates
- validators
- scope policy

Runtime hooks extend these mechanisms by giving the runtime explicit places to intercept execution and enforce external or environment-specific policy.

Hooks are the bridge between:

- language-defined constraints
- runtime-defined enforcement
- organization-defined policy

They make VIBE suitable for real-world orchestrators where AI output alone should never be trusted as the final authority.

---

## 2. Design Goals

Runtime hooks are intended to provide:

- deterministic interception points
- structured event payloads
- policy enforcement without changing the language core
- portability across runtimes
- compatibility with existing orchestrators

Hooks should not weaken the VIBE runtime contract.

They are an additional enforcement layer, not a replacement for:

- schemas
- manifests
- validators
- scope policy

---

## 3. Hook Model

A hook is a runtime-defined callback invoked when a particular execution event occurs.

Each hook receives:

- event type
- current execution context
- event payload
- optional runtime metadata

A hook may respond with one of the following actions:

- `allow`
- `reject`
- `modify`
- `pause`

### 3.1 `allow`

Continue execution without modification.

### 3.2 `reject`

Abort or fail the current action.

The hook should provide:

- error code
- reason
- optional evidence

### 3.3 `modify`

Adjust non-authoritative execution metadata before continuing.

Examples:

- add audit tags
- attach policy annotations
- enrich logs

Hooks should not silently change the semantic meaning of the program unless the runtime explicitly documents that behavior.

### 3.4 `pause`

Temporarily halt execution pending approval or external action.

Examples:

- human approval
- external security scan
- deployment gate

---

## 4. Standard Hook Points

VIBE v1 recommends the following standard hook points.

- `on_program_loaded`
- `on_program_compiled`
- `on_plan_generated`
- `on_manifest_validated`
- `before_step`
- `after_step`
- `before_tool_call`
- `after_tool_call`
- `before_operation`
- `after_operation`
- `before_validator`
- `after_validator`
- `on_run_complete`
- `on_run_failure`

Runtimes may define additional hook points, but should preserve these semantics where supported.

---

## 5. Hook Point Semantics

## 5.1 `on_program_loaded`

Triggered after source files are loaded but before full compilation.

Typical uses:

- source provenance logging
- runtime metadata initialization
- pre-compile policy checks

Payload may include:

- list of source files
- load order
- raw metadata

---

## 5.2 `on_program_compiled`

Triggered after successful parse and merge into Program IR.

Typical uses:

- compile-time policy validation
- dependency analysis
- capability negotiation
- cache key generation

Payload may include:

- normalized Program IR
- source provenance
- compile diagnostics

---

## 5.3 `on_plan_generated`

Triggered after planning artifacts and/or the plan manifest are produced.

Typical uses:

- manifest review
- diff budget evaluation
- approval workflows
- policy scanning of planned operations

Payload may include:

- planning outputs
- `spec/plan_manifest.json`
- budget summary
- planned operations list

---

## 5.4 `on_manifest_validated`

Triggered after the manifest successfully validates against schema.

Typical uses:

- final pre-apply approval
- operation auditing
- external orchestration sync

Payload may include:

- validated manifest object
- schema version
- validation results

---

## 5.5 `before_step`

Triggered immediately before a workflow step begins.

Typical uses:

- step-level policy enforcement
- rate limiting
- step authorization
- dynamic runtime annotations

Payload may include:

- `step_id`
- `step_type`
- step inputs
- attempt number

---

## 5.6 `after_step`

Triggered immediately after a workflow step completes.

Typical uses:

- result logging
- compaction
- telemetry
- policy evaluation

Payload may include:

- `step_id`
- outputs
- tool summary
- gate results
- validation snapshot

---

## 5.7 `before_tool_call`

Triggered before a tool is invoked.

Typical uses:

- tool allowlist enforcement
- argument inspection
- secret access controls
- resource tracking

Payload may include:

- tool name
- tool args
- current step id
- execution mode

---

## 5.8 `after_tool_call`

Triggered after a tool returns.

Typical uses:

- tool result validation
- logging
- anomaly detection
- cost tracking

Payload may include:

- tool name
- tool args
- tool result
- execution duration
- success/failure status

---

## 5.9 `before_operation`

Triggered before a manifest operation is applied.

Typical uses:

- path policy enforcement
- ownership checks
- protected region scanning
- external approvals
- diff review

Payload may include:

- operation object
- path
- ownership
- write policy
- step id

---

## 5.10 `after_operation`

Triggered after a manifest operation completes.

Typical uses:

- audit logging
- diff measurement
- success/failure recording
- post-write scanning

Payload may include:

- operation object
- result
- changed file count
- bytes written
- diff summary

---

## 5.11 `before_validator`

Triggered before a validator runs.

Typical uses:

- validator authorization
- command policy checks
- test environment preparation

Payload may include:

- validator id
- validator type
- validator config

---

## 5.12 `after_validator`

Triggered after a validator finishes.

Typical uses:

- result logging
- failure analysis
- orchestration callbacks

Payload may include:

- validator id
- validator result
- evidence
- pass/fail state

---

## 5.13 `on_run_complete`

Triggered after the full run succeeds.

Typical uses:

- final audit commit
- metrics emission
- artifact indexing
- orchestration status update

Payload may include:

- step summary
- validation summary
- changed files
- manifest summary
- runtime duration

---

## 5.14 `on_run_failure`

Triggered when the run terminates unsuccessfully.

Typical uses:

- incident logging
- retry workflow routing
- escalation
- failure artifact persistence

Payload may include:

- error code
- error message
- failed step
- tool evidence
- runtime summary

---

## 6. Hook Payload Structure

A runtime SHOULD provide hook payloads in a structured object form.

Recommended shape:

    {
      "event": "before_operation",
      "timestamp": "2026-03-06T12:00:00Z",
      "run_id": "abc123",
      "step_id": "apply_operations",
      "attempt": 1,
      "payload": {
        "operation": {
          "op": "write",
          "path": "src/main.ts",
          "reason": "Create main entrypoint"
        }
      },
      "meta": {
        "mode": "plan_and_apply"
      }
    }

Fields may vary by runtime, but SHOULD be consistent within an implementation.

---

## 7. Hook Response Structure

A runtime SHOULD support structured hook responses.

Recommended shape:

    {
      "action": "allow"
    }

Reject example:

    {
      "action": "reject",
      "error": {
        "code": "VIBE_OPERATION_NOT_PERMITTED",
        "message": "Writes to .git/ are forbidden"
      }
    }

Modify example:

    {
      "action": "modify",
      "meta": {
        "policy_tag": "security-reviewed"
      }
    }

Pause example:

    {
      "action": "pause",
      "reason": "Awaiting manual approval"
    }

---

## 8. Recommended Enforcement Use Cases

## 8.1 Diff budget enforcement

A runtime hook may reject operations or plans that exceed diff budgets.

Example logic:

    if diff_size > max_allowed:
        reject("VIBE_BUDGET_EXCEEDED")

This is especially useful at:

- `on_plan_generated`
- `before_operation`

---

## 8.2 Tool allowlist enforcement

Hooks may inspect requested tools and reject unsafe usage.

Example:

    if tool_name not in allowed_tools:
        reject("VIBE_TOOL_NOT_ALLOWED")

Best hook point:

- `before_tool_call`

---

## 8.3 Restricted path enforcement

Hooks may enforce organization-specific path rules in addition to VIBE scope policy.

Example:

    if operation.path starts with "infra/prod/":
        require_manual_approval()

Best hook points:

- `before_operation`
- `on_manifest_validated`

---

## 8.4 External approval workflows

Hooks may integrate with CI/CD systems, ticketing systems, or human approvals.

Examples:

- require approval for production config changes
- require security review for dependency updates
- require manager approval for deployment steps

Possible responses:

- `pause`
- `reject`

---

## 8.5 Audit logging

Hooks may emit audit trails to external systems.

Examples:

- security logs
- SIEM pipelines
- telemetry systems
- cost observability dashboards

Best hook points:

- `after_tool_call`
- `after_operation`
- `after_validator`
- `on_run_complete`
- `on_run_failure`

---

## 8.6 Resource and cost controls

Hooks may enforce:

- maximum token usage
- max tool calls
- execution duration limits
- file change budgets
- environment limits

This is especially useful in orchestrators managing many agents or shared infrastructure.

---

## 9. Interaction with Runtime Contract

Hooks do not override the VIBE runtime contract.

A runtime must still enforce:

- parse correctness
- merge rules
- manifest-only apply
- tool-truth
- scope policy
- gates
- validators

Hooks may strengthen enforcement, but should not weaken base guarantees.

For example:

- a hook may reject an otherwise valid operation
- a hook should not allow an operation forbidden by scope policy

---

## 10. Hook Ordering

If multiple hooks are registered for the same event, runtimes SHOULD define deterministic ordering.

Recommended approaches:

- registration order
- explicit priority values
- phase grouping

If a hook rejects an action, later hooks for that event should usually not run.

Runtimes should document their ordering behavior.

---

## 11. Failure Behavior

If a hook fails unexpectedly, runtimes SHOULD handle that failure explicitly.

Recommended behavior:

- fail closed for security-critical hooks
- fail open only for explicitly non-critical hooks such as telemetry

Examples:

- approval hook unavailable → reject or pause
- logging hook unavailable → warn and continue

This behavior should be runtime-configurable.

---

## 12. Security Considerations

Hooks are powerful and should themselves be treated as privileged runtime components.

Risks include:

- modifying execution behavior unexpectedly
- leaking sensitive data
- bypassing policy through custom logic
- creating nondeterministic behavior

Runtimes SHOULD:

- isolate hook execution where possible
- log hook outcomes
- treat hook code as trusted infrastructure
- avoid exposing secrets unless necessary

---

## 13. Minimal Hook Support

A minimal but useful hook-enabled runtime should support at least:

- `before_tool_call`
- `before_operation`
- `after_validator`
- `on_run_failure`

This provides enough surface for most orchestrators to enforce policy.

---

## 14. Example Policy Patterns

Examples of useful hook policies:

- reject writes larger than 500 lines
- reject changes to `package-lock.json` unless approved
- reject any `exec.run` command outside a safe allowlist
- require manual approval for changes under `infra/`
- send all failures to an incident queue
- block changes to protected files during weekends
- tag runs by environment or repository class

These are runtime concerns, not language concerns, which is exactly why hooks exist.

---

## 15. Relationship to Orchestrators

Hooks make VIBE compatible with existing agent orchestration systems.

An orchestrator can use hooks to:

- embed VIBE into a larger workflow system
- enforce organization policy
- coordinate multiple agents
- attach human approval loops
- integrate with CI/CD or ticketing

This makes VIBE suitable not just as a language, but as a runtime contract for agent execution.

---

## 16. Design Philosophy

VIBE treats AI agents as untrusted planners.

The runtime is responsible for turning plans into safe, deterministic execution.

Hooks are part of that responsibility.

They provide the final, enforceable boundary between:

- AI-generated intent
- repository state
- organizational policy