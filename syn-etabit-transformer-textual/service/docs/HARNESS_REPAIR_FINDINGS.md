# Service-harness repair findings

Date: 2026-10-31. AUTH-19B. Result: **HM-D01 and HM-D02 resolved within the bounded local validation**.

## HM-D01 — exact owner and competing cleanup path

The retained pre-repair ownership probe identifies the real worker as the base
Python interpreter spawned by the service virtual-environment redirector. In
`diagnostics-before/launch-owner.jsonl`, interpreter PID 17144 is the child of
launcher PID 10680, is confirmed in the private job and owns four file handles
to that run's `child.log`. The exact numeric PIDs and handle values are local to
that observation; the process relationship and file path are retained in the
packet.

The shared `OwnedProcess.close()` already knew how to enumerate job members,
bind synchronization handles, terminate the job, wait for process signals and
observe job zero. The native wrapper nevertheless called `TerminateJobObject`
first and waited only for the active-process count to become zero. It then
called the shared helper after live job membership could already be gone. That
ordering deprived the helper of the process handles needed to distinguish
accounting zero from completed interpreter teardown. The intermittent
`WinError 32` was the resulting visible boundary: temporary-directory deletion
could race the interpreter's final inherited-log closure.

The repair removes the wrapper's competing termination loop. It delegates the
entire capture/terminate/wait operation to the shared owner. Launch is also now
suspended until private-job assignment completes, removing the separate
redirector-before-assignment containment interval. The repair does not kill by
process name, enumerate unrelated workers for termination, retry deletion or
weaken the exclusive-open assertion.

## HM-D02 — explicit pre-start state

The former pre-start branch produced a shorter ad hoc dictionary. It now uses a
single `prestart_result()` constructor and the `/1.3` schema. The result says
that no worker started; it does not claim that a nonexistent worker stopped.
The independent meta-auditor rejects a not-started packet that claims a PID,
job completion or Boolean stopped state, and it still rejects a started packet
without resolved cleanup evidence.

## Retained development evidence

The AUTH-19A failures remain unchanged. AUTH-19B also retains:

- instrumented aggregate failures before repair;
- a first post-diagnostic ownership attempt in which the transient deletion
  denial had already cleared before Restart Manager/handle inspection;
- the stronger live ownership record that attributes the log handles to the
  base interpreter;
- an earlier passing post-repair meta run that was not designated final because
  the 24-cycle test still wrote its new evidence under the historical AUTH-16
  parent directory;
- the definitive rerun after moving new cleanup evidence to the AUTH-19B root.

No historical file was overwritten. The destination correction changed no
runtime behavior, but validation was repeated because it changed a tested
source file.

## Lessons and anti-lessons

- A wrapper must not partially perform cleanup before the component that owns
  the full cleanup proof.
- Job accounting zero and signaled process handles answer different questions.
- A venv launcher PID is not necessarily the interpreter that inherited the
  log; process ownership must preserve the launcher/descendant distinction.
- Job assignment after ordinary process startup contains a race even if most
  observed launches inherit the job correctly; assignment before resume closes
  that interval.
- Resource release must be probed at the intended boundary. Diagnostic writes,
  sleeps, delete retries and isolated reruns can conceal the race.
- A not-started operation needs a complete schema, not a successful-stop
  fiction and not an abbreviated record.
- A passing run from changed source cannot validate a later source state.
- Evidence placed under the wrong authorization root is a provenance defect
  even when filenames are unique and no historical evidence is overwritten.

## Remaining boundaries

The validation proves the declared outcomes on this local Windows system under
the retained workloads. It does not prove universal Windows behavior, arbitrary
executable containment, leak absence, security isolation or production
capacity. No Strmdocx product defect was repaired or newly established by this
increment. Product work remains gated separately.
