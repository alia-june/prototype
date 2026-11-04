# Code-Lexigraph: From Human Code Theory to Working Examples

This is an example of human-authored code theory and human-composed decomposition, with AI automation working over an explicit expert system contract as the material is rehydrated for use.

The code-lexigraph connects programming meanings, requirements, construction rules, code structures, and evidence. Its purpose is to keep the reasons for a program attached to the structures that implement them, so both can be inspected, questioned, and reconstructed.

## From decomposition to construction

The process begins by examining an idea, method, or existing program and separating its useful constituents: definitions, assertions, assumptions, conditions, responsibilities, and procedures. Their relationships remain explicit. Order, alternatives, scope, and unresolved decisions travel with the material.

Construction then proceeds upward. Foundational meanings define the vocabulary; human commitments and project choices establish contracts; contracts inform methods; declared construction instructions produce code. Evidence records what particular checks establish about the result.

Symmetry means traceability in both directions. A reviewer can follow a requirement into its construction and code roles, then follow those roles back to their meanings, assumptions, and source basis. This supports review without treating a connection between records as proof that a requirement has been satisfied.

## Human theory and AI automation

The human contribution supplies the theory, decomposition method, governing requirements, and decisions about adoption and application. AI assists with making relationships explicit, proposing structured formulations, constructing examples, and carrying out bounded checks.

The expert system contract provides the declared meanings, bindings, conditions, and construction rules for the example. Requirements, implementation intentions, local choices, and observations retain distinct roles. A generated statement does not acquire authority merely because it appears in a structured artifact.

Rehydration brings this retained material into usable form. In the demonstrated case, an explicit blueprint and selected profile reconstruct a readable contract, a Python program, and mappings between the construction records, code elements, and meanings.

## The safe-fall-through example

The worked example applies a central requirement: required JSON state must survive an exception, while the surrounding system owns the exception response.

Its local profile selects the caller's original JSON text as the required survivor. The operation receives a separately parsed, mutable working object. An error sentinel can prevent decoding and execution through a declared guard. An exception state records the system's response when an ordinary exception occurs.

The sentinel's execution effect comes from its declared interpretation and the structure that consumes it. Preservation and response compliance are assessed separately.

This example makes its survivor choice explicit. Other projects may require an interrupted working state, an earlier state, or several states to remain available, with different preservation mechanisms and response policies.

## What was demonstrated

The initial example contains 29 graph entries and 43 relationships. Rehydration adds 22 construction records, eight direct code mappings, and two supporting import declarations.

The bounded checks established that:

- Three constructions produced identical source, readable text, mappings, and locations under the tested interpreter.
- The reconstructed program matched the reference program's parsed Python syntax structure, allowing formatting and comments to differ.
- Four behavioral cases passed: successful nested mutation, mutation followed by an exception, execution blocked by an error sentinel, and independent nested working representations.
- Four negative checks refused a missing survivor binding, an unresolved survivor binding, a broken construction reference, and an unknown construction instruction.

Generated code locations are recorded separately from the retained reference locations. This preserves the distinction between the source used for comparison and the reconstructed output.

## Current scope

The demonstration covers one declared profile and a restricted construction vocabulary. The blueprint and its mappings remain explicit editorial inputs. The builder checks and uses those inputs; human review establishes the intended meaning of their connections.

These results support repeatable reconstruction of this example. Formal semantic proof, general code synthesis, cross-version repeatability, crash recovery, and guarantees about external effects remain outside the demonstrated result.

The broader aim is to make programming knowledge reusable while preserving its meaning, conditions, responsibilities, and evidence as it moves between human explanation, structured representation, and working code.
