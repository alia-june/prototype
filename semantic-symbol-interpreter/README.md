# Semantic Symbol Interpreter

A research prototype for interpreting symbols in context and tracing what their messages imply.

## Theoretical use cases

- **Disambiguate notation in context.** The same `|` can be a shell pipe, a mathematical relation, or a mark defined by a local legend. An interpretation system could keep those readings available and record what makes one fit this occurrence.
- **Work out what a notice implies.** A notice that says `IF ALARM ACTIVE -> EVACUATE` expresses a condition and a directive. It does not establish that the alarm is active. A system could distinguish the instruction, the evidence that activates it, and any consequence that still cannot be inferred.
- **Compare and test competing readings.** A reviewer could ask why one grouping, reading order, or symbol meaning was preferred, which evidence each alternative relies on, and what would change if that evidence were removed. The same approach could help test whether a parser invents a relationship, ignores a local convention, or resolves a conflict prematurely.

These are research directions. **v0.2.1 is a rule-based prototype for synthetic text and supplied textual descriptions.** It includes an adversarial validation harness and examples that exercise interpretation from source to candidate output. Diagram analysis here is a theoretical application, not a claim that the prototype reads diagram images.

## How the interpreter approaches meaning

The interpreter preserves the **whole message bearer**—the source that carries the message—before interpreting a part of it. A nearby line, a heading, or a legend elsewhere in the bearer can change the meaning of the same visible mark. The original source stays intact as interpretations are proposed.

The architecture distinguishes `OBJECT → SYMBOL → SIGN → MESSAGE → IMPLICATION`. An observed mark, a candidate symbol meaning, a sign formed in context, its message, and a consequence inferred from it are separate records or questions. Evidence can connect them without requiring a single rigid reading order.

The design applies four independent lenses at the symbol, sign, message, and implication levels:

| Lens | Question |
| --- | --- |
| **Atomics** | What parts make up this candidate? |
| **Dilation** | What changes when we consider more of the evidence already preserved? |
| **Macro dynamics** | What does this candidate do in the larger structure—for example, bind an expression, change a mode, or activate a conditional consequence? |
| **Meta context** | Which notation, convention, local legend, or other interpretive regime applies? |

The prototype exercises parts of this design. It does not yet emit a complete four-lens analysis for every candidate.

## How it works

1. **Preserve the input.** The interpreter keeps the whole supplied bearer, including its lines and whitespace, and records where each observed line occurs. Rules can use a derived view of the text without changing the original. In the alarm example, `ALARM ACTIVE` and `IF ALARM ACTIVE -> EVACUATE` remain separate source lines.
2. **Apply rules to the evidence.** The prototype recognizes the second line as a conditional directive and looks for a separate line establishing the alarm state. The words `ALARM ACTIVE` inside the directive do not count as that evidence. An active-state line supports activation; a missing state leaves activation uncertain, and conflicting state lines retain both alternatives without activating the directive.
3. **Record the interpretation.** The engine writes [`CandidateResult`](schemas/candidate-result.schema.json) JSON. Its structured `interpretation` field retains the bearer, source spans, rule references, candidates, alternatives, and uncertainty assessments. The activation implication links to source evidence and to a message or sign candidate. Those links can cover whole source segments, so they show what the rule relied on without proving that every conclusion follows.
4. **Grade the result separately.** The interpreter uses only the bearer and fixture identifier. The validator compares the result with the fixture’s expected claims, required unknowns, and explicitly forbidden claims. It also checks that the structured result preserves the fixture source and that its evidence references are valid. A passing result means it met those checks for that fixture.

## Run the prototype

Use Python 3.10 or newer. No third-party packages are required. Run these commands from the repository root, or from the extracted package directory containing `engine/`, `runner/`, and `fixtures/`:

```sh
python engine/minimal_interpreter.py fixtures/wb-021.json -o candidate.json
python runner/run_validation.py candidate.json
```

[`WB-021`](fixtures/wb-021.json) supplies this synthetic bearer:

```text
ALARM ACTIVE
IF ALARM ACTIVE -> EVACUATE
ASSEMBLY POINT A
```

The first line supplies the state that activates the conditional directive. The prototype emits `implication:evacuation directive is active`, and the validator reports `"pass": true` for the fixture. [`WB-031`](fixtures/wb-031.json) tests the contrasting case: the condition appears in the directive, but no source line establishes that the alarm is active. In that case the prototype keeps activation uncertain.

## What the prototype establishes

The recorded **v0.2.1** run passed all five packaged regression scripts. The full fixture benchmark passed **48 of 74 cases (64.9%)**, with **26 failures** retained in the [benchmark report](engine/benchmark-report.md). This is a result for the supplied corpus, not an estimate of real-world accuracy. The [validation report](validation/VALIDATION_REPORT.md) describes the checks and their limits.

Fixture coverage measures whether a mechanism is represented in the suite. A covered category does not imply that the engine can interpret every case in it. Likewise, the grader's overreach count detects claims explicitly forbidden by the fixture; a count of zero does not establish that every extra claim is supported.

## Open work

- Give repeated symbol occurrences separate identities and model their local scopes explicitly.
- Represent typed interpretation transitions, independent lens analyses, and separate presentation and semantic forms.
- Strengthen history retention and tests for unsupported claims beyond explicit forbidden lists.
- Classify the remaining benchmark failures by missing mechanism and add support in groups that can be tested independently.

The prototype does not perform OCR, computer vision, audio or tactile perception, or general natural-language interpretation. Its current outputs are for inspecting and testing interpretations of supplied data.
