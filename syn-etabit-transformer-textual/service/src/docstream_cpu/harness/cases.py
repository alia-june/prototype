"""Closed replay registry. Case files contain data and no executable commands."""
from __future__ import annotations

import base64
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import unittest

from ..catalog import CpuModel
from ..errors import ModelError
from ..executor import reference_execute
from ..format_service import FormatService
from ..markdown_adapter import export_markdown, import_markdown
from ..docx_adapter import export_docx, import_docx
from ..models import Snapshot
from ..operations import parse_batch
from ..planner import execute, plan
from ..rich import parse_snapshot
from ..service import DocumentService
from ..storage import Store
from .core import CheckFailed, SERVICE_ROOT, encoded, require, semantic_meaning

KINDS={"batch","markdown_pair","markdown_roundtrip","docx_roundtrip","invalid_request","malformed_package",
       "golden","regression","workflow","limits","network_load","crash_recovery","storage_faults","render_recovery"}
REGRESSION_MODULES=("test_cpu","test_baseline","test_service","test_mcp","test_rendering","test_formats")


def execute_case(case, root, context=None):
    kind,data=case["kind"],case["input"]
    root=Path(root)
    if kind=="batch":
        source=parse_snapshot(data["snapshot"])
        batch=parse_batch(data["batch"])
        before=source.model_dump_json()
        expected=data.get("expected_error")
        if expected:
            errors=[]
            for function in (reference_execute,plan):
                try:
                    function(source,batch)
                except ModelError as exc:
                    errors.append((exc.code,exc.operation_id))
                else:
                    raise CheckFailed("invalid request was accepted",{"expected":expected})
            require(errors[0]==errors[1] and errors[0][0]==expected,"invalid batch error differs",errors=errors,expected=expected)
            return {"expected_rejection":expected,"operation_id":errors[0][1]}
        reference=reference_execute(source,batch)
        compiled=plan(source,batch)
        output=execute(source,compiled).snapshot
        require(output.model_dump()==reference.snapshot.model_dump(),"reducer output differs from sequential reference",expected=reference.snapshot.model_dump(mode="json"),actual=output.model_dump(mode="json"))
        require(before==source.model_dump_json(),"batch mutated its immutable source")
        require(compiled.seal==plan(source,batch).seal,"plan is not deterministic")
        return {"operations":len(batch.operations),"reduced_writes":compiled.to_dict()["property_writes"],"semantic_sha256":output.digest}
    if kind=="markdown_pair":
        a,_,loss_a=import_markdown(data["left"].encode(),{})
        b,_,loss_b=import_markdown(data["right"].encode(),{})
        require(not loss_a.items and not loss_b.items,"equivalent Markdown unexpectedly loses content",left=loss_a.items,right=loss_b.items)
        require(semantic_meaning(a)==semantic_meaning(b),"equivalent Markdown differs in meaning",left=semantic_meaning(a),right=semantic_meaning(b))
        return {"equivalent":True}
    if kind in ("markdown_roundtrip","docx_roundtrip"):
        source=parse_snapshot(data["snapshot"])
        before=source.model_dump_json()
        expected_error=data.get("expected_error")
        if expected_error is not None and (kind!="docx_roundtrip" or expected_error!="UNREPRESENTABLE_DOCX"):
            raise ValueError("unsupported expected conversion rejection")
        export=export_markdown if kind=="markdown_roundtrip" else export_docx
        try:
            raw,losses=export(source,lambda _: (_ for _ in ()).throw(ValueError("fixture has no images")))
        except ModelError as exc:
            require(type(exc) is ModelError and expected_error is not None and exc.code==expected_error,
                    "conversion received wrong typed rejection",expected=expected_error,actual=exc.code,exception=type(exc).__name__)
            require(source.model_dump_json()==before,"rejected export mutated its source")
            return {"expected_rejection":exc.code}
        except Exception as exc:
            raise CheckFailed("conversion raised an unclassified exception",{"exception":type(exc).__name__,"message":str(exc)}) from exc
        require(expected_error is None,"expected conversion rejection was accepted",expected=expected_error)
        require(source.model_dump_json()==before,"export mutated its source")
        codes={item["code"] for item in losses.items}
        allowed=set(data.get("allowed_losses",[]))
        require(codes.issubset(allowed),"unexpected conversion loss",diagnostics=losses.items)
        if "DOCX_CARRIAGE_RETURN" in allowed:
            require(kind=="docx_roundtrip" and codes=={"DOCX_CARRIAGE_RETURN"},"declared carriage-return loss was not reported exactly",diagnostics=losses.items)
        if codes and codes!={"DOCX_CARRIAGE_RETURN"}:
            return {"expected_losses":sorted(codes)}
        if kind=="docx_roundtrip":
            result,_,import_losses=import_docx(raw)
        else:
            from ..format_common import read_package
            from ..models import Properties
            package=read_package(raw)
            manifest=json.loads(package["docstream.json"])
            result,_,import_losses=import_markdown(package["document.md"],package,properties=Properties(**manifest["properties"]),image_metadata=manifest["images"])
        require(not import_losses.items,"round-trip import unexpectedly loses content",diagnostics=import_losses.items)
        expected=semantic_meaning(source)
        if codes=={"DOCX_CARRIAGE_RETURN"}:
            # Only this explicitly declared loss gets an alternate oracle. All
            # other text, style, ordering and structure remain significant.
            expected=deepcopy(expected)
            def mapped(value):
                if isinstance(value,dict):
                    return {key:child.replace("\r","\n") if key in ("title","text") and isinstance(child,str)
                            else mapped(child) for key,child in value.items()}
                if isinstance(value,list): return [mapped(child) for child in value]
                return value
            expected=mapped(expected)
        require(expected==semantic_meaning(result),"round-trip changed supported meaning",expected=expected,actual=semantic_meaning(result))
        return {"export_bytes":len(raw),"meaning_preserved":not bool(codes),"expected_losses":sorted(codes)}
    if kind in ("invalid_request","malformed_package"):
        with Store(root) as store:
            try:
                if kind=="invalid_request":
                    result=DocumentService(store).ingest(data["request"])
                else:
                    result=FormatService(store).import_document({"request_key":"malformed","format":"docx","data_base64":data["data_base64"]})
            except ModelError as exc:
                code=exc.code
            else:
                require(not result["ok"],"invalid input was accepted",response=result)
                code=result["error"]["code"]
            expected=data.get("expected_errors",[data.get("expected_error")])
            require(code in expected,"invalid input received wrong error",expected=expected,actual=code)
            require(store.connection.execute("SELECT count(*) FROM documents").fetchone()[0]==0,"invalid input created a document")
            return {"expected_rejection":code}
    if kind=="regression":
        test_id=data["test_id"]
        sys.path.insert(0,str(SERVICE_ROOT/"tests")) if str(SERVICE_ROOT/"tests") not in sys.path else None
        if test_id.startswith("docstream_baseline_tests."):
            import test_baseline
            allowed={test.id():test for test in test_baseline.load_tests(unittest.defaultTestLoader,None,None)}
            if test_id not in allowed:
                raise ValueError("baseline replay is outside the six approved tests")
            suite=unittest.TestSuite([allowed[test_id]])
        else:
            if not re.fullmatch(r"test_(cpu|service|mcp|rendering|formats)\.[A-Za-z0-9_]+\.test_[A-Za-z0-9_]+",test_id):
                raise ValueError("replay regression ID is outside the closed test registry")
            suite=unittest.defaultTestLoader.loadTestsFromName(test_id)
        result=unittest.TestResult()
        suite.run(result)
        require(result.testsRun==1 and result.wasSuccessful() and not result.skipped,"regression test failed or skipped",failures=[text for _,text in result.failures],errors=[text for _,text in result.errors],skipped=result.skipped)
        return {"tests_run":result.testsRun}
    from .workloads import WORKLOADS
    if kind not in WORKLOADS:
        raise ValueError("unknown closed case kind")
    return WORKLOADS[kind](data,root,context)
