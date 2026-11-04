# Code-Lexigraph Prototype

This is an example of human-authored code theory and human-composed decomposition, with AI automation working over an explicit expert system contract as the material is rehydrated for use.

The prototype connects programming meanings, scoped requirements, construction rules, code roles, and evidence. Its current working case reconstructs a safe-fall-through Python example from a retained graph, explicit profile bindings, and an ordered construction blueprint.

The human contribution supplies the theory, methodology, requirements, and adoption decisions. The graph formulation, construction blueprint, demonstration code, and checks include AI-assisted work. Requirements, implementation intentions, local choices, and observations retain distinct roles.

## Run the example

From the hosting repository root, enter this component before running the commands:

```text
cd code-lexigraph
```

The demonstrated workflow uses Python's standard library.

```text
python -m code_lexigraph examples/safe_fallthrough.bundle.json --out build/example
```

The command creates:

- `build/example/example.py`: the reconstructed Python source.
- `build/example/CONTRACT.md`: the readable contract.
- `build/example/TRACE.json`: generated spans, construction mappings, and inverse lookups.

Choose a fresh output directory for a saved run. Existing output files are preserved. Without `--out`, the command returns the complete construction result as JSON on standard output:

```text
python -m code_lexigraph examples/safe_fallthrough.bundle.json
```

Construction returns source and descriptive views. It does not execute the generated program. The tests execute the declared example to examine its behavior.

## Replay the checks

```text
python -m unittest discover -s tests -v
```

The suite covers repeatable construction, comparison with the reference program's Python syntax structure, generated locations and inverse mappings, four behavioral cases, four construction refusals, and the command-line workflow.

The behavioral cases examine successful nested mutation, mutation followed by an exception, an error sentinel preventing decoding and operation invocation, and independent nested working representations. Preservation of the selected survivor and system response are assessed separately.

The current validation runtime is Python 3.14.3. A supported Python version range remains an open decision. See [the validation record](docs/VALIDATION.md) for the actual repository replay and its limits.

## Use the Python interface

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

The result also contains `trace`, `inverse`, and `spans`. Code locations retained inside the original graph refer to the reference program; generated locations are returned separately.

## Understand the scope

The local profile preserves the caller's exact JSON text while an operation receives a separately parsed, mutable working object. Error and exception sentinel categories have declared local meanings. The surrounding system owns the exception response.

This edition retains 29 graph entries and 43 relationships, with 22 construction records, eight direct code mappings, and two supporting import declarations.

The builder uses explicit construction instructions. The meanings assigned to their connections remain reviewable editorial inputs. The implementation supports this declared example and restricted grammar; it does not establish general code synthesis, formal semantic proof, crash recovery, or guarantees about external effects.

## Read further

- [Public overview](docs/OVERVIEW.md)
- [Design and construction contract](docs/DESIGN.md)
- [Source roles and provenance](docs/PROVENANCE.md)
- [Validation and proof boundary](docs/VALIDATION.md)
- [Open decisions](docs/OPEN_DECISIONS.md)
- [Payload integrity manifest](MANIFEST.sha256)

Hosting, licensing, wider runtime support, and additional profiles remain explicit decisions. The prototype records evidence without turning an acceptance label into authority.
