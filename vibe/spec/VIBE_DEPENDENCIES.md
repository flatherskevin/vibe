# VIBE Artifact Dependencies (v1.0)

Artifacts may declare dependencies on other artifacts.

This helps enforce deterministic generation order.

---

## depends_on Field

Example:

depends_on:
- spec/10_architecture.md
- spec/20_artifacts.json

---

## Runtime Behavior

If dependencies are declared:

- prerequisite artifacts must exist
- invariants should be satisfied

If dependencies are missing:

runtime should treat this as planning failure.

---

## Recommended Conventions

Implementation files depend on:

spec/20_artifacts.json  
spec/30_workflow.json

Tests depend on:

implementation files  
architecture documents

---

## Cycles

Dependency cycles must be rejected as invalid programs.