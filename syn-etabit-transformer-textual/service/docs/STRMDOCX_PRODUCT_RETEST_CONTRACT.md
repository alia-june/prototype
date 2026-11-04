# Strmdocx corrected-harness product-retest contract

Date: 2026-10-31. Approved scope: AUTH-19C-A. Product source is read-only.

This retest follows the completed AUTH-19B harness repair. Its governing basis
is `HARNESS_REPAIR_CONTRACT.md`, `HARNESS_REPAIR_FINDINGS.md`,
`HARNESS_REPAIR_VALIDATION.md`, the AUTH-19B delivery manifest, service harness
`docstream.harness/1.3` and the current native hardening/fuzzy-error/torture
harness. The objective is to determine whether the corrected harnesses establish
any current Strmdocx product defect. It does not assume that a repair is needed.

## Service workload

The service run uses seed 20261029 and retains:

- the closed rigid regression selection;
- 500 deterministic generated fuzzy cases;
- five bounded torture scenarios;
- four clients, 1,800 loop requests, 2,000 torture service calls, 20 actor
  crash cycles and no more than 25 render calls;
- a 1,200-second and 512-MiB evidence limit.

Every case input is retained before execution. A failure remains a failure and
an incomplete result remains incomplete. Product hashes are recorded before and
after. Each mode must retain explicit owned-worker cleanup evidence under the
repaired `/1.3` schema.

## Native workload

The native run uses seed 20261029 and retains:

- 100 hardening cases;
- 1,000 deterministic fuzzy-error cases, including 800 exact expected
  rejections and 200 valid controls;
- eight bounded torture scenarios;
- no more than 2,000 submitted transformation attempts;
- a 900-second and 512-MiB evidence limit.

Expected rejection passes only when the declared exception type and code match
and the complete state fingerprint is unchanged. Inputs and minimized replay
data remain non-executable closed data. Source identities are recorded before
and after the run.

## Evidence and decision rule

The exact run roots are:

- `.docstream/harness-runs/auth19c-20261031-before/`
- `.docstream/native-harness-runs/auth19c-20261031-before/`

Completion requires independent readback of summaries, input counts and hashes,
source preservation, limits, cleanup evidence and final matching-worker
inventory. Product and harness findings must remain separately classified.

If both runs pass, AUTH-19C-A records that no product repair is currently
justified by these workloads. If either run exposes a product failure, that
failure and its replay remain retained, but no source correction begins until a
separate bounded AUTH-19C-B proposal is explicitly approved.

## Exclusions

This scope does not authorize product-source edits, baseline changes, expectation
relaxation, dependency installation, database migration, format-policy changes,
WordNet or Etabit work, GPU work, release, registration or agentic-control
integration.
