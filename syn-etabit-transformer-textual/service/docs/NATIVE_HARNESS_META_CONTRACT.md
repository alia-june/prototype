# Native harness verification contract

AUTH-14 was approved in this chat on 2026-10-30. The user requested hardening,
loose/fuzzy and torture tests of the harness, followed by fresh project tests.
This contract supplements the historical native and service harness contracts.
It does not replace their criteria or alter native/service behavior.

## Sources and scope

The governing basis is the approved AUTH-14 proposal, PROJECT_DECISIONS.md,
NATIVE_REFERENCE_CONTRACT.md, NATIVE_HARNESS_CONTRACT.md and the original
HARNESS_CONTRACT.md/HARNESS_FINDINGS.md. CPU safe ASCII remains the native
reference. Stream lineage, atomic publication, exact bytes, expected exception
types/codes and complete rejection-state preservation remain significant.

The maintained package is `src/docstream_cpu/native_harness_meta/`. Its reviewed
dispatch fixture is `tests/fixtures/native_harness_meta/contract.json`; independent
verification is in `tests/test_native_harness_meta.py`. Run evidence is retained
under the workspace `.docstream/native-harness-meta-runs/`. Controlled native
worker doubles and isolated real native runs retain separate unique evidence
roots under `.docstream/native-harness-runs/`, linked by outer case records.

Only harness corrections are included. Product/native code, service adapters,
fidelity policy and historical evidence must remain unchanged. The earlier
HF-01/HF-02/HF-03 findings remain relevant to the subsequent service rerun.

## Independent checks

The meta runner has its own pre-execution input journal, hashes, exception
records and aggregation. It does not use the target native Journal to decide
whether its own cases passed. A synthetic actor or worker double may deliberately
fail: the outer test passes only when the target detects the declared fault.
The actor substitutions are in-process patches, never edits of product files.

| Mode | Bounded coverage |
| --- | --- |
| Hardening | 28 fixed checks: closed replay/JSON/size/path rejection; escaped surrogate retention; saved-input timing; wrong exception/code/bytes; mutation despite an expected error; reduction/interrupted shrinking; attempt/evidence limits; non-overwrite; journal/report/input integrity; sticky failure recovery; truncated tails; simulated product-identity drift |
| Loose/fuzzy | 1,000 seeded cases: 680 malformed replay mutations, 120 deliberately wrong or contradictory outcomes (40 wrong expected codes, 40 failure-journal contradictions, 40 failure-then-pass recoveries), and 200 accepted harness-input controls exercising a declared native rejection |
| Torture | Four concurrent isolated five-case native runs; eight ready-child terminations; eight early-deadline terminations; 20 interrupted journal recoveries; eight interrupted shrinks; four callers competing for 20 accepted attempt slots; a 2,000-record incomplete journal; eight isolated worker-double controls |

Seed defaults to 20261030. The 200 fuzzy controls are valid *harness cases* whose
expected product behavior is rejection; they are not 200 accepted document edits.
The later full native run separately covers accepted transformation controls.
Malformed data is loaded through the closed target replay validator and never
evaluated as code. Artifact paths are generated internally. The native run's
input paths must remain contained within its own evidence directory.

## Outcomes and failure precedence

PASS requires complete planned coverage and evidence consistent with the worker
exit. A saved failure must survive later contradictory PASS events, interrupted
shrinking and missing final summaries. An incomplete or unverified run cannot
become an unqualified PASS. Missing/tampered inputs, malformed journals, incorrect
counts, unknown report schemas, duplicate identities and path escapes must be
reported. Failure and evidence-integrity problems remain distinguishable in
case records and audit reasons.

The pre-correction run is retained before changing the target harness. Subsequent
runs use fresh directories and record source hashes; historical reports retain
the harness identity with which they were actually generated.

## Execution limits and proof boundaries

Each meta run has a 600-second ceiling and a 512-MiB retained-evidence ceiling,
including linked target runs. The final meta torture uses 16 owned timeout
cycles; native validation and regression checks remain within the approved
20-cycle meta/native cleanup allowance. The service torture's separate approved
20 actor crash cycles retain the original service harness limits.

An independent parent owns the meta worker and waits for its Windows job's active
processes to stop. Cleanup is restricted to children launched by the harness.
Evidence size guards are sampled checks, not operating-system disk quotas.
Elapsed time and memory observations are bounded local evidence, not capacity,
leak-absence, security certification or independent attestation.

Fresh native validation is limited to 900 seconds, 512 MiB and the original
2,000 submitted-attempt budget. Fresh full service validation is limited to
1,200 seconds, 512 MiB, 500 fuzzy cases, four clients/1,800 loop requests
(2,000 service calls maximum), 20 crash cycles and 25 render calls. Existing
comparators and baseline files remain unchanged.

## Commands

Run from the service directory with its project Python environment:

```powershell
.\.venv\Scripts\python.exe -m docstream_cpu.native_harness_meta before --run-id auth14-20261030-before
.\.venv\Scripts\python.exe -m docstream_cpu.native_harness_meta all --run-id auth14-20261030-final
.\.venv\Scripts\python.exe -m docstream_cpu.native_harness all --run-id auth14-20261030-native
.\.venv\Scripts\python.exe -m docstream_cpu.harness all --run-id auth14-20261030-service --max-seconds 1200 --max-mib 512
```

`before` omits torture so deliberately stopped children are not needlessly
repeated before reporting defects are corrected. A run ID cannot be reused.
Saved native cases retain the original native harness's closed replay interface.
Meta cases retain their complete input plus the seed/dispatch/source hashes;
the corresponding mode can be rerun in a fresh directory. No dependency install,
GPU work, expanded codepage, vocabulary ingestion, release, host configuration,
agentic-control integration or product repair is included.
