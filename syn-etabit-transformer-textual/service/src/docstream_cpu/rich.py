"""Version two values. Version one serialization and hashes stay unchanged."""
from __future__ import annotations

import json
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field, model_validator

from .models import Block, Identifier, Properties, Snapshot, Style, Value, digest

Hash = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


def safe_link(value: str) -> bool:
    if any(ord(c) < 32 for c in value) or "\\" in value:
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme.lower() in ("https", "http", "mailto") and not parsed.username and not parsed.password and (bool(parsed.hostname) if parsed.scheme.lower() in ("http","https") else bool(parsed.path))
    except ValueError:
        return False


class Span(Value):
    text: str = ""
    style: Style = Field(default_factory=Style)
    code: bool = False
    href: str | None = None

    @model_validator(mode="after")
    def link(self):
        if self.href is not None and not safe_link(self.href):
            raise ValueError("only http, https and mailto links without credentials are supported")
        return self


class CellText(Value):
    runs: tuple[Span, ...] = ()


class TableCell(Value):
    paragraphs: tuple[CellText, ...] = Field(min_length=1)


class TableRow(Value):
    cells: tuple[TableCell, ...] = Field(min_length=1, max_length=32)
    header: bool = False


class ImageRef(Value):
    sha256: Hash
    media_type: Literal["image/png", "image/jpeg"]
    alt: str = ""
    width_mpt: Annotated[int, Field(gt=0, le=1_000_000)]
    height_mpt: Annotated[int, Field(gt=0, le=1_000_000)]


class RichBlock(Value):
    block_id: Identifier
    kind: Literal["paragraph", "heading", "code", "list_item", "table", "image"] = "paragraph"
    text: str = ""
    style: Style = Field(default_factory=Style)
    heading_level: Annotated[int, Field(ge=1, le=6)] | None = None
    list_kind: Literal["bullet", "ordered"] | None = None
    list_depth: Annotated[int, Field(ge=0, le=8)] = 0
    list_start: Annotated[int, Field(ge=0, le=1_000_000)] = 1
    runs: tuple[Span, ...] = ()
    rows: tuple[TableRow, ...] = Field(default=(), max_length=1000)
    image: ImageRef | None = None

    @model_validator(mode="after")
    def structure(self):
        if (self.kind == "heading") != (self.heading_level is not None):
            raise ValueError("heading_level is required only for headings")
        if (self.kind == "list_item") != (self.list_kind is not None):
            raise ValueError("list_kind is required only for list items")
        if self.kind != "list_item" and (self.list_depth or self.list_start != 1):
            raise ValueError("list metadata is only valid on list items")
        if (self.kind == "table") != bool(self.rows):
            raise ValueError("table rows required only for tables")
        if self.rows and len({len(row.cells) for row in self.rows}) != 1:
            raise ValueError("tables must be rectangular")
        if (self.kind == "image") != (self.image is not None):
            raise ValueError("image reference required only for images")
        if self.kind in ("table", "image") and (self.text or self.runs):
            raise ValueError("table/image blocks cannot also contain text or runs")
        if self.runs and self.text != "".join(run.text for run in self.runs):
            raise ValueError("text must exactly match concatenated runs")
        return self


class Snapshot2(Value):
    schema_version: Literal["docstream.snapshot/2"] = "docstream.snapshot/2"
    properties: Properties = Field(default_factory=Properties)
    blocks: tuple[RichBlock, ...] = ()

    @model_validator(mode="after")
    def structure(self):
        ids = [b.block_id for b in self.blocks]
        if len(ids) != len(set(ids)):
            raise ValueError("block IDs must be unique")
        depth = -1
        for block in self.blocks:
            if block.kind == "list_item":
                if block.list_depth > depth + 1:
                    raise ValueError("list nesting cannot skip levels")
                depth = block.list_depth
            else:
                depth = -1
        return self

    @property
    def digest(self):
        return digest(self.model_dump(mode="json"))

    def block(self, block_id):
        for block in self.blocks:
            if block.block_id == block_id:
                return block
        raise KeyError(block_id)


def parse_snapshot(value):
    if isinstance(value, (Snapshot, Snapshot2)):
        return type(value).model_validate(value)
    if isinstance(value, (str, bytes)):
        value = json.loads(value)
    cls = Snapshot2 if value.get("schema_version") == "docstream.snapshot/2" else Snapshot
    return cls.model_validate_json(json.dumps(value, ensure_ascii=False, allow_nan=False))


def style_nodes(block):
    """Return stable paths to nested explicit styles, independent of display text."""
    result = {block.block_id: block.style}
    if isinstance(block, RichBlock):
        for index, run in enumerate(block.runs):
            result[f"{block.block_id}/r/{index}"] = run.style
        for row, record in enumerate(block.rows):
            for col, cell in enumerate(record.cells):
                for para, paragraph in enumerate(cell.paragraphs):
                    for index, run in enumerate(paragraph.runs):
                        result[f"{block.block_id}/t/{row}/{col}/{para}/{index}"] = run.style
    return result


def restyle(block, styles):
    payload = block.model_dump()
    payload["style"] = styles[block.block_id]
    if isinstance(block, RichBlock):
        for index, run in enumerate(payload["runs"]):
            run["style"] = styles[f"{block.block_id}/r/{index}"]
        for row, record in enumerate(payload["rows"]):
            for col, cell in enumerate(record["cells"]):
                for para, paragraph in enumerate(cell["paragraphs"]):
                    for index, run in enumerate(paragraph["runs"]):
                        run["style"] = styles[f"{block.block_id}/t/{row}/{col}/{para}/{index}"]
    return type(block)(**payload)
