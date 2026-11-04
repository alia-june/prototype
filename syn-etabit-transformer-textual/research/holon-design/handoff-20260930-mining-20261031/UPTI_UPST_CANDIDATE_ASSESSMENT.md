# UPTI/UPST Candidate Assessment

## Assessment

The supplied v0.1 and v0.2 packages are useful bounded implementation studies, not governing Holon architecture and not accepted transport protocols.

### v0.1 strengths

- Small explicit envelope and version.
- Duplicate-key, malformed JSON, NaN/Infinity, invalid UTF-8 and size rejection.
- Strict body-kind dispatch.
- Separation of numerical data, knowledge possibilities, execution and provenance.
- Exact treatment of numerical zero versus absence and logical UNKNOWN versus uncertainty grade.
- Inert namespaced extensions.
- Inert artifact reference with basename/path-traversal restriction.
- Explicit authority boundary for hints, claims, IDs and provenance.
- Unresolved radix-nine meaning remains unresolved.

### v0.1 limitations

- Assistant-generated candidate fields, not accepted canon.
- Native nested JSON body, not reference-native storage.
- Explicitly nonrecursive.
- Native JSON null in declared ABSENT fields conflicts with the later general sentinel direction.
- No accepted transport, authenticated sender, receiver, delivery or attachment acquisition.
- Canonical JSON encoding is local convenience, not UPTI wire conformance.
- The named Holoquary v1.2 source baseline is not bundled.

### v0.2 strengths

- Preserves v0.1 bytes and clearly labels lineage.
- Returns the exact input bytes after local verification instead of silently canonicalizing them.
- Explicit state distinction between STAGED, VERIFIED, READY and REJECTED.
- Mutation detection before and after verification.
- Bounded local store, nesting and node counts.
- Unpaired-surrogate rejection.
- Duplicate message ID reservation within a session.
- Read-only local receipt with explicit negative remote claims.
- Preserves assistant errors and corrected tests.

### v0.2 limitations

- `ReceiverProfile` is caller-supplied assumption, not negotiation.
- Replay protection disappears on process restart.
- Same-process mutation resistance is not a security boundary.
- No network or receiver call.
- No authenticated identity, authorization, signature, encryption or external receipt.
- `mark_ready` is only a candidate handoff state.
- API names and receipt fields are fabricated adapter proposals, not accepted UPTI methods.

## Source status versus observed evidence

| Claim | Current treatment |
| --- | --- |
| v0.1 10 tests | Independently rerun: 10/10 pass |
| v0.2 34 tests | Independently rerun: 34/34 pass |
| Nested UPTI-SF 25 integration tests | Historical claim only; runtime/test corpus absent |
| Nested fuzzy/torture/crash tests | Historical claims only |
| UPTI transport | Not implemented |
| Transport conformance | Not claimed |
| Exact local bytes returned | Supported by code and current tests |
| Authenticated sender/delivery | Explicitly false/not implemented |

## Useful transferrable lessons

1. Keep claim classification separate from authority.
2. Keep data, uncertainty/knowledge, execution and provenance separate.
3. Reject malformed input before semantic handling.
4. Preserve raw bytes where byte fidelity is required; do not call parsing a transformation.
5. Make local/remote and ready/delivered distinctions explicit.
6. Preserve failure and test-fixture errors.
7. Bound opaque extension structures.
8. Do not materialize artifact references automatically.
9. Treat replay, freshness and capability as environment-specific trust problems.
10. Record inactive specifications without activating them.

## What not to lift wholesale

- The nine top-level packet keys.
- Python API names or dataclasses.
- 64 KiB, depth 64, node 8,192 or store 64 as universal limits.
- Native-null encoding.
- The three supported kinds.
- Holoquary numerical domains as Docstream/Strmdocx primitives.
- U1/U2/U3 or radix-nine semantics.
- UPST ownership statements or sisterhood role claims.
- The inactive UPTI-SF envelope/lifecycle as a dependency.

## Integration determination

Do not integrate either package into Strmdocx under the current mining clearance. If a future boundary service is designed, mine the lessons into new requirements and implement from the accepted native reference/relationship model. The candidate code can be consulted as evidence of pitfalls and tested local behavior, not copied as architectural authority.
