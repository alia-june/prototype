# Syn-Etabit Transformer — Textual architecture

This project explores reference-native document construction and retains a CPU compatibility service. The research model explains how text and structure could be assembled and revised without destroying the source. The service implements a bounded set of document operations. Each has its own evidence and limits.

## Research construction model

1. **Build from maps.** Base symbol maps and structural assembly maps provide reusable definitions. Definition identity, map identity, and the identity of a selected occurrence are separate: two occurrences can refer to the same immutable definition without becoming the same occurrence.
2. **Resolve a document in context.** Markdown supplies primary text. A JSON plan can refer to maps, structure, metadata, assets, transformations, and emission requirements. Context and selection determine which occurrence is being interpreted or edited.
3. **Retain transformations.** A revision can create a successor stream while preserving the earlier stream and shared definitions. The transformation catalogue keeps ordered operations, intermediate occurrences, parentage, and logical outputs. A reducer can avoid unnecessary work without erasing the history that explains it.
4. **Keep emission separate.** The intended **Eject → Transform → Ejection** boundary hands an immutable conversion package to a target-format adapter and retains the derived artifact and receipt separately. Rendering or exporting a document does not make that output the authority for its native state.

The [construction overview](README.md#construction-overview) and [current proof boundary](README.md#current-proof-boundary) describe the native CPU construction work, including in-memory publication. That evidence does not establish a live Etabit mount, physical encoding, durable publication on that substrate, or multi-writer recovery. [Etabit Schema](../etabit-schema/ARCHITECTURE.md) describes a related draft model and does not supply those missing capabilities.

## Retained CPU compatibility service

The [service](service/README.md) keeps the `docstream-cpu` distribution, `docstream_cpu` module, and `docstream-local` CLI for compatibility. Its CPU reference model and persistent service adapter have different responsibilities:

| Boundary | Retained behavior | What it does not establish |
| --- | --- | --- |
| **CPU model** | Validates and stages ordered batches, retains logical outputs, and lets callers inspect recorded prefixes. A semantic commit advances the in-memory head explicitly. | Durability or visual correctness from an in-memory result. |
| **Persistent service** | Uses a separate SQLite-backed adapter for durable local requests and receipts. Importing the library does not start a listener. | Durable Etabit Drive publication, automatic startup, or agent registration. |
| **Rendering and format adapters** | Supports an explicit rendered-commit path and bounded Markdown/DOCX import and export. Detected conversion losses are refused by default; an explicit acceptance retains diagnostics in the receipt. | Unrestricted document compatibility, Word pagination fidelity, or completion of the proposed external ejection migration. |

Read the [CPU contract](service/docs/CPU_CONTRACT.md), [service contract](service/docs/M2_SERVICE_CONTRACT.md), and [format contract](service/docs/M4_FORMAT_CONTRACT.md) for the corresponding interfaces. The [M4 validation record](service/docs/M4_VALIDATION.md) reports results for its declared fixtures and explicitly notes later fuzzy failures. It should not be read as an unrestricted compatibility result.

## Where to start

- To understand the design, follow the [project README](README.md) from construction through document use and the proof boundary.
- To inspect or run the retained service examples, use the [service README](service/README.md) from `service/`. Its commands assume a prepared virtual environment that inherits bundled runtime packages. They are not a standalone installation recipe; this guide does not qualify a new environment or reproduce the recorded tests.
- For future work, treat CPU semantics as the reference. GPU acceleration and agentic control are later integration stages. The [integration gate](docs/integrations/INTEGRATION_GATE.md) preserves the approval boundary for activating those integrations.
