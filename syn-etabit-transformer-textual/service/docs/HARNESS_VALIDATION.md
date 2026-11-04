# Harness implementation and validation

Date: 2026-10-29. Harness: docstream.harness/1. Product: docstream-cpu 0.2.0.dev4.

## Delivery and acceptance distinction

The user approved the concrete rigid/fuzzy/torture proposal. The maintained
harness, fixtures, replay, journals, self-tests and bounded initial execution
are delivered. The product's combined outcome is **FAILED**, with three open
finding groups. Harness delivery does not turn a failed product run into an
acceptance result. No product source module changed.

The main final evidence is
`.docstream/harness-runs/final-validation/REPORT.md` and summary.json. All three
modes use seed 20261029. Exact timing, size, process ownership and memory metrics
are stored in that summary. The final run took 171.594 seconds, counted 1,907
torture requests and 24 renderer submissions, and retained 42,881,662 bytes
before final summary/manifest additions. All 624 case inputs were saved before
execution and their hashes are verified by delivery evidence. No mode is
incomplete. The earlier complete run `approved-verified`
recorded 155.407 seconds, 24 renderer submissions and 1,907 torture service calls;
it is retained as development evidence rather than substituted for the final run.

| Mode | Result | Passed | Failed | Coverage |
| --- | --- | ---: | ---: | --- |
| Rigid | PASS | 119 | 0 | Existing 117 regressions, reviewed golden and complete workflow |
| Loose fuzzy | FAIL | 476 | 24 | All 500 generated cases completed |
| Torture | PASS | 5 scenarios | 0 | Boundaries, storage, 20 crashes, four clients and render recovery |

The preserved prior CPU/model tests also include their original 420 generated
cases and 80 M4 rich-model cases. Those are inside the old suite and are not
misreported as new harness cases. The new fuzzy run adds 500 independently
recorded case inputs. Rigid case IDs, outcome details and failures remain
inspectable rather than reduced to one aggregate green status.

## Harness self-verification

Nineteen harness self-tests pass. They check deterministic generation, explicit
equivalence, closed replay families/test IDs, the six preserved baseline aliases,
input retention for passed/failed cases, malformed Unicode retained as escaped
JSON data, replay size limits, bounded shrinking, owned child cleanup, budget
counters, real supervisor timeout cleanup, interrupted-journal recovery, failure
precedence under interruption, mode-aware replay and configuration rejection.
Actual output is in harness-self-test-final.txt.

The final small eight-case smoke run passes and stores inputs before execution.
Three separate replay runs reproduce HF-01, HF-02 and HF-03, each with exit 1.
The timeout self-test returns incomplete/exit 2 and confirms that its owned
process has stopped. Invalid configuration returns exit 3. These expected
negative outcomes test the harness; they are not hidden as product successes.

## Observed torture behavior

- 255 and 256 operations are accepted; 257 is rejected. ASCII and multibyte
  source byte boundaries around 1 MiB behave as expected without partial heads.
- Five injected ENOSPC phases preserve the expected transaction boundary and
  retry behavior. Permission injection rolls back; a real SQLite writer lock
  produces a bounded failure and the next request succeeds after release.
- Twenty exact owned actor processes are terminated across four transaction
  phases. Restart finds interrupted or completed receipts as appropriate;
  retries yield one document, valid SQLite integrity and valid foreign keys.
- Four official MCP clients execute the planned concurrent workload. Reads,
  duplicate receipts, empty commits, plans, exports and invalid scalar types
  are checked. A shared-head contest has exactly one winner and three stale
  conflicts. All test listeners are closed.
- Renderer recovery uses six actual submissions: owned worker replacement,
  damaged artifact detection/repair, failed publication without a head change,
  successful new-request recovery and profile invalidation. Twenty repeated
  previews hit the cache without additional renders. Worker starts are two.

These are bounded local scenarios. ENOSPC/EACCES are injected, not a real full
disk or a broad permission reconfiguration. Termination uses the created process
handle, not a global process-name search. A renderer is terminated between jobs;
this run does not prove recovery from every possible mid-layout failure.

## Finding groups

HF-01: five DOCX carriage-return conversions differ at the text-codepoint level
without a loss diagnostic; an explicit normalization/fidelity policy is needed.
HF-02: ten NUL-bearing DOCX exports fail with an unclassified adapter exception
and generic service INTERNAL_ERROR. HF-03: nine malformed-surrogate dictionary
requests escape typed validation as UnicodeEncodeError. See HARNESS_FINDINGS.md
for exact boundaries, public-service confirmation, replay files and limits on
what was established.

All 500 fuzzy outcomes remain recorded. Twenty detailed failure bundles are
retained in addition to every original case input; shrinking is bounded and the
three groups have individually reproduced replay files. The remaining failures
can also be replayed directly from their saved input files. Assertions were
not weakened and product code was not repaired under this approval.

## Retained harness development failures

The first self-test run miscounted the six replay families as seven; corrected
to match the eight generation categories with three batch categories. The
initial combined run rejected the baseline module's alias and raced a removed
SQLite journal in byte accounting. Both were harness faults. Their initial
logs/run are retained, and the complete/final runs use the corrections.

The earlier complete run initially kept seeds/hashes plus detailed failed cases.
Input retention was strengthened to save every input before execution. For that
earlier run, all 624 inputs were regenerated and matched against their original
hashes; recovery provenance is explicit and original journals/results stay
unchanged. The final run stores inputs directly. Shrinkers never rewrite them.

Supplementary service confirmation first used a Windows reserved device name
for a helper directory; that helper attempt is retained and the verified helper
uses a safe prefix. No corresponding product claim is based on that helper
setup failure.

The initial memory field sampled the venv launcher, not the underlying Python
process tree. Final reporting labels that sample correctly and additionally
records owned-job committed-memory peaks. No leak absence or hardware throughput
claim is derived from these samples. The output guard is sampled at 250 ms and
is not an OS filesystem quota. Final summary creation/metadata add small amounts
after the worker's sampled byte count; final retained size is recorded separately
in HARNESS_DELIVERY.json.

## Preservation and remaining work

All ordinary product module hashes match before/after. The original ZIP and 14
baseline files are rechecked by delivery evidence. Existing stores and the M4
reviewed baseline are preserved; test stores live in the approved run roots or
legacy helpers' temporary validation directories. The new harness baseline is
read-only during tests. No new dependencies, production service, startup entry,
MCP registration, agent-control configuration, GPU execution or bypass feature
was added. Test ownership is released and workers/listeners are stopped.

The next corrective scope is separate: classify invalid Unicode/OOXML text
cleanly and settle CR/LF conversion policy before modifying that comparator or
adapter. Release/installation, measurement/acceleration and final agentic-control
integration remain subsequent work. The harness is a reusable service-development
tool; it is not the final agentic-control integration.
