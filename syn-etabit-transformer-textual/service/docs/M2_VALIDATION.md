# M2 durable service validation

Date: 2026-10-29 (America/New_York). Implementation: 0.2.0.dev2.

## Scope and result

The user explicitly approved SQLite persistence, durable receipts/recovery,
loopback MCP, a thin CLI, local dependency installation, and bounded integration
tests whose listeners stop afterward. M2 is complete for that scope.

**66 tests passed, zero failures, zero errors.** This comprises the prior 41
CPU/baseline tests plus 15 persistence/application tests and 10 MCP/CLI/transport
tests. The CPU portion still includes 420 fixed-seed generated sequences.
Actual method results and environment metadata are in m2-test-output.txt and
m2-test-results.json. No service performance benchmark was performed.

## Environment

Python 3.12.14, SQLite 3.53.1, MCP SDK and mcp-types 2.3.0, Uvicorn 0.38.0,
Pydantic 2.14.1, AnyIO 4.15.1, Starlette 1.10.0 and httpx2 2.16.0. Service
dependencies were installed in the project venv, retaining inherited bundled
CPU dependencies. requirements-service.lock records the resolved dependency
closure; it is a version constraint record, not a hash-verified offline wheel set.

The local package was successfully rebuilt/reinstalled in editable mode. No
global Python package update or Codex client configuration change was made.

## Observed persistence behavior

- Original source bytes, snapshots, streams, operations, plans, candidates and
  head revisions survive closing and reopening the store.
- Retrying an identical request after restart returns its stored receipt without
  another document or head advance. Changed payload reuse is rejected.
- A lost response injected after SQL commit replays the successful receipt.
- A failure injected after model writes and SQL flush rolls back both persistent
  changes and in-memory effects. Its failure receipt remains stable on retry.
- Real subprocesses were forcibly exited after reservation, after SQL flush and
  after commit. Restart recovered interrupted pre-commit jobs or replayed the
  committed receipt. Each resulting database passed integrity_check.
- Two callers committing against one base produce one successful head advance
  and one stale-head conflict. Inline conflict candidates remain inspectable.
- Source-size violations create no partial document. Unknown schema/digest state
  is refused. A failed committed-state reload disables further mutations.
- A second owner of the same root is rejected by the OS-held lock.

## Observed MCP and CLI behavior

- Actual loopback Streamable HTTP discovery exposes six tools with structured
  results: status, ingest, transform, commit, inspect and job.
- The real SDK client completes ingest/transform/commit/inspect/job workflows.
  Two network callers cannot silently overwrite one another.
- Legacy protocol-mode discovery passed. This is not a full compatibility matrix
  or a successful connection from the installed Codex UI.
- Typed nested snapshot/batch arrays are accepted; incorrect scalars are rejected.
- Missing/wrong tokens, invalid Host/Origin, oversized declared bodies and
  chunked-body overflow are rejected.
- The thin CLI uses the same endpoint and does not print the bearer token.
- An actual foreground CLI service was stopped and restarted; its network retry
  returned the same durable receipt.
- Graceful fixture shutdown and foreground-process shutdown checks confirm the
  test ports stop accepting connections. No test listener remains running.

## Corrections retained during validation

The first combined run had one failed immediate post-process socket assertion;
that output is retained in m2-initial-combined-run.txt. No matching Docstream
Python process remained on follow-up inspection. The test now allows a bounded
five-second Windows socket teardown interval and still fails if a listener remains.
The final combined run passes that check.

Earlier integration checks exposed bare-dictionary text output and strict tuple
validation at the SDK's decoded-dictionary boundary. The adapter now declares
structured dictionary output and explicitly routes nested JSON containers through
the CPU JSON boundary, preserving scalar strictness. The complete workflow was
then rerun successfully. A test-only SQLite cleanup connection was also closed
explicitly for Windows; it did not change production transaction semantics.

## Delivered files and state

New application modules: storage.py, service.py, mcp_server.py, cli.py and
__main__.py under src/docstream_cpu. The CPU evaluator/reducer semantics are
unchanged. The console command is docstream-local. Contract and request schemas
are in M2_SERVICE_CONTRACT.md and MCP_SCHEMAS.json. Resolved versions are in
requirements-service.lock. M2_IMPLEMENTATION_MANIFEST.json records implementation
and evidence hashes without secrets or the mutable database.

The default managed root is <source-workspace>\.docstream
when selected explicitly with --root. An empty version-1 store is initialized
there and closed; no production documents or credentials are loaded. Tests use
temporary child roots under its validation directory. M2_STORE_INIT.json records
the empty-store check.

## Limits and remaining scope

This is a local semantic service, not a visually complete document pipeline.
Visual rendering, artifact publication/cache, format-adapter completeness, GPU,
selective bypass and actual Codex host registration remain deferred. M2 job
records describe synchronous requests; there is no background execution queue,
active cancellation or hard CPU preemption. Size/concurrency/read limits are
implemented, but hostile-workload containment has not been proven.

Store ownership assumes the local account controls its directory. This is not
an OS sandbox or independent attestation. Large-corpus startup/flush scalability,
standalone deployment, multi-tenant identity, schema upgrades beyond bootstrap
v1, and recovery of a failed filesystem are not validated here.

Historical M1 evidence and the original archive remain preserved. All reported
results are bounded local validation, not blanket production readiness.
