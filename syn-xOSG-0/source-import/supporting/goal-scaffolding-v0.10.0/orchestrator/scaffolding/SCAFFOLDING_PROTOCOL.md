# Goal Scaffolding Protocol — GSP-001

## Objective

Allow the Operator to state a goal compactly while the Orchestrator wraps that goal in the exact xOSG-0 interpretive context needed by an LLM or downstream reasoning stage.

## Canonical process

```text
OPERATOR SYMBOLIC UTTERANCE
        ↓
SYNTAX PROFILE LOOKUP
        ↓
ENVELOPE PARSE
        ↓
PRESERVE GOAL VERBATIM
        ↓
EXPLICIT RULE-REFERENCE DETECTION
        ↓
RULE DESCRIPTOR PROGRAM
        ↓
MINIMUM REQUIRED xOSG CONTEXT
        ↓
PRE_CONTEXT + PAYLOAD + POST_CONTEXT
        ↓
DETERMINISTIC VALIDATION
        ↓
ATTESTED SCAFFOLD ARTIFACT
        ↓
STAGE / ROUTE UNDER CURRENT GATE
```

## No semantic inference from symbols

The parser reads symbols according to the active syntax profile. The Orchestrator cannot assign a meaning from appearance alone.

## Goal preservation

The payload is opaque data during wrapping. Context may be added around it, but not into it.

## Rule references

RDP-001 performs exact lookups. An unknown reference remains unresolved and is surfaced to the interpreting model as unresolved context.

## Data-touch minimization

Wrapping SHOULD be deterministic and requires only bounded parsing, exact identifier lookup, hashing, and template assembly. Semantic inspection of the payload is not required merely to construct the wrapper.

## Authority

```text
WRAPPING != EXECUTION
CONTEXT_INSERTION != AUTHORITY
CORE_ACCESS != PRIVILEGE
DESCRIPTOR != PERMISSION
```
