"""Windows containment for only the fixed test workers created by this batch."""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import os
import subprocess
import time

ORIGINAL_POPEN = subprocess.Popen


class JobUnavailable(RuntimeError):
    def __init__(self,message,details=None,owner=None):
        super().__init__(message)
        self.details=details or {}
        self.owner=owner


class BasicLimits(ctypes.Structure):
    _fields_=[('process_time',ctypes.c_int64),('job_time',ctypes.c_int64),
              ('flags',wintypes.DWORD),('min_ws',ctypes.c_size_t),('max_ws',ctypes.c_size_t),
              ('active_limit',wintypes.DWORD),('affinity',ctypes.c_size_t),
              ('priority',wintypes.DWORD),('scheduling',wintypes.DWORD)]


class IOCounters(ctypes.Structure):
    _fields_=[(name,ctypes.c_uint64) for name in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]


class ExtendedLimits(ctypes.Structure):
    _fields_=[('basic',BasicLimits),('io',IOCounters),('process_memory',ctypes.c_size_t),
              ('job_memory',ctypes.c_size_t),('peak_process_memory',ctypes.c_size_t),('peak_job_memory',ctypes.c_size_t)]


class ProcessIds(ctypes.Structure):
    _fields_=[('assigned',wintypes.DWORD),('count',wintypes.DWORD),('ids',ctypes.c_size_t*128)]


class Accounting(ctypes.Structure):
    _fields_=[('user',ctypes.c_int64),('kernel',ctypes.c_int64),('period_user',ctypes.c_int64),
              ('period_kernel',ctypes.c_int64),('faults',wintypes.DWORD),('total',wintypes.DWORD),
              ('active',wintypes.DWORD),('terminated',wintypes.DWORD)]


class OwnedJob:
    def __init__(self,max_processes=16):
        self.handle=None
        self.created=False
        self.stopped_associated_pids=[]
        self.pending_handles=[]
        self.pending_processes=[]
        self.cleanup_errors=[]
        self.cleanup={'job_zero_verified':True,'job_handle_closed':True,
                      'temporary_handles_closed':True,'launch_processes_closed':True}
        if type(max_processes) is not int or not 1<=max_processes<=16:
            raise JobUnavailable('Process budget must be an integer from 1 to 16')
        if os.name!='nt': raise JobUnavailable('This containment probe requires Windows')
        self.api=ctypes.WinDLL('kernel32',use_last_error=True)
        signatures={
            'CreateJobObjectW':([ctypes.c_void_p,wintypes.LPCWSTR],wintypes.HANDLE),
            'SetInformationJobObject':([wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD],wintypes.BOOL),
            'AssignProcessToJobObject':([wintypes.HANDLE,wintypes.HANDLE],wintypes.BOOL),
            'QueryInformationJobObject':([wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.c_void_p],wintypes.BOOL),
            'TerminateJobObject':([wintypes.HANDLE,wintypes.UINT],wintypes.BOOL),
            'CloseHandle':([wintypes.HANDLE],wintypes.BOOL),
            'OpenProcess':([wintypes.DWORD,wintypes.BOOL,wintypes.DWORD],wintypes.HANDLE),
            'IsProcessInJob':([wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.BOOL)],wintypes.BOOL),
            'WaitForSingleObject':([wintypes.HANDLE,wintypes.DWORD],wintypes.DWORD),
        }
        for name,(args,result) in signatures.items():
            function=getattr(self.api,name); function.argtypes=args; function.restype=result
        self.handle=self.api.CreateJobObjectW(None,None)
        if not self.handle: raise JobUnavailable(str(ctypes.WinError(ctypes.get_last_error())),owner=self)
        self.created=True
        self.cleanup.update(job_zero_verified=False,job_handle_closed=False)
        limits=ExtendedLimits()
        limits.basic.flags=0x2000|0x8  # kill on close; active process limit
        limits.basic.active_limit=max_processes
        if not self.api.SetInformationJobObject(self.handle,9,ctypes.byref(limits),ctypes.sizeof(limits)):
            primary={'stage':'set_job_limits','winerror':ctypes.get_last_error()}
            try: self.stop_and_close()
            except Exception as exc:
                raise JobUnavailable('Job setup cleanup incomplete',
                                     {'primary_error':primary,'cleanup_errors':list(self.cleanup_errors)},self) from exc
            raise JobUnavailable('Cannot configure owned job',primary,self)

    def _failure(self,stage,error):
        record={'stage':stage,'error_type':type(error).__name__,'message':str(error),
                'details':getattr(error,'details',{})}
        self.cleanup_errors.append(record)
        return record

    def _close_handle(self,handle,stage):
        if not self.api.CloseHandle(handle):
            error=JobUnavailable('Native handle close failed',{'winerror':ctypes.get_last_error()},self)
            self._failure(stage,error)
            raise error

    def _finish_launch(self,process):
        """Retain the process on failure so the caller can retry owned cleanup."""
        try:
            if process.poll() is None: process.kill()
            process.wait(timeout=5)
            for stream in (process.stdout,process.stderr):
                if stream is not None: stream.close()
            process._handle.Close()
        except Exception as exc:
            self._failure('launch_process_cleanup',exc)
            raise JobUnavailable('Launch process cleanup incomplete',owner=self) from exc
        self.pending_processes.remove(process)
        self.cleanup['launch_processes_closed']=not self.pending_processes

    def assign(self,process):
        if not self.api.AssignProcessToJobObject(self.handle,int(process._handle)):
            raise JobUnavailable(str(ctypes.WinError(ctypes.get_last_error())))

    def pids(self):
        info=ProcessIds()
        if not self.api.QueryInformationJobObject(self.handle,3,ctypes.byref(info),ctypes.sizeof(info),None):
            raise JobUnavailable(str(ctypes.WinError(ctypes.get_last_error())))
        return [int(info.ids[i]) for i in range(info.count)]

    def accounting(self):
        info=Accounting(); limits=ExtendedLimits()
        for kind,value in ((1,info),(9,limits)):
            if not self.api.QueryInformationJobObject(self.handle,kind,ctypes.byref(value),ctypes.sizeof(value),None):
                raise JobUnavailable(str(ctypes.WinError(ctypes.get_last_error())))
        return {'total_associations':info.total,'accounted_active':info.active,
                'configured_active_limit':limits.basic.active_limit,'limit_flags':limits.basic.flags}

    def live_pids(self):
        live=[]
        for pid in self.pids():
            handle=self.api.OpenProcess(0x00101000,False,pid)  # query limited + synchronize
            if not handle:
                error=ctypes.get_last_error()
                if error==87: continue  # process disappeared between the two queries
                raise JobUnavailable(str(ctypes.WinError(error)))
            self.pending_handles.append(handle)
            self.cleanup['temporary_handles_closed']=False
            primary=None
            try:
                belongs=wintypes.BOOL()
                if not self.api.IsProcessInJob(handle,self.handle,ctypes.byref(belongs)):
                    raise JobUnavailable(str(ctypes.WinError(ctypes.get_last_error())))
                waited=self.api.WaitForSingleObject(handle,0)
                if waited not in (0,258):
                    raise JobUnavailable('Cannot verify process exit state',owner=self)
                if belongs.value and waited==258:
                    live.append(pid)
            except Exception as exc: primary=exc
            try:
                self._close_handle(handle,'temporary_process_handle_close')
                self.pending_handles.remove(handle)
                self.cleanup['temporary_handles_closed']=not self.pending_handles
            except Exception as exc:
                details={'cleanup_errors':list(self.cleanup_errors)}
                if primary is not None:
                    details['primary_error']={'error_type':type(primary).__name__,'message':str(primary)}
                raise JobUnavailable('Process inspection cleanup incomplete',details,self) from exc
            if primary is not None: raise primary
        return live

    def launch(self,*args,**kwargs):
        # Associate the suspended process before Python can create descendants.
        kwargs['creationflags']=kwargs.get('creationflags',0)|0x08000000|0x4
        process=ORIGINAL_POPEN(*args,**kwargs)
        try:
            self.assign(process)
            resume=ctypes.WinDLL('ntdll').NtResumeProcess
            resume.argtypes=[wintypes.HANDLE]; resume.restype=wintypes.LONG
            status=resume(int(process._handle))
            if status!=0: raise JobUnavailable('Cannot resume owned suspended process: '+str(status))
            return process
        except Exception as primary:
            self.pending_processes.append(process)
            self.cleanup['launch_processes_closed']=False
            try: self._finish_launch(process)
            except Exception as exc:
                raise JobUnavailable('Failed launch cleanup incomplete',
                                     {'primary_error':{'error_type':type(primary).__name__,'message':str(primary)},
                                      'cleanup_errors':list(self.cleanup_errors)},self) from exc
            raise

    def stop_and_close(self):
        before=[]
        if self.handle:
            self.cleanup['job_zero_verified']=False
            before=self.pids()
            if before and not self.api.TerminateJobObject(self.handle,238):
                raise JobUnavailable('Cannot terminate owned job',{'winerror':ctypes.get_last_error()},self)
            self.stopped_associated_pids.extend(pid for pid in before if pid not in self.stopped_associated_pids)
            deadline=time.monotonic()+5
            while self.pids():
                if time.monotonic()>deadline:
                    raise JobUnavailable('Owned job did not reach zero active processes',owner=self)
                time.sleep(0.01)
            self.cleanup['job_zero_verified']=True
        for process in list(self.pending_processes): self._finish_launch(process)
        for handle in list(self.pending_handles):
            self._close_handle(handle,'temporary_process_handle_retry')
            self.pending_handles.remove(handle)
        self.cleanup['temporary_handles_closed']=not self.pending_handles
        self.cleanup['launch_processes_closed']=not self.pending_processes
        if self.handle:
            self._close_handle(self.handle,'job_handle_close')
            self.handle=None
            self.cleanup['job_handle_closed']=True
        return before
