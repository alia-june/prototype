# Service-harness meta-verification validation

Date: 2026-10-31. AUTH-19A. Result: **meta implementation PASS; target harness FAIL**.

## Focused verifier checks

Nine `test_harness_meta` methods pass after the retained first-run corrections. They verify the reviewed contract, exact 800/200 fuzzy distribution, all 20 closed mutations, duplicate-key and size rejection, sticky failure/incomplete precedence, pre-journal zero-case interruption, outer input tamper detection, configuration rejection before writes and small hardening/fuzzy target preservation.

## Final retained run

Evidence: `.docstream/harness-meta-runs/auth19a-20261031-before-final/`.

| Mode | Result | Detail |
| --- | --- | --- |
| Hardening | PASS | 30/30 |
| Fuzzy | PASS | 1,000/1,000; 800 invalid and 200 controls |
| Torture | FAIL | Seven scenarios pass; three full discoveries contain two failures and one pass |

The final run completes in 243.484 seconds and retains 7,774,536 bytes, below the 900-second and 512-MiB ceilings. All 1,038 meta-input files match their recorded SHA-256 and case schema. The target hash set before and after is identical; `target_files_changed` is empty. Final process inventory finds zero matching Python or browser workers.

The eight target service deadlines all return the expected incomplete exit code, independently audit without evidence problems and permit immediate exclusive opening of all eight `process-output.txt` files. The three paired order runs pass. Four parallel controlled packet audits, a 2,000-event interrupted journal, 20 sticky-failure recoveries and eight isolated evidence roots pass.

Three full discovery outputs are retained with exact hashes:

- `discovery-0.txt`: SHA-256 `d55cec62e862b33a8b6a407997a899f5bf235e4a869e040a00ecd70349792a98`; 276 tests; one WinError 32 cleanup error.
- `discovery-1.txt`: SHA-256 `ee7e3febce58980117cbb8e9860226384bf934eba6f1d785a22bc5fd17f6930f`; 276 tests; the same cleanup error.
- `discovery-2.txt`: SHA-256 `80b25ce3d6d896af1d2d361a0f843b2375be454c5d6015f63aedac4f73dccd82`; 276 tests; PASS.

The failed aggregate outputs are not replaced by the passing third run. This validation establishes intermittent reproduction at two of three full discoveries, not universal failure or root cause.

## Harness-focused regression selection

The final 62-method selection combines nine service-meta methods, six service-cleanup methods, 19 service-harness methods, 17 native-harness methods and 11 native-meta methods. Two separate aggregate executions each produce 61 passes and the same WinError 32 cleanup error in `test_real_supervisor_timeout_stops_its_owned_child`. An immediate isolated rerun passes in 0.198 seconds. Retained logs are `verification/harness-focused-62.txt` and `verification/native-timeout-isolated.txt`. The isolated pass does not supersede the aggregate failure.

## First retained run

The earlier `.docstream/harness-meta-runs/auth19a-20261031-before/` run is a retained FAIL: hardening 30 pass, fuzzy 1,000 pass, torture five pass/three fail. Two torture failures are meta subprocess-owner errors and its slow scan is a meta anti-lesson. Its deadline packets also exposed the pre-start incomplete schema shape. It remains historical evidence and is not used as the final target result.

## Proof boundary

These are local Windows observations. They do not prove a universal OS race, leak absence, security isolation, production capacity, product correctness or independent attestation. No target harness or product file changed. AUTH-19B must diagnose and repair only HM-D01/HM-D02, then rerun this meta contract before any AUTH-19C product work.
