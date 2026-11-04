"""Bounded mode supervisor. Only children created here can be terminated."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time

from . import HARNESS_VERSION
from .core import RUNS_ROOT, SERVICE_ROOT, WORKSPACE, footprint, load_case, save


class CleanupError(RuntimeError):
    """Owned process cleanup was attempted but could not be confirmed."""


class _SuspendedWindowsProcess:
    """Small Popen-compatible adapter created suspended and assigned atomically."""

    def __init__(self, args, log, job):
        import msvcrt
        import win32api, win32con, win32event, win32file, win32job, win32process
        self.args = [os.fsdecode(os.fspath(value)) for value in args]
        self.pid = None
        self.returncode = None
        self._handle = None
        current = win32api.GetCurrentProcess()
        source = msvcrt.get_osfhandle(log.fileno())
        output = win32api.DuplicateHandle(current, source, current, 0, True,
                                          win32con.DUPLICATE_SAME_ACCESS)
        null_source = win32file.CreateFile("NUL", win32con.GENERIC_READ,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE, None,
            win32con.OPEN_EXISTING, 0, None)
        stdin = win32api.DuplicateHandle(current, null_source, current, 0, True,
                                         win32con.DUPLICATE_SAME_ACCESS)
        null_source.Close()
        startup = win32process.STARTUPINFO()
        startup.dwFlags |= win32process.STARTF_USESTDHANDLES
        startup.hStdInput, startup.hStdOutput, startup.hStdError = stdin, output, output
        process = thread = None
        try:
            flags = (win32process.CREATE_SUSPENDED | win32process.CREATE_UNICODE_ENVIRONMENT |
                     subprocess.CREATE_NO_WINDOW)
            process, thread, self.pid, _ = win32process.CreateProcess(
                None, subprocess.list2cmdline(self.args), None, None, True, flags,
                dict(os.environ), None, startup)
            self._handle = process
            win32job.AssignProcessToJobObject(job, process)
            win32process.ResumeThread(thread)
        except BaseException:
            if process is not None:
                try: win32api.TerminateProcess(process, 3)
                except Exception: pass
                win32event.WaitForSingleObject(process, 5000)
                process.Close()
                self._handle = None
            raise
        finally:
            if thread is not None: thread.Close()
            stdin.Close(); output.Close()

    def _finish(self):
        import win32process
        if self.returncode is None:
            self.returncode = win32process.GetExitCodeProcess(self._handle)
        if self._handle is not None:
            self._handle.Close(); self._handle = None
        return self.returncode

    def poll(self):
        if self.returncode is not None: return self.returncode
        import win32con, win32event
        if win32event.WaitForSingleObject(self._handle, 0) == win32con.WAIT_OBJECT_0:
            return self._finish()
        return None

    def wait(self, timeout=None):
        if self.returncode is not None: return self.returncode
        import win32con, win32event
        milliseconds = win32event.INFINITE if timeout is None else max(0, int(timeout * 1000))
        if win32event.WaitForSingleObject(self._handle, milliseconds) != win32con.WAIT_OBJECT_0:
            raise subprocess.TimeoutExpired(self.args, timeout)
        return self._finish()

    def kill(self):
        if self.poll() is None:
            import win32api
            win32api.TerminateProcess(self._handle, 1)


class OwnedProcess:
    def __init__(self,args,log):
        self.job=None
        self.job_assigned=False
        self.launch_evidence={"strategy":"pending"}
        self.cleanup_evidence={"status":"pending"}
        self.process=None
        try:
            if os.name=="nt":
                import win32job
                self.job=win32job.CreateJobObject(None,"DocstreamHarness-"+secrets.token_hex(12))
                info=win32job.QueryInformationJobObject(self.job,win32job.JobObjectExtendedLimitInformation)
                info["BasicLimitInformation"]["LimitFlags"]=win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
                win32job.SetInformationJobObject(self.job,win32job.JobObjectExtendedLimitInformation,info)
                self.process=_SuspendedWindowsProcess(args,log,self.job)
                self.job_assigned=True
                self.launch_evidence={"strategy":"windows_suspended_job",
                    "created_suspended":True,"job_assigned_before_resume":True,
                    "primary_thread_resumed":True,"launcher_pid":self.process.pid}
            else:
                self.process=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,
                    start_new_session=True)
                self.launch_evidence={"strategy":"posix_session","created_suspended":False,
                    "job_assigned_before_resume":None,"primary_thread_resumed":None,
                    "launcher_pid":self.process.pid}
        except BaseException:
            if self.process is not None: self.close()
            elif self.job is not None:
                self.job.Close(); self.job=None
            raise

    def close(self):
        previous=self.cleanup_evidence
        if previous.get("status")=="failed":
            raise CleanupError(previous["error"])
        if previous.get("status")=="confirmed" and self.job is None and self.process.poll() is not None:
            return
        started=time.monotonic()
        evidence={"status":"pending","scope":"windows_job" if os.name=="nt" and self.job_assigned else "launcher",
                  "job_assigned":self.job_assigned,"active_processes_before":None,"active_processes_after":None,
                  "termination_requested":False,"job_query_samples":0,"job_handle_closed":False,
                  "process_ids_observed":[],"process_exit_waits":0,
                  "launch":dict(getattr(self,"launch_evidence",{"strategy":"legacy_test_double"}))}
        handles={}
        error=None
        try:
            if self.job is not None:
                try:
                    if os.name=="nt" and self.job_assigned:
                        import win32api,win32con,win32event,win32job
                        def capture():
                            # Bind wait handles only to processes enumerated in
                            # this owned job, then confirm membership against PID reuse.
                            for pid in win32job.QueryInformationJobObject(self.job,win32job.JobObjectBasicProcessIdList):
                                if pid in handles: continue
                                try:
                                    handle=win32api.OpenProcess(win32con.SYNCHRONIZE|win32con.PROCESS_QUERY_INFORMATION,False,pid)
                                except win32api.error as exc:
                                    if exc.winerror==87: continue  # Process already disappeared.
                                    raise
                                try:
                                    if not win32job.IsProcessInJob(handle,self.job):
                                        handle.Close()
                                        continue
                                except Exception:
                                    handle.Close()
                                    raise
                                handles[pid]=handle
                                evidence["process_ids_observed"].append(pid)
                        def wait_captured():
                            for handle in handles.values():
                                remaining=max(0,int((5-(time.monotonic()-started))*1000))
                                if win32event.WaitForSingleObject(handle,remaining)!=win32con.WAIT_OBJECT_0:
                                    raise TimeoutError("owned Windows process did not signal exit within five seconds")
                                evidence["process_exit_waits"]+=1
                        def active():
                            count=win32job.QueryInformationJobObject(self.job,win32job.JobObjectBasicAccountingInformation)["ActiveProcesses"]
                            evidence["job_query_samples"]+=1
                            evidence["active_processes_after"]=count
                            return count
                        count=active()
                        evidence["active_processes_before"]=count
                        capture()
                        if count:
                            win32job.TerminateJobObject(self.job,2)
                            evidence["termination_requested"]=True
                        wait_captured()
                        while count:
                            if time.monotonic()-started>=5:
                                raise TimeoutError("owned Windows job did not reach zero active processes within five seconds")
                            time.sleep(.01)
                            capture()
                            wait_captured()
                            count=active()
                finally:
                    for handle in handles.values(): handle.Close()
                    self.job.Close()
                    self.job=None
                    evidence["job_handle_closed"]=True
            elif self.process.poll() is None and os.name!="nt":
                import signal
                os.killpg(self.process.pid,signal.SIGKILL)
        except Exception as exc:
            error=exc
        finally:
            try:
                if self.process.poll() is None:
                    self.process.kill()
                self.process.wait(timeout=10)
            except Exception as exc:
                error=exc if error is None else RuntimeError(f"{error}; launcher reap failed: {exc}")
            evidence.update(status="failed" if error else "confirmed",launcher_stopped=self.process.poll() is not None,
                            elapsed_seconds=round(time.monotonic()-started,6))
            if error: evidence["error"]=f"owned-process cleanup failed: {type(error).__name__}: {error}"
            self.cleanup_evidence=evidence
        if error:
            raise CleanupError(evidence["error"]) from error

    def working_set(self):
        if os.name!="nt" or self.process.poll() is not None:
            return None
        try:
            import win32api,win32con,win32process
            handle=win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION|win32con.PROCESS_VM_READ,False,self.process.pid)
            try:
                return win32process.GetProcessMemoryInfo(handle)["WorkingSetSize"]
            finally:
                handle.Close()
        except Exception:
            return None

    def job_memory(self):
        if os.name!="nt" or self.job is None:
            return None
        try:
            import win32job
            info=win32job.QueryInformationJobObject(self.job,win32job.JobObjectExtendedLimitInformation)
            return {"peak_job_committed_bytes":info["PeakJobMemoryUsed"],"peak_process_committed_bytes":info["PeakProcessMemoryUsed"]}
        except Exception:
            return None


def product_hashes():
    root=SERVICE_ROOT/"src"/"docstream_cpu"
    return {str(p.relative_to(WORKSPACE)).replace("\\","/"):sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.glob("*.py"))}


def replay_mode(kind):
    if kind in ("regression","golden","workflow"):
        return "rigid"
    if kind in ("limits","storage_faults","crash_recovery","network_load","render_recovery"):
        return "torture"
    return "fuzzy"


def recover_interrupted(root,mode,seed,reason):
    records=[]
    renders=0
    path=root/"events.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8",errors="replace").splitlines():
            try:
                item=json.loads(line)
            except ValueError:
                continue
            if item.get("event")=="case_finished":
                records.append(item)
            if item.get("event")=="render_submitted":
                renders=max(renders,item["render_call"])
    result={"schema":HARNESS_VERSION,"mode":mode,"seed":seed,"status":"failed" if any(r["status"]=="failed" for r in records) else "incomplete","coverage_complete":False,
            "incomplete_reasons":[reason],"counts":dict(Counter(r["status"] for r in records)),"cases":records,"metrics":{"render_calls":renders},"supervisor_recovered":True}
    save(root/"results.json",result)
    return result


def prestart_result(mode,seed,reason):
    """Stable explicit result for a mode that never created an owned worker."""
    return {"schema":HARNESS_VERSION,"mode":mode,"seed":seed,"status":"incomplete",
            "coverage_complete":False,"incomplete_reasons":[reason],"counts":{},
            "cases":[],"metrics":{},"owned_worker_started":False,
            "owned_worker_pid":None,"owned_worker_stopped":None,
            "owned_cleanup":{"status":"not_started","scope":"none","job_assigned":False,
                "active_processes_before":None,"active_processes_after":None,
                "termination_requested":False,"job_query_samples":0,"job_handle_closed":False,
                "process_ids_observed":[],"process_exit_waits":0,"launcher_stopped":None,
                "elapsed_seconds":0.0,"launch":{"strategy":"not_started"}},
            "owned_job_stopped":None,
            "supervisor_metrics":{"retained_bytes_peak_sample":None,"poll_seconds":None,
                "launch_process_working_set_bytes":{"first":None,"last":None,"peak":None,"samples":0},
                "job_memory":None,"memory_scope":"worker not started"}}


def run(args):
    if not 0<=args.seed<2**32:
        raise ValueError("seed must be a 32-bit nonnegative integer")
    if not 1<=args.cases<=500 or not 4<=args.requests<=1800 or args.requests%4 or not 1<=args.crashes<=20:
        raise ValueError("case/request/crash counts exceed approved limits")
    if not 0<args.max_seconds<=1200 or not 0<args.max_mib<=512:
        raise ValueError("time or retained-byte limit exceeds approved scope")
    if args.replay:
        replay_case=load_case(args.replay)
        expected_mode=replay_mode(replay_case["kind"])
        if args.mode!="all" and args.mode!=expected_mode:
            raise ValueError("replay case belongs to mode "+expected_mode)
    run_id=args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+secrets.token_hex(3)
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",run_id):
        raise ValueError("run ID requires 1-64 letters, numbers, underscores or hyphens")
    for part in (RUNS_ROOT,*RUNS_ROOT.parents):
        if part.exists() and (part.is_symlink() or part.is_junction()):
            raise ValueError("linked harness output roots are unsupported")
    RUNS_ROOT.mkdir(parents=True,exist_ok=True)
    root=RUNS_ROOT/run_id
    root.mkdir(exist_ok=False)
    started=time.monotonic()
    original=product_hashes()
    metadata={"schema":HARNESS_VERSION,"run_id":run_id,"seed":args.seed,"python":sys.version,
        "created_utc":datetime.now(timezone.utc).isoformat(),"product_version":importlib.metadata.version("docstream-cpu"),
        "packages":{name:importlib.metadata.version(name) for name in ("mcp","pydantic","playwright","markdown-it-py","python-docx","Pillow")},
        "limits":{"seconds":args.max_seconds,"retained_bytes":args.max_mib*1024*1024,"generated_cases":args.cases,"torture_loop_requests":args.requests,"torture_total_service_calls":2000,"clients":4,"crash_cycles":args.crashes,"combined_render_calls":25},
        "product_hashes_before":original}
    metadata["harness_hashes"]={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob("*.py"))}
    save(root/"run.json",metadata)
    modes=["rigid","fuzzy","torture"] if args.mode=="all" else [args.mode]
    if args.replay:
        modes=[expected_mode]
    results=[]
    renders=0
    try:
        for mode in modes:
            remaining=args.max_seconds-(time.monotonic()-started)
            if remaining<=0 or footprint(root)>=args.max_mib*1024*1024:
                results.append(prestart_result(mode,args.seed,"combined run budget reached before mode start"))
                continue
            mode_root=root/mode
            mode_root.mkdir()
            config={"mode":mode,"root":str(mode_root),"seed":args.seed,"seconds":min(remaining,{"rigid":180,"fuzzy":300,"torture":720}[mode]),
                "max_bytes":args.max_mib*1024*1024,"render_budget":max(0,25-renders),"cases":args.cases,"requests":args.requests,"crashes":args.crashes,
                "replay":str(args.replay.resolve()) if args.replay else None}
            save(mode_root/"config.json",config)
            print(json.dumps({"event":"mode_started","mode":mode,"run":str(root)}),flush=True)
            reason=None
            memory=[]
            job_memory=[]
            peak_bytes=footprint(root)
            with (mode_root/"process-output.txt").open("wb") as log:
                owned=OwnedProcess([sys.executable,"-m","docstream_cpu.harness.worker","--config",str(mode_root/"config.json")],log)
                try:
                    deadline=time.monotonic()+config["seconds"]
                    while owned.process.poll() is None:
                        sample=owned.working_set()
                        if sample is not None:
                            memory.append(sample)
                        job_sample=owned.job_memory()
                        if job_sample is not None:
                            job_memory.append(job_sample)
                        if time.monotonic()>=deadline or time.monotonic()-started>=args.max_seconds:
                            reason="supervisor wall-clock deadline reached"
                            break
                        retained=footprint(root)
                        peak_bytes=max(peak_bytes,retained)
                        if retained>=args.max_mib*1024*1024:
                            reason="supervisor retained-byte guard reached"
                            break
                        time.sleep(0.25)
                    code=owned.process.poll()
                finally:
                    try:
                        owned.close()
                    finally:
                        save(mode_root/"cleanup.json",owned.cleanup_evidence)
            result_path=mode_root/"results.json"
            if reason or not result_path.exists():
                result=recover_interrupted(mode_root,mode,args.seed,reason or f"mode worker exited without results (exit {code})")
            else:
                result=json.loads(result_path.read_text(encoding="utf-8"))
            renders+=result.get("metrics",{}).get("render_calls",0)
            result["owned_worker_started"]=True
            result["owned_worker_pid"]=owned.process.pid
            result["owned_worker_stopped"]=owned.process.poll() is not None
            result["owned_cleanup"]=dict(owned.cleanup_evidence)
            result["owned_job_stopped"]=(owned.cleanup_evidence["status"]=="confirmed" and owned.cleanup_evidence["active_processes_after"]==0) if owned.job_assigned else None
            result["supervisor_metrics"]={"retained_bytes_peak_sample":peak_bytes,"poll_seconds":0.25,
                "launch_process_working_set_bytes":{"first":memory[0] if memory else None,"last":memory[-1] if memory else None,"peak":max(memory) if memory else None,"samples":len(memory)},
                "job_memory":{key:max(v[key] for v in job_memory) for key in ("peak_job_committed_bytes","peak_process_committed_bytes")} if job_memory else None,
                "memory_scope":"working set is the Popen launch process, which may be a venv redirector; job committed-memory peaks include owned descendants; no leak threshold"}
            results.append(result)
            print(json.dumps({"event":"mode_finished","mode":mode,"status":result["status"],"counts":result.get("counts"),"render_calls":result.get("metrics",{}).get("render_calls")}),flush=True)
    except KeyboardInterrupt:
        results.append({"mode":"supervisor","status":"incomplete","counts":{},"incomplete_reasons":["interrupted by operator"]})
    except Exception as exc:
        import traceback
        results.append({"mode":"supervisor","status":"failed","counts":{"failed":1},"message":str(exc),"traceback":traceback.format_exc()})
    after=product_hashes()
    differences=[name for name in set(original)|set(after) if original.get(name)!=after.get(name)]
    status="failed" if differences or any(r["status"]=="failed" for r in results) else "incomplete" if any(r["status"]!="passed" for r in results) else "passed"
    summary={"schema":HARNESS_VERSION,"status":status,"run_id":run_id,"root":str(root),"seed":args.seed,
        "elapsed_seconds":round(time.monotonic()-started,6),"retained_bytes":footprint(root),"render_calls":renders,
        "product_files_changed":differences,"modes":results,"limits":metadata["limits"]}
    save(root/"summary.json",summary)
    lines=["# Docstream harness run", "",f"Status: **{status.upper()}**. Seed: {args.seed}. Run: {run_id}.","",
        "| Mode | Status | Passed | Failed | Incomplete |", "| --- | --- | ---: | ---: | ---: |"]
    for result in results:
        counts=result.get("counts",{})
        lines.append(f"| {result['mode']} | {result['status']} | {counts.get('passed',0)} | {counts.get('failed',0)} | {counts.get('incomplete',0)} |")
    lines.extend(["",f"Elapsed seconds: {summary['elapsed_seconds']}. Retained bytes before final summary: {summary['retained_bytes']}. Render calls: {renders}.",
        f"Product source files changed: {differences}.","","Failures and replay files:",""])
    for result in results:
        for item in result.get("cases",[]):
            if item["status"]=="failed":
                lines.append(f"- {result['mode']} / {item['name']}: {item.get('message','failed')}. Replay: {item.get('minimized_replay_file',item.get('replay_file','see event journal'))}")
        for reason in result.get("incomplete_reasons",[]):
            lines.append(f"- {result['mode']} incomplete: {reason}")
    (root/"REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"status":status,"report":str(root/"REPORT.md"),"summary":str(root/"summary.json")}),flush=True)
    return {"passed":0,"failed":1,"incomplete":2}[status]


def main(argv=None):
    class Parser(argparse.ArgumentParser):
        def error(self,message):
            raise ValueError(message)
    parser=Parser(prog="python -m docstream_cpu.harness")
    parser.add_argument("mode",choices=("rigid","fuzzy","torture","all"))
    parser.add_argument("--seed",type=int,default=20261029)
    parser.add_argument("--cases",type=int,default=500)
    parser.add_argument("--requests",type=int,default=1800)
    parser.add_argument("--crashes",type=int,default=20)
    parser.add_argument("--max-seconds",type=float,default=1200)
    parser.add_argument("--max-mib",type=float,default=512)
    parser.add_argument("--run-id")
    parser.add_argument("--replay",type=Path)
    try:
        return run(parser.parse_args(argv))
    except (ValueError,OSError) as exc:
        print(json.dumps({"status":"harness_error","message":str(exc)}),file=sys.stderr)
        return 3
