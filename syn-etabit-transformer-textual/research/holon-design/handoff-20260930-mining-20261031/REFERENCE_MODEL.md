# Reference Model

Date: 2026-10-31. Status: mined design account, not an implemented schema.

## Controlling rule

The current direct user rule is:

> Everything is by reference.

This controls over the earlier examples that nested complete constituent objects. It does not, by itself, settle the type or meaning of each reference.

## Four concepts that must remain separate

| Concept | Meaning | Must not be silently treated as |
| --- | --- | --- |
| Holon | Independently represented semantic unit/whole | A mere pointer, UUID or storage block |
| Holoquary | A holon operating in compositional/aggregate capacity | A second object species or automatically owned tree |
| Reference | Connection to an independently represented target | Ownership, authority, truth or permission to resolve |
| Relationship | Meaning associated with one or more references | Something inferable solely from adjacency, depth or JSON nesting |

Identity remains broader than identifiers. A target can retain identity while participating in several compositions. The connection mechanism should therefore avoid duplicating the target record at each use.

## Current structural foundation

The current handoff foundation is:

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

This is not a finalized JSON shape. The historical four-field wrapper and `Holoquary Holon Order` with relative depth are retained as an earlier ordering view, not the universal foundation.

## What reference-addressedness establishes

1. Independently represented targets are not copied wholesale into every composition.
2. A reference and its target can be inspected separately.
3. The same target may potentially participate in more than one composition.
4. Source, derived records, documentation, transformations and catalogs can remain distinct while being connected.
5. A rendered or transferred view may resolve references without becoming the canonical storage representation.

## What it does not establish

Reference-addressedness alone does not answer:

- whether the reference points directly to a constituent or to an occurrence/reference holon;
- whether each occurrence has a stable identity;
- whether relationship semantics are separate holons, edge records or referenced catalog entries;
- how occurrence metadata is attached;
- which ordering view is canonical;
- whether cycles are permitted;
- whether repeated references inside one composition are permitted;
- what owns deletion or lifetime;
- what a missing, unresolved, unauthorized or stale reference means;
- how physical storage or addressing works;
- whether a block is a holon, a serialization unit or a storage allocation.

## Candidate forms still awaiting a decision

### Direct target references

```text
Nth position -> target holon
Nth position -> relationship reference
Nth position -> metadata reference
```

Advantages: target identity remains directly visible; fewer intermediary records. Questions: how the three references are bound into one occurrence and how repeated targets are distinguished.

### Occurrence/reference holons

```text
Nth position -> occurrence holon
occurrence holon -> target holon
occurrence holon -> relationship holon
occurrence holon -> metadata holon
```

Advantages: each occurrence can be addressed and extended uniformly. Questions: additional indirection, identity policy, lifecycle and whether every occurrence warrants a holon.

Neither form is adopted by this mining report.

## Order and depth

The prior wrapper used an ordered array of target identifiers with occurrence-specific relative depth. That pattern established:

- order by array position;
- relative base per order;
- reusable target records separate from order entries;
- a preorder-like hierarchical view.

The later handoff explicitly rejects depth as the universal basis of relationships and coordination. Depth may remain useful for a particular view, renderer or application profile. It cannot silently define membership, ownership, authority, derivation or every composition.

## Blocks

Story blocks and block cyphers came from the Storybook application model. Strmdocx may use blocks because streams, fragments and transformations need addressable representations, but the sources do not establish `block = holon` universally.

Before implementation, block must be assigned one or more explicit roles:

- storage block;
- immutable stream fragment;
- serialized record;
- occurrence record;
- transformation record;
- semantic holon;
- rendered projection.

A single design may use several of these, but their identities and references must not be conflated.

## Metadata at an Nth position

The current safe rule is:

> Metadata associated with an Nth occurrence is resolved by reference rather than copied as an ungoverned nested object.

The binding representation remains open. “Stored at the Nth block” must not be translated into embedded ownership without deciding whether Nth refers to a physical block, an ordinal occurrence, an occurrence holon or an index record.

## Boundary packets

The v0.1 candidate payload is a strict nested JSON application packet. It can be mined as a boundary contract, but not adopted as native reference storage. A future profile could render a closed packet by resolving a selected reference graph, then record:

- the source references;
- the traversal/profile used;
- preserved, transformed and omitted fields;
- the resulting bytes;
- fidelity and loss;
- validation and receipt evidence.

That mapping is an assistant inference, not a completed or user-adopted adapter.

## Resolution safety

A reference does not grant resolution or effect authority. The candidate `artifact_reference` illustrates the separation: filename, size and digest can be validated as metadata without opening the named artifact. A general resolver will need explicit policy for availability, capability, authorization, integrity, freshness, cycles, quotas and failure states.

## Next design decision

The first implementation-affecting decision is the reference occurrence model: direct target references with separately bound relationship/metadata references, or addressable occurrence/reference holons. Until that is decided, no native schema, resolver or storage layer should be claimed.
