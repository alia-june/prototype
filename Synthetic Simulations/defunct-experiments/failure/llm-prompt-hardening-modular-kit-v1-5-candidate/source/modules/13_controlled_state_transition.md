`[GENERATED-PROMPT]`

## Controlled state transition under uncertainty

This module applies the supplied controlled-state-transition synthesis. Its purpose is to preserve identity, meaning, integrity, authority, recoverability, and evidence while state crosses time, machines, trust boundaries, implementations, or failure domains.

### Operation classification

Do not collapse distinct operations into the word `copy`.

- `copy` produces another representation;
- `transfer` crosses a boundary;
- `synchronization` reconciles evolving states;
- `replication` maintains a current state;
- `snapshot` freezes a point in time;
- `backup` preserves historical recoverability;
- `archive` preserves information long term;
- `migration` moves authoritative operation;
- `recovery` establishes trustworthy operation;
- `rollback` returns to an earlier state;
- `sanitization` makes retired data inaccessible.

State which operation is authorized. Do not claim recovery from copying, replication, snapshotting, or retention alone.

### Transition identity

```text
TRANSITION OPERATION ID: ${TRANSITION_OPERATION_ID}
TRANSITION OBJECT ID: ${TRANSITION_OBJECT_ID}
TRANSITION KIND: ${TRANSITION_KIND}
SOURCE GENERATION: ${SOURCE_GENERATION}
EXPECTED TARGET GENERATION: ${EXPECTED_TARGET_GENERATION}
TRANSITION STATE: ${TRANSITION_STATE}
COMMIT STATUS: ${COMMIT_STATUS}
ROLLBACK STATE: ${ROLLBACK_STATE}
RECOVERY PROOF: ${RECOVERY_PROOF}
INDEPENDENT FAILURE DOMAIN: ${INDEPENDENT_FAILURE_DOMAIN}
```

Do not use a mutable pathname, display name, latest pointer, or conversational reference as the sole identity of a material source generation.

### Required invariants

Before work, classify each invariant as `required`, `not applicable`, or `unknown` and name its verification method:

- representation and completeness;
- object identity and source generation;
- structure and metadata;
- relationships and ordering;
- semantic validity;
- integrity and authenticity;
- actor, authority, and authorization;
- provenance and temporal validity;
- security classification and access restrictions;
- replay safety and idempotency;
- bounded time, size, memory, retries, and recursion;
- reversibility and rollback boundary;
- independent recovery path;
- durable evidence and observability;
- version and schema interpretation.

An unknown material invariant blocks commit. A byte-identical result may still fail metadata, relationship, authority, semantic, temporal, security, or recovery invariants.

### Transaction phases

Use this order for material transitions:

```text
identify -> freeze -> describe -> authorize -> stage -> transfer ->
mechanically verify -> semantically validate -> ready -> conditional commit ->
attest/receipt -> retain predecessor -> test recovery -> eventually retire
```

1. `identify`: bind object and source-generation identity.
2. `freeze`: obtain a stable snapshot, transactional export, or otherwise consistent generation before measuring it.
3. `describe`: create a manifest of content, structure, metadata, dependencies, schema, policy, and digests appropriate to the object.
4. `authorize`: bind actor, authority, target, intended effect, and minimum capability.
5. `stage`: write only to a non-authoritative working copy or new child state.
6. `transfer`: use a bounded, retry-safe operation ID; do not let retry create new meaning.
7. `mechanically verify`: check lengths, counts, digests, manifest integrity, metadata, and signatures when applicable.
8. `semantically validate`: parse, open, check schema and relationships, and exercise representative behavior in isolation when applicable.
9. `ready`: assert that every material invariant passed and the expected prior generation remains current.
10. `conditional commit`: publish atomically or by an explicit compare-and-swap mechanism when available. A recorded expected target is not enforcement.
11. `attest/receipt`: record accepted object, source and target generation, digests, verifier, result, and time.
12. `retain predecessor`: preserve the independently validated prior state through the rollback window.
13. `test recovery`: distinguish possession, identified bytes, and demonstrated restoration.
14. `eventually retire`: sanitize only after retention, rollback, authorization, and validation conditions pass.

Do not delete, overwrite, promote, retire, or sanitize the predecessor early merely because transfer or process execution succeeded.

### Explicit protocol state

Use `OFFER -> ACCEPT -> TRANSFER -> VERIFY -> READY -> COMMIT -> RECEIPT`. Terminal alternatives are `REJECT`, `ABORT`, `EXPIRED`, `CORRUPT`, or `CONFLICT`.

If the sender or actor cannot determine whether commit occurred, mark the state `UNKNOWN` or `CONFLICT`; do not repeat a non-idempotent operation or declare success.

### Verification strength

Keep these claims separate:

```text
POSSESSION: a representation exists.
IDENTIFICATION: the representation's object and generation are verified.
RECOVERABILITY: restoration and semantic operation were successfully tested.
```

A digest supports byte identity. It does not by itself prove application correctness, trusted origin, authorization, recoverability, or absence of inherited compromise.

### Failure domains and time

Copy count is not failure-domain independence. Record storage, administration, credentials, keys, network reachability, and destructive authority for every recovery path. A second copy controlled by the same compromised authority may remain one failure domain.

Recency and trustworthiness are independent. Preserve multiple historical generations under a time-aware retention policy sufficient to reach a known-good state. Do not assume `LATEST` is the correct recovery point.

### Control plane and dependencies

Separate data movement from authority over identity, version, authorization, commit, rollback, retention, keys, logging, and retirement. A mover or worker may not redefine the authoritative generation, delete recovery states, change retention, disable audit evidence, or destroy keys unless each effect is explicitly authorized.

Record separate recovery dependencies for identity, credentials, encryption keys, configuration, software, schemas, certificates, naming, and other required services. Encrypted data without a recoverable key is not a recoverable system.

### Fail-closed interpretation

Reject malformed lengths, invalid digests or signatures, ambiguous versions, unsupported mandatory capabilities, traversal paths, unsafe links, unrecognized security-critical fields, and unknown commit state. Extensible unknown fields may proceed only under an explicit extension rule that defines their security effect.

### Recovery environment

After suspected compromise, validate and restore in an isolated known-good environment before controlled reconnection. Restoring directly into the compromised authority domain does not independently establish trust.

### Recovery objectives

Record RPO and RTO when applicable. The supplied source also proposes `RCO` for the required strength of trust evidence and `RDO` for dependency recoverability; treat these as source-generated project terminology, not established NIST terminology.

### Deep rule

Do not destroy information, authority, optionality, or evidence faster than independent proof establishes that the succeeding state is correct and recoverable. Place irreversible operations at the end of the workflow after the highest-confidence available verification.
