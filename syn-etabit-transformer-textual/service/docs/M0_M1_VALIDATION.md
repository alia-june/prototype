# M0–M1 implementation and validation

Date: 2026-10-29 (America/New_York).

## Authorization and delivered scope

The user replied yes to the concrete CPU implementation proposal. Scope: preserve
and extract v0.1.0 under service, implement CPU streams/operations/evaluator/reducer,
create bounded conformance tests, prepare a local environment and retain evidence.
Database creation, MCP integration, service startup, browser installation/rendering,
selective bypass, GPU work and release remain outside this clearance.

M0–M1 is complete for that approved slice. Broader M0 items in the earlier plan
(real MCP-host and renderer compatibility) were excluded by the concrete proposal
and remain deferred to M2/M3. This is not a production service release.

## Baseline and lineage

Original: <local-user-home>\Desktop\Inbox\docstream-0.1.0.zip

SHA-256: `4acbdb5ee634ede3067fa2ad7c189afbd051365e6714b72ad03159fd4df8bf72`

All 15 entries were extracted under service/baseline. All 14 regular files were
hashed against their ZIP payload and matched; the explicit directory entry is
present. The original ZIP hash is unchanged. BASELINE_MANIFEST.json records the
per-entry evidence. No original source was rewritten. New implementation uses the
distinct docstream_cpu package namespace.

## Environment and build

- Python 3.12.14, Windows 11, project-local service/.venv.
- The venv inherits site-packages from the bundled runtime at
  <local-user-home>\.cache\codex-runtimes\codex-primary-runtime\dependencies\python.
- Local package docstream-cpu 0.2.0.dev1 installed in editable mode using
  `pip install --no-deps --no-build-isolation -e .`; editable build/install succeeded.
- Core dependencies: Pydantic 2.14.1, pydantic_core 2.50.1, annotated-types 0.8.0,
  typing_extensions 4.16.0 and typing-inspection 0.4.4. requirements-cpu.lock pins
  those observed versions. Baseline tests also use bundled python-docx 1.2.0.
- setuptools 84.1.0 and pip 25.0.1. No global dependency update or renderer install.

This reused environment is not an isolated release/offline reproducibility proof.
No standalone distributable was produced. Exact metadata is in test-results.json.

## Actual validation result

**41 tests passed; zero failures, zero errors.**

- Six original baseline tests executed successfully, including native structural
  DOCX round-trip and root-resolution checks.
- The original HTTP test was explicitly excluded because it starts a service.
  It is not counted as a passed or skipped executed test.
- Thirty-five CPU tests cover fixed behavioral cases plus 420 deterministic
  generated sequences: 300 assignment, 60 structural and 60 invalid sequences.
- Seeds: 20261029, 12345 and 98765. These are bounded correctness cases, not a
  benchmark, exhaustive proof or test of an external GPU/renderer.

test-output.txt contains individual method outcomes. test-results.json records
counts, runtime/package metadata, seeds and actual elapsed time. Runtime duration
is diagnostic and does not establish service latency.

## Important observed behaviors

| Case | Observed result |
| --- | --- |
| Uniform original font A; B, A, C, A | Zero reduced property writes, all requests retained. |
| B then C | Only the necessary final font cell assignment retained. |
| Mixed fonts changed and restored | Original explicit font differences and inheritance preserved; no net font writes. |
| Same effective font with different explicit override structure | Structural style difference retained rather than falsely treated as identical. |
| Disjoint styles | Final cells grouped with RED-04 explanation. |
| Structural/text dependency | Assignment regions fenced; original preconditions checked. |
| Invalid early operation followed by reversal | Original error retained; no optimization hides it. |
| Out-of-order prefix inspection | Correct recorded state materialized; document head unchanged. |
| No-op commit | New stream identity, shared identical payload. |
| Competing candidate | STALE_HEAD preserves existing head and inspectable candidate. |
| Original CRLF/BOM/Unicode | Original bytes/digest retained; semantic content does not silently normalize Unicode/newlines. |
| Removed identity across batches | Catalog rejects reuse along the lineage. |
| Wrong scalar types/extra fields/changed plan | Rejected rather than coerced or executed. |

The separately executed maintained example writes font-example.json. With one
text block it records four logical outputs, eight reference assignment-cell writes,
zero reduced writes, identical semantic digest, distinct result stream and one
stored payload. The unit fixture with two blocks has twelve reference writes;
the difference reflects the number of assignment cells, not contradictory results.

## Limits and proof boundaries

No visual rendering, HTTP/MCP listener, database, browser, GPU or service-lifecycle
test ran. The original DOCX round-trip fixture is generated temporarily and checks
structural/text behavior only; it is not visually verified Word output. This CPU
slice has no format-adapter completeness or performance claim.

Catalog state and same-candidate commit receipts are memory-only. Process restart
loses them. Cross-process ownership, crash recovery, durable idempotency, resource
worker isolation and visual artifact caching remain M2/M3 work. The current parser
boundary is typed batch JSON; text ingestion is literal UTF-8, not Markdown mining.

All results are local validation. They do not constitute independent attestation,
full correctness proof, production hardening, or user adoption of a final release.
