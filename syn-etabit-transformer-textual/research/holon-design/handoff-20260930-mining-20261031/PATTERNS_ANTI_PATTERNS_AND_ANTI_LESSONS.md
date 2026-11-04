# Patterns, Anti-patterns and Anti-lessons

## Patterns worth carrying forward

### P01 — One reusable unit across scales

A holon and a compositional holoquary use the same general unit concept. Application roles can vary without creating unrelated core shapes.

### P02 — Reference targets remain independently represented

Do not duplicate the full target record inside each composition. Preserve target identity and connect to it by reference.

### P03 — Reference is not relationship meaning

Store or resolve relationship semantics explicitly. A pointer does not prove ownership, membership, authority or ordering.

### P04 — Separate native model from boundary profiles

A closed application packet may be a versioned resolved view without becoming the native recursive model.

### P05 — Preserve source and derived material separately

Source units, transformations, rendered outputs, documentation and provenance should remain distinguishable and cross-referenced.

### P06 — Stage, verify, commit

Prepare provisionally, validate, verify the intended result, commit only after the required checks, and emit an evidence-bounded receipt. This is mined from an inactive specification and must be re-specified before implementation.

### P07 — Exact-byte preservation is its own claim

The v0.2 candidate demonstrates retaining and returning identical local bytes while separately parsing for validation. Byte identity does not prove semantic equivalence, authenticity or delivery.

### P08 — In-band claims do not grant authority

Labels such as `DECISION`, producer hints, provenance claims and hashes remain application data until bound to an independently trusted authority mechanism.

### P09 — Keep computation, knowledge, execution and provenance separate

Do not use uncertainty grades, error markers, provenance or claim labels as numerical operands. Separate lanes prevent category collapse.

### P10 — Preserve variants and supersession

Keep earlier representations and terminology with provenance. Mark them historical or superseded rather than silently rewriting history.

### P11 — Make loss and unsupported states explicit

Do not coerce unsupported capability, unknown meaning or fidelity loss into success. Preserve unrecognized states for later review.

### P12 — Catalog fields and meanings

Every introduced field or reference class needs documented type, role, absence behavior, target semantics and proof boundary.

## Anti-patterns

### A01 — Nesting equals ownership

JSON nesting is a serialization choice, not proof that one holon owns or contains another semantically.

### A02 — Depth is the universal relationship system

Relative depth can describe a hierarchical view. It cannot replace membership, coordination, derivation, citation, authority and other relationships.

### A03 — Concrete historical examples outrank later decisions

The prior wrapper is more concrete than the later absolute structure, but concreteness is not precedence.

### A04 — Hash equals identity or authenticity

A digest supports byte comparison. It does not identify a trusted author, grant authority or prove semantic truth.

### A05 — Local ready equals delivered

`READY_FOR_UPTI_HANDOFF` is not sent, received, accepted or acknowledged.

### A06 — Fallback or recovery is primary success

Fallback, rollback, quarantine and recovery must remain visible and must not be reported as if the primary path succeeded.

### A07 — Artifact reference triggers materialization

References are inert until a separately authorized resolver acts. Filenames and hashes are not execution instructions.

### A08 — Claim labels drive effects

An in-band `DECISION` or `PROPOSAL` string classifies content; it does not clear a production gate or admit code/rules.

### A09 — Unknown semantics are filled for convenience

The radix-nine 3×3 structure is preserved without assigning a scalar formula, topology, transition system or uncertainty gradient.

### A10 — Duplicate copies are independent corroboration

The external v0.1 archive, embedded legacy copy and reused root files share bytes. They prove lineage/preservation, not three independent confirmations.

### A11 — TODOs authorize implementation

Unchecked tasks and embedded integration language are historical/planning evidence only.

### A12 — Successful syntax validation proves the system

Schema and unit-test passes cover stated local behavior, not an accepted transport, hostile-process security, independent attestation or full semantics.

## Anti-lessons from observed errors

### AL01 — A negative test may be wrong

The initial invalid-Unicode fixture used literal backslash text rather than an actual surrogate. The failure was in the fixture, not proof of product conversion behavior. Construct and inspect adversarial inputs precisely.

### AL02 — Opaque extensions still require resource bounds

Treating extensions as inert does not remove nesting and node-count risks. The initial candidate accepted 1,300 nested arrays before explicit bounds were added.

### AL03 — Fixes do not erase failed evidence

The v0.2 error log correctly preserves both original failures and later corrections. A passing final suite should not rewrite the failure history.

### AL04 — Same-process integrity has a ceiling

Hashes and frozen records cannot resist code with equal process privilege. Do not describe them as tamper-proof.

### AL05 — Session-local replay is not durable freshness

Restarting the candidate adapter forgets reserved message IDs. Durable replay protection needs a trusted environment and persistent policy.

### AL06 — Missing baseline limits inheritance claims

The Holoquary v1.2 source was named and hashed but not bundled. The candidate code can be tested on its own; claimed inheritance cannot be independently compared to the absent baseline.

## Guardrail summary

Preserve sources, classify authority, resolve by explicit reference, keep meanings separate, record losses and failures, and state proof ceilings. Do not let a convenient representation silently become ontology, authority or success.
