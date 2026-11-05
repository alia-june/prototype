# Amorphous Durable AI Workspace

**A Python development kit for durable records, transactional journaling, verified checkpoints, and quorum recovery.**

The implementation is **Durable Workspace Development Kit (DWSK) 0.1.1**. It provides a Python API and the `dwsk` command for creating a local workspace, storing canonical records, verifying its journal, publishing snapshots, and recovering consistent state.

The kit combines a SQLite runtime database with three snapshot representations and an explicit recovery rule. State mutations and their journal events commit together. Checkpoints are verified before publication. Recovery requires agreement between eligible representations and the published manifest.

**Guide:** [Capabilities](#capabilities) · [Installation](#installation-from-source) · [Example](#a-complete-storage-and-recovery-example) · [API](#python-api) · [CLI](#command-line-reference) · [Storage](#storage-layout) · [Publication](#checkpoint-publication) · [Recovery](#verification-and-recovery) · [Validation](#validation-record) · [Project files](#project-files)

## R4 source adoption

This review revision adopts the qualified R4 value-admission, checker and retained-recovery repairs on the DWSK 0.1.1 source base. Keys must be nonempty strings; malformed XML integer text and non-integer counters are refused. Recovery exclusively claims a target, retains failed/interrupted targets for operator review, and blocks ordinary DWSK access while a recovery marker is present or uncheckable. See [DURABILITY_CONTRACT.md](DURABILITY_CONTRACT.md) and [RECOVERY_PLAYBOOK.md](RECOVERY_PLAYBOOK.md).

The [development runner](tools/validation/README.md) supplies owned Windows unit/self-check execution. These are development tools; the runtime remains standard-library-only. Current validation is source validation. The older installed-wheel reports and binary artifact hashes below remain historical; no new wheel, version, release tag or installed-package result is claimed by this source adoption.

## Capabilities

- Initialize an isolated workspace at a configured filesystem path.
- Store, retrieve, replace, and delete records by key.
- Commit each mutation and its hash-chained journal event in one SQLite transaction.
- Canonicalize supported values using the DWSK-CJ-1 data profile.
- Verify database integrity, journal sequence/hashes, and agreement between replayed events and current record values.
- Create SQLite, JSONL, and typed XML representations of one consistent logical state.
- Publish complete snapshot generations with a manifest of file sizes, hashes, and a logical digest.
- Inspect snapshot eligibility and recover from at least two agreeing valid representations.
- Coordinate Windows pointer promotion with a workspace-specific named mutex, bounded wait, and bounded replacement retry.

The runtime has no third-party dependencies. Source installation uses setuptools as its build backend.

## Installation from source

**Python 3.11 or later is required.** Windows with Python 3.14 is the tested platform. The declared Python minimum is not a claim that every supported interpreter or operating system has been exercised.

From the alia-june/xOSG-prototype repository root, in PowerShell:

```powershell
cd amorphous-durable-ai-workspace
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
$dwskPython = (Resolve-Path .\.venv\Scripts\python.exe).Path
$dwskCli = (Resolve-Path .\.venv\Scripts\dwsk.exe).Path
```

The distribution name is `durable-workspace-development-kit`; the import is `durable_workspace`; the executable is `dwsk`. Built binaries are held outside this source repository. Their identities and hashes are retained in [docs/build/ARTIFACTS.json](docs/build/ARTIFACTS.json).

Keep example databases and snapshots outside the source checkout. These commands create a fresh scratch directory and retain the environment paths above:

```powershell
$dwskExample = Join-Path ([System.IO.Path]::GetTempPath()) ("dwsk-kit-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $dwskExample
Set-Location $dwskExample
```

## A complete storage and recovery example

Save the following as `workspace_example.py` in the scratch directory. Initialization and recovery use fresh paths; repeating the script against existing output is deliberately refused.

```python
from durable_workspace import DurableWorkspace

workspace = DurableWorkspace.init("./demo-workspace")
settings = {
    "name": "sample-project",
    "enabled": True,
    "retry_limit": 3,
    "labels": ["example", "local"],
}

workspace.set("project/settings", settings)
workspace.set("project/state", {"phase": "ready", "completed_steps": 0})
if workspace.get("project/settings") != settings:
    raise RuntimeError("Stored settings differ")

before = workspace.verify()
snapshot = workspace.checkpoint()
inspection = DurableWorkspace.inspect_snapshot(snapshot)
if inspection["manifest_digest_matches_quorum"] is not True:
    raise RuntimeError("Checkpoint has no manifest-matching quorum")

restored = DurableWorkspace.recover(snapshot, "./demo-recovered")
if restored.get("project/settings") != settings:
    raise RuntimeError("Recovered settings differ")
if restored.verify() != before:
    raise RuntimeError("Recovered verification report differs")

print(restored.get("project/settings"))
print(snapshot)
```

Run it, then inspect the original workspace with the installed CLI:

```powershell
& $dwskPython ./workspace_example.py
& $dwskCli get ./demo-workspace project/settings
& $dwskCli verify ./demo-workspace
& $dwskCli checkpoint ./demo-workspace
```

The example writes two records, verifies them, creates a checkpoint, inspects its quorum, and reconstructs a separate workspace. Keys such as `project/settings` are opaque record keys; the slash does not create a directory.

## Python API

| Operation | Returns | Behavior |
| --- | --- | --- |
| `DurableWorkspace.init(root)` | Workspace handle | Creates the database and snapshot directory; refuses an existing runtime database |
| `DurableWorkspace(root)` | Workspace handle | Selects a path; construction alone does not initialize or verify it |
| `set(key, value)` | Committed journal event | Canonicalizes the value and atomically commits the record mutation plus event |
| `get(key)` | Current record value | Retrieves by known key; a missing record raises `KeyError` |
| `delete(key)` | Committed journal event | Deletes the current record and journals the operation; an absent key also produces a delete event |
| `verify()` | Runtime verification report | Checks SQLite integrity, the journal chain, and replay/value consistency |
| `checkpoint()` | Published generation path | Writes and publishes one verified logical bundle |
| `inspect_snapshot(path)` | Inspection report | Reports representation validity, quorum, and manifest agreement |
| `recover(snapshot, target)` | Recovered workspace handle | Requires an eligible quorum and an absent or empty target |

Mutation events carry `seq`, `event_id`, `timestamp_utc`, `kind`, `payload`, `previous_event_sha256`, and `event_sha256`. The payload records the key and revision; a set event also contains its value. Journal order is established by sequence and hash links. The event timestamp records the storage event's time.

Each `set` or `delete` is one transaction. Several separate calls do not become a single batch transaction. A revision belongs to the stored record's mutation behavior; use the journal when inspecting history rather than treating a current record as a complete history.

A successful runtime verification reports `ok`, `logical_digest`, `event_count`, and `record_count`. Snapshot inspection separately reports representation validity, `quorum_digest`, `quorum_kinds`, and `manifest_digest_matches_quorum`.

## Command-line reference

| Command | Operation |
| --- | --- |
| `dwsk init <root>` | Initialize a workspace |
| `dwsk set <root> <key> <json_value>` | Store a canonical JSON value |
| `dwsk get <root> <key>` | Print the current value as JSON |
| `dwsk delete <root> <key>` | Delete a record and journal the operation |
| `dwsk verify <root>` | Verify runtime integrity and logical consistency |
| `dwsk checkpoint <root>` | Publish a snapshot and print its generation path |
| `dwsk verify-snapshot <generation>` | Print representation/quorum inspection results |
| `dwsk recover <generation> <target>` | Recover into a new or empty directory |

Commands return zero on successful execution and two for operational errors handled by the CLI. `verify-snapshot` prints an inspection report: successful execution of that command does not mean every representation is valid or that recovery quorum exists. Read the report fields.

Use the Python API for structured values when shell JSON quoting would be inconvenient. All record values must satisfy the same canonical profile through either interface.

## Canonical data profile

DWSK-CJ-1 supports:

- null and Booleans;
- Unicode strings normalized to NFC;
- signed 64-bit integers;
- arrays whose order is preserved;
- objects with string keys, sorted after NFC normalization.

Booleans and integers retain distinct canonical representations. Floating-point values, out-of-range integers, nonstring object keys, unsupported Python containers, and object keys that collide after NFC normalization are rejected.

Represent nonintegral values with a documented string format when needed. Retain original binary/document bytes separately if exact byte identity matters; a record can store their hash and location. Canonicalization deliberately transforms supported text into its canonical form.

## Storage layout

```text
workspace/
  workspace.sqlite3
  workspace.sqlite3-wal       # SQLite-managed, when present
  workspace.sqlite3-shm       # SQLite-managed, when present
  snapshots/
    LATEST
    generation-name/
      manifest.json
      snapshot.sqlite3
      snapshot.jsonl
      snapshot.xml
```

The database contains workspace metadata, current records with revisions, and the journal. SQLite uses WAL and `synchronous=FULL`. A mutation's record update and event commit in the same transaction; failure during the transaction rolls both back.

A checkpoint exports one consistent logical bundle. SQLite, JSONL, and typed XML contain that same logical state in different representations. The manifest identifies their sizes, SHA-256 hashes, and shared logical digest. These copies occupy the same workspace storage location and are not independent off-device backups.

During publication, a generation-specific `.staging-*` directory and an owned `.LATEST-*.tmp` pointer may exist. They are intermediate state, not additional accepted snapshots. Do not substitute a copied live database or a staging directory for a verified checkpoint. Keep SQLite sidecars under SQLite's control.

## Checkpoint publication

The publication sequence writes the representations, syncs their files, writes and syncs the manifest last, and atomically promotes the generation directory. It then writes and syncs a unique temporary pointer and atomically replaces `LATEST`.

On Windows, construction remains parallel. Pointer promotion is guarded by a named mutex scoped to the current user, session, and normalized resolved workspace path. Acquisition waits up to five seconds in the Windows API. Eligible access/sharing/locking errors during pointer replacement receive a bounded two-second retry. The existing pointer is never pre-deleted.

When Windows reports an abandoned mutex owner, the next owner checks any existing pointer and its complete referenced generation before proceeding. Inconsistent state is refused; absence of a pointer is permitted for an interrupted first publication. Mutex handles and ownership are released through normal exception handling.

Coordination applies to cooperating publishers using the same normalized path, user, and session. Different aliases, sessions/users, and external programs are outside that guarantee. `LATEST` is the last completed pointer promotion, not a guarantee of ordering by generation creation time. Scheduling and in-progress OS calls can extend observed wall time beyond a wait/retry deadline.

See [DURABILITY_CONTRACT.md](DURABILITY_CONTRACT.md) for the exact state transitions and Windows qualifications.

## Verification and recovery

Runtime verification checks database integrity and the journal's sequence, hash links, event hashes, head, and event count. Replayed values must agree with the current record values. The consistency check also applies before checkpoint publication and during snapshot inspection/recovery.

A representation is eligible for recovery only when its file size/hash match the manifest, it parses, and its journal and replayed values verify. Automatic recovery requires at least two eligible representations with the same logical digest, and that digest must match the published manifest. There is no intrinsic SQLite/JSONL/XML preference.

A recovery procedure should:

1. Preserve the damaged workspace before attempting changes.
2. Inspect a published generation with `verify-snapshot`.
3. Confirm the eligible quorum and manifest agreement.
4. Recover into a separate absent or empty target.
5. Verify the recovered workspace and compare required application invariants before adopting it.

If agreement cannot be established, recovery refuses. It does not choose the newest file or a preferred format. See [RECOVERY_PLAYBOOK.md](RECOVERY_PLAYBOOK.md).

### Failure behavior

| Situation | Behavior |
| --- | --- |
| Invalid canonical value | Reject the mutation; retain committed state |
| Journal append fails during mutation | Roll back the record change and event transaction |
| Values disagree with journal replay | Fail verification/checkpoint eligibility |
| Checkpoint fails before publication | Attempt cleanup of its owned staging material |
| Generation publishes but pointer promotion fails | Retain the complete generation for inspection; do not pre-delete the existing pointer |
| Mutex acquisition times out | Raise an explicit error and clean the publisher's owned temporary pointer through ordinary exception handling |
| Abandoned owner leaves inconsistent pointer/generation state | Refuse promotion after inspection |
| One representation is damaged | Recover from the other two if they remain eligible and agree with the manifest |
| Quorum or manifest agreement is absent | Refuse automatic recovery |
| Process is forcibly terminated | Reopen and verify committed state; inspect interrupted artifacts separately |

Ordinary exception cleanup and forced termination are different cases: a killed process cannot execute cleanup. Preserve unexpected remnants for inspection and do not delete another publisher's files merely because they look temporary.

Hashes and agreement establish the stated consistency checks, not authorship or truth of record contents. Windows directory-handle synchronization is not implemented. The tests do not establish physical power-loss durability, storage-device failure tolerance, or independent backup recovery.

## Validation record

### R4 source adoption — 2026-11-04

The adopted runtime, checker and repaired process helpers passed the complete 244-case R4 qualification across ordinary and optimized Python: 24 recovery, 32 value-admission, 16 worker-lifecycle, 26 checker-control, 17 unit and seven self-check cases per mode. The added development runner separately passed the existing 17 units and seven self-checks in both modes (48 overlapping checks). These counts overlap and are not independent campaigns.

The recovery controls include real owned interruptions and competing workers, plus finite injected database/filesystem failures. Qualified executable bytes were verified against the review tree. The complete raw records remain outside the repository; the bounded result is recorded in [VALIDATION_REPORT.md](VALIDATION_REPORT.md) and the repository [validation ledger](../docs/xosg/MIGRATION_VALIDATION.md).

These are source checks, not rebuilt-wheel checks. The runtime remains standard-library-only; owned development execution is Windows-qualified. Physical power-loss durability, hostile filesystem races, external-tool coordination and application/logger integration are outside the claim.

### Historical source and installed-build evidence


Source validation and installed-wheel validation are recorded separately:

| Scope | Recorded result |
| --- | --- |
| Source hardening / deterministic fuzzy / torture | 32 / 1,000 / 8 passed |
| Source native checkpoint trials | 20 passed, covering 240 calls |
| Installed unit / self-validation | 17 / 7 passed in each mode |
| Installed retry / native mutex tests | 8 / 12 passed in each mode |
| Installed CLI checks | 15 passed in each mode |
| Installed single-format recovery variants | 3 passed in each mode |
| Installed four-process checkpoint calls | 12 passed in each mode |

Normal and optimized Python were exercised. Installed checks ran outside the source tree with installed imports verified. Native mutex tests covered exclusion, timeout, real owner termination, abandoned-state inspection/refusal, and handle cleanup. The broader source matrix was distributed across modes rather than run twice in full.

These are bounded Windows/Python 3.14 results. They do not establish exhaustive coverage or runtime acceptance on every declared interpreter/OS. Earlier failed campaigns remain retained in the private evidence; the underlying Windows cause remains unresolved.

Read the [source-validation basis](VALIDATION_REPORT.md) and [installed build report](BUILD_REPORT.md). The build report describes its stated build date. [Artifact identities](docs/build/ARTIFACTS.json) and [distribution checksums](docs/build/SHA256SUMS) refer to the original binaries held outside this repository. [SOURCE_SHA256SUMS](SOURCE_SHA256SUMS) covers this source export, including the current README.

## Project files

| Location | Contents |
| --- | --- |
| [src/durable_workspace/](src/durable_workspace) | Workspace implementation, canonical profile, formats, and CLI |
| [tests/](tests) | Included unit and readiness checks |
| [validate.py](validate.py) | Included self-validation program |
| [examples/](examples) | Small Python API example |
| [schemas/](schemas) | Snapshot manifest schema |
| [templates/workspace-control/](templates/workspace-control) | Starting files for STATE, TODO, LOG, ERROR_LOG, DECISIONS, and workspace metadata |
| [MODULE_BOUNDARY.md](MODULE_BOUNDARY.md) | Persistence boundary |
| [DEVELOPMENT_GUIDANCE.md](DEVELOPMENT_GUIDANCE.md) | Integration and source-preservation guidance |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

The control-file templates are static files included with the source. The Python package does not update them automatically.

## Working on the kit

Read the contract before changing transaction, journal, publication, or recovery behavior. Use disposable fixtures and specify the expected rejection type/cause. Check full state preservation where promised; a return code or unchanged record count alone is insufficient.

From the project directory, after source installation:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe validate.py
```

Keep databases, snapshots, raw logs, and temporary environments outside the source export. Record source-validation results separately from installed-package checks and preserve failures when reviewing a later successful run.

Licensing and attribution continue under the preserved OpenSurface [MIT license and copyright notice](../docs/xosg/LICENSE). The [migration record](../docs/xosg/MIGRATION.md) records source lineage and the original aggregate license annotation. Preserve applicable notices when redistributing source.
