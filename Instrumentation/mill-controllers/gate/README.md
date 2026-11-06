# Mill gate-recording controller

This is a narrow, deterministic controller for the existing Mill
`Set-MillGate.ps1` interface.  It is a workload-side control surface, not an
orchestrator, replacement factory, or a claim that the Mill factory has become
lightweight by itself.

It accepts one gate-recording request only after a separate authority object
binds the request digest, the identity digest of `Set-MillGate.ps1`,
`Update-MillManifest.ps1`, and `Test-MillBatch.ps1`, an allowed batch root, and
(for a non-pending result) the digest of an already-existing evidence file.
It then:

1. refuses malformed, out-of-root, mismatched, duplicate, or leased requests;
2. records a durable request receipt before calling the unchanged writer;
3. invokes the unchanged `Set-MillGate.ps1` once;
4. observes the batch metadata, gate ledger, and manifest before and after;
5. runs the unchanged `Test-MillBatch.ps1`; and
6. retains a receipt with the observation and the next permitted human action.

The controller does **not** grant authority.  Its authority JSON is an input
assertion that must be supplied by the workload owner.  A successful receipt
means only that this bounded invocation reported a recorded gate and the
unchanged structural checker returned `PASS`; it does not prove the truth of
the evidence, semantic correctness, runtime behavior, acceptance, or
promotion.

## Minimal request and authority

```json
{
  "request_id": "gate-001",
  "batch_path": "C:/approved-run/batch",
  "gate": "static",
  "result": "PASS",
  "evidence_path": "evidence/static/result.txt",
  "reviewer": "named-reviewer",
  "notes": "bounded gate record"
}
```

```json
{
  "request_digest": "sha256 of canonical request JSON",
  "tool_identity_sha256": "controller-observed source identity digest",
  "allowed_batch_roots": ["C:/approved-run"],
  "evidence_sha256": "sha256 of evidence/static/result.txt"
}
```

Run it with an existing Python interpreter and existing PowerShell launcher:

```text
python controller.py --tool-root <unchanged-mill-factory> --state-root <new-task-state> request.json authority.json
```

State, receipts, SQLite lease records, and copied workload batches belong in a
user-approved run location.  Do not place controller state inside the protected
Mill source trees.  A failed or uncertain invocation is retained as evidence;
recovery or a repeated request needs fresh user authority.

## Current boundary

The approved implementation scope covers basic validation only.  It does not
cover stress or fuzzy hardening, an LLM comparison, use of `Set-MillDecision`,
promotion, source changes, dependency changes, or a generalized orchestration
layer.
