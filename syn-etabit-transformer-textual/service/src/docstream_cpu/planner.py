"""Bounded reduction of explicit assignment cells between conservative barriers."""
from __future__ import annotations

from dataclasses import dataclass

from .errors import ModelError
from .executor import Cell, Evaluation, Prepared, State, Write, prepare_operation, validate_base
from .models import Snapshot, digest
from .operations import Batch, InsertBlock

OPTIMIZER_VERSION = "docstream.cpu.reducer/1"


@dataclass(frozen=True)
class Reduction:
    rule_id: str
    operation_ids: tuple[str, ...]
    cells: tuple[Cell, ...]
    reason: str

    def to_dict(self):
        return {"rule_id": self.rule_id, "operation_ids": list(self.operation_ids),
                "cells": [list(cell) for cell in self.cells], "reason": self.reason}


@dataclass(frozen=True)
class Dependency:
    before: str
    after: str
    reason: str


@dataclass(frozen=True)
class Step:
    operation_ids: tuple[str, ...]
    writes: tuple[Write, ...] = ()
    command: Prepared | None = None

    def to_dict(self):
        return {"operation_ids": list(self.operation_ids),
                "writes": [{"cell": list(w.cell), "value": w.value} for w in self.writes],
                "command": self.command.operation.model_dump(mode="json") if self.command else None}


@dataclass(frozen=True)
class Plan:
    base_sha256: str
    batch: Batch
    steps: tuple[Step, ...]
    reductions: tuple[Reduction, ...]
    dependencies: tuple[Dependency, ...]
    expected_output_sha256: str
    optimizer_version: str
    reserved_block_ids: tuple[str, ...]
    seal: str

    def payload(self):
        return {"base_sha256": self.base_sha256, "batch": self.batch.model_dump(mode="json"),
                "steps": [step.to_dict() for step in self.steps],
                "reductions": [r.to_dict() for r in self.reductions],
                "dependencies": [vars(edge) for edge in self.dependencies],
                "expected_output_sha256": self.expected_output_sha256,
                "optimizer_version": self.optimizer_version,
                "reserved_block_ids": list(self.reserved_block_ids)}

    def to_dict(self):
        return {**self.payload(), "plan_sha256": self.seal,
                "requested_operations": len(self.batch.operations),
                "property_writes": sum(len(step.writes) for step in self.steps),
                "structural_operations": sum(step.command is not None for step in self.steps)}


def plan(snapshot: Snapshot, batch: Batch, *, reserved_block_ids: frozenset[str] = frozenset()) -> Plan:
    validate_base(snapshot, batch)
    state = State(snapshot)
    steps: list[Step] = []
    reductions: list[Reduction] = []
    dependencies: list[Dependency] = []
    histories: dict[Cell, list[tuple[str, object]]] = {}
    starts: dict[Cell, object] = {}
    region_ids: list[str] = []
    used_ids = {b.block_id for b in snapshot.blocks} | set(reserved_block_ids)
    previous: str | None = None
    last_barrier: str | None = None

    def flush():
        selected: dict[str, list[Write]] = {}
        for cell, history in histories.items():
            last_id, last_value = history[-1]
            if starts[cell] == last_value and type(starts[cell]) is type(last_value):
                reductions.append(Reduction("RED-03", tuple(dict.fromkeys(opid for opid, _ in history)), (cell,), "exact assignment state returns to region input"))
                continue
            for opid, value in history[:-1]:
                duplicate = value == last_value and type(value) is type(last_value)
                reductions.append(Reduction("RED-01" if duplicate else "RED-02", (opid, last_id), (cell,), "unobserved duplicate assignment" if duplicate else "unobserved write superseded by final assignment"))
            selected.setdefault(last_id, []).append(Write(cell, last_value))
        origins = tuple(opid for opid in region_ids if opid in selected)
        writes = tuple(item for opid in origins for item in sorted(selected[opid], key=lambda w: w.cell))
        if writes:
            steps.append(Step(origins, writes))
            if len(origins) > 1:
                reductions.append(Reduction("RED-04", origins, tuple(w.cell for w in writes), "disjoint final cells grouped in stable source order"))
        histories.clear()
        starts.clear()
        region_ids.clear()

    for op in batch.operations:
        if isinstance(op, InsertBlock):
            if op.block.block_id in used_ids:
                raise ModelError("DUPLICATE_TARGET", "block ID cannot be reused within a batch", op.operation_id)
            used_ids.add(op.block.block_id)
        prepared = prepare_operation(state, snapshot, op)
        if prepared.barrier:
            # All structural/text commands fence assignment regions. Every earlier
            # request in the region is a conservative dependency of this command.
            predecessors = region_ids if region_ids else ([previous] if previous is not None else [])
            for predecessor in predecessors:
                dependencies.append(Dependency(predecessor, op.operation_id, "source-order barrier"))
            flush()
            steps.append(Step((op.operation_id,), command=prepared))
            last_barrier = op.operation_id
        else:
            region_ids.append(op.operation_id)
            if last_barrier is not None:
                dependencies.append(Dependency(last_barrier, op.operation_id, "follows structural/text barrier"))
            for item in prepared.writes:
                if item.cell not in histories:
                    starts[item.cell] = state.read(item.cell)
                    histories[item.cell] = []
                elif histories[item.cell][-1][0] != op.operation_id:
                    dependencies.append(Dependency(histories[item.cell][-1][0], op.operation_id, "same-property source order"))
                histories[item.cell].append((op.operation_id, item.value))
        state.apply(prepared)
        previous = op.operation_id
    flush()
    provisional = Plan(snapshot.digest, batch, tuple(steps), tuple(reductions), tuple(dependencies), state.snapshot().digest, OPTIMIZER_VERSION, tuple(sorted(reserved_block_ids)), "")
    return Plan(**{**vars(provisional), "seal": digest(provisional.payload())})


def execute(snapshot: Snapshot, compiled: Plan) -> Evaluation:
    if compiled.optimizer_version != OPTIMIZER_VERSION or digest(compiled.payload()) != compiled.seal:
        raise ModelError("INVALID_PLAN", "plan content or optimizer version differs from its seal")
    validate_base(snapshot, compiled.batch)
    if compiled.base_sha256 != snapshot.digest:
        raise ModelError("STALE_BASE", "plan input differs from snapshot")
    state = State(snapshot)
    count = structural = 0
    for step in compiled.steps:
        for item in step.writes:
            state.write(item)
            count += 1
        if step.command is not None:
            checked = prepare_operation(state, snapshot, step.command.operation)
            state.apply(checked)
            structural += 1
    result = state.snapshot()
    if result.digest != compiled.expected_output_sha256:
        raise ModelError("CONFORMANCE_FAILURE", "reduced output differs from validated symbolic result")
    return Evaluation(result, len(compiled.batch.operations), count, structural)
