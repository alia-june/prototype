# xOSG-0 Repository Provenance

This repository path is a staged research/prototype workspace.

## Historical source status

The current chat provides exact recoverable source artifacts for:

- the original xOSG-0 bare-metal reference artifact;
- the v0.2.0 actualized runtime artifact;
- the initial 58-case loose/fuzzy test suite and its report.

The previously described v0.3.x/v0.4.0 ZIP binaries are not recoverable from the current conversation file surface. They are therefore **not represented here as recovered historical binaries**.

The front-page v0.4.0 README describes the documented v0.4.0 research/hardening stage. Any v0.4.0 implementation reconstructed from those requirements must be labeled as a reconstruction and must not be confused with an unavailable historical binary.

## Population policy

1. Preserve exact historical files under `history/`.
2. Keep reconstructed or newly hardened implementations outside historical directories.
3. Do not silently rewrite historical source to match later documentation.
4. Record provenance for material changes.
5. Treat this repository path as prototype/staging unless an explicit production release is authorized.

## Available historical trees

- `history/v0.2.0/` — exact source from the recoverable v0.2.0 actualized artifact.
- `history/initial-fuzzy/` — exact initial fuzzy harness and fuzzy report.

This separation allows the repository to develop forward without manufacturing a false release lineage.
