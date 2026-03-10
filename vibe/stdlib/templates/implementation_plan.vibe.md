---
vibe: "2.0"
meta:
  name: "[feature_name]_implementation"
  description: "[Detailed implementation plan for a specific change]"
  author: "[claude | human | agent-id]"
  tags:
    - implementation
  status: draft
---

## Context

### Problem

[Describe what needs to be implemented and why]

### Constraints

[List implementation constraints: timeline, backward compatibility, etc.]

### Assumptions

[List assumptions: available dependencies, environment, etc.]

### Scope

[Define what files and systems are affected]

## Artifacts

| Path | Kind | Description | Status | Depends On | Acceptance Criteria |
|------|------|-------------|--------|------------|---------------------|
| [path/to/file1] | [language] | [What this file does] | planned | | [Criterion 1]; [Criterion 2] |
| [path/to/file2] | [language] | [What this file does] | planned | [path/to/file1] | [Criterion 1] |

## Sections

### Scope Analysis
<!-- id: scope_analysis, type: analysis -->

[Analyze the scope of changes. What files are touched?
What existing behavior is affected?]

### Implementation Approach
<!-- id: approach, type: design -->

[Describe how the implementation will proceed.
What patterns will be used? What is the strategy?]

### Artifact Specifications
<!-- id: artifact_spec, type: specification -->

[Detail the specific changes for each artifact.
Include interface changes, data format changes, etc.]

### Implementation Tasks
<!-- id: task_checklist, type: checklist -->

- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

### Verification Steps
<!-- id: verification, type: checklist -->

- [ ] [Verification step 1]
- [ ] [Verification step 2]

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_artifacts_complete | checklist | All planned artifacts are implemented | Every artifact in the Artifacts table has status: complete and meets its acceptance criteria |
| q_no_regressions | test | No existing functionality is broken | All existing tests pass. No unintended behavior changes |
