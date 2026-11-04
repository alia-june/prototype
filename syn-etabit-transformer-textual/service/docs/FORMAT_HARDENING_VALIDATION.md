# Format hardening implementation and validation

Date: 2026-10-30. AUTH-15. Local package metadata: 0.2.0.dev4.
Service harness: `docstream.harness/1.1`. Native harness: `/1.1`.

## Outcome

HF-01/HF-02/HF-03 are corrected under the explicitly approved conversion policy.
The final full-service run passes **119 rigid, 500 fuzzy and five torture
cases/scenarios**, with no incomplete coverage. The final native run passes
**100 hardening, 1,000 fuzzy and eight torture cases/scenarios**, with no audit
issues. Fifteen maintained targeted regression methods pass.

The complete verification result is **not unqualified green**: the final
77-method existing verification/regression suite has 76 passes and one cleanup
ERROR in the old service-harness deadline test. An isolated retry reproduces
that error. SH-D01 remains open; it is separate from the corrected product
findings and was not hidden by the passing workload results.

## Evidence locations

Paths below are relative to
`<source-workspace>`.

| Evidence | Location |
| --- | --- |
| Scope evidence and source preservation | `.docstream/format-hardening-runs/auth15-20261030/BEFORE.json`, `source-before/`, `IMPLEMENTATION.json`, `DELIVERY.json` |
| Initial targeted failures | Scope directory's `targeted-before.txt` |
| First correction and helper error | `targeted-after-1.txt` |
| Initial 13-method pass | `targeted-final.txt` |
| Typed-mapping failure and correction | `targeted-typed-before.txt`, `targeted-final-v2.txt` |
| Missing-field guard failure | `constructed-request-before.json`, `service-before-constructed-guard.py` |
| Final 15-method targeted pass | `targeted-final-v3.txt` |
| Earlier 77-method pass | `regressions.txt` (before the final missing-field guard correction) |
| Final 76 passes/one cleanup error | `regressions-final.txt` |
| Isolated cleanup error reproduction | `cleanup-test-retry.txt` |
| All 24 historical cases | `historical-cases/results.json` and its original/approved input pairs |
| Final native workload | `.docstream/native-harness-runs/auth15-20261030-native-final/REPORT.md`, `summary.json`, mode worker/audited summaries |
| Final full-service workload | `.docstream/harness-runs/auth15-20261030-service-final/REPORT.md`, `summary.json`, mode results/journals/inputs |
| Process readback | Scope directory's `process-inventory.json` |

The first full native/service runs without the `-final` suffix also pass and
remain retained. Their implementation predates the missing-field guard repair.
The final runs repeat full validation against the final code. This distinction
is explicit in DELIVERY.json's current-source comparisons; earlier source
differences are historical version differences, not changes during those runs.

## Implemented behavior

- CR export emits `DOCX_CARRIAGE_RETURN`; the service default rejects the loss,
  while explicit allow retains the diagnostic in its successful receipt. Title,
  body spans, table paragraphs and version-one plain blocks are covered.
- A temporary output string maps each CR to LF; existing LFs remain, so CRLF
  produces two breaks. Original source strings and hashes remain exact.
- Snapshot strings are checked against XML 1.0's character repertoire before a
  document-library object is created. Illegal characters produce exactly
  `UNREPRESENTABLE_DOCX` under both loss policies, without source repair.
- Request entry checks nested dictionary keys/values, arrays and typed values
  for malformed surrogate strings before strict UTF-8 serialization. It rejects
  with VALIDATION_ERROR before reservation/mutation. Missing constructed fields
  are left for normal typed rejection instead of raising AttributeError.
- Harness generation declares the new expectations independently of product
  calls. The CR oracle changes only the explicitly allowed expected characters
  and then checks all remaining supported meaning. Wrong typed errors, raw
  exceptions, missing diagnostics and unrelated text changes fail verification.

See FORMAT_HARDENING_CONTRACT.md for the approved rules and primary references,
and FORMAT_HARDENING_FINDINGS.md for the defect histories and remaining limits.

## Targeted and historical coverage

Fifteen targeted methods cover the service's reject/allow paths, receipt replay
and restart, source/head/artifact preservation, literal CR/LF/CRLF/TAB mapping,
title/table/plain text, all 31 XML-forbidden tested scalars (29 C0 exclusions
plus U+FFFE/U+FFFF), legal boundary scalars, style/font/link/image metadata,
dictionary and typed mapping surrogates, missing constructed fields, valid
Unicode/source hashes, and synthetic harness-oracle faults.

The final targeted run passes in 1.245 seconds. All-application-table and
in-memory semantic-map snapshots remain identical on pre-reservation rejection.
DOCX rejection checks verify no export publication and unchanged source/head;
post-reservation export failure deliberately retains its failed request receipt.

All 24 previous failing inputs are retained byte-for-byte in original copies.
Separate approved cases all pass: five explicit CR loss cases, ten specific
DOCX rejections and nine typed Unicode rejections. Source/hash/rule links are
stored before execution. Independent readback verifies those identities.

The fresh 500-case generator retains the previous texts, snapshots, requests,
random sequence and categories. Exactly 15 cases change expectation fields:
five declare the CR loss and ten declare the DOCX error. The other 485 cases,
including the nine surrogate cases, retain their original case data. No
normalization or input removal is used to make failures disappear.

## Final full-service workload

| Mode | Passed | Failed | Incomplete |
| --- | ---: | ---: | ---: |
| Rigid | 119 | 0 | 0 |
| Fuzzy | 500 | 0 | 0 |
| Torture | 5 | 0 | 0 |

The final run completes in **223.562 seconds**, below 1,200. It submits
**24 render calls** below 25 and **1,907 torture service calls** below 2,000,
including 1,800 loop requests/four clients and 20 crash cycles. Limits, storage
faults, crash recovery, network load and rendering recovery all pass. Each mode
reports its owned worker stopped; there is no source drift during the run.

The 500 fuzzy results include ten UNREPRESENTABLE_DOCX rejections and five
explicit CR-loss round trips. Other expected invalid-input rejections remain
passing expected outcomes. These are 500 passing checks, not 500 accepted
document edits. All 624 saved service inputs match their canonical case hashes.

The earlier full-service run takes 223.610 seconds and has the same 119/500/five
passing counts. Both runs independently stay within the original per-run limits;
they are not substituted for one another in the final implementation claim.

## Final native and existing verification

The final native run passes 100/1,000/eight with 54/730/736 submitted attempts,
totaling **1,520** below 2,000. All 1,108 input hashes match and every mode's audit
issue list is empty. Its native profile and three native source files remain
byte-identical to the pre-correction snapshot. Native safe ASCII is not narrowed
to the DOCX repertoire.

The additional existing verification selection is 30 fixed native methods,
17 native-harness methods, 11 meta-harness methods and 19 service-harness
methods. The final suite passes 76 of those 77 methods; its one ERROR occurs
during temporary cleanup of the service-harness supervisor-deadline test.
An isolated retry also errors with WinError 32 on process-output.txt. The
deadline itself correctly reports INCOMPLETE and a stopped owned launcher;
file-handle cleanup is the failed boundary. No test was skipped or weakened.
The initial 77-method run passed before the final guard correction, so the
cleanup behavior is intermittent across these observations, not proven fixed.

SH-D01 is retained as a follow-up harness finding. The process-owner helper and
its existing test remain unchanged because AUTH-15 does not expand into that
separate correction. Passing product workloads do not override this test error.

## Preservation, retention and shutdown

The 83-file pre-change snapshot has exactly five changed existing files:
`service.py`, `docx_adapter.py`, `harness/cases.py`, `harness/generate.py` and
`harness/__init__.py`. All changes are within the approved correction/expectation
scope. The other **78 protected files remain byte-identical**, including all
existing tests, native/core models, metadata/locks, original format contracts,
historical findings and snapshotted earlier run summaries. New tests/reports and
authorized planning-note updates are separately identified additions/changes.

Final implementation hashes match current source. Both native runs' 1,108
inputs and both service runs' 624 inputs are rechecked, totaling **3,464** saved
workload inputs with zero hash mismatches. Twenty-four historical original/
approved input pairs also match their retained identities. Service hashes use
their declared canonical encoding; native hashes cover exact saved file bytes.

| Evidence area | Bytes at audit |
| --- | ---: |
| First native run | 2,487,256 |
| Final native run | 2,487,267 |
| First full-service run | 42,690,245 |
| Final full-service run | 42,853,057 |
| Scope tests/source copies before delivery metadata | 11,403,320 |

Each area is below 512 MiB. Sampled guards and final readback are not operating
system quotas. Matching-process inventory after the last retry is empty for
Docstream module workers and project Chromium/Playwright processes. This
complements the workload stop records but does not prove file-handle ownership
or eliminate the observed SH-D01 race.

No dependency, package version, database schema, native representation or
production store was migrated. No old failure was rewritten, general comparison
relaxed, GPU enabled, release published or agent-control configuration activated.
These are bounded local results, not independent attestation or whole-product
release acceptance. Agentic-control integration remains last.
