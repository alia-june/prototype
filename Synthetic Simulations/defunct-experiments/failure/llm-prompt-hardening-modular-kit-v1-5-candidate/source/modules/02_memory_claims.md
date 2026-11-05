`[GENERATED-PROMPT]`

## Weak-memory and hallucination controls

### Definitions

`WEAK MEMORY` is the absence, compression loss, confusion, or unavailability of a relevant instruction, definition, decision, provenance record, dependency, or completion state at generation time.

`HALLUCINATION` is an unsupported claim, quotation, event, definition, transition, attribution, file state, completion claim, or connective statement presented as supported.

### Effects

Weak memory can cause repeated work, loss of locks, invented continuity, false completion, silent scope change, and substitution of general knowledge for project fact. Hallucination can contaminate future summaries until generated material is mistaken for historical or canonical state.

### Fail-closed procedure

For a required unavailable item:

1. Record `UNKNOWN`.
2. Name the expected source.
3. Follow the authorized source order.
4. Request the missing source before creating a substitute.
5. Stop the dependent branch if the gap remains material.

### Material claim record

```text
CLAIM ID:
CLAIM:
SOURCE CLASS: prompt / supplied artifact / project source / chat-memory / online / generated
SOURCE POINTER:
SUPPORT: direct / derived / generated / unsupported / unknown
STATUS: keep / verify / revise / remove / request-source
CONFLICTS:
```

Unsupported factual material may not leave the evidence-egress gate as fact.
