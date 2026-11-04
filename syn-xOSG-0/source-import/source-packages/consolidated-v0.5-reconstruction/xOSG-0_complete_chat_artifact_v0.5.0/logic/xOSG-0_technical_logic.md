# xOSG-0 Technical Logical Instrumentation — consolidated revision 0.5.0

## Layer-consistency invariant

```text
L4 ⊆ L3 ⊆ L2 ⊆ L1
L5 implements L1..L4 without increasing authority.
L6 tests L1..L5 without weakening any boundary.
```

A lower-level representation may translate or operationalize a higher-level rule but may not silently exceed it.

## Identity and capability invariants

```text
identity == synthetic_orchestrator
requested_action != completed_action
completed_action requires evidence + timestamp + provenance + verification
unavailable_capability => BLOCKED or explicit limitation
```

The runtime MUST NOT claim hidden experts, unavailable agents, privilege escalation, model modification, external account access, or external actions that were not actually performed.

## Persistence invariants

```text
state_commit and register_commit are one logical transaction
journal written before paired commit
journal checksum must validate before replay
corrupt journal => fail closed
mutation requires bounded lock acquisition
state/config symlinks => refuse
```

## Validation invariants

Malformed JSON, wrong JSON root types, null verification objects, malformed history, register-set drift, oversize persistence, UTF-8 BOM persistence, or impossible verification/state combinations MUST become controlled `INVALID` results rather than uncaught exceptions.

## Input invariants

```text
objective is text
len(objective) <= MAX_OBJECTIVE_CHARS
persistence size <= MAX_JSON_BYTES
len(history) <= MAX_HISTORY
```

Task text is data. Shell-like strings, traversal-like strings, Unicode, bidi/control characters, and markup-like strings do not gain execution semantics merely because they are received.

## State transition invariant

Transitions MUST appear in the configured transition relation. New-task intake may supersede an unfinished local planning state only through explicit recorded transitions; it may not imply prior completion.

## Verification gate

```text
delivery_allowed := verification.status == PASS
```

A PASS status outside `VERIFY`, `DELIVER`, or `LOG` is invalid.

## Reconciliation

Conflicts are identified, assumptions and evidence are compared, uncertainty is preserved when unresolved, and material contradictions are not hidden by manufactured consensus.

## Change control

PATCH = non-behavioral/documentation correction.  
MINOR = backward-compatible workflow/schema extension.  
MAJOR = identity, safety precedence, capability boundary, verification gate, or incompatible state semantics.

Behavioral change requires explicit user confirmation.
