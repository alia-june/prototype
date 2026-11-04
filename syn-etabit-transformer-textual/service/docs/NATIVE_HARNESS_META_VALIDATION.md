# Harness verification and fresh project validation

Date: 2026-10-30 (America/New_York). Approved scope: AUTH-14.

The corrected native harness passes its bounded verification. The native model
passes its fresh project run. The full service remains **FAILED** because its
fuzzy tests reproduce the same 24 existing cases in HF-01/HF-02/HF-03. Completion
of this test scope does not imply product acceptance or approval to repair it.

## Results

| Target | Fixed/hardening | Loose/fuzzy | Torture | Overall |
| --- | --- | --- | --- | --- |
| Native harness before correction | 17 passed, 11 failed | 920 passed, 80 failed | Deliberately omitted | FAIL |
| Native harness after correction | 28 passed | 1,000 passed | 8 scenarios passed | PASS |
| Native model, fresh full run | 100 passed | 1,000 passed | 8 scenarios passed | PASS |
| Full service, fresh full run | 119 rigid checks passed | 476 passed, 24 failed | 5 scenarios passed | FAILED |

Additional verification/regressions pass: 17 existing native-harness methods,
11 new meta-harness methods, 30 fixed native methods and 19 existing service
harness methods, totaling **77 passing methods**. The service rigid mode also
executes the original 117 selected regressions plus its golden/workflow checks.
These counts describe different layers of testing and should not be summed
into a claim of unique independent product defects or guarantees.

## Exact evidence locations

All paths below are relative to the workspace
`<source-workspace>`.

| Evidence | Location |
| --- | --- |
| Initial failing meta run | `.docstream/native-harness-meta-runs/auth14-20261030-before/REPORT.md`, `summary.json`, `events.jsonl`, `inputs/` |
| Original test source | The initial run's `source-snapshot/MANIFEST.json` and its 15 preserved files |
| Initial verification failures | The initial run's `verification-before.txt` |
| First corrected verification | The initial run's supplemental `verification-after-fix.txt` (10 methods at that stage) |
| Final meta run | `.docstream/native-harness-meta-runs/auth14-20261030-final/REPORT.md`, `summary.json`, `RUN.json` |
| Native run | `.docstream/native-harness-runs/auth14-20261030-native/REPORT.md`, `summary.json`, mode worker summaries and `audited-summary.json` files |
| Full service run | `.docstream/harness-runs/auth14-20261030-service/REPORT.md`, `summary.json`, mode `results.json`, saved inputs and failures |
| Final 28 harness methods | `.docstream/native-harness-meta-runs/auth14-20261030-verification/harness-tests.txt` |
| Final 49 regression methods | The verification directory's `project-regressions.txt` |
| Preservation/input/source/process audit | The verification directory's `DELIVERY.json`, `PROTECTED_BEFORE.json`, `native-audit.json`, `meta-input-audit.json`, `process-inventory.json` |

The initial run's original records were retained. The source snapshot and
verification logs are labeled supplemental artifacts; they do not replace its
failed summary. Every subsequent workload used a fresh directory. Controlled
worker-double and concurrent smoke evidence has unique native-run roots linked
from the meta cases' `artifacts` fields.

## Harness defects and correction

NH-D02: the supervisor could trust a PASS summary despite contradictory journal
records, incomplete cases, missing/tampered inputs, incorrect counts/schema,
duplicate/mismatched identities, an escaped path or malformed journal data.
NH-D03: recovery could overwrite an observed FAIL with a later PASS event.
The first run exposes these with 11 fixed failures and 80 fuzzy failures.

Corrections are confined to the native harness: a new evidence auditor,
supervisor reconciliation, sticky failure recovery and report identity
`docstream.native-harness/1.1`. The closed case schema remains `/1`. Original
worker summaries remain intact; their separately saved audited counterparts
drive the supervisor's overall status. The full findings and bounded limitations
are in NATIVE_HARNESS_META_FINDINGS.md.

The outer meta runner separately journals its own cases before execution,
verifies its own input hashes, checks its own summary against its journal and
planned completion, and supervises its owned worker independently of the target
cleanup routine. A forged-count/missing-coverage verification checks that outer
audit. This avoids using the target Journal as its own only oracle.

## Final meta coverage

The 1,000 fuzzy cases contain 680 malformed replay mutations, 120 deliberate
oracle/report/recovery contradictions and 200 valid harness-input controls.
Each of 20 mutation recipes occurs 40 times; every fifth case is a control.
The controls exercise a correctly declared product rejection, rather than
representing accepted document edits. Seed 20261030 regenerates the same data.

Torture verifies four isolated concurrent small runs, eight ready-child
terminations, eight early-deadline terminations, 20 sticky-failure recoveries,
eight interrupted shrinks, four callers sharing an attempt budget, a 2,000-record
unfinished journal and eight isolated evidence controls. All 16 deliberately
stalled children stop. The expected interrupted work remains incomplete; a
parent check passes only when it observes the expected cutoff and cleanup.

The final run completes 1,036 outer cases/scenarios in 25.906 seconds against a
600-second ceiling. The initial hardening/fuzzy run took 340.578 seconds against
the same ceiling. The meta implementation subsequently reduced repeated full
evidence-directory scans; these timings do not measure native product speed.

## Fresh native result

The 100 hardening checks, 1,000 fuzzy cases (800 expected rejections and 200
accepted transformation controls), and eight torture scenarios all pass.
Submitted transformation attempts are 54, 730 and 736 respectively: **1,520**
against the original 2,000 cap. Worker durations are 0.094, 1.015 and 10.047
seconds. The interval from recorded run timestamp to final report modification
is 24.743 seconds, including supervision and evidence audit, within 900 seconds.
That timestamp interval is distinguished from a monotonic benchmark.

All three owned workers report exit zero, stopped children, no supervisor
deadline and no audit issues. The nested native timeout scenario confirms its
expected incomplete child and cleanup. Native source identity is unchanged.
This isolated reference-model result does not validate native service integration,
persistence, GPU lowering or expanded codepages.

## Fresh full-service result

Seed 20261029 completes all 624 rigid/fuzzy/torture case records with no
incomplete coverage. Overall duration is **224.921 seconds** within 1,200.
The run submits **24 render calls** within 25 and **1,907 torture service calls**
within 2,000, including 1,800 loop requests/four clients and 20 actor crash cycles.
All five torture scenarios pass: limits, storage faults, crash recovery,
network load and render recovery. Each mode reports its owned worker stopped.

| Finding | Fresh failed cases | Observed signature |
| --- | ---: | --- |
| HF-01 | 5 | DOCX round-trip changes CR to LF without a conversion-loss diagnostic |
| HF-02 | 10 | NUL DOCX export raises an unclassified adapter exception |
| HF-03 | 9 | Malformed-surrogate direct dictionary ingestion raises UnicodeEncodeError before typed rejection |

The 24 failing case names, families, exception classes and messages match the
previous `final-validation` run exactly. All 24 failed original case inputs also
match as data. The 20 additional failure bundles and three available reductions
have matching case payloads. Their wrapper paths, tracebacks and times are
run-specific and were preserved. The last four failed cases retain their saved
inputs and journal outcomes under the existing 20-extra-bundle cap. No missing
bundle was invented or regenerated.

An initial readback assumed every failure had a reduced bundle and then compared
whole replay wrappers. Inspection corrected that audit assumption: the original
contract caps extra bundles at 20 and minimizes selected cases only. The raw
wrapper comparison remains in `DELIVERY_WRAPPER_COMPARISON.json`; DELIVERY.json
separately records exact case-payload comparisons and run-specific wrapper
differences. Product comparators and failure outcomes were not altered.

## Input integrity, retention and preservation

Independent readback verifies 1,028 initial meta inputs, 1,036 final meta inputs,
1,108 native inputs and 624 service inputs with **zero input-hash mismatches**.
Native/meta hashes cover exact saved file bytes; the historical service harness
hash covers its declared canonical case encoding. Final meta/native manifests
match the current harness files. All 15 before-correction snapshot copies match
their snapshot manifest.

Retained sizes at the final audit, including linked native artifacts for meta
runs, are below each 512-MiB ceiling:

| Run | Main directory bytes | Linked artifacts bytes | Total bytes |
| --- | ---: | ---: | ---: |
| Initial meta | 4,619,286 | 1,137,241 | 5,756,527 |
| Final meta | 4,385,006 | 1,469,230 | 5,854,236 |
| Fresh native | 2,487,258 | 0 | 2,487,258 |
| Fresh service | 43,230,437 | 0 | 43,230,437 |

The 77-file pre-change snapshot shows precisely two changed existing files,
both approved native-harness files (`runner.py`, `__init__.py`). The other 75
protected files retain their hashes. Product/native code, existing tests,
metadata/locks and snapshotted historical reports remain byte-identical. New
harness/audit files, new tests/fixtures/docs and authorized planning-note updates
are additions or explicitly scoped changes.

After completion, a read-only process inventory finds no matching Docstream
module workers or project Chromium/Playwright processes. This complements the
owned-worker stop records; it is not a system-wide process/security audit.

No dependencies were installed. No product fix, fidelity-policy change, baseline
relaxation, release, persistent server activation, GPU execution, vocabulary
ingestion, host registration or agentic-control integration occurred. HF-01's
CR/LF policy and HF-02/HF-03 product corrections remain separate future scope.
Agentic-control integration remains last.
