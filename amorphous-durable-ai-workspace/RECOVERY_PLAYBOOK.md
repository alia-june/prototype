# Recovery Playbook

1. Preserve the damaged workspace before attempting repair.
2. Run `dwsk verify <workspace>`.
3. Inspect published snapshot generations; ignore `.staging-*` as incomplete.
4. Run `dwsk verify-snapshot <generation>`.
5. If two or three representations agree and match the manifest, recover into a **new empty directory**.
6. Run `dwsk verify <recovered>`.
7. Compare higher-level application invariants before replacing any operational workspace.
8. If no quorum exists, stop. Do not select the newest, largest, or SQLite representation merely by convention.

## Failed or interrupted recovery

- `.dwsk-recovery.json` marks a claimed recovery. Its presence blocks ordinary
  DWSK initialization and workspace operations, even if its contents are damaged.
- A successful recovery closes and verifies its database before removing its own
  marker. The returned workspace is then usable normally.
- On failure, preserve the entire destination, marker and temporary receipts.
  RecoveryError details (also emitted by the recovery CLI with exit 2) identify
  the failed phase, original error, secondary errors and last confirmed state.
- FAILED records describe a reported failure; IN_PROGRESS can mean interruption
  or unsuccessful failure-report publication. Neither is permission to use it.
- GUARD_UNCERTAIN and VERIFIED_UNACKNOWLEDGED require explicit inspection; do not
  infer a usable or protected destination merely from a failed call.
- Do not delete the marker to bypass refusal, automatically resume, merge the
  destination into an operational workspace or retry into the same nonempty
  destination. Review preserved evidence and use a separately chosen new target
  for another explicitly authorized recovery.
- The marker governs DWSK calls, not other filesystem/SQLite tools. These rules
  do not establish physical-power-loss durability or block noncooperating writers.
