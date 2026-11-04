"""Closed operation registry. JSON arrays become immutable tuples; no coercion of scalars."""
from __future__ import annotations

import json
from typing import Annotated, Literal, Union

from pydantic import Field, ValidationError, field_validator, model_validator

from .errors import ModelError
from .models import Block, FontName, Identifier, Value, digest
from .rich import RichBlock

PropertyName = Literal["title", "font_family", "font_size_mpt", "page_width_mpt", "page_height_mpt"]
StyleName = Literal["font_family", "font_size_mpt", "bold", "italic"]


class Operation(Value):
    operation_id: Identifier
    version: Literal[1] = 1

    @field_validator("version", mode="before")
    @classmethod
    def exact_version(cls, value):
        if type(value) is not int or value != 1:
            raise ValueError("operation version requires the exact integer 1")
        return value


def check_value(prop: str, value: object, *, nullable: bool) -> None:
    if value is None and nullable:
        return
    if prop in {"bold", "italic"}:
        if type(value) is not bool:
            raise ValueError(f"{prop} requires an exact boolean")
    elif prop in {"font_size_mpt", "page_width_mpt", "page_height_mpt"}:
        if type(value) is not int or not 0 < value <= 2_000_000:
            raise ValueError(f"{prop} requires a positive millipoint integer")
    elif type(value) is not str or (prop == "font_family" and (not value.strip() or len(value) > 256)):
        raise ValueError(f"{prop} requires a valid string")


class Targets(Value):
    targets: tuple[Identifier, ...]

    @model_validator(mode="after")
    def target_set(self):
        if not self.targets or len(self.targets) != len(set(self.targets)):
            raise ValueError("targets must be nonempty and unique")
        return self


class SetProperty(Operation):
    kind: Literal["set_property"] = "set_property"
    property: PropertyName
    value: str | int

    @model_validator(mode="after")
    def valid_value(self):
        check_value(self.property, self.value, nullable=False)
        return self


class SetStyle(Operation, Targets):
    kind: Literal["set_style"] = "set_style"
    property: StyleName
    value: str | int | bool | None

    @model_validator(mode="after")
    def valid_value(self):
        check_value(self.property, self.value, nullable=True)
        return self


class RestoreStyle(Operation, Targets):
    kind: Literal["restore_style"] = "restore_style"
    # Restores exact explicit styles from the batch input, not effective values.


class SetFont(Operation):
    kind: Literal["set_font"] = "set_font"
    font_family: FontName
    scope: Literal["all_text"] = "all_text"

    @field_validator("font_family")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("font must not be blank")
        return value


class RestoreFont(Operation):
    kind: Literal["restore_font"] = "restore_font"
    # Restores default AND per-block font overrides from batch input.


class ReplaceText(Operation):
    kind: Literal["replace_text"] = "replace_text"
    target: Identifier
    text: str
    expected_text_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class InsertBlock(Operation):
    kind: Literal["insert_block"] = "insert_block"
    block: Block | RichBlock
    after: Identifier | None = None  # None means the start of the document.


class RemoveBlock(Operation):
    kind: Literal["remove_block"] = "remove_block"
    target: Identifier


class MoveBlock(Operation):
    kind: Literal["move_block"] = "move_block"
    target: Identifier
    after: Identifier | None = None


class ReplaceBlock(Operation):
    kind: Literal["replace_block"] = "replace_block"
    target: Identifier
    block: RichBlock
    expected_block_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]

    @model_validator(mode="after")
    def same_identity(self):
        if self.target != self.block.block_id:
            raise ValueError("replacement must preserve the block ID")
        return self


AnyOperation = Annotated[Union[SetProperty, SetStyle, RestoreStyle, SetFont, RestoreFont, ReplaceText, InsertBlock, RemoveBlock, MoveBlock, ReplaceBlock], Field(discriminator="kind")]


class Batch(Value):
    schema_version: Literal["docstream.batch/1"] = "docstream.batch/1"
    base_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    operations: tuple[AnyOperation, ...] = Field(max_length=256)

    @model_validator(mode="after")
    def unique_operations(self):
        ids = [op.operation_id for op in self.operations]
        if len(ids) != len(set(ids)):
            raise ValueError("operation IDs must be unique in a batch")
        return self

    @property
    def digest(self) -> str:
        return digest(self.model_dump(mode="json"))


def parse_batch(payload: str | dict) -> Batch:
    """One JSON boundary for JSON and dictionary callers, with strict scalar rules."""
    try:
        if type(payload) is dict:
            payload = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        if type(payload) is not str:
            raise ValueError("batch must be a JSON string or dictionary")
        return Batch.model_validate_json(payload)
    except (ValidationError, ValueError, TypeError) as exc:
        raise ModelError("VALIDATION_ERROR", str(exc)) from exc
