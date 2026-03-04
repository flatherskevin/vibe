# VIBE Step Types (v1.0)

Step types are optional but recommended.

They help runtimes apply stronger guarantees.

---

## Standard Step Types

plan  
Produces planning artifacts.

generate  
Creates new artifacts.

apply  
Applies operations from plan manifest.

validate  
Runs validators and gates.

summarize  
Produces compaction summaries.

refactor  
Performs modifications to existing code.

generic  
Default step type.

---

## Runtime Defaults

plan:
tools should be limited to read and spec writes.

apply:
tools must be manifest limited.

validate:
tools allowed include exec.run and file reads.

summarize:
should only write run logs.

---

## Recommendation

Example step tags:

plan_manifest:
type: plan

apply_operations:
type: apply

validate_and_test:
type: validate