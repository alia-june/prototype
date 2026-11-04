# Minimal-Exposure Attestation Pipeline — MAP-001

## Principle

Attestation should be derived from deterministic evidence instead of repeated semantic inspection of original content.

```text
READ-ONLY TREE
 -> canonical inventory
 -> streaming SHA-256
 -> Merkle root
 -> deterministic regression summaries
 -> invariant ledger
 -> scoped attestation
```

## Attestation scope

The attestation may establish only:
- exact package identity by digest;
- canonical file inventory and sizes;
- Merkle-root identity of the tree;
- listed deterministic checks and their recorded outcomes;
- recorded gate/release state at sealing time.

It does not establish the truth of every prose claim, the absence of all defects, or external-system state.

## Minimal return surface

The Orchestrator receives the attestation and failed invariant IDs. Original payload content is not included by default.
