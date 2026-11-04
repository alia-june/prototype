# Decisions, Conflicts and Open Questions

## Current decisions

1. Everything is by reference.
2. Holon is the general unit; a holoquary is still a holon.
3. The design is general, recursive and modular.
4. Identity describes the whole; identifiers are constituent descriptions.
5. The absolute general structure is Wrapper → Compartment → Self/Identifiers or Composition/Holoquary-Holon/Data.
6. Self-only and composition-only minimum forms are valid.
7. Empty wrapper, no-compartment wrapper and empty-compartment wrapper are distinct states.
8. Relationships/coordination are broader than relative depth.
9. The complete structure catalog is external and internal as a holon.
10. The new general representation uses cataloged sentinel holons while retaining source-native state distinctions.
11. Two encoding codices are separately located inside and outside.
12. The retained larger hierarchy is Originator → Emitter → Source → eight named components.

## Superseded general proposals

- Four mandatory root fields as the universal foundation.
- Depth as the generic relationship organization.
- Native null placeholders in the new general representation.
- Stable UUID-through-edit policy as if already accepted.
- Mandatory separate Coordination collection.
- Mandatory four-graph architecture.
- Emissions as a third compartment branch.
- Assistant-proposed recovery/regeneration definitions as settled canon.

These remain available as historical evidence or candidate techniques where applicable.

## Candidate-only decisions

The following belong to the assistant-generated UPST/UPTI application candidates, not the current general Holon canon:

- nine required packet envelope fields;
- three supported body kinds;
- 64 KiB local packet ceiling;
- canonical local JSON encoding;
- process-local duplicate message ID reservation;
- local `ReceiverProfile` assumptions;
- `LocalHandoff`, `stage`, `verify` and `mark_ready` API names;
- maximum nesting 64 and maximum nodes 8,192;
- native JSON null in declared `ABSENT` interface fields.

They may be mined as tested examples. Adoption requires a separate decision.

## Conflicts and reconciliations not yet adopted

### C01 — Everything by reference versus nested packet bodies

The current native direction is reference-addressed. The candidate packet nests data. Possible interpretation: nested JSON is a resolved boundary view. Status: assistant inference, not adopted.

### C02 — Sentinel holons versus native JSON null

The general design replaces native null; the application contract requires it in two declared ABSENT fields. Possible resolutions include historical versioning, external boundary representation or an adapter. Status: open.

### C03 — Recursion versus nonrecursive payload

Holon composition is recursive; the v0.1 packet defers generic recursion. Resolution: treat v0.1 as a bounded application interface, not the universal model. This classification is supported; the eventual adapter is not designed.

### C04 — Extensible model versus closed envelope

A strict transport profile may be closed while carrying references to an extensible model. Exact mapping, extension/version rules and fidelity reports remain open.

### C05 — Historical relative depth versus broad relationships

Relative depth can remain a particular view. It cannot define all relationships. A future view/profile must state what depth means and how it relates to explicit relationship records.

## Open questions carried forward

### Reference and storage

1. Does an ordered occurrence point directly to a target or to an occurrence/reference holon?
2. How are target, relationship and metadata references bound to one occurrence?
3. Are repeated references inside one composition allowed, and how are occurrences identified?
4. Are cycles allowed; how are traversal, rendering and validation bounded?
5. Which ordering views are canonical, derived or merely presentational?
6. What owns lifetime, deletion, revision and garbage collection?
7. What is a block: storage, stream fragment, serialization, occurrence, transformation or semantic holon?

### Identity

8. What is the full identifier format, namespace and uniqueness scope?
9. What remains stable across edits, transformations, revisions and variants?
10. How do aliases, lineage and variations reference same-holon versus distinct variant holons?

### Minimum wrapper and catalog

11. How are the three empty cases encoded?
12. Can Self and Composition coexist in one compartment?
13. How do empty and minimal forms obtain the required internal catalog?
14. How are internal and external catalogs versioned and compared?
15. How do the two codices correspond and which procedures use each?

### Sentinels and transfer

16. What are the sentinel IDs and occurrence forms?
17. Which language/format/version profiles are supported first?
18. Which transfers require semantic, lexical or byte fidelity?
19. How is unsupported native reconstruction represented?

### Larger hierarchy and protocols

20. How do Originator, Emitter and Source relate under the no-composed-holons/only-emissions condition?
21. What are Holon Atomics?
22. What constitutes each attestation and who verifies it?
23. What exact meanings distinguish recovery and regeneration?
24. Is an accepted UPTI contract eventually supplied, and who is its verified owner/implementer?

## Questions resolved by this mining pass

- UPST and UPTI are not two current protocols in these packages; UPST is the preserved older spelling, UPTI the later candidate term.
- The external v0.1 package and the v0.2 embedded legacy copy are byte-identical for all thirteen nonmanifest files.
- The v0.2 local candidate does not transmit anything.
- The nested UPTI-SF package is inactive historical evidence, not an active dependency.
- The supplied v0.1 and v0.2 local tests pass in the current environment.
- Those passes do not establish transport conformance, authenticated identity, delivery or independent attestation.
