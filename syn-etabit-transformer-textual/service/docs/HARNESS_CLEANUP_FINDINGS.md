# SH-D01 cleanup repair findings

Date: 2026-10-30. AUTH-16. Status: **resolved for the validated Windows cleanup
boundary**. Full bounded workload and verification results are in
HARNESS_CLEANUP_VALIDATION.md.

## Original failure

The old service-harness deadline test reported an incomplete worker and a
stopped launcher, then raised WinError 32 while deleting process-output.txt.
AUTH-15 retained the failed suite and isolated retry. AUTH-16's untouched
existing test also reproduced the error before correction; see
`.docstream/harness-cleanup-runs/auth16-20261030/existing-deadline-before.txt`.

The original helper closed its Windows job handle and reaped the launcher.
It had no explicit descendant-completion barrier. A controlled pre-correction
test records `job_handle_closed`, launcher kill and reap without any observed
`active-0` event. Its failed assertion remains in
`completion-contract-before.txt`. The old source is preserved in source-before/.
The specific holder of the historical file handle was not independently
attributed; this report does not invent that attribution.

## First correction was insufficient

A first repair retained the job handle, terminated the job and polled its
active-process count to zero. The first real early-interruption cycle still
failed its immediate exclusive-file open, after its job-zero and launcher-stop
assertions passed. That failure is retained in cleanup-checks-after.txt,
the partial cycle directory, and runner-job-zero-only.py.

This matters to the proof: a zero group count alone was insufficient for the
observed log-release boundary. The first repair was not delivered as complete.

## Strengthened completion and ownership checks

The shared helper now captures synchronization handles for processes enumerated
from its owned job, verifies membership against that same job, requests owned
job termination, waits for process exit signals and observes the group count at
zero before closing handles. The group/process wait shares a five-second
budget. Launcher reaping retains its original separate timeout.

The helper reports CleanupError and failed evidence on timeout or API/reap
failure. Repeated close cannot turn failed cleanup into success. A successful
close is idempotent. It does not wait on a PID whose current process is outside
the owned job. Controlled tests cover these failure/ownership properties without
terminating a real unrelated process.

Service mode results now retain cleanup.json and owned_cleanup evidence, with
a distinct owned_job_stopped observation. A cleanup error causes supervisor
failure. Successfully stopping a deliberately interrupted worker does not change
that worker's INCOMPLETE outcome into PASS.

## Measurement was strengthened before final acceptance

An intermediate 20-cycle sequence passed after process-handle waits were added.
Its diagnostic retention wrote a JSON record before attempting exclusive open.
Although it had no retry loop, that write could delay the measurement. The
test was therefore strengthened: exclusive open is the first operation after
the parent's log context closes; success/failure evidence is written afterward.
The intermediate source and result remain retained as development evidence.

The final strict sequence passes all 20 cycles, including eight early, eight
ready-descendant and four already-exited-launcher cases. Every log opens
exclusively on the first attempt. All four exited-launcher cases confirm the
launcher had stopped while an owned descendant remained before cleanup. There
is no log deletion, retry sleep or ignored error to hide the observation.

Across development, one initial real cycle failed, one intermediate sequence
completed 20 cycles and the final stricter sequence completed 20. These are
separate bounded attempts, not a claim of only 20 lifetime executions. The final
acceptance evidence is the strict 20-cycle sequence identified in DELIVERY.json.

## Resolution and preserved limits

The original failing deadline test passes unchanged in the final 92-method
regression selection. Six maintained cleanup methods pass, including the
20-cycle sequence and controlled failures. Fresh native and full-service runs
pass, with service job completion explicitly confirmed for all three modes.
The final matching-process inventory is empty.

Only harness/runner.py and harness/__init__.py change among 89 protected
pre-existing files. The other 87 remain byte-identical, including old tests,
product/native source, existing native/meta cleanup wrappers and historical
failure reports. Product rules from AUTH-15 remain unchanged.

This resolves SH-D01 within the tested ownership/cleanup boundary. It is not
proof of every Windows/kernel/I/O failure, attribution of historical file-handle
ownership, redesigned process admission, POSIX descendant certification,
production capacity or release acceptance. Agentic-control integration remains
last and outside this scope.
