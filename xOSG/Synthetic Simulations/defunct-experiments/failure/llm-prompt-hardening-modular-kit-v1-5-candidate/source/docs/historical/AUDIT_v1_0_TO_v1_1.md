> **FABRICATION FLAG — GENERATED TEXT BEGINS**

# Candidate 1.0 Audit and Candidate 1.1 Disposition

`[GENERATED-VERIFICATION-REPORT]`

| Candidate 1.0 finding | Effect | Candidate 1.1 disposition |
|---|---|---|
| Single-profile selector treated profiles as a hierarchy | Combined effects could lose required controls | Repeated/comma-separated profiles now produce a module union before dependency closure |
| Resident and template capsule schemas differed | Actor, authority, unknown, and checkpoint state could be lost | One canonical ordered schema governs A, B, templates, compression, and tests |
| Raw template substitution | Multiline or fenced values could escape their field | Values are encoded as one ASCII JSON string with structural characters escaped |
| Arbitrary output overwrite | Modules, configuration, or parent could be overwritten | Package writes are limited to generated Markdown in `builds/`; existing builds require explicit atomic replacement |
| Unknown disable and set names could be ignored | Typographical errors could produce unintended configuration | Unknown variables/modules and duplicate assignments now fail closed |
| Dependency closure could silently undo a disable | Effective configuration could differ from operator intent | Dependency, mandatory, and selected-profile removals are rejected |
| Literal `UNKNOWN`/`UNSPECIFIED` values passed placeholder checks | An inert template could appear operational | Headers expose instance readiness; `--require-ready` refuses unresolved required values |
| No complete fallback when offloading could not run | Continuity depended on the missing capability | Resident degraded continuity contracts the task and emits a bounded packet without false persistence claims |
| Validation was descriptive only | Regressions were not mechanically repeatable | Standard-library unit tests now cover assembly, composition, capsule parity, encoding, protected outputs, readiness, and fallback presence |
| External parent identity claim was not independently reproducible from the ZIP | Self-consistency could be mistaken for external provenance proof | Provenance now states the exact boundary of what this package can verify |

These dispositions are generated candidate implementations. Test success establishes the listed mechanical invariants only; it does not establish model-behavior immunity.

> **FABRICATION FLAG — GENERATED TEXT ENDS**
