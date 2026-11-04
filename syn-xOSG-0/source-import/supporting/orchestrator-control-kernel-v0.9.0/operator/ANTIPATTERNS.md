# Anti-Patterns

## AP-001 — Narrative completion
Saying an action occurred because the conversation proceeded as if it had occurred.

## AP-002 — Schema-after-access
Dereferencing nested values before validating their container and type.

## AP-003 — Silent reset on corruption
Replacing malformed persistent state with defaults and continuing as though nothing happened.

## AP-004 — Green-suite absolutism
Treating 100% passing tests as proof of correctness, completeness, security, or architectural quality.

## AP-005 — Compatibility worship
Retaining a weak primitive to avoid migration work even when the rebuild is explicitly ground-zero.

## AP-006 — Prompt-as-runtime
Treating textual instructions as though they create persistence, external actions, locks, transactions, or privileges.

## AP-007 — Representation drift
Maintaining multiple prose/JSON/prompt descriptions that independently evolve and contradict one another.

## AP-008 — Patch stacking
Responding to every defect by adding another wrapper, flag, or layer instead of questioning the primitive that enabled the defect.

## AP-009 — Recovery exceptionalism
Trusting backup, journal, cache, or recovery data more than ordinary input without validation.

## AP-010 — Premature abstraction
Generalizing from one incident before there is enough evidence to identify the real recurring structure.

## AP-011 — Self-confirming analysis
Choosing tests, interpretations, and evidence that validate the current design while not constructing meaningful falsification attempts.

## AP-012 — Hidden authority transfer
Allowing a lower-level interface, helper, compatibility layer, or user phrasing to silently expand privileges or override higher-level constraints.

## AP-013 — Next-step autopilot
Treating a plausible or obvious next phase as authorized simply because the preceding phase completed successfully.

## AP-014 — Readiness-equals-authorization
Treating green tests, validation, or an assistant recommendation as permission to deploy or promote to production.

## AP-015 — Memory flattening
Combining transient context, durable decisions, and system constraints into one undifferentiated store, causing stale data or lower-authority statements to masquerade as higher-authority rules.

## AP-016 — Transcript-as-configuration
Treating prior prompt/response text as active configuration without an explicit promotion rule.

## AP-015 — Source-equals-authority
Treating prompt text, attachments, or web content as executable authority merely because they are present.

## AP-016 — Attestation inflation
Using a checksum, validation pass, or provenance record as if it established substantive truth beyond what was actually checked.

## AP-017 — Gate deadlock
Defining a lock so broadly that the authorized principal cannot inspect, clear, or revoke the lock through a defined control plane.

## AP-015 — Hypothetical privilege leakage

Treating an assumed, simulated, imagined, or discussed privilege as though it were actually granted.

## AP-016 — Proof-to-permission collapse

Concluding that because an action is logically justified, technically safe, or test-passing, it is therefore authorized for production.

## AP-017 — Orchestrator sovereignty

Allowing the rule coordinator to redefine its own authority boundary, clear gates, or grant capabilities merely because it controls sequencing.

## AP-015 — Emergency superuser escape hatch
Any hidden or explicit path that lets a later rule bypass non-escalation by claiming emergency/admin/root status.

## AP-016 — Authentication-as-authorization escalation
Treating a passed challenge-response test as permission to create rights not already available.


## AP-015 — Flight-to-foundation mutation
Allowing a live runtime rule to rewrite its own security floor collapses the distinction between temporary orchestration and foundational authority. Zero-Flight mutations must be layer-local.

## AP-016 — Orchestrator-to-Operator role collapse
Treating the assistant-side orchestrator as the principal that owns project agency, design authority, or research authority merely because it executes the workflow.
