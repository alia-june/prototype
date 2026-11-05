> **FABRICATION FLAG — GENERATED TEXT BEGINS**

# Age-Gate Selection and Offload Heuristics

`[GENERATED-PROPOSAL]`

## Selection trigger

Select profile `age_gate` when the user requests age-appropriate mitigation or when the planned output contains difficult, sensitive, consequential, explicit, graphic, developmentally dependent, or materially age-bound content.

When selected, set `AGE_GATE_STATE=screen-all`. This means every candidate result receives the lightweight tri-axis screen. It does not mean every result receives a restrictive transformation.

Use `AGE_DATA_POLICY=no-collection-screen`, `AGE_GATE_RETENTION_POLICY=none`, `AGE_GATE_DEPLOYMENT_MODE=development`, `AGE_GATE_ASSURANCE_STATE=development-only`, and `AGE_GATE_CONTROL_STATE=locked` unless verified external records authorize a different posture. The default screen evaluates the candidate output and task; it does not ask for or infer a person's age axes.

## Full-gate escalation

Escalate from the lightweight screen to the full difficult-question gate only when a declared trigger in module 14 is present. Record the trigger. If none is present, use `STANDARD` and `NO MATERIAL AGE ADJUSTMENT` when the screen passes.

Before a triggered branch collects data, materially restricts an answer, or takes a consequential action, apply modules 15 and 16. The branch remains locked unless an externally validated encrypted authorization envelope yields a scoped, expiring, unconsumed receipt bound to the exact configuration. Unlock does not bypass privacy, human-review, appeal, impact-assessment, evidence, or deployment controls.

## Heuristic offload boundary

Mechanical checks may be offloaded when the contract preserves the three independent axes, the factual core, the source pointers, and the selected delivery mode. Do not offload:

- the authority to change mission or actor;
- the authority to establish a legal age or diagnosis;
- the final decision to omit a supported central fact;
- human review required by a higher-priority rule.

An offloaded classifier returns candidate features and evidence pointers. Its score is not authority and cannot replace ordinary evidence egress.

Cryptographic validation is also an external control-plane function. Do not send plaintext secrets, keys, encrypted envelopes, decrypted claims, or bearer tokens to an LLM or store them in the prompt package.

> **FABRICATION FLAG — GENERATED TEXT ENDS**
