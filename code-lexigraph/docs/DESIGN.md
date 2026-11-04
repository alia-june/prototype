# Design and Construction Contract

## Data and construction

The prototype has three principal inputs: a retained code-lexigraph, selected profile bindings, and an ordered construction blueprint. The example bundle contains all three.

The retained graph identifies meanings, commitments, a local profile, a contract, a method, code roles, a conditional claim, and finite observations. Its 29 nodes and 43 relationships are preserved from the reviewed chat example.

The construction blueprint supplies 22 statement and handler records. Its eight explicit code mappings connect selected construction records to code roles and meanings. Two supporting declarations account for the Enum and JSON imports. These mappings describe intended relationships; they are not machine-checked semantic proofs.

## Current profile

Profile L01 selects the caller's exact valid JSON text as the required survivor. The boundary extends from entry into the system function through its return. Working state is parsed separately.

READY permits the operation path. ERROR skips decoding and the operation. COMPLETE reports normal return. EXCEPTION reports an ordinary Exception caught by the system function. These meanings are local to the example.

The example's required response is catching and returning the declared report. Other response contracts can require additional behavior. Preserving an interrupted working object, rollback, continuation, external effects, and persistence across process termination remain separate decisions.

## Grammar

The statement vocabulary consists of from-import, import, class, function, assignment, return, if, raise, expression, and try records. The try record contains one explicit exception handler.

Expressions distinguish names, selected bound names, string literals, attributes, calls, ordered dictionary pairs, and identity comparisons. Module, body, argument, parameter, and dictionary-pair arrays preserve declared order.

The builder supports the declared format and one profile. It validates selected bindings, identifiers, referenced graph endpoints, construction IDs, direct mappings, and construction coverage. Generated text must parse as Python before the result is returned.

The grammar description documents the builder's supported vocabulary. It is not a separate executable rule engine or a general Python grammar. Malformed or adversarial inputs are not comprehensively qualified by this prototype's finite refusal cases.

## Rehydration interface

The preserved builder returns a dictionary with Python source, readable contract text, construction-to-code mappings, inverse lookups, and construction spans. The original builder is retained unchanged in the library module.

Reference graph locations identify the retained reference source. Generated spans identify the reconstructed output. A successful reconstruction does not overwrite reference locations.

The readable view draws its commitments from the graph and its selected state representation from the bindings. Construction uses the blueprint. The reference source is used by the test suite for comparison and is not a builder input.

## Command-line boundary

The command-line wrapper reads one UTF-8 JSON bundle. It either emits the complete result as JSON to standard output or writes example.py, CONTRACT.md, and TRACE.json into an output directory.

Construction finishes before output-directory creation. Existing output filenames are checked before writes, and each new file is opened exclusively. A pre-existing output file causes refusal rather than replacement. Filesystem failures during a multi-file write can leave partial new output; this edition does not provide transactional directory publication.

The wrapper reports input, construction, and output errors with a nonzero status. It does not execute generated source. The test suite executes only the declared example.

## Authority and qualification

A selected binding, descriptive status, or passing test is data about a particular scope. It does not grant production permission or establish adoption of a universal policy.

Changes remain subject to the governing human approval process. This repository does not implement an operating-system permission interlock, global production gate, or general expert-system inference engine.
