# VIBE Repository Scope and Path Policy (v1.0)

This document defines repository scope rules for VIBE runtimes.

These rules determine where a runtime may read, write, patch, delete, or execute commands.

The goal is to make AI execution safe, bounded, and auditable.

---

## 1. Purpose

Repository scope rules exist to prevent AI systems from:

- modifying files outside intended boundaries
- traversing unsafe paths
- changing protected content
- executing dangerous commands
- bypassing manifest or runtime controls

Scope policy is one of the main enforcement layers in VIBE.

---

## 2. Meta Scope Configuration

A VIBE program may define repository scope in `meta.repo_write_scope`.

Example:

    meta:
      repo_write_scope:
        allowed:
          - src/
          - spec/
          - docs/
        forbidden:
          - .git/
          - node_modules/
          - dist/
          - build/

If present, runtimes SHOULD enforce this configuration during apply.

---

## 3. Allowed and Forbidden Prefixes

## 3.1 Allowed prefixes

`allowed` is a list of repository-relative path prefixes that may be written.

Examples:

- `src/`
- `spec/`
- `docs/`

If an allowed list is present, writes SHOULD match at least one allowed prefix.

---

## 3.2 Forbidden prefixes

`forbidden` is a list of repository-relative path prefixes that must never be written.

Examples:

- `.git/`
- `node_modules/`
- `dist/`

If a path matches a forbidden prefix, the runtime must reject the operation.

Forbidden rules take precedence over allowed rules.

---

## 4. Path Safety Rules

Runtimes MUST enforce the following minimum path protections:

- no absolute paths
- no `..` path traversal
- no writes outside repository root
- no writes that violate forbidden prefixes
- no writes to protected artifacts unless explicitly permitted

Examples of forbidden paths:

- `/etc/passwd`
- `../../outside.txt`
- `C:\Windows\System32`
- `.git/config`

If path validation fails, the runtime should reject the operation with:

    VIBE_OPERATION_NOT_PERMITTED

---

## 5. Read Scope

VIBE v1 primarily constrains writes, but runtimes SHOULD also apply safe read behavior.

Recommended read behavior:

- allow reads within repository root
- reject absolute paths
- reject traversal outside repo root
- optionally restrict reads for high-security environments

Reads are less dangerous than writes, but still affect privacy and policy compliance.

---

## 6. Ownership Semantics

Artifacts may define `ownership`.

Supported values:

- `generated`
- `managed`
- `protected`

---

## 6.1 `generated`

The runtime may create or overwrite the file.

Typical use:

- generated code
- planning documents
- machine-owned output files

---

## 6.2 `managed`

The runtime may modify the file, but should prefer patching and preserve protected regions where applicable.

Typical use:

- partially human-edited files
- configuration files
- maintained docs

---

## 6.3 `protected`

The runtime must not modify the file unless the runtime explicitly supports and allows an override mechanism.

Typical use:

- security-sensitive files
- manually curated documents
- human-owned config

---

## 7. Write Policy

Artifacts or operations may define `write_policy`.

Supported values:

- `patch_preferred`
- `full_overwrite_allowed`

---

## 7.1 `patch_preferred`

The runtime should prefer targeted edits for existing files.

Recommended for:

- managed files
- user-maintained source files
- documentation with human ownership

---

## 7.2 `full_overwrite_allowed`

The runtime may rewrite the entire file.

Recommended for:

- generated files
- build outputs
- planning docs fully owned by the runtime

Even when full overwrite is allowed, scope restrictions still apply.

---

## 8. Protected Regions

Managed files may include protected regions that humans own.

Default markers:

- `BEGIN HUMAN`
- `END HUMAN`

Example:

    # BEGIN HUMAN
    This section is maintained manually.
    # END HUMAN

A compliant runtime SHOULD avoid modifying content inside these markers for managed files.

Protected region enforcement is strongly recommended but may be implementation-dependent in v1.

---

## 9. Directory Creation and Deletion

Manifest operations may include:

- `mkdir`
- `delete`

These operations are subject to the same scope rules as writes.

Recommended behavior:

- allow `mkdir` only in allowed scope
- deny delete by default unless explicitly permitted
- never allow delete in forbidden prefixes

Deletion is inherently higher risk than write and should be treated conservatively.

---

## 10. Diff Budgets

Scope policy may be complemented by diff budgets.

Examples:

- max lines added
- max lines removed
- max files changed

These are not path constraints, but they do constrain execution scope operationally.

Diff budgets should be enforced at:

- manifest validation
- step gates
- apply time

---

## 11. Plan Manifest Relationship

Repository scope rules apply to all operations in:

    spec/plan_manifest.json

A valid manifest does not override scope policy.

If the manifest requests an operation outside allowed scope, the runtime must reject it even if the manifest itself is structurally valid.

This ensures that:

- schemas validate structure
- scope policy validates authority

Both are necessary.

---

## 12. Exec Policy

`exec.run` is high-risk and should be treated as privileged.

A runtime MAY support:

    meta:
      exec_allowlist:
        - npm test
        - npm run lint
        - git status

Recommended behavior:

- allow only explicitly approved commands when allowlist is present
- deny destructive commands by default
- log all command executions

Examples of commands that should usually be blocked unless explicitly allowed:

- `rm -rf`
- `git push`
- `curl | sh`
- package manager install commands that mutate the environment unexpectedly

---

## 13. Default Scope Recommendations

If `repo_write_scope` is omitted, runtimes SHOULD apply conservative defaults.

Recommended defaults:

Allowed:

- `spec/`
- `docs/`
- `src/`
- `test/`
- `tests/`
- `vibe/`

Forbidden:

- `.git/`
- `node_modules/`
- `dist/`
- `build/`
- `.next/`
- `.cache/`

These defaults are recommendations, not hard requirements.

---

## 14. Runtime Enforcement Order

Recommended enforcement order for a manifest operation:

1. validate path syntax
2. validate repository root containment
3. check forbidden prefixes
4. check allowed prefixes
5. check ownership policy
6. check protected regions
7. check diff budget if applicable
8. perform operation

This order reduces risk and improves explainability.

---

## 15. Error Mapping

Recommended error mappings:

- invalid path syntax → `VIBE_OPERATION_NOT_PERMITTED`
- forbidden prefix → `VIBE_OPERATION_NOT_PERMITTED`
- protected artifact write → `VIBE_OPERATION_NOT_PERMITTED`
- protected region mutation → `VIBE_OPERATION_NOT_PERMITTED`
- delete failure → `VIBE_OPERATION_FAILED`

---

## 16. Design Philosophy

AI agents should not decide repository authority on their own.

In VIBE:

- the program defines intended work
- the manifest defines planned work
- the runtime scope policy defines permitted work

Scope policy is the final line of defense between AI-generated intent and real repository state.