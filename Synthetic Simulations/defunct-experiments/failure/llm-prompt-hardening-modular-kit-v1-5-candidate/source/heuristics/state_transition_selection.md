> **FABRICATION FLAG — GENERATED TEXT BEGINS**

# Controlled State Transition Selection

**Status:** `[GENERATED-PROPOSAL]` derived from the supplied controlled-state-transition synthesis.

Load the `state_transition` profile whenever the task changes, publishes, transfers, synchronizes, replicates, backs up, archives, migrates, restores, rolls back, or retires persistent state. Also compose every independently triggered profile.

## Minimum classification

| Question | Consequence |
|---|---|
| Is an existing authoritative object changing? | Require copy/version lineage and conditional commit |
| Is state crossing a machine, trust, implementation, or failure-domain boundary? | Require explicit transition identity, manifest, verification, and receipt |
| Can retry repeat an effect? | Require operation ID and idempotency classification |
| Can partial output be mistaken for completion? | Require non-authoritative staging and explicit `READY` state |
| Can newest state be corrupted? | Require historical generations and selected recovery point |
| Do copies share administrator, credentials, keys, network, or storage? | Do not claim independent recovery |
| Does the result require an application to understand it? | Require semantic validation in addition to digests |
| Is encryption involved? | Record a separate key-recovery path |
| Is the source suspected compromised? | Require isolated recovery and controlled reconnection |
| Is commit outcome unknown? | Stop in `CONFLICT` or `UNKNOWN`; do not repeat unsafely |

## Offloading interaction

The state-transition contract remains resident even when bulk work is offloaded. A shard or external engine may stage, move, hash, or validate data, but it cannot authorize commit, destroy the predecessor, change retention, certify recovery, or promote the result.

## Completion vocabulary

Use the strongest proven state only:

`IDENTIFIED`, `FROZEN`, `MANIFESTED`, `AUTHORIZED`, `STAGED`, `TRANSFERRED`, `MECHANICALLY VERIFIED`, `SEMANTICALLY VALIDATED`, `READY`, `COMMITTED`, `RECEIPT VERIFIED`, `PREDECESSOR RETAINED`, `RESTORATION TESTED`, `RETIRED`.

Do not compress these into `complete` when later gates remain open.

> **FABRICATION FLAG — GENERATED TEXT ENDS**
