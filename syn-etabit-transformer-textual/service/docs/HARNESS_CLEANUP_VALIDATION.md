# Owned-process cleanup validation

Date: 2026-10-30. Approved scope: AUTH-16. Harness reporting: `/1.2`.

**SH-D01 is corrected within the validated Windows cleanup boundary.** The
unchanged formerly failing test passes, the final dedicated sequence passes
20 immediate exclusive-log checks, all 92 existing selected verification methods
pass, and fresh native/full-service runs pass. The six new cleanup methods also
pass; these are 98 distinct verification/regression methods across the recorded
invocations, not one 98-method command.

## Results

| Check | Outcome |
| --- | --- |
| Existing deadline test before correction | ERROR/WinError 32, retained |
| Controlled close-order contract before correction | FAIL: no observed job-zero event, retained |
| Initial count-only repair | First real cycle failed exclusive open, retained |
| Final strict dedicated sequence | 20/20 PASS: eight early, eight ready, four launcher-exited |
| Controlled cleanup behavior | Five methods PASS: ordering/idempotence, group timeout, query failure, process-signal timeout and PID-membership mismatch |
| Existing selected regressions | 92/92 PASS, including the unchanged original deadline test |
| Fresh native harness | 100 hardening, 1,000 fuzzy, eight torture PASS |
| Fresh full-service harness | 119 rigid, 500 fuzzy, five torture PASS |

## Evidence map

All paths below are relative to
`<source-workspace>`.

- Scope: `.docstream/harness-cleanup-runs/auth16-20261030/`.
- Original identities/source copies: BEFORE.json and source-before/.
- Original reproduced failure: existing-deadline-before.txt.
- Pre-correction ordering failure: completion-contract-before.txt.
- Insufficient count-only repair: cleanup-checks-after.txt,
  runner-job-zero-only.py and its partial cycle directory.
- Intermediate corrected sequence: cleanup-checks-handles.txt and its cycle
  directory, plus test-before-immediate-probe.py identifying the pre-probe write.
- Final strict cycle result: cleanup-cycles-final.txt and the final directory
  named in DELIVERY.json's final_cleanup_sequence.
- Additional handle/ownership faults: handle-fault-checks.txt.
- Existing regressions: regressions-final.txt.
- Implementation/readback: IMPLEMENTATION.json, DELIVERY.json and
  process-inventory.json. The pre-probe-strengthening implementation record is
  retained separately rather than silently discarded.
- Fresh native: `.docstream/native-harness-runs/auth16-20261030-native/`.
- Fresh service: `.docstream/harness-runs/auth16-20261030-service/`.

Each workload area retains its REPORT.md, summary.json, exact inputs and event
journals. Service modes additionally retain cleanup.json. Historical AUTH-15
failures and reports remain unchanged.

## Dedicated cleanup tests

The final strict sequence completes 20 cycles in **9.922 seconds**, below 600.
The longest observed individual cleanup is **0.016 seconds**, below the
five-second process/group budget. These are local observations, not performance
guarantees. The sequence retains **44,933 bytes**, below 512 MiB.

All 20 inputs are saved before launch and independently hash-verified. Fixture
roles are closed. A gate lets ready/exited fixtures spawn descendants after the
parent has been assigned to its private job. Four cases prove that waiting only
for the launcher is insufficient to describe the intended cleanup scope: the
launcher is already exited while a descendant remains before close.

Every final cycle confirms job zero, a stopped launcher and successful exclusive
log open on the first attempt. The exclusive-open operation occurs immediately
after closing the parent log context, before any diagnostic file write. Logs
are preserved. No cleanup retry, ignored exception or file-deletion workaround
is used to obtain a passing result.

The other five methods use controlled API/process doubles. They verify ordering
and repeated-close behavior, honest failure on active-group timeout/query error/
process wait timeout, and refusal to wait on a reused/nonmember PID. Synthetic
cleanup failures are expected test outcomes, not unreported live process leaks.

The real-cycle development history is explicit: one failed initial cycle,
20 intermediate passes before measurement strengthening, and the final strict
20 passes. Each attempt stays within its bounded count/time/evidence limits.
The final sequence is the acceptance result; earlier observations are preserved.

## Existing regressions and workload runs

The 92-method regression selection passes in **6.008 seconds**. It includes
30 fixed native, 17 native-harness, 11 meta-harness, 19 service-harness and
15 format-hardening methods. No existing test source/assertion changes.
The new cleanup methods are maintained separately in test_harness_cleanup.py.

Fresh native validation passes 100/1,000/eight, with zero mode audit issues and
1,520 submitted attempts against its 2,000 cap. All 1,108 saved input hashes
match. The native model and its own cleanup wrapper remain byte-identical.

Fresh full-service validation completes in **177.562 seconds** below 1,200:
119 rigid, 500 fuzzy and five torture cases pass with no incomplete coverage.
It submits **24 render calls** below 25 and retains the existing four-client,
1,800-loop-request/2,000-total-call and 20-actor-crash limits. All 624 saved
service input hashes match their declared canonical encoding.

Each of the three service modes reports confirmed owned-job cleanup, zero active
processes, a closed job handle and a stopped launcher. Those mode workers had
already exited normally, so their handle-capture/wait lists are empty; the
dedicated cases separately exercise active descendants and interruption.
The shared helper is also exercised by the native/meta regression callers.
No source drift occurs during either full run.

Passing fuzzy cases still include the deliberately expected rejections and
explicit CR-loss cases approved in AUTH-15. Format policy, source fidelity and
error classification remain unchanged; cleanup repair does not broaden their
comparison rules.

## Preservation and final readback

The 89-file initial snapshot has exactly two changed existing files:
service/src/docstream_cpu/harness/runner.py and harness/__init__.py. The other
**87 protected files remain byte-identical**, including product/native modules,
existing tests, native/meta wrappers, metadata/locks, AGENTS.md and snapshotted
historical reports/logs. New cleanup tests/reports and authorized planning-note
updates are separate additions or scoped changes.

Final native/service product-source identities match the current code. Independent
readback verifies **1,732 saved workload inputs** plus the final 20 cleanup inputs,
with zero hash mismatches. Existing failed results are not relabeled as passes.

| Evidence area | Bytes at audit |
| --- | ---: |
| Final native run | 2,487,154 |
| Final full-service run | 42,786,960 |
| Final strict cleanup sequence | 44,933 |
| Entire cleanup scope before delivery metadata | 207,843 |

All areas are below 512 MiB. The size guards are sampled software checks rather
than operating-system quotas. The matching-process inventory is empty after
completion, including test fixture workers and project browser processes.

No dependency install, production-store migration, transformation change,
format-policy change, release, GPU, bypass or agent-control activation occurred.
The result establishes the stated bounded Windows cleanup observations; it is
not universal file-handle attribution or independent operating-system/security
certification. Agentic-control integration remains last.
