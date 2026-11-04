# Native hardening, fuzzy-error and torture harness

Date: 2026-10-29 (America/New_York). AUTH-13.
Harness: `docstream.native-harness/1`. Product: `docstream.native.safe-ascii/1`
in the existing docstream-cpu 0.2.0.dev4 development environment.

## Scope

This is a maintained developer harness, separate from the native implementation
and the earlier service/format harness. It adds no product correction, relaxed
expectation, dependency, database, renderer, listener, vocabulary dataset or
agentic-control integration. The native and earlier service contracts remain
unchanged. The report must distinguish passing expected rejections, unexpected
failures and incomplete coverage.

The governing behavior is NATIVE_REFERENCE_CONTRACT.md. Expected outcomes come
from its explicit scalar, identity, layer, occurrence, publication and resource
rules. Results are not learned from whatever the implementation currently emits.
Hardening/fuzz success is bounded evidence, not general security certification.

## Commands

From the workspace root in the prepared development environment:

```powershell
& service/.venv/Scripts/python.exe -m docstream_cpu.native_harness all
& service/.venv/Scripts/python.exe -m docstream_cpu.native_harness hardening
& service/.venv/Scripts/python.exe -m docstream_cpu.native_harness fuzzy-error --seed 20261029
& service/.venv/Scripts/python.exe -m docstream_cpu.native_harness torture
```

All modes default to seed 20261029. `--run-id` accepts 1..64 ASCII letters,
digits, underscores or hyphens. Existing run directories are refused, not
overwritten. Linked/reparse-point output ancestry is rejected. Every normal run
is retained under `.docstream/native-harness-runs/<run-id>/`.

`--fuzzy-cases` can select a multiple of five in 5..1000; the ratio remains four
invalid cases to one valid control. The approved full run uses all 1000.
`--seconds` can lower the combined supervisor deadline, up to 900 seconds.
Malformed configuration is rejected before a new run directory is created.

Exit codes: 0 PASS, 1 FAIL, 2 INCOMPLETE, 3 CONFIG_ERROR. An observed failure
retains failure precedence if later shrinking or execution is interrupted.
Worker exit/summary disagreement cannot yield an unqualified pass.

## Hardening mode

The default fixture defines 84 error cases plus 16 fixed probes: 100 recorded
cases. Error cases cover all 20 error-recipe families in several fixed variants,
with all eight configured resource boundaries included.

The probes cover the complete 128-position alphabet and escaped inspection,
literal et/te/ette/-ette construction, immutable public values/views, detached
records, edits of a shared occurrence, definition versus history identity,
empty/no-op streams, request content versus batch occurrence identity, five
publication preparation fault points and three definition preparation points.

Faults deliberately raise MemoryError from a closed, trusted test patch point.
They are not a process out-of-memory simulation. After each fault, complete
state is compared and a subsequent valid action must succeed. Source patching
is restored by its context manager; product source files are not rewritten.

## Fuzzy-error mode

The full workload has exactly 1000 reproducible cases: 800 invalid inputs and
200 valid controls. Each of 20 error recipes receives 40 generated cases:

1. Symbol values above 127.
2. Negative symbol values.
3. Boolean symbols.
4. Wrong symbol scalar/container types.
5. Non-ASCII and malformed-surrogate literals.
6. High-byte literals.
7. Mutable literal containers.
8. Over-length literals.
9. Malformed operation identifiers.
10. Wrong edit index types/values.
11. Wrong path index types/values.
12. Invalid edit kinds/argument combinations.
13. Wrong structural layer values.
14. Well-formed but missing definition references.
15. References to an impermissible layer.
16. Duplicate operation IDs.
17. Mutable or invalid batch containers.
18. Invalid late ranges after an earlier valid operation.
19. Invalid late paths after an earlier valid operation.
20. Exhausted configured resource limits.

For an expected rejection, the harness checks exact declared exception type and
NativeError code where applicable. It compares a complete state fingerprint and
the retained state object before and after. The fingerprint covers definition
payloads, expansion lengths/work accounts, stream ancestry, retained batches,
reference-slot totals and ID counters. Counts alone are insufficient.

Valid controls preserve exact byte data, including arbitrary ASCII controls.
Each has two ordered structural edits. A separate bytearray sequence oracle
computes expected results; native expansion is not used to generate expectations.
Every retained prefix is checked in reverse order and the original stays intact.

## Torture mode

Eight scenarios run in separate fresh models where appropriate:

| Scenario | Work and required behavior |
| --- | --- |
| Wide retained history | 10,000 direct references/root, 500 replacement batches; verify each result, original, older selections and 501-entry ancestry. |
| Deep sharing | Eight structural layers, 200 shared occurrences, 32 selected-occurrence edits; other placements stay unchanged. |
| Empty amplification | Expand an accepted empty graph accounting for 1,990,200 traversal visits; reject the next over-budget definition atomically. |
| Expansion boundary | Expand exactly 1,000,000 bytes; reject the next byte above the configured maximum without state change. |
| Resource exhaustion | Exercise all eight configured native resource accounts with specific LIMIT_EXCEEDED results and intact state. |
| Four callers | Four threads submit 40 edits each on branches from a shared base; verify branch content, ancestry and gap-free unique stream ordinals. |
| Publication faults | Repeat eight controlled preparation faults after retained work; verify unchanged state and successful subsequent action. |
| Supervisor timeout | Start an owned stalled worker, observe readiness, terminate on the test deadline and verify cleanup. The child probe is explicitly INCOMPLETE; the parent scenario passes only when that expected result is observed. |

Concurrency establishes bounded consistency for this owned in-memory model, not
parallel speedup, distributed transactions or service HTTP behavior.

## Combined budgets and owned workers

The three main modes share a 900-second supervisor deadline and a maximum of
2000 submitted native transformation attempts. An attempt is a requested Edit
in a submitted apply_batch call; malformed/empty submissions count as at least
one. Rejected submissions do not refund attempts. Standalone constructor and
definition checks are separately bounded by the closed case counts, not
misreported as successful transformations. Optional failure reduction consumes
the same operation account. Earlier native/service regression tests are
separately reported verification, not folded into this main-run counter.

The default retained-run byte budget is 512 MiB, monitored by the supervisor and
pre-execution evidence checks. The approved run's final measured footprint is
recorded in NATIVE_HARNESS_VALIDATION.md. A guard is not an operating-system
filesystem quota. Coverage interrupted by a budget remains explicit.

Each selected mode is launched as an owned subprocess, with no visible Windows
console. Windows job objects cover descendants. The native harness reuses the
existing process owner helper and adds a local stop routine that waits for job
ActiveProcesses to reach zero before releasing handles and logs. This addresses
the venv-launcher/descendant cleanup race found during development; it does not
alter the earlier harness helper.

Only processes created by this harness are terminated. Windows job committed
memory peaks cover owned descendants; they are neither a Python-only working
set nor an enforced RAM cap. Missing measurements remain unavailable. Timings
and peaks are one-run observations, not throughput or leak-absence proofs.

## Evidence and replay

Each mode has inputs/, failures/, events.jsonl and summary.json. A case input is
saved and its exact file SHA-256 journaled before execution. JSON uses escaped
ASCII, so malformed Unicode test data can be retained without encoding repair.
RUN.json records source identities, harness identities, environment and limits.
Top-level summary.json and REPORT.md combine the modes and supervisor outcomes.

```powershell
& service/.venv/Scripts/python.exe -m docstream_cpu.native_harness all --replay <saved-input.json>
```

`all --replay` selects the saved case's mode. Explicit mode mismatches are
rejected. Replay accepts only `docstream.native-harness.case/1`, closed families,
known recipe/probe/scenario names, checked fields and expected error labels.
Unknown fields, duplicate JSON keys, non-finite JSON constants and files above
2 MiB are rejected. No replay field selects a command, executable, module import
or caller-supplied program. Worker output is restricted to the native run tree.

An unexpected failure retains the original input and exact error. Fuzzy
reduction tries at most 12 smaller, schema-valid data candidates, preserving
the failure type/tag and actual error type/code. It does not edit expected
outcomes or native source. A reduction is not promised for every family.

Case failures are journaled before optional reduction. If a worker is stopped,
the supervisor reconstructs finished/failed/pending cases from its journal.
Unknown consumption after interruption prevents additional main modes from
starting; the remaining attempt budget is not guessed.

Harness self-tests deliberately exercise failure, interruption, reduced replay,
wrong error classifications, state-change detection, timeouts and configuration
rejection. Their expected negative outcomes are distinct from product defects.
Actual verification results are retained in NATIVE_HARNESS_VALIDATION.md.

## Scope boundaries

This harness does not certify a renderer, font, Word compatibility, GPU backend,
untrusted-code sandbox, transport, persistent store, whole-service release or
standalone installation. Existing HF-01/HF-02/HF-03 remain open. Product fixes
require their own concrete approved scope; final agentic-control integration
remains last.
