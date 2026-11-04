# Artifact Lineage and Provenance

## Available historical binaries preserved verbatim

The final bundle includes every historical archive that is actually available in the current conversation/container:

| Archive in this bundle | Source | Meaning |
|---|---|---|
| `history/archives/xOSG-0_original.zip` | user upload | original portable reference artifact |
| `history/archives/xOSG-0_v0.2.0_actualized.zip` | generated in this chat | first actualized runtime workspace |
| `history/archives/xOSG-0_initial_fuzzy_suite.zip` | generated in this chat | first loose/fuzzy suite and its 58-case report |

The archives are also unpacked under `history/extracted/` for direct inspection.

## Missing historical binaries

Earlier assistant responses described downloadable **v0.3.0 hardened** and **v0.4.0 loose/fuzzy-hardened** ZIPs. Those archives are not present in the current conversation file inventory or active `/mnt/data` filesystem.

This final artifact therefore does not create fake historical binaries and label them as originals. The later hardening requirements described in those responses are instead implemented in the new consolidated **v0.5.0** source tree and verified by the included tests.

## Consolidated build

`v0.5.0` is a new consolidation created from:

- the exact available historical archives;
- the visible chat requirements and reported findings;
- the original four-layer architecture;
- the actualized v0.2 runtime;
- the initial fuzzy harness findings;
- the subsequent hardening requirements described in the thread.

The purpose is faithful consolidation with transparent provenance, not retroactive reconstruction of missing binaries.
