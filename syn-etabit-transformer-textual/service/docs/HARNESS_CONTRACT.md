# Docstream rigid fuzzy and torture harness

Implementation: `docstream.harness/1`. Product under test: `docstream-cpu 0.2.0.dev4`.

The user approved the concrete harness proposal on 2026-10-29. The scope is a
maintained developer harness, fixed fixtures, self-tests, bounded runs and
replayable evidence. Product fixes and agentic-control integration are outside
this scope. Harness code is separate under src/docstream_cpu/harness; existing
product modules, operation contracts, schema, service registration and behavior
are unchanged.

## Running it

From the workspace root in the prepared development environment:

```powershell
& service/.venv/Scripts/python.exe -m docstream_cpu.harness all
& service/.venv/Scripts/python.exe -m docstream_cpu.harness rigid
& service/.venv/Scripts/python.exe -m docstream_cpu.harness fuzzy --seed 20261029
& service/.venv/Scripts/python.exe -m docstream_cpu.harness torture
```

Each command creates a new directory under `.docstream/harness-runs/`. An
optional `--run-id` uses 1–64 letters, numbers, underscores or hyphens; an
existing run ID is refused rather than overwritten. Linked output roots are
refused. This harness requires the source checkout and its prepared development
environment; it is not a standalone release installer.

To replay saved data:

```powershell
& service/.venv/Scripts/python.exe -m docstream_cpu.harness all --replay <case-json>
```

`all --replay` chooses the appropriate mode for that case. Explicit mode/case
mismatches are rejected. Replay data selects a closed case family, never a
command, executable, module path or caller-supplied program. Files are capped at
2 MiB. Regression replay permits only the known test modules and the six approved
preserved baseline tests. The original baseline HTTP test remains excluded.

Exit codes: 0 all selected checks pass; 1 at least one check fails; 2 the run is
incomplete without an observed failed check; 3 invalid configuration or startup
error. A failed check retains failure status if a later interruption prevents
completion; incomplete coverage remains explicit. A passing harness self-test
does not imply that the product passes the workloads.

## Rigid mode

Runs the 117 existing regression tests by explicit registry, plus two fixed
checks: the reviewed semantic/visual golden and a complete service workflow.
The resulting rigid case count is 119. The extra workflow checks import,
out-of-order inspection, four retained logical font outputs, zero necessary
font writes, explicit commit, both export formats, reimport and restart retry.

The golden in tests/fixtures/harness/reviewed-m4.json was frozen from the final
visually reviewed M4 example. It includes exact semantic JSON, source/digest
expectations, renderer/browser/font identity and the PNG hash. PDF checks cover
page count, dimensions and required text rather than unstable container dates.
The PNG itself is retained beside the golden JSON.

An environment mismatch makes the visual comparison incomplete and requires
explicit baseline review. Tests never update the baseline to match observed
output. The one-time preparation helper refuses an existing destination and
requires the fixed reviewed PNG hash; normal runs never invoke that helper.

## Loose fuzzy mode

The default is 500 generated cases, reproducible from a 32-bit seed. Eight
generation categories form six replay families:

- Version-one batches, version-two batches and invalid-first-operation batches.
- Equivalent supported Markdown syntax, such as ATX/setext headings, list
  markers and reference/inline links.
- Markdown semantic round trips with varied text and spans.
- DOCX semantic round trips with ordinary text, Unicode, tabs, line breaks,
  carriage returns and NUL input.
- Invalid typed ingestion requests, including a malformed Unicode surrogate.
- Malformed ZIP/OOXML inputs with explicit rejection expectations.

Valid batches compare reduced execution with the sequential reference exactly,
check deterministic plan seals and ensure that source values are unchanged.
Invalid batches must preserve the expected first error and operation ID. Invalid
requests must reject without creating a document. A generic internal error is
not substituted for a declared validation/conversion expectation.

The loose comparator permits only declared export representation differences:
new document block IDs, fragmentation into adjacent equivalent spans, and
explicit-versus-inherited equivalent font/bold/italic values. Text codepoints,
order, heading/list levels and starts, links, cell structure/header flags,
image identity/dimensions and document properties remain significant. There is
no broad Unicode normalization, approximate text matching, score threshold or
automatic tolerance for undocumented losses. The CR/LF finding remains failed
pending an explicit conversion-policy decision.

Every input is saved before execution. Failure artifacts include the input,
hash, exception/details and traceback. Up to 20 failures receive an additional
full failure bundle; all cases still retain their inputs and journal outcome.
Up to five distinct signatures receive bounded shrinking, with at most 40
candidate attempts each. Shrinking preserves the same failure signature and
does not alter product code, expectations, original inputs or golden files.
Batch-operation removal and single-span text reduction are supported; other
families may retain their original minimal replay with zero shrink attempts.

## Torture mode

Five scenarios exercise actual boundaries and recovery:

1. 255/256/257 operations and ASCII/multibyte sources around the 1 MiB limit.
2. Injected disk-full failures around reservation/model/flush/commit, injected
   permission failure and a real competing SQLite write lock.
3. Twenty actor processes terminated by their exact owned process handles at
   after-reservation, after-flush, before-commit and after-commit boundaries.
   Restart checks receipts, one resulting document, SQLite integrity and
   foreign keys.
4. Four official MCP clients sharing a loopback test service. The default is
   1,800 loop requests plus setup/competition requests: reads, retries, commits,
   plans, exports and invalid scalar types. Four additional candidates compete
   for one head; exactly one may commit.
5. Six render submissions covering worker replacement, artifact damage/repair,
   publication failure without head advance, a new request recovery, profile
   changes and 20 cache reuses without extra actual rendering.

The actual whole torture mode counts service calls and SDK-rejected requests,
including actor submissions. It stops before exceeding 2,000. Numeric replay
parameters are bounded in the scenario itself. No real disk is filled and no
permissions on user files are changed. The injected storage failures exercise
specific application paths; they are not proof of every filesystem failure.

## Budgets and ownership

Combined default limits: 20 minutes, 512 MiB newly retained run data, 500 fuzzy
cases, four clients, 20 crash cycles, at most 2,000 torture calls and at most 25
renderer submissions including existing regression render attempts. Defaults
allocate up to 180 seconds to rigid, 300 to fuzzy and 720 to torture, always
bounded by the remaining combined deadline. `--cases`, `--requests`, `--crashes`,
`--max-seconds` and `--max-mib` can reduce their respective limits, not expand
them beyond clearance. The network loop is capped at 1,800 so other torture
calls fit inside 2,000.

Each mode runs in a process owned by the supervisor. On Windows it is placed
in a kill-on-close job so timeout/interruption cleanup reaches descendants,
including crash actors and renderer processes. The harness never terminates a
process found by global name/PID search. Unix uses an owned process group.
Normal completion closes the renderer/listener before ownership is released.

The supervisor polls deadline and retained-file size at 250 ms intervals. This
is a monitored guard, not a filesystem quota or real-time scheduler; transient
writes and cleanup can cross the sampling instant. File-size accounting handles
SQLite journals disappearing during enumeration. Case-boundary checks add a
second guard. A cutoff remains incomplete and completed journal entries are
recovered after forced shutdown. Cleanup is attempted even when a case fails.

Resource data is diagnostic. Working-set samples refer to the Popen launch
process, which may be the small Windows venv redirector. Final harness versions
also record owned-job committed-memory peaks including descendants. These
measurements have no invented leak threshold and do not prove absence of leaks.
Browser starts, render counts, cache reuse and final process ownership checks
provide additional bounded lifecycle evidence.

## Evidence and proof limits

Each run has run.json, summary.json, REPORT.md and per-mode config/results,
event journal, process output, inputs, failure bundles and optional minimized
replays. Test stores and produced artifacts remain under the run folder.
Historical regression helpers retain their existing temporary validation roots;
their original source/example stores are not mutated.

Product module hashes are recorded before/after. The harness does not fix a
product failure, loosen a failed expectation or change the baseline. Harness
implementation faults may be corrected with their failed run retained. New
product fixes require a separately scoped proposal and approval.

The sequential reference shares some validation/preparation code with the
reducer, so agreement is not independent proof of every semantic rule. Fixed
goldens and metamorphic cases add different checks. Matching one reviewed PNG
on a matching backend is not Word-layout certification. Bounded workloads are
not a broad security audit, all-document compatibility claim or hardware soak.
See HARNESS_VALIDATION.md and HARNESS_FINDINGS.md for actual outcomes.
