"""Sequential semantics and symbolic state used by planning.

Planning mutates a small symbolic map, not every intermediate full snapshot.
No filesystem, network, rendering or executable operation is provided here.
"""
from __future__ import annotations

from dataclasses import dataclass

from .errors import ModelError
from .models import Block, Properties, Snapshot, Style, text_digest
from .rich import Snapshot2, RichBlock, parse_snapshot, restyle, style_nodes
from .operations import (Batch, InsertBlock, MoveBlock, Operation, RemoveBlock,
                         ReplaceText, RestoreFont, RestoreStyle, SetFont,
                         SetProperty, SetStyle, ReplaceBlock)

Cell = tuple[str, str, str]
Scalar = str | int | bool | None


@dataclass(frozen=True)
class Write:
    cell: Cell
    value: Scalar


@dataclass(frozen=True)
class Prepared:
    operation: Operation
    writes: tuple[Write, ...]
    barrier: bool


@dataclass(frozen=True)
class Evaluation:
    snapshot: Snapshot
    operation_count: int
    property_writes: int
    structural_operations: int


class State:
    def __init__(self, snapshot: Snapshot):
        self.snapshot_type = type(snapshot)
        self.properties = snapshot.properties.model_dump()
        self.order = [block.block_id for block in snapshot.blocks]
        self.blocks = {block.block_id: block for block in snapshot.blocks}
        self.styles = {key: style.model_dump() for block in snapshot.blocks for key, style in style_nodes(block).items()}

    def require(self, target: str, operation_id: str) -> None:
        if target not in self.blocks:
            raise ModelError("UNKNOWN_TARGET", f"unknown block: {target}", operation_id)

    def read(self, cell: Cell) -> Scalar:
        category, target, prop = cell
        return self.properties[prop] if category == "document" else self.styles[target][prop]

    def write(self, item: Write) -> None:
        category, target, prop = item.cell
        if category == "document":
            self.properties[prop] = item.value
        else:
            self.styles[target][prop] = item.value

    def snapshot(self) -> Snapshot:
        blocks = tuple(restyle(self.blocks[key], self.styles) for key in self.order)
        return self.snapshot_type(properties=Properties(**self.properties), blocks=blocks)

    def apply(self, prepared: Prepared) -> None:
        for item in prepared.writes:
            self.write(item)
        op = prepared.operation
        if not prepared.barrier:
            return
        if isinstance(op, ReplaceText):
            block = self.blocks[op.target]
            self.blocks[op.target] = type(block)(**{**block.model_dump(), "text": op.text})
        elif isinstance(op, InsertBlock):
            index = 0 if op.after is None else self.order.index(op.after) + 1
            self.order.insert(index, op.block.block_id)
            self.blocks[op.block.block_id] = op.block
            self.styles.update({key: style.model_dump() for key, style in style_nodes(op.block).items()})
        elif isinstance(op, ReplaceBlock):
            self.blocks[op.target] = op.block
            self.styles = {k: v for k, v in self.styles.items() if k != op.target and not k.startswith(op.target + "/")}
            self.styles.update({key: style.model_dump() for key, style in style_nodes(op.block).items()})
        elif isinstance(op, RemoveBlock):
            self.order.remove(op.target)
            del self.blocks[op.target]
            self.styles = {k: v for k, v in self.styles.items() if k != op.target and not k.startswith(op.target + "/")}
        elif isinstance(op, MoveBlock):
            self.order.remove(op.target)
            index = 0 if op.after is None else self.order.index(op.after) + 1
            self.order.insert(index, op.target)
        else:
            raise ModelError("INVALID_PLAN", "unsupported structural command", op.operation_id)
        if self.snapshot_type is Snapshot2:
            depth = -1
            for key in self.order:
                block = self.blocks[key]
                if block.kind == "list_item":
                    if block.list_depth > depth + 1:
                        raise ModelError("INVALID_STRUCTURE", "operation would leave an orphaned list level", op.operation_id)
                    depth = block.list_depth
                else:
                    depth = -1


def prepare_operation(state: State, base: Snapshot, op: Operation) -> Prepared:
    """Validate original sequential preconditions before optimization can remove work."""
    writes: list[Write] = []
    if isinstance(op, SetProperty):
        writes.append(Write(("document", "", op.property), op.value))
    elif isinstance(op, SetStyle):
        for target in op.targets:
            state.require(target, op.operation_id)
            writes.append(Write(("block", target, op.property), op.value))
    elif isinstance(op, RestoreStyle):
        for target in op.targets:
            state.require(target, op.operation_id)
            try:
                original = base.block(target)
            except KeyError as exc:
                raise ModelError("RESTORE_BASE_MISSING", f"block has no batch baseline: {target}", op.operation_id) from exc
            writes.extend(Write(("block", target, key), value) for key, value in original.style.model_dump().items())
    elif isinstance(op, SetFont):
        # Effective all-text assignment: set the default and remove per-block overrides.
        writes.append(Write(("document", "", "font_family"), op.font_family))
        writes.extend(Write(("block", target, "font_family"), None) for block_id in state.order for target in style_nodes(state.blocks[block_id]))
    elif isinstance(op, RestoreFont):
        writes.append(Write(("document", "", "font_family"), base.properties.font_family))
        originals = {key: value for block in base.blocks for key, value in style_nodes(block).items()}
        for block_id in state.order:
            for target in style_nodes(state.blocks[block_id]):
                if target not in originals:
                    raise ModelError("RESTORE_BASE_MISSING", f"style has no batch baseline: {target}", op.operation_id)
                writes.append(Write(("block", target, "font_family"), originals[target].font_family))
    elif isinstance(op, ReplaceText):
        state.require(op.target, op.operation_id)
        block = state.blocks[op.target]
        if isinstance(block, RichBlock) and (block.runs or block.kind in ("table", "image")):
            raise ModelError("RICH_REPLACEMENT_REQUIRED", "use guarded replace_block for structured content", op.operation_id)
        if text_digest(state.blocks[op.target].text) != op.expected_text_sha256:
            raise ModelError("PRECONDITION_FAILED", "text digest does not match logical input", op.operation_id)
    elif isinstance(op, InsertBlock):
        if (state.snapshot_type is Snapshot2) != isinstance(op.block, RichBlock):
            raise ModelError("SCHEMA_MISMATCH", "inserted block must match the snapshot version", op.operation_id)
        if op.block.block_id in state.blocks or any(b.block_id == op.block.block_id for b in base.blocks):
            raise ModelError("DUPLICATE_TARGET", "block ID already exists or belonged to the baseline", op.operation_id)
        if op.after is not None:
            state.require(op.after, op.operation_id)
    elif isinstance(op, ReplaceBlock):
        from .models import digest
        state.require(op.target, op.operation_id)
        if state.snapshot_type is not Snapshot2:
            raise ModelError("SCHEMA_MISMATCH", "rich replacement requires snapshot version two", op.operation_id)
        current = restyle(state.blocks[op.target], state.styles)
        if digest(current.model_dump(mode="json")) != op.expected_block_sha256:
            raise ModelError("PRECONDITION_FAILED", "block digest does not match logical input", op.operation_id)
    elif isinstance(op, (RemoveBlock, MoveBlock)):
        state.require(op.target, op.operation_id)
        if isinstance(op, MoveBlock) and op.after is not None:
            state.require(op.after, op.operation_id)
            if op.after == op.target:
                raise ModelError("INVALID_POSITION", "a block cannot follow itself", op.operation_id)
    else:
        raise ModelError("UNSUPPORTED_OPERATION", type(op).__name__, op.operation_id)
    return Prepared(op, tuple(writes), not writes and isinstance(op, (ReplaceText, InsertBlock, RemoveBlock, MoveBlock, ReplaceBlock)))


def validate_base(snapshot: Snapshot, batch: Batch) -> None:
    parse_snapshot(snapshot)
    Batch.model_validate(batch)
    if snapshot.digest != batch.base_sha256:
        raise ModelError("STALE_BASE", "batch input digest differs from the supplied snapshot")


def reference_execute(snapshot: Snapshot, batch: Batch, *, reserved_block_ids: frozenset[str] = frozenset()) -> Evaluation:
    """Execute all requests sequentially, without invoking the reducer."""
    validate_base(snapshot, batch)
    state = State(snapshot)
    writes = structural = 0
    used_ids = {block.block_id for block in snapshot.blocks} | set(reserved_block_ids)
    for op in batch.operations:
        if isinstance(op, InsertBlock):
            if op.block.block_id in used_ids:
                raise ModelError("DUPLICATE_TARGET", "block ID cannot be reused within a batch", op.operation_id)
            used_ids.add(op.block.block_id)
        prepared = prepare_operation(state, snapshot, op)
        state.apply(prepared)
        writes += len(prepared.writes)
        structural += int(prepared.barrier)
    return Evaluation(state.snapshot(), len(batch.operations), writes, structural)
