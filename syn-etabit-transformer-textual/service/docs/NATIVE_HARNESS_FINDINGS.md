# Native harness findings

Date: 2026-10-29 (America/New_York). AUTH-13.
Harness: docstream.native-harness/1. Product profile: safe-ascii/1.

## Native product outcome

The approved full run passes 100 hardening cases, 1000 fuzzy-error cases and
eight torture scenarios. There are no unexpected native product failures in
that workload and no failed native cases requiring a corrective replay packet.
The 800 fuzzy rejections are expected outcomes, not 800 defects. Exact error
types/codes and complete state preservation are checked for those rejections.

Source evidence is retained under
`.docstream/native-harness-runs/auth13-20261029-validation/`. Every one of its
1108 input files is retained with a pre-execution file digest. Separate saved
case replays cover an invalid surrogate literal, controlled publication fault,
valid byte-sequence edits and deep shared assembly editing.

No native source, original test expectation or previous validation report was
changed to obtain these results. A passing bounded workload is not proof of
absence of all defects, universal hardening or production capacity.

## NH-D01 — Harness development cleanup race, corrected

The first native-harness self-verification run completed 17 tests with one
cleanup error. Its timeout assertion had stopped the Popen launch process, but
a descendant still held child.log during temporary-directory cleanup:

```text
PermissionError: [WinError 32] The process cannot access the file because it is being used by another process
...
Ran 17 tests in 1.370s
FAILED (errors=1)
```

The corrective change is confined to the new native harness. Its stop_owned
routine terminates the owned Windows job when necessary, waits for its active
process count to reach zero, and then closes/reaps the original owner. Both
normal mode supervision and the nested timeout probe use it. No unrelated
process is selected or terminated. The pre-existing process-owner helper is
unchanged.

The subsequent self-verification run passes all 17 tests, including real timeout
cleanup, and all main-mode supervisors plus the nested stalled-child scenario
record stopped owned children. This is a corrected harness defect, not a repair
to the native assembly model. Full final self-test output and source identities
are retained in NATIVE_HARNESS_VALIDATION.md.

## Pre-existing service findings remain open

HF-01 (CR/LF DOCX conversion policy), HF-02 (NUL export error classification)
and HF-03 (malformed-surrogate direct dictionary ingestion) are recorded in
HARNESS_FINDINGS.md. This native harness does not rerun or repair those service
boundaries. Native-harness PASS does not turn the earlier overall service
harness FAILED result into acceptance.
