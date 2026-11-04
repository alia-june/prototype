"""Fixed end-to-end, boundary, concurrent, crash and renderer workloads."""
from __future__ import annotations

import asyncio
import base64
from concurrent.futures import ThreadPoolExecutor
import errno
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

from ..errors import ModelError
from ..format_service import FormatService
from ..models import Block, Properties, Snapshot
from ..operations import parse_batch
from ..rendering import Renderer, RenderProfile
from ..rich import RichBlock, Snapshot2, Span, parse_snapshot
from ..service import DocumentService
from ..storage import Store
from ..visual_service import VisualService
from .core import BudgetExceeded, CheckFailed, SERVICE_ROOT, require, semantic_meaning


def good(reply):
    require(reply.get("ok") is True,"service request failed",response=reply)
    return reply["result"]


def fixture(name):
    if name!="reviewed-m4":
        raise ValueError("unknown fixed fixture")
    return json.loads((SERVICE_ROOT/"tests"/"fixtures"/"harness"/"reviewed-m4.json").read_text(encoding="utf-8"))


def golden(data,root,context):
    from pypdf import PdfReader
    f=fixture(data.get("fixture","reviewed-m4"))
    with Store(root) as store:
        formats=FormatService(store)
        payload={**f["import_request"],"request_key":"golden-import"}
        source=good(formats.import_document(payload))
        actual=store.model.materialize(source["stream_id"])
        require(actual.model_dump(mode="json")==f["snapshot"],"fixed semantic golden changed")
        require(actual.digest==f["semantic_sha256"],"fixed semantic digest changed")
        require(store.model.source(source["document_id"]).original_sha256==f["source_sha256"],"fixed source byte hash changed")
        visual=VisualService(store)
        try:
            from ..assets import AssetStore
            spec=visual.renderer.prepare(actual,RenderProfile(),AssetStore(store).get)
            expected=f["renderer_identity"]
            current={key:spec.metadata[key] for key in expected}
            if current!=expected:
                raise BudgetExceeded("reviewed PNG environment differs; explicit baseline review required")
            preview=good(visual.render({"request_key":"golden-preview","stream_id":source["stream_id"]}))
            png=preview["artifacts"]["png"]
            require(png["sha256"]==f["png_sha256"],"fixed PNG pixel baseline changed",expected=f["png_sha256"],actual=png["sha256"])
            pdf=visual.artifacts.path(preview["artifacts"]["pdf"]["relative_path"])
            document=PdfReader(pdf)
            require(len(document.pages)==f["pdf"]["pages"],"fixed PDF page count changed")
            page=document.pages[0]
            require(float(page.mediabox.width)==612 and float(page.mediabox.height)==792,"PDF page dimensions changed")
            text=" ".join(" ".join(p.extract_text() or "" for p in document.pages).split())
            for token in f["pdf"]["required_text"]:
                require(token in text,"fixed PDF lost required text",missing=token)
            return {"semantic_sha256":actual.digest,"png_sha256":png["sha256"],"pdf_pages":len(document.pages),"renderer_environment_matched":True}
        finally:
            visual.close()


def workflow(data,root,context):
    with Store(root) as store:
        service=DocumentService(store)
        snapshot=Snapshot2(properties=Properties(title="Strict stream workflow",font_family="Arial"),blocks=(RichBlock(block_id="body",text="Original text",runs=(Span(text="Original "),Span(text="text")),),))
        source=good(service.ingest({"request_key":"source","snapshot":snapshot.model_dump(mode="json")}))
        operations=[{"operation_id":f"font{i}","kind":"set_font","font_family":font} for i,font in enumerate(("Consolas","Arial","Times New Roman"))]
        operations.append({"operation_id":"restore","kind":"restore_font"})
        request={"request_key":"plan","base_stream_id":source["stream_id"],"mode":"plan","batch":{"base_sha256":source["semantic_sha256"],"operations":operations}}
        planned=good(service.transform(request))
        require(planned["property_writes"]==0,"exact font restoration was not reduced to zero")
        require(len(planned["output_stream_ids"])==4,"logical operation outputs were lost")
        for index in (3,0,2,1):
            content=good(service.inspect({"target_id":planned["output_stream_ids"][index],"section":"content"}))
            require(content["properties"]["font_family"]==("Arial" if index in (1,3) else "Consolas" if index==0 else "Times New Roman"),"out-of-order stream inspection is wrong")
        require(store.model.head(source["document_id"]).revision==0,"inspection or planning advanced the head")
        committed=service.commit({"request_key":"commit","candidate_id":planned["candidate_id"]})
        good(committed)
        formats=FormatService(store)
        meanings=[]
        for name in ("markdown_bundle","docx"):
            artifact=good(formats.export_document({"request_key":"export-"+name,"stream_id":planned["result_stream_id"],"format":name}))["artifact"]
            raw=formats.artifacts.path(artifact["relative_path"]).read_bytes()
            imported=good(formats.import_document({"request_key":"reimport-"+name,"format":name,"data_base64":base64.b64encode(raw).decode()}))
            meanings.append(semantic_meaning(store.model.materialize(imported["stream_id"])))
        require(all(item==semantic_meaning(snapshot) for item in meanings),"end-to-end export changed supported meaning")
    with Store(root) as reopened:
        service=DocumentService(reopened)
        require(service.commit({"request_key":"commit","candidate_id":planned["candidate_id"]})==committed,"committed request retry differs after restart")
        require(reopened.model.head(source["document_id"]).revision==1,"restart lost committed revision")
    return {"logical_outputs":4,"reduced_writes":0,"formats":2,"restart_replay":True}


def limits(data,root,context):
    results=[]
    with Store(root) as store:
        service=DocumentService(store)
        original=good(service.ingest({"request_key":"small","text":"Boundary"}))
        for count in (255,256,257):
            payload={"base_sha256":original["semantic_sha256"],"operations":[{"kind":"set_property","operation_id":f"o{i}","property":"title","value":str(i)} for i in range(count)]}
            try:
                parsed=parse_batch(payload)
            except ModelError as exc:
                require(count==257 and exc.code=="VALIDATION_ERROR","operation limit rejected wrong boundary",count=count,error=exc.code)
            else:
                require(count<=256,"operation limit accepted too many operations")
                good(service.transform({"request_key":"limit-"+str(count),"base_stream_id":original["stream_id"],"mode":"materialize","batch":parsed.model_dump(mode="json")}))
            results.append({"operations":count,"accepted":count<=256})
        for index,(text,accepted) in enumerate((("x"*1_048_575,True),("x"*1_048_576,True),("x"*1_048_577,False),("é"*524288,True),("é"*524289,False))):
            before=len(store.model._heads)
            reply=service.ingest({"request_key":f"source-limit-{index}","text":text})
            require(reply["ok"]==accepted,"source byte boundary is wrong",bytes=len(text.encode()),response=reply)
            require(len(store.model._heads)==before+int(accepted),"source boundary left a partial document")
            results.append({"source_bytes":len(text.encode()),"accepted":accepted})
        require(store.connection.execute("PRAGMA integrity_check").fetchone()[0]=="ok","boundary store integrity failed")
    return {"boundaries":results}


def storage_faults(data,root,context):
    outcomes=[]
    for index,phase in enumerate(("after_reserved","after_model","after_flush","before_commit","after_commit")):
        path=root/phase
        def fault(current):
            if current==phase:
                raise OSError(errno.ENOSPC,"injected test-store disk-full error")
        request={"request_key":"write","text":"Retained bytes"}
        with Store(path,fault=fault) as store:
            try:
                reply=DocumentService(store).ingest(request)
            except OSError:
                reply=None
        with Store(path) as store:
            service=DocumentService(store)
            committed=phase=="after_commit"
            require(len(store.model._heads)==int(committed),"storage fault changed wrong commit boundary",phase=phase)
            retry=service.ingest(request)
            if phase in ("after_reserved","after_commit"):
                good(retry)
            else:
                require(retry==reply and not retry["ok"],"failed storage receipt was not retained",phase=phase)
                good(service.ingest({**request,"request_key":"repair"}))
            require(len(store.model._heads)==1,"storage recovery duplicated or lost a document",phase=phase)
            require(store.connection.execute("PRAGMA integrity_check").fetchone()[0]=="ok","storage fault left corrupt SQLite")
            outcomes.append({"phase":phase,"committed_before_retry":committed,"recovered":True})
    with Store(root/"permission") as store:
        def permission(current):
            if current=="after_flush":
                raise PermissionError(errno.EACCES,"injected test-store permission error")
        store.fault=permission
        reply=DocumentService(store).ingest({"request_key":"permission","text":"x"})
        require(not reply["ok"] and not store.model._heads,"permission injection left a committed document")
    with Store(root/"busy") as store:
        other=sqlite3.connect(store.root/"state.sqlite3",isolation_level=None)
        other.execute("BEGIN IMMEDIATE")
        started=time.monotonic()
        try:
            try:
                DocumentService(store).ingest({"request_key":"busy","text":"x"})
            except (sqlite3.OperationalError,ModelError):
                pass
            else:
                raise CheckFailed("second SQLite writer unexpectedly bypassed its lock")
        finally:
            other.execute("ROLLBACK")
            other.close()
        require(time.monotonic()-started<8,"busy SQLite failure exceeded its bounded wait")
        good(DocumentService(store).ingest({"request_key":"after-busy","text":"x"}))
    return {"disk_full_injections":outcomes,"permission_injection":True,"real_sqlite_busy":True,"actual_disk_filled":False}


def crash_recovery(data,root,context):
    cycles=int(data.get("cycles",20))
    if not 1<=cycles<=20:
        raise ValueError("crash replay is bounded to 20 cycles")
    outcomes=[]
    for index in range(cycles):
        context.journal.check_budget()
        phase=("after_reserved","after_flush","before_commit","after_commit")[index%4]
        path=root/f"cycle-{index:02d}"
        path.mkdir(parents=True,exist_ok=True)
        signal=path/"crash-ready.json"
        args=[sys.executable,"-m","docstream_cpu.harness.worker","--crash-actor",str(path),phase]
        process=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
        try:
            deadline=time.monotonic()+12
            while not signal.exists():
                if process.poll() is not None or time.monotonic()>deadline:
                    raise CheckFailed("owned crash actor did not reach its boundary",{"phase":phase,"returncode":process.poll()})
                time.sleep(0.02)
            context.spend("api")  # The child submits exactly one service request.
            process.terminate()  # Exact Popen child handle; never a name/PID search.
            process.wait(timeout=5)
            with Store(path) as store:
                service=DocumentService(store)
                after_commit=phase=="after_commit"
                require(len(store.model._heads)==int(after_commit),"OS termination left wrong durable state",phase=phase)
                row=store.connection.execute("SELECT state FROM requests").fetchone()
                require(row[0]==("completed" if after_commit else "interrupted"),"crash receipt recovery is wrong",phase=phase,state=row[0])
                reply=good(service.ingest({"request_key":"crash","text":"Crash recovery"}))
                require(len(store.model._heads)==1,"crash retry duplicated or lost its document")
                require(store.connection.execute("PRAGMA integrity_check").fetchone()[0]=="ok","OS termination damaged database integrity")
                require(not store.connection.execute("PRAGMA foreign_key_check").fetchall(),"OS termination damaged foreign keys")
                outcomes.append({"phase":phase,"terminated_pid":process.pid,"recovered":True,"document_id":reply["document_id"]})
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            if process.stderr:
                process.stderr.close()
    return {"cycles":cycles,"outcomes":outcomes,"termination":"owned Popen process handle"}


def network_load(data,root,context):
    count=int(data.get("requests",1800))
    if not 4<=count<=1800 or count%4:
        raise ValueError("network replay requires a multiple of four, at most 1800 requests")
    sys.path.insert(0,str(SERVICE_ROOT/"tests")) if str(SERVICE_ROOT/"tests") not in sys.path else None
    from test_mcp import RunningServer
    from mcp import Client
    from mcp.client.streamable_http import streamable_http_client
    import httpx2
    server=RunningServer(root)
    started=time.perf_counter()
    try:
        async def run_client(number):
            headers={"Authorization":"Bearer "+server.token}
            async with httpx2.AsyncClient(headers=headers,timeout=httpx2.Timeout(10,read=30),trust_env=False) as http:
                async with Client(streamable_http_client(server.url,http_client=http),read_timeout_seconds=30) as client:
                    async def call(name,payload):
                        response=await client.call_tool(name,{"request":payload})
                        return response.structured_content if response.structured_content is not None else {"is_error":response.is_error}
                    request={"request_key":f"source-{number}","snapshot":Snapshot(properties=Properties(font_family="Arial"),blocks=(Block(block_id="body",text=f"Client {number}"),)).model_dump(mode="json")}
                    receipt=await call("docstream_ingest",request)
                    source=good(receipt)
                    current=source["stream_id"]
                    commits=0
                    for index in range(count//4):
                        context.journal.check_budget()
                        choice=index%6
                        if choice==0:
                            reply=await call("docstream_inspect",{"target_id":source["document_id"],"section":"head"})
                            require(good(reply)["stream_id"]==current,"concurrent head read differs")
                        elif choice==1:
                            require(await call("docstream_ingest",request)==receipt,"duplicate network request changed its receipt")
                        elif choice==2:
                            reply=good(await call("docstream_transform",{"request_key":f"commit-{number}-{index}","base_stream_id":current,"mode":"commit","batch":{"base_sha256":source["semantic_sha256"],"operations":[]}}))
                            current=reply["result_stream_id"]
                            commits+=1
                            require(reply["head"]["revision"]==commits,"network revision sequence differs")
                        elif choice==3:
                            good(await call("docstream_transform",{"request_key":f"plan-{number}-{index}","base_stream_id":current,"mode":"plan","batch":{"base_sha256":source["semantic_sha256"],"operations":[{"operation_id":"font","kind":"set_font","font_family":"Times New Roman"}]}}))
                        elif choice==4:
                            reply=good(await call("docstream_export",{"request_key":f"export-{number}-{index}","stream_id":current,"format":"docx"}))
                            require(reply["committed"] is False,"export advanced the head")
                        else:
                            reply=await call("docstream_transform",{"request_key":f"invalid-{number}-{index}","base_stream_id":current,"mode":"commit","batch":{"base_sha256":source["semantic_sha256"],"operations":[{"operation_id":"bad","kind":"set_font","font_family":"Arial","version":1.0}]}})
                            require(reply.get("is_error") or reply.get("ok") is False,"network scalar coercion accepted an invalid version")
                            if reply.get("is_error"):
                                context.spend("api")  # Rejected by SDK before a service method executes.
                    return {"client":number,"requests":count//4+1,"document_id":source["document_id"],"commits":commits,"head_id":current}
        def target(number):
            return asyncio.run(run_client(number))
        with ThreadPoolExecutor(max_workers=4) as pool:
            clients=list(pool.map(target,range(4)))
        with server.store.lock:
            for item in clients:
                head=server.store.model.head(item["document_id"])
                require(head.stream_id==item["head_id"] and head.revision==item["commits"],"concurrent final head differs")
            require(server.store.connection.execute("PRAGMA integrity_check").fetchone()[0]=="ok","concurrent store integrity failed")
        # Four candidates compete for the same exact head, using real clients.
        from ..cli import client_call
        shared=good(asyncio.run(client_call(server.url,server.token,"docstream_ingest",{"request_key":"shared","text":"Shared head"})))
        candidates=[]
        for index in range(4):
            candidate=good(asyncio.run(client_call(server.url,server.token,"docstream_transform",{"request_key":f"shared-plan-{index}","base_stream_id":shared["stream_id"],"mode":"plan","batch":{"base_sha256":shared["semantic_sha256"],"operations":[]}})))
            candidates.append(candidate["candidate_id"])
        def commit(item):
            return asyncio.run(client_call(server.url,server.token,"docstream_commit",{"request_key":f"shared-commit-{item[0]}","candidate_id":item[1]}))
        with ThreadPoolExecutor(max_workers=4) as pool:
            competing=list(pool.map(commit,enumerate(candidates)))
        require(sum(r["ok"] for r in competing)==1,"competing network commits did not produce exactly one winner",responses=competing)
        require(all(r["error"]["code"]=="STALE_HEAD" for r in competing if not r["ok"]),"competing network commits returned wrong conflict")
        return {"loop_requests":count,"setup_and_competition_requests":13,"clients":clients,"competing_winners":1,"elapsed_seconds":round(time.perf_counter()-started,6)}
    finally:
        server.close()


def render_recovery(data,root,context):
    f=fixture("reviewed-m4")
    with Store(root) as store:
        source=good(FormatService(store).import_document({**f["import_request"],"request_key":"source"}))
        service=DocumentService(store)
        renderer=Renderer()
        visual=VisualService(store,renderer)
        try:
            first=good(visual.render({"request_key":"first","stream_id":source["stream_id"],"profile":{"formats":["png"]}}))
            owned_pid=renderer.process.pid
            renderer.process.terminate()
            renderer.process.join(5)
            require(not renderer.process.is_alive(),"owned renderer did not stop")
            def candidate(key,font):
                head=store.model.head(source["document_id"])
                content=store.model.materialize(head.stream_id)
                return good(service.transform({"request_key":key,"base_stream_id":head.stream_id,"mode":"plan","batch":{"base_sha256":content.digest,"operations":[{"operation_id":"font","kind":"set_font","font_family":font}]}}))
            changed=candidate("changed","Times New Roman")
            second=good(visual.render({"request_key":"replacement","candidate_id":changed["candidate_id"],"commit":True,"profile":{"formats":["png"]}}))
            require(renderer.starts==2,"dead renderer was not replaced")
            damaged=visual.artifacts.path(second["artifacts"]["png"]["relative_path"])
            require(damaged.resolve().is_relative_to(root.resolve()),"damage fixture escaped owned store")
            damaged.write_bytes(b"injected artifact damage")
            try:
                visual.artifact({"artifact_id":second["artifacts"]["png"]["artifact_id"]})
            except ModelError as exc:
                require(exc.code=="ARTIFACT_INTEGRITY","wrong damaged artifact error")
            else:
                raise CheckFailed("damaged artifact was served as ready")
            good(visual.render({"request_key":"repair","stream_id":changed["result_stream_id"],"profile":{"formats":["png"]}}))
            later=candidate("later","Consolas")
            before=store.model.head(source["document_id"])
            def fail(phase):
                if phase=="after_artifact_files":
                    raise OSError(errno.ENOSPC,"injected publication failure")
            store.fault=fail
            failed=visual.render({"request_key":"publication-failure","candidate_id":later["candidate_id"],"commit":True,"profile":{"formats":["png"]}})
            require(not failed["ok"] and store.model.head(source["document_id"])==before,"failed publication advanced the head")
            store.fault=lambda phase:None
            good(visual.render({"request_key":"publication-retry","candidate_id":later["candidate_id"],"commit":True,"profile":{"formats":["png"]}}))
            request={"stream_id":later["result_stream_id"],"profile":{"formats":["png"],"margin_mpt":42000}}
            good(visual.render({"request_key":"different-profile",**request}))
            count=renderer.render_count
            for index in range(20):
                reply=good(visual.render({"request_key":f"cache-{index}",**request}))
                require(reply["cache_hit"] and renderer.render_count==count,"repeated preview failed to reuse artifacts")
            require(count==6,"render recovery workload exceeded its six actual renders",actual=count)
            return {"actual_renders":count,"worker_starts":renderer.starts,"terminated_owned_worker":owned_pid,"cache_reuses":20,"head_revision":store.model.head(source["document_id"]).revision}
        finally:
            visual.close()


WORKLOADS={"golden":golden,"workflow":workflow,"limits":limits,"storage_faults":storage_faults,
           "crash_recovery":crash_recovery,"network_load":network_load,"render_recovery":render_recovery}
