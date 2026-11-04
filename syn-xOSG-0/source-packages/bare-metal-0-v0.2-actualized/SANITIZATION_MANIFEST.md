# Sanitization Manifest

- Source package: `xOSG-0_bare-metal_0_actualized`
- Published UTF-8 files: 17
- Redaction substitutions: 0
- Excluded files: 0

## Policy

Technical source is preserved unless it contains personal identifiers, credentials, local user/host paths, compiled caches, or nested binary archives.
Nested archives are excluded because their extracted sanitized contents are represented separately; compiled caches are reproducible build artifacts.

## Redactions

- None required by the configured identifier/credential scan.

## Exclusions

- None.

## Integrity

`PUBLISHED_SHA256SUMS.txt` hashes the published sanitized files as staged before this manifest was added.
