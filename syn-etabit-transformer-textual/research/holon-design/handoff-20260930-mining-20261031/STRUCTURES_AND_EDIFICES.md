# Structures and Edifices

This catalogue distinguishes current structures, historical structures, application structures, candidate boundary structures and unresolved large edifices.

## Current general structures

### Absolute wrapper

```text
Holon Wrapper
└── Holon Compartment
    ├── Holoquary Self
    │   └── Holoquary Identifiers
    │       └── ID
    └── Holoquary Composition
        └── Holoquary / Holon
            └── Data
```

Status: recorded user structure and current general foundation. Unresolved: number and coexistence of branches, serialization, sentinels and reference forms.

### Self-only minimum

```text
Holon Wrapper
└── Holon Compartment
    └── Holoquary Self
        └── Holoquary Identifiers
            └── ID
```

Status: current minimum form. It may contain no data.

### Composition-only minimum

```text
Holon Wrapper
└── Holon Compartment
    └── Holoquary Composition
        └── Holoquary / Holon
            └── Data
```

Status: current minimum form. It may be selfless; Data may be unary or composite.

### Empty distinctions

1. Empty wrapper.
2. Wrapper with no compartment.
3. Wrapper with one or more empty compartments.

Status: distinct required meanings with unresolved encodings.

## Category collections

The handoff records thirteen elaboration categories: identifiers, identities, descriptors, roles, relationships, context, rights/responsibilities, edges, validator, data, data metadata, data validator and capability. These are not thirteen mandatory nonempty fields. Placement, entry forms and validation remain open.

## Catalog and codices

- Complete structure catalog: required externally and internally as a holon.
- Encoding codices: one inside and one outside the wrapper.

Neither requirement specifies equality, correspondence algorithm, byte representation, processing order or codec implementation.

## Originator edifice

```text
Originator
└── Emitter
    └── Source
        ├── Encoder
        ├── Database
        ├── Data and Metadata
        ├── Holon Atomics
        ├── Encoded Holon Wrapper
        ├── Recovery Information
        ├── Regeneration Information
        └── Protocol Wrapper and Attestation
```

Status: retained supplied hierarchy. The displayed edges do not settle ownership or composed-holon semantics. Originator was also described as having no composed holons, only emissions; the Emitter/Source relationship remains unresolved.

## Historical four-field/depth wrapper

```text
Full Holon
├── Holon Identifier
├── Holon Name
├── Holon Role
└── Holon Data
    └── Holoquary Holon Order
        └── target identifier + occurrence depth
```

Status: earlier user-approved documentation package, preserved byte-for-byte but superseded as the general foundation. Reusable lessons: separate target records from occurrence placement, document every field, make order explicit, restart relative depth per view. Nonreusable universal claim: depth organizes all relationships.

## Storybook application edifice

The prior application separated source, parsing, documentation, manual, and references/indexes/tables payloads. It also used story blocks, block cyphers and read-aloud holons. Status: application-specific precedent. It does not establish a universal parser or block ontology.

## UPST v0.1 packet structure

```text
application packet
├── contract/version/message_id/kind
├── claim_class
├── producer_hint / consumer_hint
├── body
└── namespaced extensions
```

Supported bodies: `state_record`, `design_target`, `artifact_reference`. Status: strict nonrecursive assistant-generated candidate boundary, not accepted transport or native Holon structure.

## UPTI v0.2 local staging structure

```text
raw immutable JSON bytes
    -> stage(local profile assumptions)
    -> verify(same bytes + contract)
    -> mark_ready
    -> original bytes + local receipt
    -> [future accepted UPTI boundary]
```

Status: candidate local implementation. `mark_ready` is not transfer. The receipt explicitly denies authenticated sender, delivery and receiver acknowledgment.

## Historical UPTI-SF edifice

```text
Protocol A <-> Adapter A <-> neutral envelope <-> Adapter B <-> Protocol B
```

Lifecycle: inspect, negotiate, capture, provenance, checkpoint, stage, transform, validate, verify, commit, receipt, optional authorized release. Status: `NOT_USED / INACTIVE / EXCLUDED`. It contributes lessons but no active component or dependency.

## Strmdocx candidate edifice

The mined sources support—but do not implement—a possible separation:

```text
immutable native blocks/holons
        +
reference and relationship structures
        +
ordered transformation records
        +
replaceable maps/profiles
        ->
resolved render or boundary packet
```

This remains a crosswalk target. It needs decisions about atomicity, occurrence references, relationship semantics, identity, storage, cycles and native versus rendered forms.
