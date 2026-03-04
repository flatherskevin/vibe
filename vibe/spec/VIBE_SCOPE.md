# VIBE Repository Scope and Path Policy (v1.0)

This document defines how `.vibe` programs restrict where agents may read and write files.

---

## 1) Repository Write Scope

The meta field may define:

repo_write_scope

Structure:

allowed:
- directory prefixes allowed for writes

forbidden:
- directory prefixes forbidden for writes

---

## 2) Path Safety Rules

Runtimes MUST enforce:

- no absolute paths
- no ".." path traversal
- writes must match allowed prefixes
- writes must not match forbidden prefixes

---

## 3) Default Scope

If repo_write_scope is not defined, runtimes SHOULD default to:

allowed:
- spec/
- docs/
- src/
- tests/
- vibe/

forbidden:
- .git/
- node_modules/
- dist/
- build/

---

## 4) Ownership Policies

Artifacts may define ownership:

generated
managed
protected

generated:
runtime may overwrite

managed:
runtime should patch and preserve protected regions

protected:
runtime must refuse modifications

---

## 5) Write Policies

write_policy options:

patch_preferred
full_overwrite_allowed

patch_preferred is recommended.

---

## 6) Protected Regions

Files may contain protected regions owned by humans.

Markers:

BEGIN HUMAN
END HUMAN

Content between these markers should not be modified.

---

## 7) Directory Creation and Deletion

Operations such as mkdir or delete must follow the same scope rules.

Deletion should be disabled by default unless explicitly allowed.

---

## 8) Exec Policy

Because exec.run is powerful, runtimes SHOULD support an allowlist.

Example:

meta.exec_allowlist

Allowed commands might include:

npm test
npm run lint
git status