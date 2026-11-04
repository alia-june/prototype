# Etabit schema v0.2 — Recursive audit reconciliation

**Date:** 2026-11-04  
**Status:** research draft, NOT ADMITTED  
**Source basis:** Decomposition Recursive Audit 2026-11-04 (20 checks); direct October 2026 user decisions; GitHub Etabit v0.1 baseline and sibling Syn-Etabit textual README.

The v0.1 descriptor and four-symbol example remain unchanged. Version 0.2 is a **proposed additional descriptor**, not a new Etabit on-media/wire standard or implementation of Cypher authority.

## Changes responding to the recursive audit

| Audit check | v0.1 gap | v0.2 treatment | What it does NOT prove |
| --- | --- | --- | --- |
| T02/T03 | Source type mostly free text | Drive `roles` and explicitly identified object declarations with classification, display surface, payload *type descriptor*, encoding status and provenance status | Object bytes, payload integrity, arbitrary-object decoder |
| T04/T05 | Four-symbol example without status typing | Keep exactly four stored symbols as an example and add a separate `result_boundaries` section distinguishing stored Error/Unknown from I/O failure/reference unresolved | Four-valued logic, working read-result ABI |
| T06/T07 | Codepages not associated with referential drives | `codepages[].referential_drive_ids` and process namespace | Mapping tables, translation authorization, executable conversion |
| T09/T10 | Constructor/reader restrictions only declared | Optional per-drive `out_of_band_meta_disks` with scoped constructor and denied reader, explicitly disallow automatic disclosure | Information-flow noninterference or isolation |
| T11 | Cypher flags without constituents | `cypher_disk.constituents` as draft descriptive entries; still allows empty list while membership/protocol unknown | Voting, quorum, joint authority, deployed decision mechanism |
| T11 | Five Cypher duties fixed in one array order | Five unique *unordered* responsibilities: each required exactly once, no ordering contract | Policy precedence or authority delegation |
| T12 | Physical mechanism possibility conflated with unknown status | Separate `physical_mechanism_selected:false` and list of possible mechanisms | Mechanical construction or accepted design |
| T13 | Refusal boolean only | Explicit separate refusal and revocation **protocol statuses** | A real revocation mechanism |
| T15 | Free-form reference description | Explicit reference identity, source drive, target drive/object IDs, grammar/order/multiplicity/cycle statuses | Runtime graph semantics, cross-file reference correctness |
| T18 | Sibling textual Etabit conflation risk | Keep separate project identity and source-scoped repository evidence | Transplanted or certified CPU implementation |
| T20 | Description mistaken for enforcement | `DRAFT_NOT_ADMITTED`, default-deny and `runtime_activated:false` constants | A sandbox or cryptographic proof |

The older `USF` naming remains historical; current-facing documentation uses `UNSF`. This draft does not invent a meaning for `UNSF`.

## Required negative tests

1. Reject wrong system name, unknown drive roles, missing required fields or prohibited `null` when schema is applied.
2. Reject duplicate responsibilities, missing Cypher responsibilities, or sixth unknown responsibility.
3. Accept a permutation of the five Cypher responsibilities; **no precedence is assigned**.
4. Reject `reader_access` other than `DENIED` and `automatic_disclosure:true`.
5. Reject `codepages[].execution_permission:true`, `runtime_activated:true` and `refusal_bypass_permitted:true`.
6. Supplement JSON Schema validation with graph referential-integrity checks: unique IDs, drive references and codepage referential-drive role.
7. Ensure stored `Error` and `Unknown` objects are not syntactically identified as operational statuses.

## Known incompleteness and constraints

- `objects[].payload_type` is a **descriptive label**, not a validated payload schema or storage encoding. Arbitrary source objects are permitted conceptually, not fully implemented by this draft.
- Cross-object references can be checked by an independent validator but JSON Schema alone does not enforce all graph foreign keys.
- No on-media object encoding, read-result transport structure, live writer, durable transaction, crash-recovery algorithm, independent attester, or actual `eo-drive` exists from this commit.
- No quorum, voting, arbitration, threshold, mechanical interlock, constructor access implementation or reader noninterference proof is selected.
- The schema `$id` is a convenient repository address pointing to `main`, **not an immutable publication identifier**; pin to an audited commit/release for reproducible consumers.
- Existing Syn-Etabit Textual CPU artifacts remain a separate implementation with separate test/evidence scope; no code imported wholesale.

## Admission

Keep v0.2 noncanonical and default-deny. Promotion requires explicit user acceptance of semantics, independent validators and demonstrated reference and authority boundaries. This research descriptor cannot authorize reading metadata, writing disks or executing input objects.
