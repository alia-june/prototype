# Durable Workspace Development Guidance

Treat durability as a control-plane concern, not a substitute for source control.

Recommended separation:

```text
project/
├── source/ or normal project files     # Git or equivalent remains authoritative for code history
├── workspace-control/                  # STATE/TODO/LOG/ERROR_LOG/DECISIONS
└── .durable-workspace/                 # DWSK runtime database + snapshots
```

Persist machine state and recovery-critical metadata through DWSK. Keep human-readable control files for inspection and handoff. When a control file becomes operationally authoritative, record its content hash or normalized representation in DWSK rather than assuming filesystem presence implies validity.

Checkpoint before structural migrations, dependency upgrades, schema changes, and handoff. Verify immediately after checkpoint creation. Recover into a new directory; never overwrite the only damaged copy.

For the initial Lattice arrangement, keep durable state and snapshots per
project and designate one writer for each project. The shared context service
supplies profile and ethic sources; it is not imported by the readiness checks.
An adapter, operational record schema, and live source import remain separately
reviewed work. Keep original artifact bytes outside canonical normalization and
link them through source locations and hashes where exact byte identity matters.

Review the Windows qualification in DURABILITY_CONTRACT.md before assigning a
durability claim. A checkpoint exception can occur after a complete generation
has been published but before `LATEST` promotion; preserve the generation and
inspect evidence rather than assuming every exception means no files changed.
