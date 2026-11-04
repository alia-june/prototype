# Changelog

## 0.5.0 — Complete chat consolidation

- Preserved all historical ZIP artifacts available from the current chat.
- Added transparent lineage documentation for unavailable previously described v0.3/v0.4 binaries.
- Consolidated described hardening into a new verified runtime implementation.
- Added defensive JSON load classification and nested-type validation.
- Added bounded objective, persistence, and history sizes.
- Added paired state/register transaction journaling with SHA-256 verification.
- Added recovery for valid interrupted transactions and fail-closed behavior for invalid journals.
- Added mutation lock with timeout and stale-lock recovery.
- Added symlink refusal for protected runtime paths.
- Added explicit transition relation and bounded transition history.
- Added 50-test deterministic hardening suite.
- Expanded loose/fuzzy harness to 206 deterministic probes.
- Added complete visible-chat transcript, chat summary, and technical summary.

## 0.2.0 — Actualization (historical archive)

- Added a local runtime, persistent state/register files, validation command, provenance conventions, state schema, change-control metadata, and explicit requested-vs-completed distinction.

## Initial reference artifact

- Established four-layer architecture, five registers, core pipeline, role abstractions, verification gate, and capability boundary.
