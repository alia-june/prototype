"""Strict, immutable values for the CPU reference model.

Snapshots describe content; stream IDs describe occurrences. Original source bytes
are retained independently from semantic JSON and never newline-normalized.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Identifier = Annotated[str, StringConstraints(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")]
FontName = Annotated[str, StringConstraints(min_length=1, max_length=256, strip_whitespace=False, pattern=r"\S")]
Positive = Annotated[int, Field(gt=0, le=2_000_000)]


class Value(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True, revalidate_instances="always")

    @model_validator(mode="after")
    def valid_unicode(self):
        # A semantic value must be serializable as UTF-8 without silent repair.
        for name in type(self).model_fields:
            value = getattr(self, name)
            if isinstance(value, str):
                try:
                    value.encode("utf-8")
                except UnicodeError as exc:
                    raise ValueError("unpaired Unicode surrogate is not supported") from exc
        return self


class Style(Value):
    font_family: FontName | None = None
    font_size_mpt: Positive | None = None
    bold: bool | None = None
    italic: bool | None = None


class Properties(Value):
    title: str = ""
    font_family: FontName = "Aptos"
    font_size_mpt: Positive = 11000
    page_width_mpt: Positive = 612000
    page_height_mpt: Positive = 792000


class Block(Value):
    block_id: Identifier
    kind: Literal["paragraph", "heading", "code", "list_item"] = "paragraph"
    text: str = ""
    style: Style = Field(default_factory=Style)
    heading_level: Annotated[int, Field(ge=1, le=6)] | None = None
    list_kind: Literal["bullet", "ordered"] | None = None

    @model_validator(mode="after")
    def validate_kind(self):
        if (self.kind == "heading") != (self.heading_level is not None):
            raise ValueError("heading_level is required only for heading blocks")
        if (self.kind == "list_item") != (self.list_kind is not None):
            raise ValueError("list_kind is required only for list_item blocks")
        return self


class Snapshot(Value):
    schema_version: Literal["docstream.snapshot/1"] = "docstream.snapshot/1"
    properties: Properties = Field(default_factory=Properties)
    blocks: tuple[Block, ...] = ()

    @model_validator(mode="after")
    def unique_ids(self):
        ids = [block.block_id for block in self.blocks]
        if len(ids) != len(set(ids)):
            raise ValueError("block IDs must be unique")
        return self

    @property
    def digest(self) -> str:
        return digest(self.model_dump(mode="json"))

    def block(self, block_id: str) -> Block:
        for block in self.blocks:
            if block.block_id == block_id:
                return block
        raise KeyError(block_id)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: object) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def text_digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()
