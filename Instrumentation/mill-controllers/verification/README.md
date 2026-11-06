# Mill batch verification controller

This is a deterministic, local controller for one unchanged Mill operation:
`Test-MillBatch.ps1 -BatchPath <directory>`.

It is not a general orchestrator, a replacement for Mill Factory, a gate or
decision authority, a hypervisor, or a bare-metal shell. It makes no LLM call.

## What it controls

The controller accepts a complete request and a local authority assertion. It
checks the requested path and current identities of the two source scripts the
operation uses, obtains a controller-side exclusive verification lease, invokes
the unchanged validator, retains bounded process evidence, and writes a receipt.

The source operation itself checks a batch's required structure, metadata,
ledgers, registries, decision logic, and manifest integrity. It calls
`Update-MillManifest.ps1` without its `-Write` switch. This controller does not
call `-Write`, reseal a manifest, repair a batch, set a gate, set a decision, or
promote a batch.

## Invocation

```powershell
python -B .\controller.py `
  --tool-root ..\source-lf\mill-factory `
  --state-root .\state `
  --powershell pwsh `
  .\request.json .\authority.json
```

The request requires `request_id` and `batch_path`. The authority assertion must
include the exact digest of the complete request, the current two-file Mill
source identity, and one or more allowed batch roots.

An accepted assertion is a local operating boundary only. It is not user
approval, cryptographic authorization, authority to promote, or proof that a
batch's claims are true.

## Results and limits

Exit code `0` means the request was admitted and the Mill validator reported
`PASS`. Exit code `2` means the controller retained a refused, failed, or
uncertain receipt. Exit code `3` means it could not establish a required source
or input boundary.

The receipt keeps these separate facts:

- admission by this controller;
- child-process launch, exit, timeout, and bounded output;
- Mill's own structured validation result, if one was emitted;
- retained controller state;
- the local assertion boundary; and
- the next permitted action.

A `PASS` still establishes only the underlying Mill structural and
internal-consistency result at the observed time. It does not prove semantics,
external runtime behavior, ongoing integrity, user approval, or promotion
authority. Direct calls to Mill that bypass the controller are outside its
protection.

## State

The controller uses Python's standard-library SQLite interface for request,
receipt, and lease records. It uses no third-party Python package. PowerShell is
used solely to invoke the unchanged declared Mill validator. During local SQLite
initialization, it retries only transient `database is locked` errors with a
bounded increasing delay; other state errors remain retained failures.

The lease serializes controller-mediated verification of one batch path. It
cannot block an external process that modifies a batch directly while the
validator is reading it; such interference can only be detected to the extent
that the existing validator observes it.
