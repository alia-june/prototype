# Reference-Occurrence Pilot Contract

Contract ID: `strmdocx:reference-occurrence-pilot:0.1`  
Fixture format: `strmdocx-reference-occurrence/0.1-pilot`  
Status: bounded, fixture-specific research contract.

The normative machine-readable companion is `reference_occurrence_contract.json`. This document explains its intent; it does not broaden the machine contract.

## Record families

| Family | Required fields | Purpose |
| --- | --- | --- |
| Target | `id`, `kind`, `role`, `payload`, `payload_sha256` | Independently represents an immutable text block or the transformation description. |
| Relationship | `id`, `kind`, `meaning`, `operation_ref`, `input_ref`, `result_ref` | Gives explicit meaning to the three participating target references. |
| Metadata | `id`, `kind`, `scope`, `provenance` | Independently represents occurrence/transformation context. |
| Occurrence | `id`, `kind`, `target_ref`, `relationship_ref`, `metadata_ref` | Binds one target participation to relationship and metadata references. |
| View | `id`, `kind`, `purpose`, `order_semantics`, `occurrence_refs` | Supplies one inspection order over occurrence references. |

Unknown root or record fields are rejected. The allowed kinds are exact; a kind is not inferred from its collection or identifier.

## Reference rules

- `target_ref`, `operation_ref`, `input_ref`, and `result_ref` resolve to target records.
- `relationship_ref` resolves to a relationship record.
- `metadata_ref` and transformation `scope_ref` resolve to metadata records.
- `occurrence_refs` resolve to occurrence records.
- An occurrence field must be a scalar reference string. Embedded objects or arrays are invalid.
- A view may reuse an occurrence already used by another view.
- Within this fixture profile, each view uses the same occurrence set exactly once. Only order changes.

## Payload and digest rule

Target payloads are JSON objects. Their digest is SHA-256 over UTF-8 bytes of the payload serialized as JSON with:

- keys sorted lexicographically;
- no insignificant whitespace;
- Unicode preserved rather than ASCII-escaped; and
- standard JSON values only.

This digest establishes deterministic payload-byte identity under the stated canonicalization. It does not establish authorship, semantic truth, authority, or trusted time.

For this fixture:

- immutable text blocks have exactly `encoding` and `text` payload fields;
- the encoding is exactly `utf-8`;
- the transformation has exactly `operation`, `argument`, `input_ref`, `result_ref`, and `scope_ref`;
- the operation is exactly `append_text`; and
- applying the transformation argument to B0 must yield B1 exactly.

## Order and inspection

`view:V0` is chronological: `O0`, `O1`, `O2`. `view:V1` is reverse inspection: `O2`, `O1`, `O0`.

Order is local to the named view. Neither order creates ownership. Reverse inspection is not rollback and does not imply inverse execution.

## Safety and boundedness

The machine contract defines resource ceilings for the harness: one MiB input documents, 4,096 records per collection, 128 views, 4,096 occurrence references per view, 8,192 characters per string, and at most 128 reported validation errors. These are harness bounds, not adopted system-wide limits.

The strict loader rejects invalid UTF-8, malformed JSON, duplicate JSON properties, and `NaN`/`Infinity` constants. The semantic validator rejects JSON `null` anywhere, booleans masquerading as integers, unresolved or wrong-family references, duplicate identifiers, malformed identifiers, digest mismatch, inconsistent transformation links, profile-order changes, and additional fields.

## Proof boundary

Passing this contract proves only that a document meets this small pilot’s checked representation and fixture invariants in the executed environment. It does not validate arbitrary transformation semantics, general graph safety, service behavior, storage durability, security, rendering fidelity, or the larger Holon architecture.
