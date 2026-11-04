# sf-Edabit / sf-AmorphDataDrive
## Canonical Architecture Specification — Locked Baseline v0.2

**Status:** LOCKED BASELINE  
**Environment:** Non-Production / Safe-Hardening  
**Primary posture:** fail by construction against architectural deviance  
**Canonical rule:** `sf-AmorphDataDrive` contains raw amorphous data only. No metadata, file data structures, identification structures, interpretation structures, attestation structures, or composition structures may exist on that drive.

---

# 0. Canonical Lock

This specification locks the following invariant:

> **D0 knows nothing. D1 describes relationships to D0. D2 describes relationships among D1 relationships.**

The storage roles are physically and logically separated.

```text
D0 = existence
D1 = relation / interpretation
D2 = composition / coherence
```

No higher-layer structure may be written onto D0.

---

# 1. System Overview

```text
┌─────────────────────────────────────────────────────┐
│ D0 — sf-AmorphDataDrive                             │
│                                                     │
│ RAW / FLAT / CLEAN / ENUMERATED                     │
│                                                     │
│ no metadata                                         │
│ no filesystem                                       │
│ no partition                                        │
│ no object information                               │
│ no type information                                 │
│ no encoding information                             │
│ no attestation information                          │
│ no reconstruction information                       │
└─────────────────────────────────────────────────────┘
                         ▲
                         │ external references only
                         │
┌─────────────────────────────────────────────────────┐
│ D1 — sf-RelationDrive                               │
│                                                     │
│ RELATION / INTERPRETATION                           │
│                                                     │
│ sf-DataType                                         │
│ encoding                                            │
│ code page                                           │
│ symbols                                             │
│ tuples                                              │
│ relational bitmaps                                  │
│ references into D0                                  │
│ atoms / molecules                                   │
│ attestation of D0                                   │
└─────────────────────────────────────────────────────┘
                         ▲
                         │ references D1 structures
                         │
┌─────────────────────────────────────────────────────┐
│ D2 — sf-StackDrive                                  │
│                                                     │
│ COMPOSITION / COHERENCE                             │
│                                                     │
│ ordered bitmap stacks                               │
│ words                                               │
│ sentences                                           │
│ paragraphs                                          │
│ calculations                                        │
│ code                                                │
│ papers                                              │
│ files                                               │
│ programs                                            │
│ arbitrary coherent structures                       │
└─────────────────────────────────────────────────────┘
```

---

# 2. D0 — sf-AmorphDataDrive

`sf-AmorphDataDrive` is a flat raw value space.

It contains only raw data values.

For a fully enumerated 64-bit implementation:

```text
0000000000000000
0000000000000001
0000000000000002
...
FFFFFFFFFFFFFFFF
```

The physical representation may be defined by the implementation, but no on-drive structure may describe that representation.

## 2.1 Forbidden content on D0

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
execution information
```

This prohibition is absolute for the canonical baseline.

## 2.2 Self-description prohibition

D0 must not contain information that describes:

- itself;
- its format;
- its geometry;
- its meaning;
- its interpretation;
- its generation;
- its integrity state;
- its intended use;
- the contents of D1;
- the contents of D2.

D0 must not identify itself as `sf-AmorphDataDrive`.

That identification exists externally.

---

# 3. Raw-Value Invariant

A value physically present on D0 has no intrinsic semantic interpretation.

Example raw value:

```text
0000000000000041
```

D0 does not say that this represents:

```text
65
'A'
ASCII
UTF-8
a string character
a memory value
a register value
a mathematical value
an instruction component
an address
an opcode
```

Those interpretations exist only outside D0.

Therefore:

```text
RAW VALUE ≠ MEANING
```

and:

```text
presence on D0 does not imply datatype
presence on D0 does not imply encoding
presence on D0 does not imply use
presence on D0 does not imply ordering
presence on D0 does not imply object membership
```

---

# 4. Full 64-Bit Enumeration

A complete 64-bit value space contains:

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

A physically complete enumerated 64-bit D0 therefore requires approximately 128 EiB of raw substrate storage before any redundancy.

The architecture may also operate with smaller drives.

A smaller implementation is not a physically complete 64-bit enumeration and must not claim to be one.

That distinction must be recorded externally, never on D0.

---

# 5. D1 — sf-RelationDrive

D1 provides external interpretation of D0.

D1 may contain:

```text
references to D0 positions
relational bitmaps
sf-DataType definitions
encoding definitions
code-page definitions
symbol definitions
tuple definitions
atom definitions
molecule definitions
attestation information
integrity information
coverage descriptions
drive identity information
generation information
```

D1 is therefore the first semantic layer.

Its purpose is to answer questions such as:

```text
Which D0 positions participate in this relation?

How is this raw value interpreted?

Which encoding applies?

Which code page applies?

Which semantic datatype applies?

Which raw values together form this atom or molecule?
```

---

# 6. sf-DataType

`sf-DataType` identifies the semantic role assigned to referenced raw values.

The baseline permits independent identities such as:

```text
sf-RawBits
sf-Math
sf-StringChar
sf-MemoryChar
sf-RegisterChar
```

Additional types may be defined externally.

Equal raw bits with different `sf-DataType` values are different semantic objects.

Example:

```text
raw 0x41 + sf-StringChar
```

is distinct from:

```text
raw 0x41 + sf-RegisterChar
```

which is distinct from:

```text
raw 0x41 + sf-Math
```

The distinction exists only on D1.

D0 remains unchanged.

---

# 7. Encoding and Code Pages

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

Every encoding family that requires a code page must carry an explicit external code-page identity.

No encoding may be inferred from raw D0 bits alone.

No code page may be inferred from raw D0 bits alone.

No semantic datatype may be inferred from encoding alone.

---

# 8. External Tuple Model

The tuple does not exist on D0.

A tuple exists entirely on D1 and references D0 externally.

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

The tuple may also include external identifiers and attestation information.

Those fields remain entirely on D1.

A tuple can therefore interpret the same D0 value in multiple ways without modifying or duplicating that raw value.

---

# 9. Relational Bitmaps

D1 uses relational bitmaps to identify sets or sequences of references associated with semantic structures.

A bitmap may designate:

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

The bitmap describes relationship and membership.

It does not alter D0.

---

# 10. Atoms and Molecules

D1 may form semantic atoms and molecules from D0 references.

Examples:

```text
atom:
    one typed interpreted reference

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

These are D1 structures.

No corresponding object metadata is written onto D0.

---

# 11. D2 — sf-StackDrive

D2 provides coherent ordered composition.

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

D2 therefore supplies ordering, grouping, nesting, and reconstruction structure.

---

# 12. Stack Model

A stack is an ordered composition of references to D1 relations or derived D1 structures.

Conceptually:

```text
sf-Stack
[
    D1Reference-1,
    D1Reference-2,
    D1Reference-3,
    ...
]
```

The stack may itself participate in a higher-level stack.

This permits recursive composition such as:

```text
raw values
    ↓
atoms
    ↓
molecules
    ↓
words
    ↓
sentences
    ↓
paragraphs
    ↓
documents
```

or:

```text
raw values
    ↓
tokens
    ↓
expressions
    ↓
statements
    ↓
functions
    ↓
modules
    ↓
programs
```

---

# 13. Files Are Reconstructed Objects

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

A coherent file or program exists only as a deterministic reconstruction through the separated layers.

---

# 14. Attestation Separation

Attestation information must never be stored on D0.

Any attestation of D0 exists externally.

The dependency direction is:

```text
D1 may attest D0.

D2 may attest D1 and reconstructed objects.

D0 attests nothing.
```

This maintains the amorphous property of the raw drive.

Possible external attestation material includes:

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

# 15. Drive Replacement Rule

Because no identity is stored on D0, the relationship between a particular physical D0 and its D1 interpretation must be established externally.

A mismatched D0/D1 pair must fail closed.

Canonical rule:

```text
unverified D0
    → no semantic interpretation

wrong D0
    → sf-Fail

wrong D1
    → sf-Fail

wrong D2
    → sf-Fail
```

No heuristic repair or guessed association is permitted.

---

# 16. Minimum Two-Drive Configuration

Three drives are preferred because they preserve clean separation:

```text
D0 = raw values
D1 = relations
D2 = coherent stacks
```

A two-drive implementation is permitted.

In that case:

```text
D0 = raw values only

D1 = relation namespace
     +
     stack namespace
```

The two namespaces must remain logically distinct even if they occupy the same physical device.

D0 remains unchanged and entirely free of metadata.

---

# 17. Canonical Invariants

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

I-13  D0 contains no ordering information.

I-14  D0 contains no object membership information.

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
```

---

# 18. Canonical Reduction

The architecture reduces to:

```text
D0 = existence
D1 = relation / interpretation
D2 = composition / coherence
```

or:

```text
RAW
 ↓
RELATION
 ↓
COMPOSITION
 ↓
COHERENT OBJECT
```

The canonical statement is:

> **D0 knows nothing. D1 describes relationships to D0. D2 describes relationships among D1 relationships.**

This statement and the prohibition against all metadata or self-description on D0 are **LOCKED** for this baseline.

---

# 19. Change Control

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
file information
stack information
reconstruction information
```

is an architectural deviation.

Default handling:

```text
deviation
    → sf-Fail
    → reject proposed change
    → require explicit unlock/revision authority
```

No future extension may silently weaken this boundary.
