# Build status for R4 source adoption — 2026-11-04

The current review revision changes source and development tools. No replacement wheel, sdist, source ZIP, installed-wheel test, package version or release tag was produced by this adoption. Current source checks are recorded in [VALIDATION_REPORT.md](VALIDATION_REPORT.md).

The earlier artifact inventory and distribution checksums describe the original 2026-10-31 binary set retained outside this repository. They are historical identifiers, not a claim that those binaries contain the adopted R4 changes. SOURCE_SHA256SUMS is the current source inventory. A new binary release needs its own build, package-content and outside-source installation validation.

## Historical binary build record

# DWSK 0.1.1 build report — 2026-10-31

**Build and installed-package validation: PASS.** The wheel and source distribution
were built offline from the validated Windows mutex source candidate. A fresh
wheel rebuilt from the sdist has identical uncompressed contents. This is an
installable source build, not a remotely published release.

## Package contents and identity

- Package: durable-workspace-development-kit 0.1.1.
- Required Python: >=3.11, matching the exception-note API used by cleanup.
- Tested platform: Windows, Python 3.14. Other interpreters/OS were not tested.
- Runtime dependencies: Python standard library only; no Requires-Dist entries.
- Console entrypoint: dwsk = durable_workspace.cli:main.
- Runtime implementation files are byte-identical to the validated mutex candidate;
  __init__ differs only in its version string. Metadata/docs are updated, the
  historical report retained, and source archive inclusion made explicit.

The wheel's five package source files match staged bytes. Wheel RECORD hashes and
sizes, version/requirements and entrypoint were verified. The sdist contains all
28 curated source inputs, including documentation, schemas,
templates, examples and tests. Archive paths and ownership fields were inspected.
The documented source ZIP contains the curated source, this report and the input
manifest. Exact artifact hashes belong to ARTIFACTS.json and SHA256SUMS.

## Installed distribution checks

The wheel was installed into a disposable environment, with no dependency fetches
or working-environment installation. Imports were verified inside that environment's
site-packages. Tests ran from a directory outside the source tree with isolated
interpreter flags. Adapted test launchers remove source-path insertion, enforce
installed imports and preserve the original test assertions.

| Installed checks | Normal | Optimized |
| --- | ---: | ---: |
| Unit tests | 17/17 | 17/17 |
| Self-validation | 7/7 | 7/7 |
| Retry tests | 8/8 | 8/8 |
| Native mutex tests | 12/12 | 12/12 |
| CLI checks | 15/15 | 15/15 |
| Single-format damage/recovery variants | 3/3 | 3/3 |
| Four-process checkpoint calls | 12/12 | 12/12 |

Native worker import locations were checked. Each parallel trial retained twelve
complete valid generations, unchanged runtime state, a valid LATEST and no owned
temporary entries. CLI tests exercised mutation/journaling, installed checkpoint
and recovery, missing-key and float rejection, lost-quorum inspection and refusal
to create a recovery target. Process cleanup receipts were verified.

The broader source campaign previously passed 32 hardening, 1,000 fuzzy and eight
torture cases and twenty native checkpoint trials. That source evidence is distinct
from these fresh installed-artifact checks; it was not rerun or relabelled as an
installed-wheel fuzz campaign.

## Build inspection correction

The first metadata inspection stopped because its checker assumed LF while the
wheel used valid CRLF metadata. Headers contained the correct version and Python
requirement. The checker was corrected to parse headers with the standard library,
and the same built artifacts continued through validation. Original controller
source and failed log are retained in local evidence; they are not shipped here.

## Limits and disposition

Windows coordination covers cooperating publishers using the same normalized path,
user and session. Persistent access failures remain errors; the OS cause remains
unresolved. Directory-handle fsync on Windows, physical power loss, external backup
recovery, cross-session/user coordination and application/logger integration are
not demonstrated. Read DURABILITY_CONTRACT.md and MODULE_BOUNDARY.md.

Pattern/content scans found no caches, known local identifiers, absolute local
paths, email addresses or credential-pattern matches in the distributions. Approved
project names and existing attribution are preserved. A zero-result scan is not a
proof against every identifying detail. Local logs/environment are excluded from
the distributions. No license was invented or changed.

Build tools: pip 26.2.1, setuptools 82.0.1.
Measured successful subprocess execution totalled 47.278 seconds. The resumed
controller elapsed 56.862 seconds including its inspections;
both were below the 900-second limit. Final preservation/checksum inspection is
separate. Final output size is checked against 256 MiB. All 94,876
protected historical files were verified unchanged. No global install, repository
update or cloud publication occurred.
