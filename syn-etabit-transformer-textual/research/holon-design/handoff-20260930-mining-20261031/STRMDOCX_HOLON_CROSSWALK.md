# Strmdocx–Holon Crosswalk

This crosswalk identifies compatible directions and unresolved integration decisions. It does not change Strmdocx code, storage or service behavior.

| Strmdocx direction | Holon/reference contribution | Compatibility | Required decision before integration |
| --- | --- | --- | --- |
| Immutable edit/transformation streams | Independently represented units plus references support non-destructive lineage | Strong conceptual fit | Define stream, fragment, transformation and occurrence identities |
| New stream per continuous edit | Reference-addressed results can retain prior targets and ordered transformation evidence | Strong conceptual fit | Define whether result references source blocks, transformations, rendered bytes or all three |
| Logical transformation ordering | Relationship/coordination must be explicit and broader than historical depth | Compatible | Define dependency, precedence, reversal, commutation and cancellation relationships |
| Deduplicate reversed changes | Separate transformation identity from rendered outcome | Compatible in principle | Define semantic equivalence and proof required before bypassing operations |
| Inspect transformations in and out of order | Multiple ordering/projection views are anticipated but unresolved | Compatible with caution | Define canonical versus inspection-only views and cycle bounds |
| Render then add new stream | Stage/verify/commit discipline offers a safety pattern | Candidate lesson | Specify render fidelity, verification, commit receipt and failure handling |
| CPU model then GPU representation | Native/reference model can remain independent of rendering substrate | Compatible | Define transfer/profile fidelity and GPU resource/object identities |
| Glyph/component/word/sentence/paragraph assemblies | Recursive compositional holons and references can represent multiple scales | Conceptual fit | Decide atomics, occurrence references and whether scalar symbols are holons |
| Per-system codepages/maps | Separate catalogs and profiles can reference shared semantic units | Compatible | Define map identity, version, namespace and reconstruction guarantees |
| HTML/Python native maps | Closed boundary profiles can coexist with extensible native references | Compatible | Define native token records versus rendered syntax and escaping |
| Etabit multiple drives | Shared targets may participate in several referenced maps | Conceptual fit | Define drive identity, cross-drive relationships, lineage and authority |
| WordNet transmigration | Source-faithful, decoded, construction, inferred and enriched maps should remain separate | Strong provenance fit | Define map schemas and attribution; do not flatten inferred data into WordNet claims |
| Agentic control last | In-band claims and references do not grant execution authority | Strong safety fit | Define external authority, resolver permissions and effect policy only at integration stage |

## Important alignments

### Preserve intermediate transformations

Holon/reference separation supports retaining source units, transformation records and resulting streams without overwriting the source. The inactive UPTI-SF specification contributes the useful pattern of staging, verification and visible recovery. Neither source supplies Strmdocx transformation semantics.

### Rendered view is not native truth

A renderer may resolve references into Markdown, HTML, Python, DOCX or a GPU structure. That output is a view/result with its own identity and fidelity record. JSON nesting or rendered containment must not be mistaken for native ownership.

### Bypass needs semantic evidence

The proposed optimization—omitting later-reversed operations—cannot rely on textual similarity alone. It needs transformation algebra or an application-specific equivalence proof. For example, whole-document font changes may cancel under a specific scope and inheritance model, while apparently reversed edits may still differ in provenance, selection boundaries or side effects.

### Multiple maps without flattening

A single source unit may be referenced by grammar, syntax, rendering, relationship and knowledge maps. Each map needs identity, version, source basis and derivation. “Everything is relative and replaceable” is compatible with replaceable map profiles, not with losing the references that explain which profile produced a result.

## Boundaries exposed by the candidate payloads

- The v0.1 packet is too application-specific and nested to become the native Strmdocx reference store without redesign.
- Its separation of data, knowledge, execution and provenance is a useful anti-collapse lesson.
- Its inert artifact reference is a useful model for safe unresolved external objects.
- Its use of native null conflicts with the later sentinel-holon direction and needs a versioned adapter if reused.
- Its `DECISION` claim class must never substitute for the user's production approval.
- The v0.2 staging API demonstrates local byte preservation but is not a transport or service integration.

## Recommended next design work

The next bounded design scope should define one small native occurrence/reference form and exercise it on a tiny Strmdocx example: two immutable text blocks, one transformation, one result, one relationship/metadata record and two inspection orders. That future scope would require a separate production proposal because this mining clearance does not authorize schema or code implementation.
