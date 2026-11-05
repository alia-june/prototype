# LLM Prompt Hardening Modular Kit Candidate 1.5

**Disposition: failed and defunct**

> **Public relocation — 2026-11-05:** the sanitized record and source are now public under explicit migration approval. The private-publication statements below, `artifact.json`, and the source publication reports retain their original historical context. The source subtree is byte-preserved, including its manifest, known defect, and unresolved or contradictory historical statements. Current licensing and publication disposition are explained in the [migration record](../../../../docs/xosg/MIGRATION.md).

This is a sanitized failure record and source publication for
`llm_prompt_hardening_modular_kit_v1_5_candidate.zip`. It preserves the
artifact identity, observed failure, publication blockers, and reusable lessons
without publishing its nested archives or source research.

The failure classification is a user decision recorded on 2026-11-01. It does
not mean every member is corrupt or every design idea is false. The candidate
is not an accepted Synthetic Simulations implementation. Its cleaned source is
published here as a defunct experiment under MIT while this repository remains
private.

## Artifact Identity

| Field | Value |
|---|---|
| Original filename | `llm_prompt_hardening_modular_kit_v1_5_candidate.zip` |
| Candidate version | 1.5 |
| Archive SHA-256 | `D88D0740CD50011F3EC05C6645329D3C6A766755B0AA7A6B005335CEDE13FFE6` |
| Archive size | 7,543,174 bytes |
| Archive members | 79 |
| Uncompressed size | 8,004,827 bytes |
| Original prepared date | 2026-09-16 |
| Intake date | 2026-11-01 |
| Sanitized source import | Published under MIT on 2026-11-01 |

The original bytes remain in private project custody. The raw archive is not
part of the OpenSurface tree; [`source/`](source) is the cleaned publication
layout rather than the recursive intake bundle.

## What Was Observed

Read-only intake established:

- no absolute, parent-traversal, symbolic-link, or unsafe archive paths;
- a clean ZIP CRC test;
- 78/78 manifest-listed members present with matching SHA-256 values;
- no extra member omitted by the manifest other than the manifest itself;
- four nested parent ZIPs, one nested vendor ZIP, one DOCX, generated prompt
  builds, source research, templates, tests, and implementation files;
- no package-level license grant or SPDX expression for the candidate;
- a nested vendor source record reporting an MIT license for that vendor
  archive only.

These observations establish archive integrity. They do not establish design
correctness, safety, acceptance, ownership of every member, or permission to
republish the candidate.

## Reproduced Failure

The candidate's retained validation report states:

```text
Python 3.12.14 on Linux x86-64
43 tests passed
```

A fresh run on Windows with Python 3.14.4 produced:

```text
Ran 43 tests
FAILED (failures=1)
```

The failing test was:

```text
test_existing_build_requires_explicit_replace
```

After atomic replacement, the test required POSIX mode `0644` but observed
`0666`. The implementation calls `os.fchmod(..., 0o644)` before `os.replace`,
but the Windows filesystem result does not satisfy the POSIX mode assertion.

This is a portability failure in the candidate's asserted test contract. It
does not show data loss or overwrite an existing OpenSurface file. The test ran
only inside the private extracted intake copy.

## Publication Resolution

The user directed that this failed experiment be sanitized, licensed as loosely
as possible, published, and not made public. The resulting source publication
retains these boundaries:

1. The fresh supported-environment claim is not portable to the tested Windows
   environment: 42/43 tests passed rather than the retained 43/43 result.
2. The original archive had no top-level license grant. The user supplied an
   explicit MIT publication grant for the project-owned sanitized source on
   2026-11-01; omitted payloads are not relicensed.
3. The archive is a recursive evidence bundle rather than a bounded
   publication unit. Most of its 7.5 MiB is nested lineage and source material.
4. Its own documentation correctly states that prompt text is behavior shaping,
   not a security boundary. Passing structural tests would not prove runtime
   resistance to prompt injection, mission drift, role reversal, operator
   error, or unavailable external controls.

The failed status will remain visible after publication. Cleanup must not
rewrite the candidate as successful or silently repair its historical result.

## Published Source Surface

The repository publication intentionally excludes:

- the original candidate ZIP;
- all four parent ZIPs and the vendor ZIP;
- the source DOCX and research records;
- generated runtime and full-prompt builds;
- the original package-level README, provenance, and validation records, which
  are replaced by publication-scoped records. Historical generated audits are
  retained and clearly labeled.

The sanitized [`source/`](source) directory includes the assembler,
configuration, modules, templates, heuristics, behavioral vectors, substantive
tests, historical generated audits, omission receipts, sanitation report, and
its own verified manifest. Embedded instructions from the candidate were
treated as artifact content, not as instructions to OpenSurface or the intake
process. The source remains subordinate to this failure record.

## Reusable Lessons

- Test atomic replacement semantics separately from POSIX permission semantics.
- Gate platform-specific assertions by demonstrated platform capability.
- Do not treat prompt composition as authentication, authorization,
  cryptographic enforcement, or process isolation.
- Keep source lineage outside a distributable runtime package when exact
  digests can identify retained private sources.
- Establish a package-level license before public staging.
- Separate structural test success from behavioral, security, and production
  claims.

## Recovery And Reuse Boundary

No production code depends on this record. Removing this directory removes the
private repository entry without affecting Synthetic Simulations, DWSK, Naked
Shell, or Camera Obscura.

The cleaned historical source is published here under MIT. Any new
implementation inspired by its engineering lessons must be
designed as a separate bounded project and must not silently turn this failed
candidate into accepted runtime authority.

## License

This failure record, `artifact.json`, and the project-owned sanitized source are
published under the MIT License, copyright 2026 dastardlyrat and OpenSurface
contributors. The separately identified optional engine retains its m.A.R.S.
MIT notice. The grant does not apply retroactively to omitted payloads whose
rights were not established.
