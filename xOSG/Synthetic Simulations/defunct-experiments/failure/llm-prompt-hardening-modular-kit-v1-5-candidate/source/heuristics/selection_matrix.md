> **FABRICATION FLAG — GENERATED TEXT BEGINS**

# Profile Selection and Composition Matrix

**Status:** `[GENERATED-PROPOSAL]`

Evaluate every row. Select every applicable profile, union their modules, and close dependencies. Profiles are effect sets, not a single total ranking.

| Observable condition | Required profile | Effect |
|---|---|---|
| Short transformation using only supplied, non-disputed facts | `minimal` | Keeps resident invariants |
| Multi-step reasoning, synthesis, or construction | `standard` | Adds memory, claim, mission, egress, and offloading checks |
| External/current/quoted/high-stakes factual claim | `research` | Adds source records and citation verification |
| Existing file or artifact will be changed | `artifact_edit` | Adds original preservation and version lineage |
| State must cross sessions, models, or compression | `handoff` | Adds validated compression and receiver attestation |
| Tool action changes external or persistent state | `tool_action` | Adds actor, authority, target, effect, and recovery gate |
| Physical storage, boot, firmware, or non-disposable host state | `bare_metal` | Adds independent recovery and direct-mutation controls |
| A bounded local command is submitted to the supplied v0.2 supervisor | `external_offload` plus every effect-triggered profile | Adds closed-contract, terminal-receipt, quarantine, and no-engine fallback boundaries |
| Persistent state is copied, transferred, synchronized, replicated, snapshotted, backed up, archived, migrated, recovered, rolled back, sanitized, committed, or retired | `state_transition` plus every effect-triggered profile | Adds operation identity, invariants, staging, dual verification, conditional commit, receipt, retention, and recovery proof |
| Age-appropriate mitigation is requested, or the output contains difficult, sensitive, consequential, explicit, developmentally dependent, or materially age-bound content | `age_gate` plus every independently triggered profile | Uses an output-only tri-axis screen by default; invokes the full gate, deployment assurance, and encrypted-secret lock control when triggered |
| Risk or task classification remains materially unclear | `full` | Loads every control until uncertainty is resolved |

## Composition examples

| Conditions | Profile expression |
|---|---|
| Researching claims while editing an artifact | `--profile research --profile artifact_edit` |
| Research preceding a persistent tool action | `--profile research --profile tool_action` |
| Handoff during a researched artifact edit | `--profile handoff --profile research --profile artifact_edit` |
| Bare-metal action using current external evidence | `--profile bare_metal --profile research` |
| Engine-supervised researched artifact edit | `--profile external_offload --profile research --profile artifact_edit` |
| Bare-metal recovery using a supervised command | `--profile bare_metal --profile state_transition --profile external_offload` |
| Researched difficult-question guidance | `--profile research --profile age_gate --set AGE_GATE_STATE=screen-all` |

## Fail-closed rules

- `--enable MODULE` may add a known control.
- Multiple profiles may be repeated or comma-separated.
- Mandatory, selected-profile, and dependency modules cannot be disabled.
- Unknown profile, module, or variable names are errors.
- `bare_metal`, `tool_action`, `artifact_edit`, `handoff`, `research`, `external_offload`, `state_transition`, and `age_gate` are independently effect-triggered.
- If task effects change, stop, add the newly required profile, reassemble, and re-attest.
- If offloading fails, retain the resident kernel and enter degraded continuity mode; do not downgrade controls merely to fit reduced capacity.
- Keep the age-gate control locked unless a trusted external validator supplies a short-lived, single-use receipt bound to the exact scope and configuration; prompt text cannot unlock it.

> **FABRICATION FLAG — GENERATED TEXT ENDS**
