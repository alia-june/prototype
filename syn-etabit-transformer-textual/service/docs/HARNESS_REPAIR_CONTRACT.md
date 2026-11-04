# Service-harness repair contract

Date: 2026-10-31. Approved scope: AUTH-19B. Service harness: `docstream.harness/1.3`.

This increment repairs only HM-D01 and HM-D02 from the AUTH-19A independent
meta-verification. Its governing evidence is `HARNESS_META_FINDINGS.md`,
`HARNESS_META_VALIDATION.md`, the retained failed discovery and 62-method
aggregate outputs, the AUTH-16 cleanup contract and the AUTH-19B ownership
diagnostics. Strmdocx product behavior remains outside this repair.

## HM-D01 ownership and lifecycle rules

The Windows worker launch is owned by one `OwnedProcess` instance and one
private named job. The owner now creates the launch process suspended, assigns
that suspended process to the configured kill-on-close job, and resumes the
primary thread only after assignment succeeds. Construction failure terminates
and waits for only the process created by that constructor. It does not scan or
terminate unrelated Python processes.

The suspended launch closes the interval in which a Windows virtual-environment
redirector could create the real interpreter before job assignment. The
retained cleanup evidence records the launch strategy, suspension, assignment
before resume, resume completion and launcher PID.

The shared owner is the sole cleanup authority. The native-harness wrapper may
call `close()` but may not pre-terminate the job or consume its live membership
before the owner captures process synchronization handles. On close, the owner:

1. Enumerates the exact private job and opens synchronization/query handles only
   for PIDs whose membership in that job is confirmed.
2. Requests job termination when active owned processes remain.
3. Waits for every captured process handle to signal and for job accounting to
   reach zero within the existing five-second shared budget.
4. Closes captured/job handles, then reaps the launch process within the
   existing ten-second launcher bound.
5. Retains explicit failed cleanup evidence if any query, signal wait, job-zero
   wait or launcher reap cannot be established. A later close cannot relabel a
   failed cleanup as confirmed.

Launcher exit, descendant exit, job zero and release of the retained log are
distinct observations. Success requires the process/job evidence plus immediate
exclusive opening of the log after the parent's log context closes. There is no
sleep, retry, deletion workaround or ignored `WinError 32` between close and
that probe.

## HM-D02 result-schema rules

`docstream.harness/1.3` adds an explicit `owned_worker_started` field. A started
mode uses `true`, a concrete PID, a Boolean `owned_worker_stopped`, and confirmed
or failed cleanup evidence.

A mode whose combined budget is exhausted before worker creation uses one
stable incomplete shape:

- `owned_worker_started` is `false`;
- `owned_worker_pid`, `owned_worker_stopped` and `owned_job_stopped` are null;
- `cases` is empty, `counts` is empty and `coverage_complete` is false;
- `owned_cleanup.status` is `not_started`, its scope is `none` and
  `job_assigned` is false;
- no cleanup file or event journal is required because no worker existed.

The independent auditor accepts `not_started` only with those corresponding
null/false claims. It continues to require Boolean stopped state and confirmed
or failed cleanup for any mode that did start. A nonexistent worker is never
reported as stopped.

## Maintained verification

The bounded validation requires:

- 24 strict cleanup cycles: eight early, eight ready-descendant and eight
  launcher-exited/descendant-live cases;
- first-attempt exclusive log opening in every cycle;
- three consecutive 62-method harness-focused aggregates and an immediate
  isolated comparison;
- nine focused meta-verifier methods;
- 30 meta hardening cases, 1,000 deterministic fuzzy cases and eight torture
  scenarios;
- three consecutive complete project discoveries;
- exact verification of all 1,038 meta inputs, target source identities and a
  final no-worker inventory.

Validation remains bounded to 1,200 seconds for repair work, 900 seconds for a
meta run, 512 MiB retained evidence, 1,000 fuzzy cases, 24 cleanup cycles, three
discoveries and three focused aggregates. No dependency is added.

## Exclusions

This increment does not change document transformations, native-model
semantics, format policy, WordNet or Etabit maps, persistence, rendering, GPU
work, release behavior or agentic control. It does not establish a universal
Windows file-release bound or independent attestation. AUTH-19C product repair
remains closed.
