# Module Boundary

DWSK is infrastructure, not an application authority.

It may:
- persist opaque higher-level records within its canonical data profile;
- journal accepted mutations;
- create and verify snapshots;
- reconstruct a workspace from an unambiguous published quorum.

It may not:
- decide whether a higher-level semantic record is true, accepted, canonical, or executable;
- infer governance authority from persistence;
- silently reconcile conflicting valid state;
- write outside its configured workspace root except when an operator explicitly chooses a recovery target.

For a Universal Workbench integration, expose DWSK through a bounded persistence adapter. Do not make it the workbench root or semantic registry.
