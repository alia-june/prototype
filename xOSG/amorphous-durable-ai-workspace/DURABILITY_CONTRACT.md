# Durability Contract — DWSK-1

## Commit rule
A state mutation is durable only when its state change and corresponding journal event commit in the same SQLite transaction.

## Journal rule
The first event uses 64 zeroes as `previous_event_sha256`. Each later event references the immediately preceding event hash. `event_sha256` is SHA-256 over the DWSK-CJ-1 canonical bytes of the event core excluding `event_sha256` itself.

The readiness candidate checks that replaying the chain yields the declared
current record values during ordinary verification, checkpoint creation,
snapshot inspection, and recovery. Values are compared using DWSK-CJ-1 bytes
(including the distinction between booleans and integers). The snapshot format
and existing `record.set` / `record.delete` interpretation are unchanged.

## Canonical data rule
All journal payloads and snapshot logical content use DWSK-CJ-1: NFC strings/keys, sorted object keys, arrays in order, null/boolean/string/signed-64-bit integers only, UTF-8, no whitespace. Floats are rejected.

## Key and counter admission

Public `set`, `get`, and `delete` keys must be nonempty strings, including string
subclasses accepted by the canonical normalizer. API keys are NFC-normalized.
Invalid keys raise WorkspaceError before database access or mutation. A valid
missing get still raises KeyError; a valid absent delete still journals an event.
Snapshot record keys and recognized set/delete event keys obey the same
string/nonempty domain. Payload null, false, zero, empty strings and collections
remain valid canonical data, including empty string keys inside payload objects.

Snapshot event_count must be an actual integer from zero through INT64_MAX and
equal the number of events. Journal sequence numbers are actual positive
integers through INT64_MAX, consecutive from one. Recognized set/delete event
revisions are actual positive integers through INT64_MAX. These metadata fields
exclude booleans and integer subclasses. The existing delete/recreate revision
behavior is unchanged; no new monotonic revision-history rule is introduced.
Missing or invalid key/counter fields raise SnapshotError during bundle
verification, before recovery can create a target. Snapshot inspection marks
such representations invalid; recovery retains its existing quorum refusal.

Typed XML integers require present, nonempty text; absence is never converted to
zero. Existing conversion of other nonempty integer text and signed-64-bit
canonical normalization are retained. Empty base64 string encodings remain valid.

## Snapshot publication state machine
1. Read one consistent logical bundle from the runtime database.
2. Create `snapshots/.staging-<generation>`.
3. Write SQLite, JSONL, XML representations.
4. fsync each representation.
5. Compute per-file SHA-256 and one logical digest.
6. Write and fsync `manifest.json` **last**.
7. fsync the staging directory.
8. Atomically rename staging directory to the generation name.
9. fsync `snapshots/`.
10. Write and fsync a generation-specific temporary pointer file, atomically
    replace `snapshots/LATEST`, and fsync the directory again where supported.

A `.staging-*` directory is never a published snapshot and may be removed after inspection.

Each publisher creates its own temporary pointer exclusively and cleans up only
that owned pointer on failure. Failure before generation publication leaves the
existing tree intact. Failure after generation publication but before pointer
promotion can leave a complete unreferenced generation; that generation is
preserved, and the prior `LATEST` remains in place. Failure after pointer
promotion does not roll back that completed promotion.

`LATEST` records the last completed pointer replacement. Concurrent publication
does not make it a semantic authority, a project acceptance decision, or an
ordering guarantee by generation creation time.

The repair candidate retries only Windows errors 5 (access denied), 32
(sharing violation), and 33 (lock violation) during the atomic `LATEST`
replacement. It waits initially 10 ms, increasing to at most 100 ms between
attempts, within a two-second retry deadline. No replacement is deliberately
started after that deadline; an OS call already in progress can outlast it.
The same fully written, fsynced, publisher-owned temporary pointer is used
throughout. The existing target is never pre-deleted. Other errors propagate
immediately; persistent eligible failures re-raise the original final error.
Normal failure cleanup still removes only the owned temporary pointer and
retains any complete published generation. This is a bounded mitigation for
observed contention, not a guarantee of successful replacement under persistent
access denial or a claim that the underlying Windows cause is established.

## Windows qualification
Windows pointer promotion is coordinated by a named mutex scoped to the current
user SID, Windows session (`Local` namespace), and normalized resolved snapshot
directory path. Its opaque name is a SHA-256 digest; it does not contain the path
or SID in plaintext. Publishers referring to the same storage through different
normalized names are not guaranteed to coordinate. Cross-session/different-user
publishers and external programs are outside this coordination contract.

Generation construction and temporary-pointer file fsync stay outside the mutex.
Only pointer replacement (including its existing bounded retry) and the following
directory-sync step are protected. Acquisition waits at most five seconds in the
Windows wait API; timeout raises SnapshotError. Scheduling/OS calls can extend
observed wall time. No filesystem lock files are introduced.

If the previous owner terminates and Windows reports abandonment, the next owner
checks an existing LATEST and its complete referenced three-format generation
before promotion. Inconsistent names, paths, hashes, replay or manifest digests
cause explicit refusal. Absence of LATEST is permitted for an interrupted first
publisher. The mutex is released and its handle closed on success and exceptions;
abandonment itself is not acceptance. A complete generation published before a
timeout/refusal remains retained, and ordinary owned-temp cleanup applies.

The mutex coordinates cooperating local publishers; the retry remains for access
or sharing failures from sources outside that coordination. This does not prove
the underlying Windows cause or guarantee successful publication under persistent
access denial. The non-Windows publication sequence remains unchanged.

On Windows, `_fsync_file` uses a non-truncating writable descriptor (`r+b`) so
`os.fsync` can execute; the supplied read-only-descriptor form raised errno 9 in
the native readiness baseline. SQLite requests WAL and `synchronous=FULL`.

`_fsync_dir` returns without performing directory-handle synchronization on
Windows. Accordingly, steps 7, 9, and the directory-sync portion of step 10 are
not performed there. Atomic replacement and file-fsync calls do not by
themselves establish persistence of directory entries after physical power
loss. The readiness pass does not test power interruption, hardware caches,
storage-device failure, or independent backup recovery. All three formats in
one workspace share that storage location.

## Recovery rule
A representation is eligible only if its file hash/size match the published manifest, it parses, its journal chain verifies, and its current values agree with journal replay. Automatic recovery requires at least **two eligible representations with the same logical digest**, and that digest must equal the published manifest logical digest. Replay consistency is checked before creating or changing a recovery target.

There is no intrinsic SQLite/JSONL/XML precedence. If quorum cannot be established, recovery stops for explicit operator review.

Recovery accepts an absent or empty destination, validates the source first, then
exclusively creates `.dwsk-recovery.json` before database construction. Ordinary
DWSK init/get/set/delete/verify/checkpoint refuse any marked workspace, including
an unreadable marker. Only the active instance owning the current claim performs
internal verification. This protocol coordinates cooperating DWSK calls; it is
not an operating-system access restriction.

The recovered database is built once, closed, and verified against the expected
logical digest before the owned marker is removed and a usable workspace is
returned. Invalid preflight and occupied-target errors retain their previous
messages. A competing claim is never overwritten or removed.

Failure retains generated files and the recovery claim for operator review.
RecoveryError details and recovery CLI errors report RECOVERY_INCOMPLETE, phase,
original/secondary errors, builder closure and last confirmed marker/target state;
CLI exit remains 2. A FAILED receipt is published atomically for an owned marker;
if that fails, the original IN_PROGRESS claim and any temporary receipt remain
evidence. Claim/reporting uncertainty is reported explicitly. No automatic resume,
marker removal, failed-target cleanup or adoption occurs.

Process interruption before completion leaves an incomplete destination guarded
by its persistent claim. Namespace errors can make guard presence uncertain;
errors never claim protection that was not observed. Interruption after verified
marker removal can leave a complete workspace without an acknowledged return.
File fsync is used for claim/receipt writes; the existing Windows directory-sync
and physical-power-loss proof limits still apply. This is not exhaustive hostile
path-race or external-writer coordination.
