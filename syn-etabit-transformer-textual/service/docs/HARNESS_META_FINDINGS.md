# Service-harness meta-verification findings

Date: 2026-10-31. AUTH-19A. Final target status: **FAIL — harness cleanup race reproduced**.

## HM-D01 — Native supervisor log handle can outlive returned cleanup

Two of three complete 276-test discoveries fail in the same existing test, `NativeHarnessTests.test_real_supervisor_timeout_stops_its_owned_child`. The test's temporary-directory cleanup raises `PermissionError: [WinError 32]` while removing its retained `child.log`.

Discovery 0 fails after 65.034 seconds; discovery 1 fails after 58.430 seconds; discovery 2 passes after 57.515 seconds. The two failed outputs have different run-specific paths and hashes but the same exception boundary. Three separately ordered pairs of the service deadline test and native timeout test pass in 0.505–0.534 seconds. A later 62-method harness-focused selection reproduces the same error twice in two aggregate attempts; its immediate one-method rerun passes in 0.198 seconds. Therefore simple two-test order is not sufficient; the symptom is associated with aggregate execution pressure or lifecycle timing.

The current evidence proves the open-handle symptom and intermittent aggregate reproduction. It does not yet prove whether the unreleased handle belongs to the direct log object, a surviving child/descendant, the venv launcher, an inherited Windows handle or delayed process teardown. AUTH-19B must instrument ownership before choosing a repair.

## HM-D02 — Pre-start incomplete mode has a different result shape

In the first retained meta run, one 50 ms service-harness deadline was consumed before the mode worker started. The service harness retained an incomplete mode row with `mode`, `status`, `incomplete_reasons`, `counts` and `metrics`, but without `cases`, `owned_worker_stopped`, `owned_cleanup` or `owned_job_stopped`.

This is not a false PASS and no worker existed to clean. It is nevertheless a schema-shape inconsistency: the existing service-harness deadline test directly indexes `owned_worker_stopped`, and the earlier 267-test aggregate run produced a `KeyError` at that exact assertion. A later run in which all eight workers started has all eight audited deadline packets and all eight immediate exclusive log opens passing.

AUTH-19B should make the skipped/pre-start state explicit and schema-stable rather than weakening the test or pretending a nonexistent worker was stopped.

## Meta implementation findings retained during development

The first AUTH-19A run is retained at `.docstream/harness-meta-runs/auth19a-20261031-before`. It exposed two errors in the new meta-harness: a full evidence-tree scan on every fuzzy case created quadratic filesystem work, and the independent subprocess owner supplied an invalid null Windows job name. Neither is attributed to the target harness.

The meta implementation was corrected within AUTH-19A: size is sampled every 50 cases with exact final observation, and meta jobs use unique non-null names. Nine focused tests pass afterward. The final target run uses a fresh evidence directory; the failed first run was not rewritten.

## Anti-lessons

- A launcher `poll()` result does not prove every inherited handle is released.
- A Windows job active-process count of zero is not by itself proof that a retained log is immediately deletable.
- An incomplete mode that never started should still have an explicit stable schema.
- An ultra-short deadline can expire during setup; tests must distinguish pre-start from started-and-stopped.
- Repeated isolated passes do not negate an aggregate intermittent failure.
- Full recursive evidence scans inside every generated case turn bounded validation into quadratic work.
- A failed meta scenario must be classified before it is called a target defect.

## Product boundary

No Strmdocx product defect was established by AUTH-19A. The failed full discoveries stop in harness-test cleanup after the substantive tests have otherwise run. Product repair remains closed until the harness repairs pass AUTH-19B and a fresh corrected harness identifies product failures.
