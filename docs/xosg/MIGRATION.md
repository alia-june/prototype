# xOSG migration from OpenSurface

Date: 2026-11-05

## Source and destination

- Source: `dastardlyrat/OpenSurface`, revision `276957db0f374edf6fc02b6919e2ec42c8960290`, subtree `xOSG/`.
- Destination: `alia-june/xOSG-prototype`, preserving the existing project families and adding this `xOSG/` tree.
- Authority: explicit approval in the migration chat for public publication of the reviewed current source family, followed by verified source working-tree cleanup. Earlier private-only publication decisions remain historical.
- Source coverage: 100 files; DWSK 37, Naked Shell 1, Synthetic Simulations 61, family overview 1. No source file is silently omitted.

The [manifest](MIGRATION_MANIFEST.json) records original and destination file digests, byte-preserved files, and documentation/inventory edits. Executable source is unchanged. Existing destination history and project files remain in place. This is a clean current-tree import; private OpenSurface history is not grafted into this public repository.

## License and attribution

The original root MIT license and its `2026 dastardlyrat and OpenSurface contributors` copyright notice are copied to [LICENSE](LICENSE). OpenSurface's `REUSE.toml` applied an aggregate MIT annotation to `xOSG/**`; that grant and attribution continue for this migrated tree. This record is not a claim of whole-repository REUSE compliance.

Existing file notices remain intact. The failed experiment also retains its own MIT license and third-party notices. The optional m.A.R.S. engine and other omitted payloads are not bundled or relicensed. Source receipts identify retained private artifacts without redistributing them.

## Evidence and historical records

DWSK retains the merged R4 repairs and its dated [source-validation report](../../amorphous-durable-ai-workspace/VALIDATION_REPORT.md): 244 R4 checks, plus 48 overlapping development-entrypoint checks. The migration runs a fresh 48-check fixed unit/self campaign on Windows in ordinary and optimized Python. These counts overlap and must not be added as independent coverage. Older binaries, installed-package checks, and artifact hashes remain historical. No new version, wheel, release tag, installed result, physical power-loss guarantee, or cross-platform qualification is created.

Synthetic Simulations' private v0.4 control-plane runtime is not included. Its published documentation and the sanitized failed modular-kit tree are migrated. The failed record retains 42/43 original Windows intake checks; the cleaned-source report records 35/36. Neither is rerun or repaired here. Earlier private-only visibility fields are preserved as dated evidence, not statements about the current public repository. The source provenance report's unresolved-license sentence is also retained as historical text; the later MIT grant is recorded in that source's LICENSE and PUBLICATION_GATE.md and continues here.

## Publication review and limits

Every imported file is checked as complete bytes against the pinned source inventory and scanned for private home paths, personal contact addresses and known account markers, credential forms, private-key headers, and excluded artifacts. Documentation, configuration, receipts, and scan hits receive contextual review. No actionable private residue was detected in this bounded review; this is not proof that every possible secret representation is detectable.

The separate conversation logger, Control Draft, repair packets, raw tests and diagnostics, recursive archives, omitted source research, candidate simulation packages, and machine-specific workshop files remain outside this publication. Nothing in a retained prompt or acceptance label grants instructions to the migration process.

The [validation summary](MIGRATION_VALIDATION.md) records this migration's checks. Source cleanup occurs only after public destination readback succeeds. Historical commits, retained branches, and local evidence are preserved.

## Root layout follow-up — 2026-11-05

After the original verified migration, the user approved moving the three project directories directly into the repository root. The shared overview, LICENSE and migration records moved to `docs/xosg/`. The former `xOSG/` current directory is removed. Original paths and digests in the manifest remain historical; the root-layout mapping records current locations and digests. Relative links, the DWSK source-install command and dependent inventory are updated. Executable bytes, failed status, historical reports and repository history remain preserved. No source repair, binary release or integration is implied.
