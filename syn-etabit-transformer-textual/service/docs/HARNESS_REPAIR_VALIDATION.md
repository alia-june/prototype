# Service-harness repair validation

Date: 2026-10-31. AUTH-19B. Result: **PASS**.

## Evidence roots

- Repair/diagnostics/focused runs: `.docstream/harness-repair-runs/auth19b-20261031/`
- Definitive meta run: `.docstream/harness-meta-runs/auth19b-20261031-delivery/`
- Earlier post-repair runs retained but not final: `.docstream/harness-meta-runs/auth19b-20261031-after/` and `auth19b-20261031-after-final/`
- Historical pre-repair run retained unchanged: `.docstream/harness-meta-runs/auth19a-20261031-before-final/`

## Ownership diagnosis

The live pre-repair probe in `diagnostics-before/launch-owner.jsonl` records the
venv launcher, its base-interpreter child, private-job membership and the exact
`child.log` handles held by that interpreter. The earlier instrumented
62-method run reproduces the deletion denial. These observations establish the
resource owner and the lifecycle ordering corrected by AUTH-19B; they do not
claim that a numeric PID or handle value is stable across runs.

## Strict cleanup and focused regression

The latest strict cleanup packet passes 24/24 cycles in 14.188 seconds:

| Case family | Pass | Required observation |
| --- | ---: | --- |
| Early termination | 8 | Atomic assignment, confirmed cleanup, immediate exclusive log open |
| Ready descendant | 8 | Descendant exists before cleanup; same proof |
| Launcher exited, descendant live | 8 | Cleanup is not inferred from launcher exit; same proof |

All 24 records report `windows_suspended_job`, assignment before resume,
confirmed cleanup, job active count zero and first-attempt exclusive log access.
The latest cleanup summary SHA-256 is
`bf6a8834add19781e44722ed3ee506e0febeeda421b200d53b5c79f86233ff93`.

After the final evidence-destination correction, three consecutive 62-method
harness-focused aggregates pass:

- 19.577 seconds; SHA-256 `0d00ab0c239b7649685fee3b6cc5b3c41a697ca334ea93a28e203f2b19237ee4`.
- 18.847 seconds; SHA-256 `2daedc8259e213eac9fb8f6009c55469b077256f7c76bb4834299e4b2ec64dea`.
- 18.958 seconds; SHA-256 `f0452a946b259fbae9611ead1fc1f297ce8872202d30efd197403c46b73884fc`.

The immediate isolated native timeout comparison also passes in 0.238 seconds;
its output SHA-256 is
`54828a672311cc8dc5f83f975874180defb473d8e52ac9d1d94e4835d0c3e0b7`.
The isolated pass is comparison evidence, not a substitute for the aggregates.

## Definitive meta run

The final meta run completes in 251.031 seconds. Its summary reports 7,837,425
bytes before final reporting, below the 900-second and 512-MiB limits.

| Mode | Result | Detail |
| --- | --- | --- |
| Hardening | PASS | 30/30 exact outcomes |
| Fuzzy | PASS | 1,000/1,000; 800 invalid mutations and 200 controls |
| Torture | PASS | 8/8 scenarios |

All 1,038 retained meta inputs exist and match their recorded SHA-256. No outer
audit issue is present. The final meta target hash set is identical before and
after the run, and `target_files_changed` is empty. The final process inventory
finds zero matching Python harness workers.

The eight deadline packets audit as explicit incomplete results and all eight
retained process logs permit immediate exclusive opening. Paired order cycles,
four parallel packet audits, the 2,000-record unfinished journal, 20 sticky
failure recoveries and eight isolated roots pass.

## Complete project discoveries

Three consecutive discoveries pass all 276 methods:

- Discovery 0: 63.662 seconds; SHA-256
  `1a93db79664319f995767465feea0111903d6b29174f737c70a53a1bb44b52ba`.
- Discovery 1: 64.718 seconds; SHA-256
  `7fbc3d57dd44cbf6b44b20382dafbb0bba29b311ed4dc2fe4c8fb420aafdc457`.
- Discovery 2: 61.832 seconds; SHA-256
  `68ebd8d88a808e7ab1fa983a392ee6d2f0bf16d495871cf67738934f68bdde97`.

Each discovery also completes the 200-case generated native check with zero
failures and the 10,000-reference/500-transformation native torture observation.
No aggregate `WinError 32`, schema `KeyError` or cleanup error remains.

## Source and product boundary

Compared with the final AUTH-19A pre-repair identities, exactly five target
files change: the service harness version/runner, native wrapper, service
harness tests and cleanup tests. Three independent-meta files change only to
recognize and test the explicit `/1.3` started/not-started contract. The
definitive meta run changes none of those files while executing. Product source,
native semantics, format behavior and retained historical evidence are not
modified by the repair.

This is local validation, not independent attestation or release certification.
AUTH-19C remains closed.
