# Deterministic Self-Task Catalog — STC-001

`self-task` means a bounded task composed by MOS-001 and executed synchronously by admitted deterministic machinery. It does **not** mean an autonomous agent, background job, or independent authority.

| ID | Task | Default touch | Output |
|---|---|---|---|
| ST-001 | inventory package | DT1 | canonical path/size inventory |
| ST-002 | hash package files | DT2 | SHA-256 records |
| ST-003 | compute Merkle root | DT2 | root digest |
| ST-004 | validate required structure | DT1/DT3 | invariant results |
| ST-005 | run regression suites | DT3 | pass/fail/count summaries |
| ST-006 | validate tool-policy schema | DT3 | pass/fail |
| ST-007 | validate gate state | DT4 bounded control probe | gate-state result |
| ST-008 | compose scoped attestation | evidence-only | attestation JSON/MD |
| ST-009 | package artifact | metadata/bytes | ZIP |
| ST-010 | verify archive | DT2/DT3 | archive hash/integrity |
| ST-011 | relock production gate | control-plane | locked gate record |

Task composition must preserve Operator objective and may only choose mechanical details inside that objective.

## Seal ordering

The final production-cycle order is intentionally:

```text
candidate evidence complete
 -> ST-011 verify/relock production gate
 -> ST-009 seal final archive
 -> ST-010 verify final archive
```

This ensures the sealed archive records the requested post-production gate lock rather than an earlier transient unlocked state.
