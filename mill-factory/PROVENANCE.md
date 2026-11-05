# Mill Factory Provenance

## Source

This public repository component is adapted from a working research tool on
2026-11-04.

The source tool supplied the batch model, PowerShell commands, templates,
sentinel/reference/glue contracts, manifest behavior, and positive/negative
controls.

## Repository adaptations

The nested repository version:

- replaces the workstation-specific default workspace path with the caller's
  current working directory;
- adds a portable-default-root regression control;
- rewrites the README for standalone repository use;
- adds this provenance record, a validation record, and a project manifest;
- preserves the initial fail-closed promotion and evidence boundaries.

No source archives, private batch contents, user identifiers, absolute
workstation paths, live credentials, or local runtime evidence are included.

## Authority boundary

This component is generated implementation work. Repository inclusion does not
make it accepted project canon, authorize a particular promotion, or validate
an imported artifact. Each created batch retains its own evidence and decision
state.
