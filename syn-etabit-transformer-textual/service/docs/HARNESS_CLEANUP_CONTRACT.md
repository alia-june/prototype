# Owned-process cleanup contract

Date: 2026-10-30. Approved scope: AUTH-16. Service harness: `/1.2`.

This increment repairs SH-D01 in the shared service-harness process owner. The
governing sources are PROJECT_DECISIONS.md, FORMAT_HARDENING_FINDINGS.md,
FORMAT_HARDENING_VALIDATION.md and their retained WinError 32 logs. The user
approved the bounded helper repair, 20 dedicated cycles, regression checks and
fresh native/service validation. Previous evidence remains historical and intact.

## Owned cleanup boundary

OwnedProcess manages only the process it launched and its private Windows job.
It does not enumerate or terminate unrelated system processes. A successful
constructor records that assignment to the job completed. If construction fails
before assignment, fallback cleanup concerns the owned launcher and does not
claim Windows-job completion.

On Windows, normal close now performs these steps:

1. Query the owned job's active-process count and enumerate its process IDs.
2. Open synchronization/query handles for those processes and confirm membership
   in that exact job. A reused PID outside the job is not waited or terminated.
   A process that has already disappeared is recorded only through the remaining
   job observations; unexpected API failures are explicit cleanup errors.
3. Request termination of the owned job if it still has active processes.
4. Wait for captured process handles to signal exit and poll the job until its
   active-process count reaches zero. Capture any still-listed owned members
   while the job remains active. The shared wait budget is five seconds from
   cleanup entry.
5. Close synchronization/job handles and reap the launcher. The launcher's
   existing ten-second reap timeout remains separate from the five-second job
   completion budget.

Waiting for process signals matters: the first job-count-only correction reached
zero but still failed the immediate exclusive-log test. That failed attempt and
its source are retained. The strengthened implementation checks process exit
signals as well as the group count; no log-open retry or cleanup-error suppression
is used to produce a pass.

Microsoft documents that job termination applies to associated processes and
nested child jobs, and that terminating another process initiates asynchronous
termination. See [TerminateJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject)
and [TerminateProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess).
The job's active count is an accounting observation; see
[job accounting](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information).
These references support the mechanism. The local tests establish only the
declared observed outcomes, not a universal operating-system completion bound.

## Success, error and reporting

`cleanup_evidence` records scope, assignment, active counts, termination request,
observed process IDs, wait observations, handle closure, launcher stop, duration
and status. Wait counters count calls and may include repeated observations of
the same handle; they are not unique-process totals.

Successful repeated close is idempotent. A timeout or API/reap failure produces
CleanupError, retains failed evidence and cannot turn into confirmed success
merely because close is called again. Failure handling still attempts handle
closure and launcher reaping. If cleanup cannot be established, no success is
claimed.

Each service mode retains `cleanup.json`, even if close raises. The final mode
record includes `owned_cleanup` and an explicit Windows `owned_job_stopped`
observation. The existing launcher-stop field remains distinct. A cleanup error
propagates to a failed supervisor result rather than becoming a product PASS.
Deliberately timed-out work retains INCOMPLETE; confirmed cleanup does not change
that work outcome into PASS.

The normal non-Windows process-group behavior is retained. The new Windows
checks do not certify POSIX descendant shutdown or general arbitrary-process
containment. Job assignment/creation policy is not redesigned by this increment.

## Dedicated verification

Maintained verification is `tests/test_harness_cleanup.py`:

- Eight early-interruption cycles.
- Eight cycles after an owned descendant reports readiness.
- Four cycles where the launcher exits while an owned descendant remains.
- Controlled checks of group-zero/handle-close ordering and idempotence.
- Controlled active-group timeout, query error and process-signal timeout.
- A controlled PID-membership mismatch check that performs no wait on that PID.

The 20-cycle sequence retains each input before launch, its exact file hash,
process observations and cleanup evidence. An explicit gate lets fixture parents
spawn descendants only after assignment to their owned job. Fixture roles and
output roots are closed; inputs cannot select arbitrary executable code.

After closing the parent's log handle, each cycle opens the retained log with
Windows sharing disabled. There is no intervening retry loop or artificial
file-release delay. The file is preserved. Dedicated checks assert a 600-second
run budget, bounded readiness and the helper's completion budget, and retained
evidence below 512 MiB. An initial partial failed development run is separate
from the final 20-cycle sequence.

## Outputs and limits

Changes are confined to `harness/runner.py` and its reporting identity in
`harness/__init__.py`, plus the new cleanup tests, three HARNESS_CLEANUP reports
and authorized project-note updates. Existing tests and native/meta cleanup
wrappers retain their source bytes.

Evidence is under `.docstream/harness-cleanup-runs/auth16-20261030/` and fresh
`auth16-*` native/service run areas. Native validation retains 900 seconds,
512 MiB, 100/1,000/eight and 2,000 submitted attempts. Service validation retains
1,200 seconds, 512 MiB, 500 fuzzy cases, four clients/1,800 loop requests,
2,000 torture calls, 20 actor crash cycles and 25 render calls.

No product transformation, format policy, source hash, database schema,
dependency, package version, release, GPU, bypass or agent-control integration
changes. The previously approved CR policy remains intact. Agentic-control
integration remains last.
