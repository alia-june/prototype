"""Build the approved AUTH-18A vertical relative-map composition probe."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .model import RelativeMapStore
from .values import MapDraft, MapEntry, MapRef, canonical, require
from .wordnet_pull import PullLimits, PullResult, SOURCE_SHA256, pull_wordnet_sample


PROBE_SCHEMA = "docstream.relative-maps.auth18a-result/1"
PROBE_CONTEXT = "auth18a"


@dataclass(frozen=True, slots=True)
class ProbeResult:
    pull: PullResult
    aliases: Mapping[str, str]
    relation_records: tuple[dict, ...]
    store_stats: Mapping[str, int]
    context_resolutions: Mapping[str, str]

    def to_summary(self) -> dict:
        return {"schema": PROBE_SCHEMA, "status": "COMPLETE",
                "pull": self.pull.to_summary(), "relation_records": len(self.relation_records),
                "map_aliases": len(self.aliases), "store_stats": dict(self.store_stats),
                "context_resolutions": dict(self.context_resolutions)}


def _entry(kind: str, **payload) -> MapEntry:
    return MapEntry.create(kind, payload)


def _record_payload(record) -> dict:
    value = record.to_record()
    value["record_id"] = record.record_id
    return value


def _relation_records(pull: PullResult) -> tuple[dict, ...]:
    targets = {}
    for record in pull.selected_records + pull.target_records:
        targets[(record.synset_type, record.synset_offset)] = record.record_id
        if record.synset_type == "s":
            targets[("a", record.synset_offset)] = record.record_id
        if record.synset_type == "a":
            targets[("s", record.synset_offset)] = record.record_id
    output = []
    for selection_index, record in enumerate(pull.selected_records):
        for pointer in record.pointers:
            target_id = targets.get((pointer.target_pos, pointer.target_offset))
            body = {"selection_index": selection_index, "source_record_id": record.record_id,
                    "pointer_index": pointer.pointer_index, "symbol": pointer.symbol,
                    "target_offset": pointer.target_offset, "target_pos": pointer.target_pos,
                    "source_target": pointer.source_target,
                    "resolution_status": "resolved" if target_id else "unresolved",
                    "target_record_id": target_id}
            body["relation_id"] = sha256(canonical(body)).hexdigest()
            output.append(body)
    return tuple(output)


def build_probe(archive_path: str | Path, expected_sha256: str = SOURCE_SHA256,
                pull_limits: PullLimits | None = None) -> tuple[ProbeResult, RelativeMapStore]:
    pull = pull_wordnet_sample(archive_path, pull_limits, expected_sha256=expected_sha256)
    relations = _relation_records(pull)
    records = pull.selected_records + pull.target_records
    object_entries = tuple(_entry("source-record", **_record_payload(record)) for record in records)
    selected_archive_order = sorted(pull.selected_records, key=lambda item: item.byte_offset)
    source_order = tuple(record.record_id for record in selected_archive_order)
    selection_order = tuple(record.record_id for record in pull.selected_records)
    relation_order_a = tuple(row["relation_id"] for row in relations)
    relation_order_b = tuple(row["relation_id"] for row in
                             sorted(relations, key=lambda row: (row["symbol"], row["target_pos"],
                                                                row["target_offset"], row["relation_id"]),
                                    reverse=True))
    source_structures = tuple(_entry("record-structure", record_id=record.record_id,
                                     word_ids=[word.raw_token for word in record.words],
                                     pointer_relation_ids=[row["relation_id"] for row in relations
                                                           if row["source_record_id"] == record.record_id])
                              for record in pull.selected_records)
    relation_entries_a = tuple(_entry("projected-relation", projection="placeholder-a", **row)
                               for row in relations)
    relation_entries_b = tuple(_entry("projected-relation", projection="placeholder-b", **row)
                               for row in reversed(relations))
    grouped = {}
    for row in relations:
        grouped.setdefault(row["symbol"], []).append(row["relation_id"])
    structure_entries_b = tuple(_entry("relation-group", symbol=symbol,
                                       relation_ids=ids) for symbol, ids in sorted(grouped.items()))

    drafts = (
        MapDraft("objects", "objects", "wordnet-objects", 1, PROBE_CONTEXT, (), object_entries),
        MapDraft("orders.source", "orders", "source-orders", 1, PROBE_CONTEXT, ("objects",), (
            _entry("order", order_name="archive-byte-order", object_ids=list(source_order),
                   positions=list(range(len(source_order)))),
            _entry("order", order_name="selection-score-order", object_ids=list(selection_order),
                   positions=list(range(len(selection_order))))),),
        MapDraft("structures.source", "structures", "source-structures", 1, PROBE_CONTEXT,
                 ("objects",), source_structures),
        MapDraft("processes.source", "processes", "source-pull-process", 1, PROBE_CONTEXT,
                 ("objects", "orders.source", "structures.source"), (
                     _entry("process", process_name="deterministic-wordnet-pull",
                            seed=pull.seed, archive_sha256=pull.archive_sha256,
                            limits=pull.limits.to_record()),)),
        MapDraft("grammar.a", "grammar", "grammar-placeholder-a", 1, PROBE_CONTEXT,
                 ("objects", "structures.source"), (
                     _entry("placeholder", status="TEST_ONLY_MECHANICAL_PROJECTION",
                            statement="category references without linguistic authority"),)),
        MapDraft("syntax.a", "syntax", "syntax-placeholder-a", 1, PROBE_CONTEXT,
                 ("objects", "orders.source", "structures.source"), (
                     _entry("placeholder", status="TEST_ONLY_MECHANICAL_PROJECTION",
                            statement="order and structure references without linguistic authority"),)),
        MapDraft("theory.a", "theory", "government-binding-placeholder-a", 1, PROBE_CONTEXT,
                 ("grammar.a", "syntax.a", "processes.source"), (
                     _entry("placeholder", status="TEST_ONLY_MECHANICAL_PROJECTION",
                            theory_label="Government-and-Binding-placeholder-a",
                            privileged=False),)),
        MapDraft("theory.b", "theory", "alternative-placeholder-b", 1, PROBE_CONTEXT,
                 ("grammar.a", "syntax.a", "processes.source"), (
                     _entry("placeholder", status="TEST_ONLY_MECHANICAL_PROJECTION",
                            theory_label="Alternative-placeholder-b", privileged=False),)),
        MapDraft("orders.relation-a", "orders", "relation-order-a", 1, PROBE_CONTEXT,
                 ("objects",), (_entry("order", order_name="pointer-source-order",
                                       relation_ids=list(relation_order_a),
                                       positions=list(range(len(relation_order_a)))),)),
        MapDraft("orders.relation-b", "orders", "relation-order-b", 1, PROBE_CONTEXT,
                 ("objects",), (_entry("order", order_name="reverse-symbol-target-order",
                                       relation_ids=list(relation_order_b),
                                       positions=list(range(len(relation_order_b)))),)),
        MapDraft("structures.relation-a", "structures", "relation-structure-a", 1,
                 PROBE_CONTEXT, ("objects", "structures.source"), source_structures),
        MapDraft("structures.relation-b", "structures", "relation-structure-b", 1,
                 PROBE_CONTEXT, ("objects", "structures.source"), structure_entries_b),
        MapDraft("relations.a", "relations", "relation-projection-a", 1, PROBE_CONTEXT,
                 ("objects", "theory.a", "orders.relation-a", "structures.relation-a"),
                 relation_entries_a),
        MapDraft("relations.b", "relations", "relation-projection-b", 1, PROBE_CONTEXT,
                 ("objects", "theory.b", "orders.relation-b", "structures.relation-b"),
                 relation_entries_b),
        MapDraft("adjective.a", "composed", "adjective-composed-a", 1, PROBE_CONTEXT,
                 ("objects", "grammar.a", "syntax.a", "theory.a", "relations.a",
                  "orders.relation-a", "structures.relation-a", "processes.source"), (
                     _entry("composition", role="adjective", projection="a",
                            relative=True, replaceable=True),)),
        MapDraft("adjective.b", "composed", "adjective-composed-b", 1, PROBE_CONTEXT,
                 ("objects", "grammar.a", "syntax.a", "theory.b", "relations.b",
                  "orders.relation-b", "structures.relation-b", "processes.source"), (
                     _entry("composition", role="adjective", projection="b",
                            relative=True, replaceable=True),)),
        MapDraft("context.a.v1", "context", "context-a", 1, "context-a",
                 ("adjective.a",), (_entry("selection", role="adjective",
                                           selected_input_index=0),)),
        MapDraft("context.b.v1", "context", "context-b", 1, "context-b",
                 ("adjective.a",), (_entry("selection", role="adjective",
                                           selected_input_index=0),)),
        MapDraft("replacement.ledger", "replacement-ledger", "replacement-ledger", 1,
                 PROBE_CONTEXT, ("adjective.a", "adjective.b", "context.a.v1"), (
                     _entry("replacement", prior_input_index=0, replacement_input_index=1,
                            context_input_index=2, relation="supersedes-in-context",
                            destructive=False),)),
        MapDraft("context.a.v2", "context", "context-a", 2, "context-a",
                 ("adjective.b", "context.a.v1", "replacement.ledger"), (
                     _entry("selection", role="adjective", selected_input_index=0),
                     _entry("context-predecessor", prior_context_input_index=1,
                            replacement_ledger_input_index=2))),
        MapDraft("derivation.ledger", "derivation-ledger", "derivation-ledger", 1,
                 PROBE_CONTEXT, ("processes.source", "theory.a", "theory.b", "relations.a",
                                 "relations.b", "adjective.a", "adjective.b", "context.a.v1",
                                 "context.a.v2", "context.b.v1", "replacement.ledger"), (
                     _entry("derivation", status="TEST_ONLY", input_roles=[
                         "source-process", "theory-a", "theory-b", "relations-a", "relations-b",
                         "adjective-a", "adjective-b", "context-a-v1", "context-a-v2",
                         "context-b-v1", "replacement-ledger"]),)),
    )
    store = RelativeMapStore()
    refs = store.publish_batch(drafts)
    resolution = {
        "context-a-v1": store.resolve_role(refs["context.a.v1"], "adjective").map_id,
        "context-a-v2": store.resolve_role(refs["context.a.v2"], "adjective").map_id,
        "context-b-v1": store.resolve_role(refs["context.b.v1"], "adjective").map_id,
    }
    require(resolution["context-a-v1"] == refs["adjective.a"].map_id,
            "INVARIANT_ERROR", "initial context A does not resolve projection A")
    require(resolution["context-a-v2"] == refs["adjective.b"].map_id,
            "INVARIANT_ERROR", "replacement context A does not resolve projection B")
    require(resolution["context-b-v1"] == refs["adjective.a"].map_id,
            "INVARIANT_ERROR", "context B changed when context A was replaced")
    require(refs["adjective.a"] != refs["adjective.b"], "INVARIANT_ERROR",
            "different theory/order/structure compositions must have different identity")
    result = ProbeResult(pull, MappingProxyType({key: ref.map_id for key, ref in refs.items()}),
                         relations, MappingProxyType(store.stats()),
                         MappingProxyType(resolution))
    return result, store
