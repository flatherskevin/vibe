# VIBE Step Types (v1.0)

VIBE step types are optional but strongly recommended classifications for workflow steps.

They help runtimes apply stricter, more predictable behavior based on the intent of each step.

If a step type is omitted, the runtime SHOULD treat it as:

    generic

---

## 1. Purpose

Step types improve:

- execution clarity
- runtime policy enforcement
- AI planning quality
- debugging
- tool restriction defaults

Without step types, all steps must be treated the same. That is safe, but less expressive.

---

## 2. Standard Step Types

VIBE v1 defines the following recommended step types:

- `plan`
- `generate`
- `apply`
- `validate`
- `summarize`
- `refactor`
- `generic`

Runtimes may define additional types, but should preserve the semantics of the standard ones.

---

## 3. `plan`

A planning step produces structured planning artifacts or planning state.

Typical outputs:

- `spec/00_overview.md`
- `spec/10_architecture.md`
- `spec/20_artifacts.json`
- `spec/30_workflow.json`
- `spec/plan_manifest.json`

Typical characteristics:

- side effects should usually be limited to `spec/`
- should not directly modify implementation files unless explicitly allowed
- should be highly schema-driven

Typical tools:

- `fs.read`
- `fs.list`
- `fs.write`

Example use cases:

- artifact planning
- architecture planning
- manifest generation
- budget planning

---

## 4. `generate`

A generation step creates new artifacts from approved specifications.

Typical characteristics:

- usually writes new files
- may generate code, docs, tests, or config
- should respect artifact invariants
- should remain bounded by manifest and scope policy

Typical tools:

- `fs.read`
- `fs.write`
- `fs.apply_patch`

Example use cases:

- generate source files
- generate test files
- generate docs from spec artifacts

---

## 5. `apply`

An apply step executes planned operations from the manifest.

Typical characteristics:

- side effects are expected
- operations should be manifest-driven
- should strictly enforce tool allowlists
- should reject non-manifest changes

Typical tools:

- `fs.read`
- `fs.write`
- `fs.apply_patch`
- `fs.list`

Example use cases:

- apply operations from `spec/plan_manifest.json`
- materialize repo changes
- create files and directories listed in the manifest

This is one of the most important step types because it crosses from planning into real side effects.

---

## 6. `validate`

A validate step proves correctness.

Typical characteristics:

- should not modify repository state except optional logs
- should execute validators and gates
- should produce pass/fail evidence

Typical tools:

- `fs.read`
- `fs.list`
- `exec.run`
- optional `fs.write` for run logs

Example use cases:

- run tests
- validate schemas
- check required files
- verify content rules

Validate steps are a core part of the program contract.

---

## 7. `summarize`

A summarize step produces compact summaries or run logs.

Typical characteristics:

- should not modify implementation files
- should produce documentation about execution state
- often used for long-running agent compaction

Typical tools:

- `fs.read`
- `fs.write`

Typical outputs:

- `spec/runlog_compacted.md`
- step summaries
- remaining work summaries

---

## 8. `refactor`

A refactor step changes existing files while preserving structure and behavior.

Typical characteristics:

- should prefer patches over full rewrites
- should strongly respect diff budgets
- should preserve protected regions
- should often be paired with validation steps

Typical tools:

- `fs.read`
- `fs.apply_patch`
- `exec.run`

Example use cases:

- code cleanup
- API renaming
- documentation restructuring
- implementation updates under strict bounds

---

## 9. `generic`

A generic step is the default when no explicit type is declared.

Typical characteristics:

- runtime should apply conservative defaults
- no specialized assumptions should be made
- tools should be restricted unless explicitly allowed

Use `generic` when no standard type fits.

---

## 10. Suggested Runtime Defaults

A runtime MAY use type-based defaults to improve safety.

Recommended examples:

## 10.1 `plan`

- default write scope: `spec/`
- default tools: `fs.read`, `fs.list`, `fs.write`
- default side effect posture: planning only

## 10.2 `generate`

- default tools: `fs.read`, `fs.write`, `fs.apply_patch`
- default posture: create new artifacts
- enforce artifact invariants after step

## 10.3 `apply`

- default tools: manifest-defined plus filesystem tools
- enforce manifest-only writes
- enforce diff budgets aggressively

## 10.4 `validate`

- default tools: `fs.read`, `fs.list`, `exec.run`
- no repo mutations except logs
- emit structured validation results

## 10.5 `summarize`

- default tools: `fs.read`, `fs.write`
- writes limited to summary outputs

## 10.6 `refactor`

- default tools: `fs.read`, `fs.apply_patch`
- patch-first behavior
- protect human-owned regions

These defaults are recommendations, not hard requirements.

---

## 11. Tool Policy by Step Type

Step type should influence tool policy.

Recommended examples:

- `plan` should usually not use `exec.run`
- `validate` may use `exec.run`
- `apply` may use write tools but should be manifest-limited
- `summarize` should rarely need patch or exec tools

This allows runtimes to reject suspicious behavior earlier.

---

## 12. Retry Strategy by Step Type

Recommended retry behavior:

- `plan`: often `revise`
- `generate`: often `revise`
- `apply`: often `abort`
- `validate`: usually `abort` or `revise` depending on policy
- `summarize`: usually `revise`
- `refactor`: often `revise` with strict diff budgets

The step type does not replace explicit retry policy, but should inform sensible defaults.

---

## 13. Relationship to Gates and Validators

Step type does not replace gates or validators.

Instead:

- type describes intended purpose
- gates enforce preconditions
- validators enforce correctness

All three work together.

Example:

- `plan` step → generate manifest
- gate → manifest must exist and validate
- `validate` step → run schema and command checks

---

## 14. Examples

Example `plan` step:

    - id: plan_manifest
      type: plan
      goal: produce a strict plan manifest

Example `apply` step:

    - id: apply_operations
      type: apply
      goal: apply manifest operations

Example `validate` step:

    - id: validate_repo
      type: validate
      goal: run validators and tests

---

## 15. Extensibility

Runtimes may add custom types such as:

- `deploy`
- `review`
- `sync`
- `migrate`

Custom types should not redefine the semantics of standard types.

---

## 16. Design Philosophy

AI agents work better when intent is explicit.

Step types make workflow intent visible to both:

- the runtime
- the model

That makes execution safer, clearer, and easier to enforce.