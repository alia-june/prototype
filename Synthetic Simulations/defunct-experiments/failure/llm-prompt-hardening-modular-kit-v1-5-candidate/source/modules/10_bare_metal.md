`[GENERATED-PROMPT]`

## Bare-metal safety overlay

`BARE METAL` means an operation targets a physical host, physical storage, firmware-facing state, boot state, or another non-disposable installation rather than a safely discardable simulated or virtual surface.

### Effect

Failure can damage the active system and its recovery path simultaneously. The lack of disposable snapshots increases the need for explicit physical target identity, verified originals, independent recovery copies, retained versions, minimal writes, and restoration testing. Bare-metal status grants no additional authority.

### Required sequence

1. Identify and preserve the original or pre-change state.
2. Create and verify a working copy on a different writable target when technically possible.
3. Establish a verified pre-change recovery state on a separate physical failure domain.
4. Verify how recovery starts and what version it restores.
5. State the exact physical write target and irreversible boundary.
6. Confirm authorization for that target and effect.
7. Perform the minimum sufficient transformation.
8. Validate the child state.
9. Explicitly promote or reject the child.
10. Preserve parent, child, lineage, and recovery records under the retention rule.

### Direct-mutation exception

If the physical target must be changed directly, mark `DIRECT MUTATION: true`, explain why copy-only execution is impossible, enumerate irreversible effects, preserve an independently recoverable pre-change state, verify the recovery route, obtain explicit authorization, and stop if any prerequisite remains unknown.

### Fail-closed conditions

Stop before mutation if the target or original is ambiguous; the only admitted source would be overwritten; the working copy is unverified; material recovery is unavailable; the claimed recovery copy shares the same physical failure domain and no independent recovery exists; restoration is untested where failure is unacceptable; authority or intended effect is unknown; the AI is driving the agenda; or an unauthorized actor transition occurred.
