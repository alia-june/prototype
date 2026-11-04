# Docstream local agent service — M2

Date: 2026-10-29. Package: docstream-cpu 0.2.0.dev2.

## Delivered behavior

One foreground loopback process owns a SQLite store and the CPU model. Agents
submit structured requests through MCP; a thin CLI uses that same interface.
Stored data includes original source bytes, semantic payloads, stream lineage,
transformations, plans, candidates, heads, commits, request receipts, jobs and events.

This stage constructs and commits semantic stream results. It explicitly reports
visual output as not_rendered/unavailable. Browser rendering, GPU execution,
selective bypass, startup registration and Codex connection configuration are absent.

## Running the installed service

The installed command is:

`<source-workspace>\service\.venv\Scripts\docstream-local.exe`

Explicit foreground startup from the service directory:

```powershell
$env:DOCSTREAM_TOKEN = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
.\.venv\Scripts\docstream-local.exe serve --root ..\.docstream --port 8765
```

The process binds 127.0.0.1 only. Its MCP endpoint is `/mcp`; port 0 chooses a
temporary port and prints the selected endpoint. Startup output is configuration
information, not a readiness assertion: a client must establish the connection.
Keep the token private and provide the same value to the calling client's
environment. The service never prints it or writes it to project configuration.
Stop a foreground service with Ctrl+C. No automatic-start task is installed.

From a client shell configured with the same DOCSTREAM_TOKEN:

```powershell
.\.venv\Scripts\docstream-local.exe call list --url http://127.0.0.1:8765/mcp
.\.venv\Scripts\docstream-local.exe call docstream_status --url http://127.0.0.1:8765/mcp
.\.venv\Scripts\docstream-local.exe call docstream_ingest --input examples\ingest-request.json
```

`--input -` reads a JSON object from stdin. The CLI sends MCP calls and does not
open its own mutable database. No global Codex configuration is changed by these
commands. The SDK client is tested; an actual Codex host connection is deferred.

## Tools

Input schemas are declared from strict request models. JSON arrays in nested CPU
values are explicitly converted through the existing JSON boundary; scalar
coercions remain rejected. Tools have structured object output schemas and a text
representation. Domain errors are structured in `ok:false` replies; SDK argument
errors remain MCP tool errors. MCP_SCHEMAS.json records the application models.

| Tool | Input | Result |
| --- | --- | --- |
| docstream_status | none | Versions, limits, storage readiness and actual capabilities. |
| docstream_ingest | request_key, exactly one of text/source_base64/snapshot, optional title | Durable source document, root stream, digests and block index. |
| docstream_transform | request_key, base_stream_id, batch, mode | A preserved candidate, plan summary, logical outputs and optional semantic commit. |
| docstream_commit | request_key, candidate_id | Guarded semantic commit of an existing candidate. |
| docstream_inspect | target_id, section, optional block_id/offset/limit | Paginated head/stream/history/plan/source/content views. |
| docstream_job | job_id | Durable state and receipt; interrupted requests are marked retryable. |

For MCP calls, application input is under the tool's `request` argument, except
status (no arguments) and job (`job_id` directly). CLI input files omit that wrapper.

Transform modes are plan, materialize and commit. Plan catalogs every logical
output without moving the head. Materialize constructs the final semantic payload.
Commit materializes and advances the head under the existing base/revision guard.
No mode claims to render visually. Commit of a staged candidate uses its own
request key through docstream_commit.

Inspect sections:

- head: target a document ID for its current stream and revision.
- stream: target a stream ID for provenance and materialization status.
- history: target a stream ID; offset/limit select lineage records.
- plan: target a candidate ID; offset/limit select reduction explanations.
- source: target a document ID for original byte digest, encoding and size.
- content: target a stream ID; without block_id return a page of block metadata;
  with block_id return a page of text in Unicode-codepoint units. Inspection may
  persist a materialized payload but never advances a head.

## Durable requests and failures

Choose a unique request_key for each intended mutation. The identity is scoped by
the store, authenticated local principal and operation family. All callers using
this one token share that local principal and must avoid key collisions. Reuse
the same key and identical payload when a response is lost. Do not change mode,
base, content or operations under an existing key.

Request reservation is durable before work begins. Successful model changes,
head updates, job state, events and receipt commit together. A retry after that
commit returns the stored receipt. An interrupted pre-commit request is recovered
as interrupted and can be retried using the original request. It is not silently
reported completed or automatically run at startup.

Expected validation failures are terminal receipts for that key. Corrected work
uses a new key. A changed payload under an existing key receives
IDEMPOTENCY_CONFLICT. Stale commits cannot overwrite newer heads. A candidate
constructed by an inline stale commit is retained with a conflict receipt for
inspection, as are separately staged candidates.

Failures before final commit roll back model writes and reload the committed
model. If reloading fails, storage readiness becomes false and further mutations
are refused. An unexpected failure after commit has an unknown outcome at the
transport boundary; inspect/retry the identical request to obtain its receipt.
The adapter does not claim an unobserved commit was rolled back.

Jobs are a durable ledger for synchronous requests in M2. There is no background
worker queue or active cancellation interface. Client disconnection can leave
work completing; idempotent retries resolve the outcome.

## Storage and execution boundaries

Schema version 1 uses SQLite rollback journaling, synchronous FULL, foreign keys,
short atomic transactions and one OS-held owner lock per managed root. A second
owner is rejected. Unknown schema versions, snapshot/source digest mismatches and
plans incompatible with the pinned CPU semantics fail startup.

Unchanged records avoid redundant SQL writes, although small in-memory catalog
maps are scanned when flushing. Existing plans are checked against current CPU
semantics at startup. This design is unbenchmarked; a large-corpus scalability
claim is not made.

The server accepts no per-request filesystem path, executable, Python code, shell,
SQL or converter arguments. Store roots are startup configuration; linked/reparse
roots and managed database/lock files are rejected. This is a local-account trust
model, not an OS sandbox against the account owner or a compromised process.

HTTP requires a bearer token of at least 32 characters, loopback Host, valid
same-origin supplied Origin, and bounded bodies. Missing Origin is allowed for
native clients and does not replace authentication. Bounds include 2 MiB HTTP
body, 1 MiB source/result, 256 operations, 128 KiB application replies and 100-item
inspection pages. Chunked bodies are bounded too. Oversized uploads already in
flight can appear as a TCP reset on Windows; early declared-length rejection is
tested as HTTP 413. These bounds are not a benchmark or hard CPU preemption.

The service has no browser and cannot execute active content from a document.
Actual renderer timeouts, artifact publication/cache and export fidelity remain
later stages. No running listener is retained after the approved tests.
