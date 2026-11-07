# Etabit Schema architecture

Etabit describes how a construction could refer to source objects across multiple drives while keeping interpretation and authority explicit. The repository provides a [v0.2 research descriptor](schema/etabit-project.v0.2.schema.json), a [worked descriptor](examples/four-symbol-source.v0.2.json), and validation checks. The draft is **not admitted for execution**. The earlier [v0.1 descriptor](schema/etabit-project.schema.json) remains a separate source record.

## Roles in a construction

| Role | What it describes | What remains open |
| --- | --- | --- |
| **Source drive** | Supplies addressable objects or symbols. The four-symbol example is one source, not a limit on object types. | A payload type label does not establish an encoding or a decoder. |
| **Referential drive** | Describes relationships or assemblies by referring to drive and object identities. | Reference grammar, order, multiplicity, cycle handling, and bounds are not a runtime contract yet. |
| **Constructor and optional out-of-band metadata** | The constructor would assemble admitted references. Optional metadata is scoped to the constructor and declared unavailable to readers. | A descriptor does not implement isolation, disclosure control, or permission to write. |
| **Cypher Disk** | Describes distributed authority responsibilities among its own constituents. | The draft does not select a quorum, voting protocol, precedence rule, or physical mechanism. |
| **Codepages** | Associate representations and referential drives with a process-specific interpretive context. | Recognition or translation does not grant execution rights. |
| **EO-Drive and reader** | Identify the intended constructed outcome and an admitted reader boundary. | No persistent EO-Drive format, working mount, or reader ABI is established. |

These roles describe relationships, not a fixed drive count, a prescribed physical topology, or an executable sequence. The [architecture overview](README.md#architecture-at-a-glance) explains the broader model and its access boundaries.

## What validation checks

The descriptor distinguishes stored `Error` and `Unknown` objects from operational outcomes such as an I/O failure or an unresolved reference. It records refusal and revocation protocol status separately. These distinctions let a checker reject a malformed description without pretending to know how a live system would report, refuse, or revoke access.

JSON Schema can check shape and declared constraints. The [v0.2 test script](tests/test_v0_2.py) also checks selected graph relationships, such as unique identities and valid drive references. This extra check matters because schema validation alone does not enforce every cross-object relationship. A passing descriptor does not demonstrate a working reader, constructor, Cypher authority mechanism, or durable store.

Start with the [validation instructions](README.md#validation-and-how-to-run-it), then read the [audit reconciliation](docs/V0_2_AUDIT_RECONCILIATION.md) for required negative checks and unresolved contracts. The [Syn-Etabit Textual architecture](../syn-etabit-transformer-textual/ARCHITECTURE.md) is a related but separate document implementation and research line, with its own evidence. Its CPU results do not admit this descriptor or establish a shared runtime.
