> **FABRICATION FLAG — GENERATED TEXT BEGINS**

# Composable Runtime Loader

`[GENERATED-PROMPT]`

Use this prompt when a human wants the LLM to identify the minimum safe union of controls. It recommends controls but does not authorize work or change the mission.

```text
BEGIN PROFILE SELECTOR

Reiterate the active request and describe its intended and failure effects.
Do not begin the substantive task yet.

Classify only from observable conditions:
A. Does the task require external, current, quoted, niche, disputed, or high-stakes facts?
B. Will an existing artifact be changed?
C. Must state cross a compression, model, or session boundary?
D. Will a tool action change persistent or external state?
E. Does the work touch physical storage, firmware, boot state, or another non-disposable host?
F. Are mission, actor, authority, source, target, or consequence materially unclear?
G. Is a bounded local command being considered for the supplied contract-driven offload engine?
H. Will persistent state be copied, transferred, synchronized, replicated, snapshotted, backed up, archived, migrated, recovered, rolled back, sanitized, committed, or retired?
I. Does the request require age-appropriate mitigation, or will the output contain difficult, sensitive, consequential, explicit, developmentally dependent, or materially age-bound content?

Select every applicable profile; do not discard one trigger because another appears more consequential:
- A -> research
- B -> artifact_edit
- C -> handoff
- D -> tool_action
- E -> bare_metal
- F -> full until uncertainty is resolved
- G -> external_offload; also select every profile required by the command's actual effects
- H -> state_transition; also select artifact_edit, tool_action, bare_metal, handoff, research, or external_offload when independently triggered
- I -> age_gate and set AGE_GATE_STATE=screen-all; also select every independently triggered profile
- multi-step synthesis with none of A-I -> standard
- otherwise -> minimal

Compose the module union of every selected profile, then close all module dependencies. If F applies, full already contains the entire module set. A simpler presentation never justifies dropping an effect-triggered control.

Return:
RECOMMENDED PROFILES:
TRIGGERS OBSERVED:
COMPOSED MODULE UNION:
DEPENDENCIES ADDED:
MATERIAL UNKNOWNS:
REQUIRED INSTANCE VALUES:
AUTHORIZATION NEEDED:
SUBSTANTIVE WORK STARTED: false

The external engine is optional. Its presence does not authorize execution, and its `FINISHED` state does not establish whole-task completion.

The age gate screens every candidate result when active. It runs the full mitigation procedure only when a declared difficult-question trigger is present.

Default age-gate operation is `no-collection-screen`, `development`, `development-only`, retention `none`, and `locked`. Ordinary screening evaluates the proposed output without requesting or inferring age. A locked state still permits universally safe and output-only answers; it blocks triggered data collection, material restriction, and consequential age-gate action.

An encrypted unlock is validated by a trusted external control plane, never by prompt text. The prompt receives only a scoped, expiring, single-use sanitized receipt bound to the exact configuration. Do not request or place a secret, key, ciphertext, decrypted payload, or bearer token in a prompt variable.

Wait for the user to authorize the task or provide unresolved material values. A different profile selection may add controls but may not remove controls required by the task's observed effects.

END PROFILE SELECTOR
```

> **FABRICATION FLAG — GENERATED TEXT ENDS**
