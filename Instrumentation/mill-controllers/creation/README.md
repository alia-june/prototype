# Mill single-tool controller

This is a deterministic controller for the unchanged `New-MillBatch.ps1` interface. It is not a general orchestrator, a replacement Mill factory, a hypervisor or a bare-metal shell. It makes no LLM call.

The controller accepts a bound request and locally supplied authority assertion. It applies declared input rules, holds a SQLite-backed destination lease, invokes the existing tool, retains raw process records, runs the existing structural validator after a reported creation, and emits a separate-field receipt. It cannot grant authority, authorize promotion, retry, delete a partial batch, or protect against direct writes that bypass the controller.

The Python standard library is the only Python dependency. PowerShell is used only to invoke the unchanged Mill scripts. A later approved scope may compile or package this controller; compilation is not required for deterministic ownership of the operation.

## Invocation

```powershell
python -B .\controller.py `
  --tool-root ..\source-lf\mill-factory `
  --state-root .\state `
  --powershell pwsh `
  .\request.json .\authority.json
```

The request requires `request_id`, `slug`, `title`, `scope`, `date`, and `workspace_root`; `output_root` and `owner` are optional. The authority assertion must bind the complete request digest, the controller's current tool identity digest, and one or more allowed output roots. It is an assertion supplied by a human or calling harness, not a substitute for actual user approval.

An exit code of `0` means the request was permitted and structural verification passed. Exit code `2` means the controller retained a non-success receipt. Exit code `3` means it could not establish the source/request boundary.
