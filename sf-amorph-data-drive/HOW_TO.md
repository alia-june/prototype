# How to review a change to sf-AmorphDataDrive

This is a reading and review guide for the published specifications. It keeps the locked storage boundary, the proposed member identity contract, and the unresolved design work distinct. It is not a guide to provisioning a drive or running a storage service.

## Start with the controlling baseline

Read [locked v0.3](specifications/sf_edabit_amorph_data_drive_locked_spec_v0_3.md) before looking at a successor proposal. Ask which layer a claim affects:

| Layer | Question to ask during review |
| --- | --- |
| **D0 — existence** | Does the proposed change keep the raw values free of identity, metadata, interpretation, and composition structures? |
| **D1 — relation / interpretation** | Which external relationship or interpretation is being described? Does it leave the raw values intact? |
| **D2 — composition / coherence** | Which relationships are being composed, and what makes the result coherent? |

Use the [historical v0.2 baseline](specifications/sf_edabit_amorph_data_drive_locked_spec_v0_2.md) to examine lineage. Do not substitute it for locked v0.3 when reviewing a current claim.

## Review the identity proposal in its own scope

Read the [proposed sf-UUID member identity contract](contracts/SF_UUID_IDENTITY_CONTRACT_v0.1_PROPOSED.md). Its subject is a **logical member**. The proposed identifier is an opaque token, not a raw value, D0 position, or physical drive location. Use the proposal to find the stated rule for issuance, duplicate or collision handling, and continuity through a copy or replacement. Do not infer continuity from equal payload bytes alone.

For example, if a change says that a replacement drive inherits a member identity, separate the two subjects first: **which logical member is claimed to continue, and which physical object was replaced?** Then point to the applicable proposed rule and record the evidence it would need. Do not place the identifier in D0 or treat the proposal as a locked rule merely because the example fits it.

## Record what the change would and would not settle

1. Cite the baseline passage the change must preserve.
2. Cite the proposal or current direction the change relies on, with its status. If the claim crosses from proposal to controlling specification, identify the explicit acceptance or lock that would be required.
3. Keep the [open decisions](docs/OPEN_DECISIONS.md) visible. The member identity proposal does not settle physical ID/data/metadata topology, bitmap mapping and ordering, or packing and recursion contracts.
4. Check the [source and proof boundary](docs/SOURCE_BOUNDARY.md) before citing an export check or reconciliation summary. File identity and documentation consistency do not establish operating behavior or a production implementation.

Use the [project map](README.md#project-map) to find the current direction and supporting evidence. The [Etabit relationship note](docs/ETABIT_RELATION.md) is a comparison between separate projects; it does not import Etabit authority or execution semantics into this baseline.
