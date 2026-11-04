# Relative and replaceable map probe contract

Contract date: 2026-10-30 (America/New_York)  
Authorization: AUTH-18A  
Profile: `docstream.relative-maps.auth18a/1`

## 1. Purpose

AUTH-18A is a local mechanical probe of the user's Etabit direction: objects,
orders, structures and processes form generic map kinds; grammar and syntax are
separate referenced drives; theory drives are relative and replaceable; derived
relation maps can be composed into lexical drives; and a replacement changes a
particular context without deleting or globally replacing the displaced drive.

The probe does not implement Etabit, Government and Binding Theory, or a
linguistically authoritative WordNet decoder. Every grammar, syntax and theory
entry created here is marked `TEST_ONLY_MECHANICAL_PROJECTION`.

## 2. Source and scope

The source is the preserved Princeton WordNet 3.1 database archive with SHA-256
`3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a`.
The fixed selection seed is `etabit-auth18a-relative-drive-1`.

| Limit | Approved ceiling |
| --- | ---: |
| Selected adjective records | 8 |
| Resolved unique one-hop targets | 32 |
| Logical decompressed source bytes | 4,194,304 |
| Candidate adjective records | 50,000 |
| Runtime | 120 seconds |
| Peak process working set | 134,217,728 bytes |

The reader scans `dict/data.adj`, validates that each source `synset_offset`
equals its member byte offset, computes a SHA-256 selection score over seed,
offset and raw record, and selects the eight lowest scores. Every selected
pointer tuple is retained in source order. Up to 32 unique targets are read by
their WordNet member/offset. Missing, capped or unresolvable targets remain
explicitly unresolved; they are never guessed.

## 3. Immutable map identity

A map definition contains:

- map type;
- name and positive integer version;
- context identifier;
- exact ordered input-map IDs; and
- exact ordered canonical entries.

Its map ID is the SHA-256 of canonical JSON containing all of those fields and
the profile/schema identity. An identical recipe reuses identity. A changed
input, order, theory, entry, version or context changes identity.

Entries store canonical JSON text internally so caller mutation of a detached
payload cannot modify the retained definition. Public catalog views are
read-only snapshots. The store has no mutable global current map.

## 4. Atomic publication and acyclic composition

`publish_batch` accepts immutable drafts with local dependency keys. It validates
types, limits, external inputs, order positions, context selections and
replacement indices; topologically resolves the drafts; constructs all
definitions in temporary state; and replaces the state pointer once. Missing
inputs, duplicate keys, cycles, invalid orders, invalid selections, invalid
replacement indices or limits publish nothing.

The initial model rejects cycles. Recursive/fixed-point maps are not implicitly
supported. A later scope may define them explicitly without weakening this
probe's acyclic proof boundary.

## 5. Relative contexts and replacement

A context is another immutable map. A `selection` entry identifies a role and
an exact input index. Resolving a role requires an explicit context-map
reference; no global head exists.

Replacement is represented by:

1. the prior composed drive;
2. the replacement composed drive;
3. the prior context;
4. an immutable replacement-ledger entry; and
5. a new context version selecting the replacement.

The prior drive and context remain present. Other contexts retain their prior
selection. AUTH-18A demonstrates Context A v1 and Context B v1 selecting
composition A, followed by Context A v2 selecting composition B while Context B
continues selecting A.

## 6. Probe map graph

The retained probe publishes 21 aliases across these map kinds:

- objects;
- source and relation orders;
- source and relation structures;
- source-pull process;
- placeholder grammar and syntax;
- Government-and-Binding placeholder A and alternative placeholder B;
- relation projections A and B;
- adjective compositions A and B;
- Context A v1, Context A v2 and Context B v1;
- replacement ledger; and
- derivation ledger.

The two relation projections retain the same raw WordNet pointer evidence but
reference different theory, order and structure maps. Therefore the two
adjective compositions have different identities. Neither is asserted to be
linguistically correct.

## 7. Evidence

The approved destination is:

`.docstream/etabit-map-tests/auth18a-vertical-composition-probe/`

It contains:

- `aliases.json`;
- `maps.jsonl`;
- `source-records.jsonl`;
- `relations.jsonl`;
- `result.json`; and
- `manifest.json`.

The maintained `--verify` command checks the exact file set and hashes, rebuilds
the probe from the approved source, compares every deterministic payload,
validates all map inputs and rechecks the three context resolutions.

## 8. Exclusions

AUTH-18A creates no live Etabit directories, service database records, actual
grammar or syntax canon, Government-and-Binding rule set, complete WordNet
decoder, full-corpus load, GPU representation or agentic integration. Raw
pointer symbols remain source evidence. Integration into agentic control remains
last.
