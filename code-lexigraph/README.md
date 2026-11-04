<div align="center">

# Code-Lexigraph

### From human code theory to inspectable, reconstructable programs

![Stage](https://img.shields.io/badge/stage-prototype-orange)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Runtime](https://img.shields.io/badge/runtime-Python-3776AB)
![Method](https://img.shields.io/badge/method-rehydration-6f42c1)
![Validation](https://img.shields.io/badge/tests-19%20passing-2da44e)

**A prototype for keeping programming meanings, requirements, construction rules, code roles, and evidence connected as code is reconstructed for use.**

</div>

---

## The idea

Most source code preserves **what was written**.

A Code-Lexigraph asks whether we can also preserve:

- what a construct means;
- which requirement it serves;
- which local assumptions make it valid;
- how it should be reconstructed;
- where it appears in generated code;
- what evidence was used to test it;
- and which questions are still unresolved.

The goal is not to replace source code with a graph.

The goal is to keep enough structured context around code that a reviewer can move in both directions:

```text
meaning
   ↓
requirement
   ↓
contract
   ↓
method
   ↓
construction
   ↓
code
   ↓
evidence
```

and then trace back upward again.

That bidirectional trace is the central idea of the prototype.

---

## Theoretical use cases

Code-Lexigraph is an experiment in making programming knowledge reusable without detaching it from its meaning and evidence.

Potential applications include:

### Explainable code reconstruction

A retained graph plus explicit bindings and a construction blueprint can reconstruct code while preserving links back to the concepts and requirements that informed each generated part.

### Human-authored theory with bounded AI automation

Humans can define theory, decomposition, requirements, profiles, and adoption decisions while AI assists with graph formulation, explicit mappings, construction, and finite checks.

The automation operates over a declared contract rather than silently inventing the governing semantics.

### Requirement-to-code traceability

A reviewer can move from a requirement to the code role that implements it, then back from generated code to the meanings, commitments, and construction records associated with it.

### Rehydration of retained programming knowledge

A code lexigraph can act as a retained intermediate representation that is later **rehydrated** into source code, readable contracts, traces, and inverse mappings.

### Multiple implementation profiles

The current prototype supports one profile, but the model points toward preserving different implementation choices under explicit profiles rather than treating one implementation as universal.

### Evidence-aware code generation

Tests and observations can remain distinct from requirements and mappings. Passing checks provide evidence for a bounded case without turning the graph itself into a semantic proof.

---

## What is implemented

The current prototype demonstrates one bounded rehydration profile for a safe-fall-through Python example.

It uses three principal inputs:

```text
retained code lexigraph
        +
selected profile bindings
        +
ordered construction blueprint
        ↓
      rehydrate()
        ↓
┌─────────────────────────────────────┐
│ generated Python source             │
│ readable contract                   │
│ construction trace                  │
│ inverse lookups                     │
│ generated source spans              │
└─────────────────────────────────────┘
```

The retained example contains:

| Structure | Count |
| --- | ---: |
| Graph entries | **29** |
| Relationships | **43** |
| Construction records | **22** |
| Direct code mappings | **8** |
| Supporting declarations | **2** |

The builder deliberately uses a restricted construction grammar rather than arbitrary Python synthesis.

---

## Worked example: safe fall-through

The example explores a local requirement:

> **Required JSON state should survive an operation failure while the surrounding system owns the exception response.**

The selected profile keeps the caller's original JSON text as the required survivor.

A separately parsed mutable representation is handed to the operation:

```text
caller JSON text
      │
      ├────────────── retained survivor
      │
      ↓
parse separate working representation
      │
      ↓
operation may mutate working state
      │
      ├── completes → COMPLETE
      │
      └── raises    → EXCEPTION
      │
      ↓
report still carries original survivor
```

An `ERROR` gate prevents decoding and operation invocation entirely.

These meanings are local to the declared example. They are not claimed as universal sentinel semantics.

---

## Validation

The current repository replay was performed with **Python 3.14.3**.

```text
19 tests passed

11  construction / behavior tests
 8  CLI integration tests
```

The replay established, for the tested case:

- three constructions produced identical source, readable text, mappings, and spans;
- the input bundle remained unchanged during construction;
- generated Python matched the reference program's parsed syntax structure;
- all eight generated code locations matched their parsed code elements;
- inverse mappings resolved for declared links;
- all 22 construction records were accounted for;
- nested mutation preserved the selected survivor;
- mutation followed by `RuntimeError` preserved the survivor and returned the declared response;
- the `ERROR` gate blocked both decoding and operation invocation;
- separate calls received independent nested working objects;
- four malformed/unresolved construction cases were refused;
- CLI output and filesystem refusal behavior passed the declared integration checks.

See **[VALIDATION.md](docs/VALIDATION.md)** for the actual proof boundary.

---

## Run the example

From the repository root:

```text
cd code-lexigraph
```

Generate the reconstructed source, readable contract, and trace:

```text
python -m code_lexigraph examples/safe_fallthrough.bundle.json --out build/example
```

Outputs:

```text
build/example/
├── example.py
├── CONTRACT.md
└── TRACE.json
```

Without `--out`, the complete construction result is emitted as JSON:

```text
python -m code_lexigraph examples/safe_fallthrough.bundle.json
```

The CLI **constructs** source. It does not execute generated source.

---

## Replay the checks

```text
python -m unittest discover -s tests -v
```

The test suite executes only the declared worked example and its bounded refusal cases.

---

## Python interface

```python
import json
from pathlib import Path

from code_lexigraph import rehydrate

bundle = json.loads(
    Path("examples/safe_fallthrough.bundle.json").read_text(encoding="utf-8")
)

result = rehydrate(bundle)

print(result["human"])
print(result["python"])
```

The result also includes:

```text
trace
inverse
spans
```

Reference locations retained by the original graph and generated source locations remain separate.

---

## Construction boundary

The builder validates and consumes:

- declared bundle and graph formats;
- profile selection;
- graph-node and edge references;
- selected bindings;
- Python identifiers;
- explicit construction IDs;
- restricted statements and expressions;
- code mappings;
- construction coverage;
- generated Python syntax.

The current construction vocabulary includes:

```text
from_import
import
class
function
assign
return
if
raise
expression
try
```

Expression forms include names, selected bindings, string literals, attributes, calls, ordered dictionaries, and identity comparisons.

This is a declared construction vocabulary, **not a general Python grammar or inference engine**.

---

## Human and AI roles

The prototype intentionally keeps authorship roles distinct.

### Human contribution

The human contribution supplies:

- code theory;
- decomposition methodology;
- governing requirements;
- local profile decisions;
- adoption and application decisions.

### AI-assisted contribution

AI-assisted work includes:

- scoped graph formulation;
- construction blueprint and mappings;
- demonstration implementation;
- reconstruction tooling;
- bounded tests;
- documentation.

Structured representation does not confer authority by itself. A relationship encoded in JSON remains a reviewable editorial assertion unless separately established by evidence or proof.

---

## What this does not claim

The current prototype does **not** establish:

- general code synthesis;
- formal semantic proof;
- arbitrary-input hardening;
- universal sentinel semantics;
- automatic requirement satisfaction;
- crash-atomic multi-file publication;
- persistence across process termination;
- guarantees about external effects;
- a supported Python-version range beyond the tested environment;
- a general expert-system inference engine.

The demonstrated result is narrower:

> **A declared graph, profile, and construction blueprint can reproducibly reconstruct this worked Python example while preserving inspectable mappings between meanings, construction records, generated code, and bounded evidence.**

---

## Project map

```text
code-lexigraph/
│
├── code_lexigraph/
│   ├── __init__.py
│   ├── __main__.py
│   └── rehydration.py
│
├── examples/
│   ├── safe_fallthrough.bundle.json
│   └── reference.py
│
├── tests/
│   ├── test_rehydration.py
│   └── test_cli.py
│
├── docs/
│   ├── OVERVIEW.md
│   ├── DESIGN.md
│   ├── PROVENANCE.md
│   ├── VALIDATION.md
│   └── OPEN_DECISIONS.md
│
└── MANIFEST.sha256
```

---

## Read further

- **[Overview](docs/OVERVIEW.md)** — conceptual model and worked example
- **[Design and construction contract](docs/DESIGN.md)** — grammar, bindings, construction, and authority boundary
- **[Source roles and provenance](docs/PROVENANCE.md)** — human and AI contribution boundaries
- **[Validation](docs/VALIDATION.md)** — replay results and proof boundary
- **[Open decisions](docs/OPEN_DECISIONS.md)** — unresolved design and stewardship questions
- **[Integrity manifest](MANIFEST.sha256)** — retained payload hashes

---

## Status

**Prototype / research artifact.**

The graph, mappings, construction rules, and tests are inspectable inputs and evidence—not self-authorizing proof.

Licensing, wider runtime support, additional profiles, broader language backends, schema hardening, and release policy remain explicit future decisions.

<div align="center">

---

**Keep the reasons for code close enough to the code that they can still be inspected.**

</div>
