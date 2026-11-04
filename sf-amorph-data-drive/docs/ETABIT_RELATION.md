# Candidate relation to Etabit

Status: candidate relationship; not admitted integration.

[Etabit Schema](../../etabit-schema/README.md) describes generalized multi-drive construction with heterogeneous source and referential/bitmap drives, optional out-of-band meta disks, and internally distributed Cypher Disk authority. It produces an Experience Orchestration Drive.

sf-AmorphDataDrive is narrower at its base: raw D0 is flat, ordered, enumerated, and carries no identity or metadata. D1 supplies relation/interpretation; D2 supplies composition/coherence.

An sf-AmorphDataDrive may eventually qualify as a strict raw-source substrate or profile used by an Etabit construction. That is not yet an implementation, dependency, admission, or deployment decision.

Etabit does not relax D0:

- an Etabit source drive is not automatically D0;
- arbitrary-object source semantics do not apply to raw D0;
- an out-of-band meta disk does not authorize metadata on D0;
- Cypher Disk authority is not imported into sf-AmorphDataDrive;
- generic Etabit drive IDs are not automatically member sf-UUIDs;
- historical Etadisk A/B/C roles are not automatically the current ID/data/metadata topology;
- a reference, codepage, or result does not grant execution authority.

## Required cross-map

1. Qualify the substrate and interface exposed to Etabit.
2. Map sf-UUID, drive, object, copy, and replacement identities.
3. Specify reference ordering, multiplicity, bounds, failures, and reconstruction.
4. Relate optional Etabit meta disks to sf-Edabit roles without weakening D0.
5. Define whether gestalt/gesple is an Etabit object, sf-Edabit composition, or bridge object.
6. Define constructor, reader, Cypher, attester, and operator authority.
7. Preserve refusal, evidence, and one-way-transfer boundaries.
8. Review recursion, recovery, versioning, and independent attestation.

Until this is reviewed, the projects remain separate related research.
