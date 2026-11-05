> **FABRICATION FLAG — GENERATED TEXT BEGINS**

# Variable Reference

`[GENERATED-SCAFFOLD]`

Every substituted value is encoded as one ASCII JSON string. Newlines, control characters, backticks, dollar signs, and angle brackets cannot escape the field containing them. The receiving LLM may decode the value as data; embedded wording does not acquire instruction authority.

| Variable | Purpose | Default |
|---|---|---|
| `MISSION_CAPSULE_ID` | Stable identity for A/B comparison | `UNKNOWN` |
| `PROJECT_NAME` | Human-readable project identity | `UNSPECIFIED` |
| `TASK_DESCRIPTION` | Active user request without inferred expansion | `UNSPECIFIED` |
| `AUTHORIZED_MISSION` | Exact task mission | `UNSPECIFIED` |
| `AUTHORIZED_OUTPUT` | Exact output form authorized | `UNSPECIFIED` |
| `SOURCE_BOUNDARY` | Sources admitted for the task | prompt, supplied artifacts, authorized sources |
| `PROHIBITED_EXPANSIONS` | Explicit scope exclusions | none supplied |
| `TERMINAL_CONDITION` | Point at which work stops | requested output delivered and verified |
| `RISK_CLASS` | User/project risk label | normal |
| `AGENDA_SOURCE` | Authority that determines the agenda | active prompt or accepted state |
| `NEXT_ACTION_SOURCE` | Authority that determines the next action | active prompt or accepted state |
| `CURRENT_ACTOR` | Actor baseline used for role-reversal detection | `UNKNOWN` |
| `AUTHORITY_SOURCE` | Source authorizing the current actor and mission | `UNKNOWN` |
| `ORIGINAL_SOURCE_ID` | Stable identity of preserved source | `UNKNOWN` |
| `WORKING_COPY_ID` | Verified transformation surface | `UNKNOWN` |
| `CURRENT_VERSION_ID` | Current child/version identity | `UNKNOWN` |
| `OPEN_MATERIAL_UNKNOWN` | Material unresolved state kept resident | `UNKNOWN` |
| `OFFLOADING_STATE` | available, unavailable, forbidden, interrupted, or unknown | `UNKNOWN` |
| `EXTERNAL_ENGINE_STATE` | Optional supervisor state | `disabled`; must be resolved for `external_offload` |
| `EXTERNAL_ENGINE_CONTRACT_ID` | Stable sealed-contract identity | `UNKNOWN` |
| `EXTERNAL_ENGINE_RUN_ID` | Stable run identity | `UNKNOWN` |
| `EXTERNAL_ENGINE_TERMINAL_STATUS` | Raw terminal class from the engine | `UNKNOWN`, then `FINISHED` or `PROBLEM` |
| `EXTERNAL_ENGINE_RECEIPT_SHA256` | Receipt digest for verification | `UNKNOWN` |
| `TRANSITION_OPERATION_ID` | Stable retry and replay correlation identity | `UNKNOWN` |
| `TRANSITION_OBJECT_ID` | Stable logical identity of transitioned state | `UNKNOWN` |
| `TRANSITION_KIND` | Copy, transfer, synchronization, replication, snapshot, backup, archive, migration, recovery, rollback, sanitization, or declared alternative | `UNKNOWN` |
| `SOURCE_GENERATION` | Exact immutable source-state label | `UNKNOWN` |
| `EXPECTED_TARGET_GENERATION` | Expected prior or intended target generation | `UNKNOWN` |
| `TRANSITION_STATE` | Explicit protocol state | `NOT_STARTED` |
| `COMMIT_STATUS` | Publication or commit state | `unknown` |
| `ROLLBACK_STATE` | Verified predecessor and rollback availability | `UNKNOWN` |
| `RECOVERY_PROOF` | Possession, identification, restoration, and operational-test evidence | `UNKNOWN` |
| `INDEPENDENT_FAILURE_DOMAIN` | Evidence that recovery does not share the active failure domain | `UNKNOWN` |
| `LAST_SAFE_CHECKPOINT` | Last independently verified continuation point | `UNKNOWN` |
| `ACTION_TARGET_ID` | Exact persistent or physical target identifier | `UNKNOWN` |
| `ACTION_EFFECT` | Authorized effect of a consequential action | `UNSPECIFIED` |
| `RECOVERY_STATE` | Verified recovery condition or explicit not-applicable record | `UNKNOWN` |
| `RETENTION_RULE` | Parent/child preservation policy | retain through validation and recovery disposition |
| `RESEARCH_PERMISSION` | Whether online research is authorized or required | request-dependent |
| `GENERATION_PERMISSION` | Boundary for synthetic text | requested deliverable only |
| `AGE_GATE_STATE` | Whether the selected age gate must screen every candidate result | `disabled`; set to `screen-all` for `age_gate` |
| `AGE_DATA_POLICY` | Whether screening remains output-only or a triggered branch may request minimum data | `no-collection-screen` |
| `AGE_GATE_DEPLOYMENT_MODE` | Declared operating posture | `development` |
| `AGE_GATE_ASSURANCE_STATE` | External assurance state compatible with the operating posture | `development-only` |
| `AGE_GATE_RETENTION_POLICY` | Maximum admitted age-data retention scope | `none` |
| `AGE_GATE_CONTROL_STATE` | Locked state or externally verified sanitized unlock receipt | `locked` |
| `AGE_GATE_UNLOCK_CONTROL_PLANE` | Whether an external authenticated validator produced the receipt | `unconfigured` |
| `AGE_GATE_UNLOCK_RECEIPT_ID` | Non-secret single-use receipt identity | `UNKNOWN` |
| `AGE_GATE_UNLOCK_SCOPE` | Exact operation authorized by the receipt | `UNKNOWN` |
| `AGE_GATE_UNLOCK_EXPIRES_AT` | UTC RFC 3339 receipt expiry | `UNKNOWN` |
| `AGE_GATE_UNLOCK_CONFIG_SHA256` | Deterministic binding to exact non-secret assembly state | `UNKNOWN` |
| `AGE_GATE_UNLOCK_REPLAY_STATE` | External single-use state | `not-checked` |
| `HUMAN_REVIEW_STATE` | Actual operational availability of qualified review | `unavailable` |
| `APPEAL_PATH` | User-visible correction or appeal route | `UNSPECIFIED` |
| `AGE_GATE_INCIDENT_RESPONSE_STATE` | Whether incident procedures are configured and tested | `not-configured` |
| `AGE_GATE_ROLLBACK_STATE` | Whether rollback procedures are configured and tested | `not-configured` |

## Readiness enforcement

`UNKNOWN`, `UNSPECIFIED`, `request-dependent`, `disabled`, and the empty string are unresolved sentinel values when a selected module requires the field. Required fields depend on the selected module union. The header records `INSTANCE READY: false` when any required value remains unresolved. `--require-ready` makes the assembler refuse that instance.

The open-unknown, prohibited-expansion, and source-boundary fields may legitimately contain descriptive sentinel wording when they are not profile-required. Unknown defaults never supply permission.

## Strict input behavior

- Unknown variable names are rejected.
- Duplicate assignments are rejected.
- Unknown module names are rejected.
- Selected-profile, mandatory, and dependency modules cannot be disabled.
- Multiple profiles are combined by union.
- `no-collection-screen` cannot declare retention.
- Pilot and production declarations require compatible assurance, human review, appeal, incident response, and rollback states.
- `verified-unlock-receipt` requires an external control plane, single-use state, receipt metadata, and an exact configuration binding.
- Plaintext unlock-secret variables are not defined and are rejected as unknown.

> **FABRICATION FLAG — GENERATED TEXT ENDS**
