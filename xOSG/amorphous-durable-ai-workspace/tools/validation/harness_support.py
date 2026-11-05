"""Explicit validation, owned execution, and atomic local harness evidence."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import uuid

from owned_job import OwnedJob,JobUnavailable

SCHEMA='DWSK-HARNESS-RESULT-2'
CAPTURE_LIMIT=8*1024*1024


class HarnessError(RuntimeError):
    def __init__(self,code,message,details=None):
        super().__init__(message)
        self.code=code
        self.details=details or {}


def check(condition,code='INVALID_RESULT',message='Harness validation failed'):
    if not condition: raise HarnessError(code,message)


def run_id(value):
    check(type(value) is str and re.fullmatch(r'[A-Za-z0-9_-]{1,80}',value) is not None,
          'INVALID_RUN_ID','Run ID must contain only ASCII letters, digits, hyphen or underscore')
    return value


def claim(root,stem,fixture):
    root=Path(root).resolve(); fixture=Path(fixture).resolve()
    check(fixture.is_relative_to(root),'INVALID_ROOT','Fixture root is outside the declared output')
    evidence=root/'evidence'
    evidence.mkdir(parents=True,exist_ok=True)
    check(not list(evidence.glob(stem+'-*')),'RUN_CONFLICT','Prior evidence already exists for this run ID')
    try: fixture.mkdir(parents=True,exist_ok=False)
    except FileExistsError as exc: raise HarnessError('RUN_CONFLICT','Run fixture directory already exists') from exc


def _write_to_handle(handle,data):
    handle.write(data)
    handle.flush()
    os.fsync(handle.fileno())


def atomic_bytes(path,data,root):
    path=Path(path); root=Path(root).resolve()
    check(path.parent.resolve().is_relative_to(root),'INVALID_ROOT','Evidence destination escaped its output root')
    check(not path.is_symlink() and not (hasattr(path,'is_junction') and path.is_junction()),
          'INVALID_ROOT','Evidence destination is a link')
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    owned=False; published=False
    try:
        with temporary.open('xb') as handle:
            owned=True
            _write_to_handle(handle,data)
        os.replace(temporary,path); owned=False; published=True
        if os.name!='nt':
            fd=os.open(path.parent,os.O_RDONLY)
            try: os.fsync(fd)
            finally: os.close(fd)
    except OSError as exc:
        raise HarnessError('IO_ERROR','Evidence publication failed',
                           {'errno':exc.errno,'published':published,'path':str(path)}) from exc
    finally:
        if owned and temporary.parent.resolve().is_relative_to(root): temporary.unlink(missing_ok=True)


def atomic_json(path,value,root):
    try: data=(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
    except (ValueError,TypeError,UnicodeError) as exc: raise HarnessError('INVALID_RESULT','Result is not serializable') from exc
    atomic_bytes(path,data,root)


def once_or_equal(path,data,root):
    path=Path(path)
    if path.exists():
        check(path.read_bytes()==data,'SOURCE_MISMATCH','Existing shared inventory differs')
    else: atomic_bytes(path,data,root)


def strict_json(text,code='INVALID_RESULT'):
    def pairs(items):
        value={}
        for key,item in items:
            check(key not in value,code,'Duplicate JSON field')
            value[key]=item
        return value
    def constant(value): raise HarnessError(code,'Non-finite JSON constant')
    try: return json.loads(text,object_pairs_hook=pairs,parse_constant=constant)
    except (ValueError,TypeError,UnicodeError) as exc: raise HarnessError(code,'Malformed JSON evidence') from exc


def load_json(path,code='INVALID_EVIDENCE'):
    path=Path(path)
    check(path.is_file(),'MISSING_EVIDENCE','Required evidence is missing: '+path.name)
    try: return strict_json(path.read_text(encoding='utf-8'),code)
    except OSError as exc: raise HarnessError('IO_ERROR','Cannot read evidence',{'errno':exc.errno}) from exc


def integer(value,expected=None,code='INVALID_RESULT'):
    check(type(value) is int and value>=0,code,'Counter must be a nonnegative integer, excluding bool')
    if expected is not None: check(value==expected,code,'Unexpected counter value')
    return value


def runtime_report(value):
    check(type(value) is dict,'INVALID_RESULT','Runtime report must be an object')
    check(value.get('ok') is True,'INVALID_RESULT','Runtime verification did not report Boolean true')
    integer(value.get('event_count'));integer(value.get('record_count'))
    check(type(value.get('logical_digest')) is str and re.fullmatch('[0-9a-f]{64}',value['logical_digest']) is not None,
          'INVALID_RESULT','Invalid logical digest')
    return value


def snapshot_report(value,valid=True):
    check(type(value) is dict,'INVALID_RESULT','Snapshot report must be an object')
    check(type(value.get('manifest_digest_matches_quorum')) is bool,'INVALID_RESULT','Manifest-match flag must be Boolean')
    if valid:
        check(value['manifest_digest_matches_quorum'] is True,'INVALID_RESULT','Manifest does not match quorum')
        check(type(value.get('quorum_kinds')) is list and len(value['quorum_kinds'])==3 and
              set(value['quorum_kinds'])=={'sqlite','jsonl','xml'},'INVALID_RESULT','Invalid representation set')
        check(type(value.get('quorum_digest')) is str and re.fullmatch('[0-9a-f]{64}',value['quorum_digest']) is not None,
              'INVALID_RESULT','Invalid quorum digest')
    else:
        check('quorum_digest' in value,'INVALID_RESULT','Snapshot report is missing quorum_digest')
        check(value['quorum_digest'] is None and value['manifest_digest_matches_quorum'] is False,
              'INVALID_RESULT','Damaged snapshot unexpectedly has quorum')
    return value


def units(text,expected,success=True):
    text=text.replace('\r\n','\n').replace('\r','\n')
    text=re.sub(r'\x1b\[[0-9;]*m','',text)
    totals=re.findall(r'^Ran ([0-9]+) tests?(?: in [^\r\n]+)?\s*$',text,re.M)
    outcomes=re.findall(r'^(OK(?: \([^\r\n]*\))?|FAILED(?: \([^\r\n]*\))?)\s*$',text,re.M)
    rows=re.findall(r'^test[^\r\n]*? \.\.\. (ok|FAIL|ERROR|skipped[^\r\n]*|expected failure|unexpected success)\s*$',text,re.M)
    check(len(totals)==1 and len(outcomes)==1,'INVALID_RESULT','Missing or contradictory unit summary')
    integer(int(totals[0]),expected)
    check(len(rows)==expected,'INVALID_RESULT','Unit status rows do not match executed total')
    counts={'executed':expected,'passed':rows.count('ok'),'failures':rows.count('FAIL'),
            'errors':rows.count('ERROR'),'skipped':sum(r.startswith('skipped') for r in rows),
            'expected_failures':rows.count('expected failure'),'unexpected_successes':rows.count('unexpected success')}
    good=counts['passed']==expected and outcomes[0]=='OK'
    if success: check(good,'INVALID_RESULT','Unit results contain failure, error, skip or contradictory status')
    return {**counts,'success':good}


def self_checks(text):
    text=text.replace('\r\n','\n').replace('\r','\n')
    totals=re.findall(r'^([0-9]+)/([0-9]+) checks passed\s*$',text,re.M)
    passed=re.findall(r'^PASS\s+[^\r\n]+$',text,re.M)
    failed=re.findall(r'^FAIL(?:\s|$)',text,re.M)
    check(len(totals)==1 and tuple(map(int,totals[0]))==(7,7) and len(passed)==7 and not failed,
          'INVALID_RESULT','Self-check transcript is incomplete or contradictory')
    return {'executed':7,'passed':7,'failures':0,'errors':0,'skipped':0,'success':True}


def probe(value):
    code='INVALID_EVIDENCE'
    required={'processes','published_generations','all_three_formats_valid','runtime_logical_state_unchanged',
              'latest_references_complete_generation','temporary_files_remaining'}
    check(type(value) is dict and set(value)==required,code,'Probe fields are missing or unrecognized')
    integer(value['processes'],4,code);integer(value['published_generations'],12,code);integer(value['temporary_files_remaining'],0,code)
    for key in ('all_three_formats_valid','runtime_logical_state_unchanged','latest_references_complete_generation'):
        check(value[key] is True,code,'Probe failed: '+key)
    return value


def run_process(argv,*,cwd,env=None,timeout=120,max_processes=16,capture_limit=CAPTURE_LIMIT,**unused):
    check(0<timeout<=120,'INVALID_CONFIG','Worker timeout out of bounds')
    check(type(capture_limit) is int and 0<capture_limit<=CAPTURE_LIMIT,'INVALID_CONFIG','Capture budget out of bounds')
    job=None;process=None;readers=[];buffers=[bytearray(),bytearray()];overflow=threading.Event();read_errors=[]
    primary=None;cleanup_errors=[];secondary_errors=[]
    cleanup={'configured_limit':max_processes,'job_created':False,'process_created':False,
             'live_before_cleanup':None,'stopped_associated_pids':[],
             'job_zero_verified':False,'job_handle_closed':False,'process_exited':False,
             'readers_completed':False,'streams_closed':False,'process_handle_closed':False,
             'temporary_handles_closed':False,'launch_processes_closed':False}

    def cleanup_failure(stage,error):
        cleanup_errors.append({'stage':stage,'error_type':type(error).__name__,'message':str(error),
                               'details':getattr(error,'details',{})})

    def retry_cleanup(stage,operation):
        # Two attempts only; an observed failure remains reportable after recovery.
        for attempt in range(2):
            try:
                operation()
                return True
            except Exception as exc: cleanup_failure(stage,exc)
        return False

    def drain(stream,index):
        try:
            while True:
                chunk=stream.read(65536)
                if not chunk: break
                room=max(0,capture_limit-len(buffers[index])); buffers[index].extend(chunk[:room])
                if len(chunk)>room: overflow.set()
        except Exception as exc: read_errors.append(type(exc).__name__)
        finally:
            try: stream.close()
            except Exception as exc: cleanup_failure('reader_stream_close',exc)
    try:
        job=OwnedJob(max_processes)
        cleanup['job_created']=job.created
        process=job.launch(list(map(str,argv)),cwd=str(cwd),env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        cleanup['process_created']=True
        for index,stream in enumerate((process.stdout,process.stderr)):
            reader=threading.Thread(target=drain,args=(stream,index),daemon=True);readers.append(reader);reader.start()
        deadline=time.monotonic()+timeout
        while process.poll() is None:
            if overflow.is_set(): raise HarnessError('OUTPUT_LIMIT','Worker exceeded capture limit')
            if time.monotonic()>=deadline: raise HarnessError('WORKER_TIMEOUT','Worker exceeded its deadline')
            time.sleep(.01)
        settle=time.monotonic()+.5
        while job.live_pids() and time.monotonic()<settle: time.sleep(.01)
        if job.live_pids(): raise HarnessError('WORKER_DESCENDANTS','Worker returned with live descendants')
    except HarnessError as exc: primary=exc
    except Exception as exc:
        if job is None and isinstance(exc,JobUnavailable): job=exc.owner
        primary=HarnessError('CONTAINMENT_ERROR',str(exc),
                             {'error_type':type(exc).__name__,'cause_details':getattr(exc,'details',{})})
    finally:
        if job is not None:
            cleanup['job_created']=job.created
            try:
                cleanup['live_before_cleanup']=job.live_pids() if job.handle else []
            except Exception as exc:
                cleanup_failure('pre_cleanup_inspection',exc)
            def stop_job():
                job.stop_and_close()
            retry_cleanup('owned_job_cleanup',stop_job)
            cleanup.update(job.cleanup)
            cleanup['stopped_associated_pids']=list(job.stopped_associated_pids)
            cleanup_errors.extend(job.cleanup_errors)
        else:
            # No owner was acquired; this is not evidence about a nonexistent job.
            cleanup.update(job_zero_verified=True,job_handle_closed=True,
                           temporary_handles_closed=True,launch_processes_closed=True)
        if process is not None:
            def reap_process():
                if process.poll() is None: process.kill()
                process.wait(timeout=5)
            cleanup['process_exited']=retry_cleanup('process_wait',reap_process)
        else: cleanup['process_exited']=True
        for reader in readers:
            retry_cleanup('reader_join',lambda reader=reader:reader.join(timeout=5))
        cleanup['readers_completed']=not any(reader.is_alive() for reader in readers)
        if process is not None:
            if cleanup['readers_completed']:
                for stream in (process.stdout,process.stderr):
                    if stream is not None and not stream.closed:
                        retry_cleanup('process_stream_close',stream.close)
                cleanup['streams_closed']=all(stream is None or stream.closed for stream in (process.stdout,process.stderr))
            if cleanup['process_exited']:
                cleanup['process_handle_closed']=retry_cleanup('process_handle_close',process._handle.Close)
        else: cleanup.update(streams_closed=True,process_handle_closed=True)
    if read_errors:
        capture=HarnessError('CAPTURE_ERROR','Worker streams could not be fully captured',{'read_errors':read_errors})
        if primary is None: primary=capture
        else: secondary_errors.append({'code':capture.code,'message':str(capture)})
    if overflow.is_set():
        limit=HarnessError('OUTPUT_LIMIT','Worker exceeded capture limit')
        if primary is None: primary=limit
        else: secondary_errors.append({'code':limit.code,'message':str(limit)})
    stdout=bytes(buffers[0]).decode('utf-8',errors='replace');stderr=bytes(buffers[1]).decode('utf-8',errors='replace')
    required=('job_zero_verified','job_handle_closed','process_exited','readers_completed',
              'streams_closed','process_handle_closed','temporary_handles_closed','launch_processes_closed')
    if cleanup_errors or not all(cleanup[field] is True for field in required):
        if not cleanup_errors:
            cleanup_errors.append({'stage':'closure_evidence','error_type':'UnverifiedCleanup',
                                   'message':'Required cleanup evidence is incomplete'})
        original=None if primary is None else {'code':primary.code,'message':str(primary),'details':dict(primary.details)}
        failure=HarnessError('CLEANUP_INCOMPLETE','Owned cleanup was not completed without failure',
                             {'primary_error':original,'cleanup_errors':cleanup_errors,'secondary_errors':secondary_errors,
                              'stdout':stdout,'stderr':stderr,'cleanup':cleanup})
        # Preserve ownership for caller-directed recovery; never put handles in JSON.
        failure.resource_owner=(job,process,readers)
        raise failure from primary
    if primary is not None:
        primary.details.update(stdout=stdout,stderr=stderr,cleanup=cleanup,secondary_errors=secondary_errors)
        raise primary
    try: stdout=bytes(buffers[0]).decode('utf-8');stderr=bytes(buffers[1]).decode('utf-8')
    except UnicodeError as exc: raise HarnessError('INVALID_OUTPUT','Worker output is not UTF-8',{'cleanup':cleanup}) from exc
    result=subprocess.CompletedProcess(argv,process.returncode,stdout,stderr)
    result.harness_cleanup=cleanup
    return result


def status_for(error):
    return 'INCOMPLETE' if error.code in {'WORKER_TIMEOUT','CLEANUP_INCOMPLETE'} else 'ERROR' if error.code in {'IO_ERROR','CONTAINMENT_ERROR','CAPTURE_ERROR','RUN_CONFLICT'} else 'FAIL'


def cli_entry(main):
    try: return main()
    except HarnessError as error:
        print(json.dumps({'schema':SCHEMA,'status':status_for(error),'error_code':error.code,
                          'error':str(error),'details':error.details}),file=sys.stderr)
        return 3 if error.code in {'WORKER_TIMEOUT','CLEANUP_INCOMPLETE'} else 2
