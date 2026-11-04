# sf-Edabit / sf-AmorphDataDrive
## Canonical Architecture Specification — Locked Baseline v0.3

**Status:** LOCKED BASELINE  
**Environment:** Non-Production / Safe-Hardening  
**Security posture:** high-friction attestation; fail by construction against architectural deviance  
**Canonical rule:** `sf-AmorphDataDrive` contains raw amorphous data only. No metadata, file data structures, partition data, filesystem information, rights, identity, interpretation, attestation, or composition structures may exist on that drive.

---

# 0. Canonical Lock

The architecture is defined by three primary layers:

```text
D0 = existence
D1 = relation / interpretation
D2 = composition / coherence
```

Canonical statement:

> **D0 knows nothing. D1 describes relationships to D0. D2 describes relationships among D1 relationships.**

A later filesystem, rights model, ownership model, metadata layer, or execution environment may be overlaid only above the attested relational/compositional substrate.

---

# 1. System Overview

```text
                 FUTURE OVERLAYS
       filesystem / rights / ownership / metadata
                         ▲
                         │
                 NOT YET PRESENT
                         │
──────────────────────────────────────────────────────
                  ATTESTATION LAYER
      persistent validation + optional memory witness
──────────────────────────────────────────────────────
                         ▲
                         │
┌─────────────────────────────────────────────────────┐
│ D2 — sf-StackDrive                                  │
│                                                     │
│ COMPOSITION / COHERENCE                             │
│                                                     │
│ ordered stacks                                      │
│ alternate stack paths                               │
│ coherent reconstruction                             │
│ words / sentences / calculations / code / papers   │
│ files / programs / arbitrary coherent structures   │
└─────────────────────────────────────────────────────┘
                         ▲
                         │ references D1 structures
                         │
┌─────────────────────────────────────────────────────┐
│ D1 — sf-RelationDrive                               │
│                                                     │
│ RELATION / INTERPRETATION                           │
│                                                     │
│ sf-DataType                                         │
│ encodings                                           │
│ code pages                                          │
│ symbols                                             │
│ tuples                                              │
│ relational bitmaps                                  │
│ alternate equivalent bitmaps                        │
│ atom / molecule relations                           │
│ external attestation of D0                          │
└─────────────────────────────────────────────────────┘
                         ▲
                         │ external references only
                         │
┌─────────────────────────────────────────────────────┐
│ D0 — sf-AmorphDataDrive                             │
│                                                     │
│ RAW / FLAT / CLEAN / ORDERED / ENUMERATED           │
│                                                     │
│ no metadata                                         │
│ no filesystem                                       │
│ no partition                                        │
│ no identity                                         │
│ no type information                                 │
│ no encoding information                             │
│ no attestation information                          │
│ no reconstruction information                       │
└─────────────────────────────────────────────────────┘
```

---

# 2. D0 — sf-AmorphDataDrive

`sf-AmorphDataDrive` is a flat raw value space.

It contains only raw values.

For a fully enumerated 64-bit implementation:

```text
0000000000000000
0000000000000001
0000000000000002
...
FFFFFFFFFFFFFFFF
```

The physical representation may be defined externally by the implementation, but no on-drive structure may describe that representation.

## 2.1 Absolute D0 prohibition

D0 must contain none of the following:

```text
metadata
headers
magic numbers
signatures
superblocks
partition tables
filesystem structures
file tables
directory structures
filenames
paths
object identifiers
drive identifiers
generation identifiers
datatype identifiers
encoding identifiers
code-page identifiers
symbol identifiers
tuple identifiers
atom identifiers
molecule identifiers
stack identifiers
hashes
checksums
attestation records
indexes
relationship maps
bitmap descriptions
stack descriptions
reconstruction instructions
rights
permissions
ownership information
execution information
```

## 2.2 Self-description prohibition

D0 must not contain information describing:

- itself;
- its format;
- its geometry;
- its intended use;
- its identity;
- its generation;
- its integrity state;
- its encoding;
- its semantic interpretation;
- its relation to D1 or D2.

D0 must not identify itself as `sf-AmorphDataDrive`.

That identity exists externally.

---

# 3. Ordered Enumeration Rule

D0 is deterministic and ordered.

For the canonical full-enumeration form:

```text
D0[n] = n
```

Examples:

```text
offset 0 → 0
offset 1 → 1
offset 2 → 2
...
offset N → N
```

The substrate must not use random placement, random permutation, computed placement, derived placement, alias placement, or redirected placement.

Forbidden placement semantics include:

```text
random(n)
permute(n)
compute(n)
derive(n)
transform(n)
alias(n)
redirect(n)
```

Canonical placement exists to prevent hidden semantic or computational behavior from entering the raw substrate through placement choice.

---

# 4. Literal Value Versus Computation

D0 stores literal raw values only.

It does not confer computational authority.

Therefore:

```text
literal value       permitted
computed meaning    external
operation            external
instruction          external
execution authority  external
```

A representation may describe an operation without authorizing the operation.

Canonical distinction:

```text
"1"             = data
"A"             = data
"Virus 1"       = constructed data
"Virus A"       = constructed data
"Compute 1"     = operation request
```

The final form is not a D0 primitive.

Proper construction does not confer execution authority.

---

# 5. Full 64-Bit Enumeration

A complete 64-bit space contains:

```text
2^64
```

distinct values.

At eight bytes per value:

```text
2^64 × 8 bytes
= 2^67 bytes
= 128 EiB
≈ 147.574 EB
```

A physically complete enumerated 64-bit D0 therefore requires approximately 128 EiB of raw substrate storage before redundancy.

A smaller drive may implement a bounded ordered subset.

A smaller drive must not claim full physical 64-bit enumeration.

That fact is recorded externally.

---

# 6. D1 — sf-RelationDrive

D1 provides all interpretation of D0.

D1 may contain:

```text
references to D0 positions
relational bitmaps
alternate bitmaps
sf-DataType definitions
encoding definitions
code-page definitions
symbol definitions
tuple definitions
atom definitions
molecule definitions
coverage descriptions
drive identity information
generation information
attestation information
integrity information
```

D1 is the first semantic layer.

It may answer questions such as:

```text
Which D0 positions participate in this relation?
How is this raw value interpreted?
Which encoding applies?
Which code page applies?
Which semantic datatype applies?
Which relation or bitmap selects the value?
Which alternate relation yields an equivalent result?
```

---

# 7. sf-DataType

`sf-DataType` identifies the semantic role assigned to referenced raw values.

Initial examples include:

```text
sf-RawBits
sf-Math
sf-StringChar
sf-MemoryChar
sf-RegisterChar
```

Equal raw bits with different `sf-DataType` values are different semantic objects.

Example:

```text
raw 0x41 + sf-StringChar
```

is distinct from:

```text
raw 0x41 + sf-RegisterChar
```

and distinct from:

```text
raw 0x41 + sf-Math
```

The distinction exists only outside D0.

---

# 8. Encoding and Code Pages

Encoding identity is separate from semantic datatype.

D1 may define mappings for:

```text
raw binary
EBCDIC families
ASCII
extended ASCII code pages
UTF-8
UTF-16
UTF-32
implementation-defined encodings
```

Multiple code pages may interpret the same D0 substrate.

Those code pages are not stored on D0.

Example:

```text
D0 raw values
    │
    ├─ ASCII relation
    ├─ UTF-8 relation
    ├─ EBCDIC code-page relation
    └─ other explicitly defined relation
```

No encoding may be inferred from raw D0 bits alone.

No code page may be inferred from raw D0 bits alone.

---

# 9. External Tuple Model

The tuple exists entirely on D1.

Canonical conceptual form:

```text
sf-Tuple
{
    D0Reference
    sf-DataType
    Encoding
    CodePage
    Symbol
}
```

The tuple may include external identifiers and attestation data.

None of those fields exist on D0.

A single D0 value may participate in multiple independent tuples.

---

# 10. Relational Bitmaps

D1 uses relational bitmaps to select and relate raw substrate values.

Bitmaps may designate:

```text
raw value occurrences
typed atoms
characters
numbers
operators
stems
endings
tokens
instructions
words
sentence components
calculation components
code components
```

A bitmap establishes relation and membership.

It does not alter D0.

---

# 11. Redundant Relation Paths

More than one bitmap may validly produce the same semantic result.

Two classes are distinguished.

## 11.1 Replica relation

```text
sf-ReplicaRelation
```

Two or more relation structures are exact duplicates.

Example:

```text
B1 = {1, 7, 9}
B2 = {1, 7, 9}
```

Purpose:

```text
protect against corruption of the relation record itself
```

## 11.2 Equivalent relation

```text
sf-EquivalentRelation
```

Different relation paths reconstruct the same semantic result.

Example:

```text
B1 = {1, 7, 9}
B2 = {22, 41, 88}
```

when both resolve to the same intended semantic object.

Purpose:

```text
avoid dependence on one relation path
```

Replica equivalence and semantic equivalence must never be conflated.

---

# 12. Representation Diversity

Redundancy and representational diversity are separate properties.

Example redundancy:

```text
UTF8-A
UTF8-B
UTF8-C
```

Example representation diversity:

```text
ASCII
UTF-8
EBCDIC
```

Different code pages or encoding families may serve as independent semantic witnesses when they reconstruct the same intended semantic result.

This provides:

```text
sf-RepresentationDiversity
```

without altering D0.

---

# 13. Atoms and Molecules

D1 may construct semantic atoms and molecules from external relations to D0.

Examples:

```text
atom:
    one typed interpreted relation

molecule:
    a defined relation among atoms
```

Possible molecules include:

```text
character group
word stem
word ending
word
number
operator
instruction component
token
```

No corresponding object metadata is written to D0.

---

# 14. D2 — sf-StackDrive

D2 provides ordered coherent composition.

D2 references D1 structures and composes them into larger semantic objects.

Examples include:

```text
words
sentences
paragraphs
papers
calculations
source code
functions
modules
programs
serialized objects
file-like objects
```

D2 supplies ordering, grouping, nesting, and reconstruction structure.

---

# 15. Redundant Stack Paths

More than one D2 stack may validly reconstruct the same coherent object.

Example:

```text
Stack-X1
    → R1
    → R2
    → R3

Stack-X2
    → R7
    → R9
    → R12

Stack-X3
    → R18
    → R22
    → R30
```

All may satisfy:

```text
reconstruct(Stack-X1)
=
reconstruct(Stack-X2)
=
reconstruct(Stack-X3)
```

This is:

```text
sf-CompositionalRedundancy
```

Multiple valid stacks must not create nondeterministic selection.

Redundancy increases evidence.

Redundancy does not authorize arbitrary choice.

---

# 16. Files Are Reconstructed Objects

A file does not physically exist on D0.

A file-like object is reconstructed through:

```text
D2 ordered composition
        ↓
D1 semantic relations
        ↓
D0 raw values
```

Therefore:

```text
D0 is not a file store.
D1 is not a file table.
D2 is not a conventional filesystem.
```

A conventional filesystem, if later added, is an overlay above this architecture.

---

# 17. Redundancy Classes

The architecture supports multiple independent redundancy mechanisms.

They do not have to be used in conjunction.

## 17.1 sf-PhysicalRedundancy

Multiple physical D0 substrates.

Example:

```text
D0-A
D0-B
D0-C
```

Each independently satisfies the canonical enumeration rule.

## 17.2 sf-RelationalRedundancy

Multiple D1 relation or bitmap paths over the same or different D0 substrates.

## 17.3 sf-SemanticRedundancy

Multiple semantic interpretations or encoding/code-page paths converging on the same intended semantic result.

## 17.4 sf-CompositionalRedundancy

Multiple D2 stack paths reconstructing the same coherent result.

## 17.5 sf-RepresentationDiversity

Different representation families provide independent semantic witnesses.

---

# 18. Intra-Substrate Redundancy

`sf-IntraSubstrateRedundancy` uses multiple relation, encoding, bitmap, or stack paths over one D0 substrate.

Example:

```text
                 D0-A
                  │
       ┌──────────┼──────────┐
       │          │          │
     D1-A1      D1-A2      D1-A3
       │          │          │
    Stack A1   Stack A2   Stack A3
```

This mode is independently valid.

It does not require multiple D0 drives.

---

# 19. Inter-Substrate Redundancy

`sf-InterSubstrateRedundancy` uses multiple physically independent D0 substrates.

Example:

```text
D0-A
D0-B
D0-C
```

Each substrate independently satisfies:

```text
D0[n] = n
```

for its declared coverage.

This mode is independently valid.

It does not require multiple relation or stack paths per substrate.

---

# 20. Combined Redundancy

The two redundancy modes may also be combined.

Example:

```text
                D0-A
                  │
       ┌──────────┼──────────┐
       │          │          │
     D1-A1      D1-A2      D1-A3
       │          │          │
    Stack A1   Stack A2   Stack A3


                D0-B
                  │
       ┌──────────┼──────────┐
       │          │          │
     D1-B1      D1-B2      D1-B3
       │          │          │
    Stack B1   Stack B2   Stack B3
```

Combined use provides:

```text
path diversity × substrate diversity
```

but combined use is optional.

---

# 21. Valid Redundancy Profiles

All of the following are valid:

```text
Profile A
    one D0
    multiple relations / code pages / bitmaps / stacks

Profile B
    multiple independent D0 drives
    one canonical relation/stack path per substrate

Profile C
    multiple independent D0 drives
    multiple relation/stack paths per substrate

Profile D
    one D0
    one relation/stack path
    no redundancy beyond the minimum architecture
```

Attestation must accurately state which redundancy mechanisms were actually used.

It must not imply a stronger profile.

---

# 22. Determinism Under Redundancy

Multiple valid paths must not introduce arbitrary selection.

Forbidden:

```text
choose random valid bitmap
choose random valid stack
choose arbitrary surviving relation
```

Permitted design patterns include externally defined deterministic validation and selection rules.

Canonical rule:

```text
redundancy increases evidence
redundancy does not create nondeterminism
```

---

# 23. Disagreement Handling

Agreement is evidence.

Disagreement is not silently repaired.

For high-assurance objects:

```text
all required witnesses agree
    → sf-Pass

any required witness disagrees
    → sf-Fail
```

A weaker profile may classify some divergence as `sf-Warning`, but the profile must define that explicitly.

No majority result automatically redefines truth.

No path wins merely because more copies agree with it.

---

# 24. Attestation Separation

Attestation information must never be stored on D0.

Any attestation of D0 exists externally.

Dependency direction:

```text
D1 may attest D0.

D2 may attest D1 and reconstructed objects.

Memory may witness completed attestation.

D0 attests nothing.
```

Possible persistent attestation material includes:

```text
device identity
drive geometry
coverage
enumeration status
hashes
integrity roots
generation identity
relation integrity
stack integrity
reconstructed-object integrity
```

All such information belongs outside D0.

---

# 25. Memory as Attestation Witness

Memory may participate in attestation only as a secondary witness.

Canonical rule:

> **Memory may witness attestation, but memory may not reduce the cost of attestation.**

Memory is never authoritative.

Memory is never a final fallback.

Memory is never permitted to bypass persistent validation.

## 25.1 Permitted memory role

Memory may:

```text
record that an attestation occurred
hold a transient witness value
participate in comparison after canonical validation
report disagreement with persistent evidence
```

## 25.2 Forbidden memory role

Memory must not:

```text
skip validation
shorten validation
accelerate validation
replace persistent validation
substitute cached success for revalidation
override persistent disagreement
become sole recovery authority
become final fallback
create implied continuity after restart
```

---

# 26. High-Friction Attestation

This architecture intentionally treats verification cost as a security property.

Canonical flow:

```text
persistent evidence
      ↓
full validation
      ↓
required redundancy checks
      ↓
reconstruction checks
      ↓
attestation
      ↓
memory may record or corroborate the completed result
```

Forbidden shortcut:

```text
memory says it was valid
      ↓
skip validation
```

Previously observed agreement does not remove the requirement to validate again.

Cached success does not confer current trust.

Restart or context loss requires trust to be re-established from persistent evidence.

---

# 27. Memory Is Not Final Fallback

If all persistent authoritative evidence is unavailable or invalid, memory must not become the final recovery source.

Canonical rule:

```text
persistent authority unavailable
    +
memory witness available
        ≠
canonical recovery
```

Instead:

```text
persistent authority unavailable
    → sf-Fail
    → recovery authority absent
    → memory may report prior state
    → memory may not assert canonical current state
```

---

# 28. Pre-Filesystem Boundary

Filesystem semantics, ownership, rights, permissions, names, and conventional metadata remain above the redundant and attested substrate.

```text
Layer 0
sf-AmorphDataDrive
canonical ordered raw space

Layer 1
sf-RelationDrive
typed and encoded interpretations

Layer 1R
redundant/equivalent relation sets

Layer 2
sf-StackDrive
ordered coherent composition

Layer 2R
redundant/equivalent stack sets

Layer 3
sf-Attestation
persistent validation
optional memory witness

──────────────────────────────
ONLY AFTER THIS BOUNDARY
──────────────────────────────

Layer 4
filesystem namespace

Layer 5
ownership / rights / permissions

Layer 6
metadata / provenance / policy
```

The filesystem is therefore an overlay.

It is not the source of truth for the raw substrate.

---

# 29. Canonical Invariants

```text
I-01  D0 contains raw data only.
I-02  D0 contains no metadata.
I-03  D0 contains no filesystem information.
I-04  D0 contains no partition information.
I-05  D0 contains no datatype information.
I-06  D0 contains no encoding information.
I-07  D0 contains no code-page information.
I-08  D0 contains no symbol information.
I-09  D0 contains no tuple information.
I-10  D0 contains no attestation information.
I-11  D0 contains no identity information.
I-12  D0 contains no reconstruction information.
I-13  D0 contains no ordering metadata.
I-14  D0 contains no object-membership metadata.
I-15  D0 does not identify itself.
I-16  All interpretation is external to D0.
I-17  D1 owns relation and interpretation.
I-18  D2 owns ordered composition and coherence.
I-19  D1 and D2 may reference D0; D0 never references D1 or D2.
I-20  Equal raw values may support multiple independent semantic interpretations.
I-21  Semantic interpretation never mutates D0.
I-22  Reconstruction never mutates D0.
I-23  Attestation never mutates D0.
I-24  A mismatched layer fails closed.
I-25  No invalid or missing relationship is heuristically reconstructed.
I-26  Raw data does not imply meaning.
I-27  Meaning does not imply ordering.
I-28  Ordering does not imply execution authority.
I-29  A complete 64-bit physical enumeration requires 2^64 values.
I-30  Smaller implementations must not claim complete physical enumeration.

I-31  D0 enumeration is deterministic and ordered.
I-32  For canonical full enumeration, D0[n] = n.
I-33  D0 values may not be randomly positioned.
I-34  D0 values may not be permuted as part of their representation.
I-35  D0 contains literal values, never computational instructions.
I-36  No D0 value carries computation authority.
I-37  Proper construction does not confer execution authority.
I-38  A semantic object may describe an operation without authorizing that operation.
I-39  Reconstruction and computation are separate authorities.
I-40  No relation or stack may convert representation into execution merely by being syntactically valid.

I-41  Redundancy shall not place metadata on D0.
I-42  Physical D0 redundancy uses independently valid canonical substrates.
I-43  Multiple D1 relations may resolve the same semantic object.
I-44  Multiple encodings or code pages may provide independent semantic witnesses.
I-45  Multiple bitmaps may provide equivalent relation paths.
I-46  Multiple D2 stacks may reconstruct the same coherent object.
I-47  Replica equivalence and semantic equivalence are distinct.
I-48  Redundancy must not introduce nondeterministic selection.
I-49  Witness disagreement must be externally visible.
I-50  Agreement supplies attestation evidence but never execution authority.
I-51  Filesystem, rights, and conventional metadata remain above the redundancy and attestation layers.

I-52  Intra-substrate and inter-substrate redundancy are both permitted.
I-53  Intra-substrate redundancy provides multiple independent relational or compositional paths over one D0.
I-54  Inter-substrate redundancy uses physically independent canonical D0 drives.
I-55  Inter-substrate D0 drives must independently satisfy the same canonical enumeration rule.
I-56  Redundancy may cross both axes simultaneously.
I-57  Agreement within one D0 and agreement across multiple D0 drives are separate attestation facts.
I-58  A stronger attestation profile may require both forms.
I-59  Redundant relation paths need not use the same encoding, code page, bitmap, or stack structure.
I-60  Equivalent reconstruction across independently generated substrates is stronger evidence than duplicate copies alone.
I-61  No redundancy mechanism may alter D0's zero-metadata rule.
I-62  No redundancy mechanism may introduce nondeterministic selection.
I-63  Divergence between supposedly equivalent substrates or paths must surface as sf-Fail or explicitly classified sf-Warning.

I-64  Intra-substrate redundancy and inter-substrate redundancy are independently optional.
I-65  Neither redundancy class requires the presence of the other.
I-66  A system using only intra-substrate redundancy is valid.
I-67  A system using only inter-substrate redundancy is valid.
I-68  A system may combine both redundancy classes.
I-69  Attestation must state which redundancy class or classes were actually used.
I-70  Absence of one redundancy class is not a fault unless that class is explicitly required by the selected attestation profile.

I-71  Memory may serve only as a secondary attestation witness.
I-72  Memory is never authoritative.
I-73  Memory must not bypass, shorten, skip, or accelerate canonical validation.
I-74  Cached validation results must not substitute for revalidation against persistent evidence.
I-75  Previously observed agreement does not remove the requirement to verify again.
I-76  Memory may record that an attestation occurred, but that record is not itself sufficient evidence of current validity.
I-77  Memory may participate in comparison only after canonical persistent validation has been performed.
I-78  Memory may never be the sole recovery source.
I-79  Memory may never be the final fallback.
I-80  Memory may never override persistent disagreement.
I-81  Loss of memory must not weaken the ability to reconstruct or attest canonical state.
I-82  Restart or context loss requires re-establishment of trust from persistent evidence.
I-83  High-friction revalidation is intentional and must not be optimized away by caching, prediction, remembered success, or inferred continuity.
```

---

# 30. Canonical Reduction

The complete pre-filesystem architecture reduces to:

```text
RAW SUBSTRATE
      ↓
RELATION / INTERPRETATION
      ↓
REDUNDANT RELATION PATHS
      ↓
COMPOSITION / COHERENCE
      ↓
REDUNDANT STACK PATHS
      ↓
HIGH-FRICTION ATTESTATION
      ↓
OPTIONAL MEMORY WITNESS
      ↓
FUTURE FILESYSTEM / RIGHTS / METADATA OVERLAY
```

The canonical statements are:

> **D0 knows nothing. D1 describes relationships to D0. D2 describes relationships among D1 relationships.**

> **Redundancy may exist within one substrate, across multiple substrates, or both. Neither redundancy class requires the other.**

> **Memory may witness attestation, but memory may not reduce the cost of attestation.**

> **Memory is never the final fallback.**

> **Proper construction does not confer execution authority.**

---

# 31. Change Control

Any future proposal that places any of the following on D0:

```text
metadata
identity
type
encoding
code page
symbol
hash
attestation
relation
ordering
filesystem information
rights
permissions
ownership
stack information
reconstruction information
```

is an architectural deviation.

Any future proposal that allows memory to:

```text
skip validation
accelerate validation
replace persistent evidence
become final fallback
override persistent disagreement
```

is also an architectural deviation.

Default handling:

```text
deviation
    → sf-Fail
    → reject proposed change
    → require explicit unlock / revision authority
```

No future extension may silently weaken these boundaries.
