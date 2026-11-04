"""Maintained format service operations; callers supply data, never script paths."""
import base64
from dataclasses import asdict
from hashlib import sha256
import json
from typing import Literal

from pydantic import Field, field_validator, model_validator

from .artifacts import ArtifactStore
from .assets import AssetStore, validate_image, validate_references
from .catalog import Source
from .docx_adapter import export_docx, import_docx
from .errors import ModelError
from .format_common import MAX_SOURCE, read_package, safe_asset_name
from .markdown_adapter import export_markdown, import_markdown
from .models import Identifier, Properties, Value, canonical_bytes
from .service import DocumentService, RequestKey, MAX_TEXT_BYTES, parse_request


class ImportRequest(Value):
    request_key: RequestKey
    format: Literal["markdown", "markdown_bundle", "docx"]
    data_base64: str = Field(max_length=1_398_104)
    assets: dict[str, str] = Field(default_factory=dict, max_length=64)
    loss_policy: Literal["reject", "allow"] = "reject"

    @field_validator("assets")
    @classmethod
    def names(cls, value):
        if any(len(name)>256 or not safe_asset_name(name) for name in value):
            raise ValueError("asset names must be safe relative identifiers")
        return value

    @model_validator(mode="after")
    def encoded_limit(self):
        if len(self.data_base64)+sum(map(len,self.assets.values())) > 1_398_104:
            raise ValueError("combined base64 input exceeds the bounded source limit")
        return self


class ExportRequest(Value):
    request_key: RequestKey
    stream_id: Identifier
    format: Literal["markdown_bundle", "docx"]
    loss_policy: Literal["reject", "allow"] = "reject"


def decode(value):
    if len(value) > (MAX_SOURCE+2)//3*4:
        raise ModelError("SOURCE_LIMIT", "base64 source exceeds 1 MiB decoded limit")
    try:
        raw = base64.b64decode(value, validate=True)
    except ValueError as exc:
        raise ModelError("VALIDATION_ERROR", "invalid base64 source") from exc
    if len(raw) > MAX_SOURCE:
        raise ModelError("SOURCE_LIMIT", "source exceeds 1 MiB")
    return raw


def inspect_structure(snapshot, request):
    """Read a bounded JSON subtree; paths navigate fields/array indices explicitly."""
    value = snapshot.block(request.block_id).model_dump(mode="json") if request.block_id else snapshot.model_dump(mode="json")
    try:
        for component in request.path:
            if type(component) is int and component < 0:
                raise KeyError(component)
            value = value[component]
    except (KeyError, IndexError, TypeError) as exc:
        raise ModelError("UNKNOWN_PATH", "structure path does not exist") from exc
    if isinstance(value, (str, list)):
        return {"value": value[request.offset:request.offset+request.limit], "total":len(value), "offset":request.offset, "path":list(request.path)}
    if isinstance(value, dict):
        keys = list(value)
        return {"value":{key:value[key] for key in keys[request.offset:request.offset+request.limit]}, "total":len(keys), "offset":request.offset, "path":list(request.path)}
    return {"value":value, "path":list(request.path)}


class FormatService:
    def __init__(self, store):
        self.store = store
        self.service = DocumentService(store)
        self.assets = AssetStore(store)
        self.artifacts = ArtifactStore(store)

    def import_document(self, payload):
        request = parse_request(ImportRequest, payload)

        def action(model):
            raw = decode(request.data_base64)
            supplied = {name:decode(value) for name,value in request.assets.items()}
            if len(raw)+sum(map(len,supplied.values())) > MAX_SOURCE:
                raise ModelError("SOURCE_LIMIT", "combined source and supplied assets exceed 1 MiB")
            if request.format != "markdown" and supplied:
                raise ModelError("VALIDATION_ERROR", "separate assets apply only to Markdown")
            if request.format == "docx":
                snapshot, images, losses = import_docx(raw)
            elif request.format == "markdown_bundle":
                package = read_package(raw)
                if "document.md" not in package or "docstream.json" not in package:
                    raise ModelError("INVALID_PACKAGE", "Markdown bundle requires document.md and docstream.json")
                try:
                    manifest = json.loads(package["docstream.json"])
                    if set(manifest) != {"schema", "properties", "images"} or manifest["schema"] != "docstream.markdown-bundle/1":
                        raise ValueError("manifest")
                    props = Properties.model_validate(manifest["properties"])
                    image_metadata = manifest["images"]
                    if type(image_metadata) is not dict or len(image_metadata)>64:
                        raise ValueError("images")
                    for key,value in image_metadata.items():
                        if len(key)!=64 or type(value) is not dict or set(value)!={"width_mpt","height_mpt"} or any(type(v) is not int or not 0<v<=1_000_000 for v in value.values()):
                            raise ValueError("image dimensions")
                except (ValueError, TypeError, KeyError) as exc:
                    raise ModelError("INVALID_PACKAGE", "invalid bundle manifest") from exc
                allowed = {"document.md", "docstream.json"} | {name for name in package if name.startswith("assets/")}
                if set(package) != allowed:
                    raise ModelError("INVALID_PACKAGE", "unexpected bundle entries")
                snapshot, images, losses = import_markdown(package["document.md"], package, properties=props, image_metadata=image_metadata)
            else:
                snapshot, images, losses = import_markdown(raw, supplied)
            losses.check(request.loss_policy)
            if len(canonical_bytes(snapshot.model_dump(mode="json"))) > MAX_TEXT_BYTES:
                raise ModelError("LIMIT_EXCEEDED", "imported semantic content exceeds 1 MiB")
            for content in images.values():
                self.assets.put(content)
            validate_references(snapshot, self.assets.get)
            head = model.ingest(snapshot, original_bytes=raw)
            source_id = model._document_sources[head.document_id]
            model._sources[source_id] = Source(source_id, raw, request.format)
            return {**asdict(head), "semantic_sha256":snapshot.digest, "schema_version":snapshot.schema_version,
                    "original_sha256":sha256(raw).hexdigest(), "total_blocks":len(snapshot.blocks),
                    "assets":sorted(images), "diagnostics":losses.items, "loss_policy":request.loss_policy, "visual_state":"not_rendered"}

        return self.service._mutate("import", request, action)

    def export_document(self, payload):
        request = parse_request(ExportRequest, payload)

        def action(model):
            snapshot = model.materialize(request.stream_id)
            validate_references(snapshot, self.assets.get)
            raw, losses = (export_docx(snapshot,self.assets.get) if request.format == "docx" else export_markdown(snapshot,self.assets.get))
            losses.check(request.loss_policy)
            artifact = self.artifacts.publish_blob(raw, "docx" if request.format == "docx" else "zip")
            return {"stream_id":request.stream_id, "semantic_sha256":snapshot.digest, "format":request.format,
                    "artifact":artifact, "diagnostics":losses.items, "loss_policy":request.loss_policy, "committed":False}

        reply = self.service._mutate("export", request, action)
        if reply.get("ok"):
            try:
                with self.store.lock:
                    self.artifacts.metadata(reply["result"]["artifact"]["artifact_id"])
            except ModelError:
                return {"ok":False, "job_id":reply["job_id"], "state":reply["state"], "error":{"code":"ARTIFACT_UNAVAILABLE", "message":"receipt retained; use a new export request key to repair an unavailable artifact", "committed":False}}
        return reply
