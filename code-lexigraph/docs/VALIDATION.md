# Validation Record

Repository preparation date: 2026-11-04.

## Historical basis and current replay

The retained chat example recorded three repeatable constructions, a matching Python syntax structure, four behavioral cases, four construction refusals, eight code mappings, and 22 construction records.

This preparation recovered the named source blocks, preserved the reference and builder, and replayed the example in the local repository. Historical observation records embedded in the graph remain unchanged; the checks below report the current repository replay.

## Runtime and commands

Validation ran on Windows using Python 3.14.3 and the standard library.

```text
python -B -m unittest discover -s tests -v
python -m code_lexigraph examples/safe_fallthrough.bundle.json --out build/example
```

The suite passed all 19 tests: 11 construction/behavior tests and eight command-line integration tests. The documented generation command also completed successfully and created the three declared outputs.

## Construction and behavior

- Three constructions produced identical source, readable text, mappings, and spans, including a JSON round-trip with object keys sorted.
- The input bundle remained unchanged during construction.
- The reconstructed program matched the reference program's parsed Python syntax structure, excluding formatting, comments, and source-location attributes.
- The eight generated code locations matched their parsed code elements.
- Inverse mappings resolved for the direct code/meaning links and supporting declarations.
- The 22 construction records were accounted for by direct mappings, enclosed constructs, or supporting declarations.
- Successful nested mutation preserved the selected survivor.
- Nested mutation followed by RuntimeError preserved the selected survivor and returned the declared system response.
- The ERROR gate prevented decoder and operation invocation.
- Separate calls received independent nested working containers.

The four construction refusal cases passed: missing survivor, unresolved survivor, missing construction target, and unknown construction instruction. These finite cases do not qualify every malformed input.

## Command-line integration

The eight integration tests passed:

- JSON output matched the Python interface's complete result.
- Directory output contained the expected source, readable contract, and trace data.
- A pre-existing output file was preserved, with no new sibling outputs created in that tested refusal.
- Missing input was reported without output-directory creation.
- Invalid JSON was reported without output-directory creation.
- An unresolved survivor binding was reported without output-directory creation.
- Input and output paths containing spaces worked.
- A wrong top-level JSON shape produced a concise error without output-directory creation.

Filesystem failures during a multi-file output write are not qualified as transactional or crash-atomic.

## Source fidelity and public payload

The restored 204-line builder, 34-line reference, and construction bundle matched their selected chat source blocks. The overview copy matched its approved source, and the original overview remained unchanged.

The public payload contains 15 files plus MANIFEST.sha256. Six Markdown documents contain seven local documentation links. Core Markdown structure, paired code fences, link targets, UTF-8 text, and LF line endings were checked.

The payload was screened for known account identifiers, absolute workstation paths, email addresses, private chat UUIDs, and tool-specific locators. None of those known classes was found. This finite screen does not establish anonymity against every external correlation.

Generated build outputs, QA scratch data, and bytecode caches are ignored by Git. Private recovery archives and identifying provenance material were not included.

## Original local preparation and integrity

MANIFEST.sha256 covers the 15 payload files and excludes itself, Git metadata, ignored build outputs, and caches. Its entries are checked against the delivered bytes.

In the original local preparation, Git was initialized on main with the 16 intended files staged for review. That phase created no commit or remote publication. Payload/index agreement and the staged whitespace check are part of the final seal.

## Hosting-repository staging

This copy is prepared under code-lexigraph/ in the private hosting repository. The existing container README is outside this component and is preserved.

Executable sources, reference, construction bundle, tests, and the public overview retain their source bytes. The README, provenance, open-decision, and validation documents are adapted for the nested location. The component manifest is resealed after those adaptations.

Nested-location replay passed all 19 tests under Python 3.14.3. The documented construction command also completed and produced the three declared review artifacts.

Transport and publication status are reported separately from this validation record. Repository location does not widen the example's qualification scope.

## Proof boundary

These results support repeatable reconstruction of this declared example under the tested interpreter. They do not establish formal semantic proof, general code synthesis, a supported runtime range, arbitrary-input hardening, persistence across process termination, or guarantees about external effects.

The selected immutable-text survivor remains a local profile choice. Wider sentinel, reference/version, resource-budget, and process-qualification policies remain open decisions.
