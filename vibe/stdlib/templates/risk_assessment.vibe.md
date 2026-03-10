---
vibe: "2.0"
meta:
  name: "[subject]_risk_assessment"
  description: "[Comprehensive risk analysis for a project, system, or decision]"
  author: "[claude | human | agent-id]"
  tags:
    - risk
  status: draft
---

## Context

### Problem

[Describe the context requiring risk assessment]

### Constraints

[List constraints on risk tolerance or mitigation options]

### Assumptions

[List assumptions about the operating environment]

### Scope

[Define what is being assessed for risk]

## Sections

### Risk Context
<!-- id: context_analysis, type: analysis -->

[Provide background on the system, project, or decision being
assessed. What is the current state? What changes are proposed?]

### Identified Risks
<!-- id: identified_risks, type: risk -->

[List and describe each identified risk. For each risk include:
- Description
- Likelihood (high/medium/low)
- Impact (high/medium/low)
- Category (technical/operational/security/business)]

### Mitigation Strategies
<!-- id: mitigations, type: risk -->

[For each identified risk, describe mitigation strategies.
Include preventive measures and contingency plans.]

### Monitoring Plan
<!-- id: monitoring, type: checklist -->

- [ ] [Monitoring item 1]
- [ ] [Monitoring item 2]

### Risk Acceptance
<!-- id: risk_acceptance, type: decision -->

[Document which risks are accepted and why.
What is the residual risk after mitigations?]

## Quality

| ID | Type | Description | Criteria |
|----|------|-------------|----------|
| q_risks_comprehensive | review | Risk identification is thorough | Risks cover technical, operational, security, and business categories. No obvious risk categories are missing |
| q_mitigations_actionable | review | Mitigations are concrete and actionable | Each mitigation describes specific actions, not just aspirations. Responsible parties or triggers are identified |
