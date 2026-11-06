# Provenance and boundary

ES-xOSG-0 is an Instrumentation-layer working example. Its method is informed
by xOSG-0 themes of explicit state, bounded deterministic offload, visible
authority, retained evidence, and fail-closed behavior. It does not alter or
extend the canonical `ES-xOSG-7 → xOSG-0 bare-metal 0 → v0.2 → v0.3 → v0.4 →
Seed` growth spine.

The receipt adapters are derived from the public controller examples under
`Instrumentation/mill-controllers/`:

- creation controller: `receipt_version`, `admission`, `creation_reported`,
  `artifact_verification`, `retained_state`, `authority`, and
  `next_permitted_action`;
- verification controller: `receipt_schema`, `admission`, `process`, nested
  `validator.reported_result`, `retained_state`, `authority`, and
  `next_permitted_action`; and
- gate controller: `receipt_schema`, `admission`, `gate_write_reported`,
  `structural_validation`, `retained_state`, `authority`, and
  `next_permitted_action`.

The fixture files are synthetic public examples of those limited fields. They
are not retained production receipts, authority grants, evidence files, batch
data, or source truth. The output hides unrelated receipt content and returns
only mapped status facts.

SHA-256 values in this package's manifest establish byte identity of named
files, not semantic correctness, authority, acceptance, authenticity, or a
guarantee that a future controller revision preserves the same receipt shape.
