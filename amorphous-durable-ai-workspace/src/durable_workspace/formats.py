"""Snapshot representation encoders/decoders."""
from __future__ import annotations

import base64
import json
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .canonical import dumps, loads, normalize


def bundle(records: dict[str, Any], events: list[dict[str, Any]], meta: dict[str, Any]) -> dict[str, Any]:
    return normalize({
        "meta": meta,
        "records": [{"key": k, "value": records[k]} for k in sorted(records)],
        "events": events,
    })


def write_jsonl(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(dumps({"kind": "meta", "value": data["meta"]}) + "\n")
        for row in data["records"]:
            f.write(dumps({"kind": "record", **row}) + "\n")
        for event in data["events"]:
            f.write(dumps({"kind": "event", "value": event}) + "\n")


def read_jsonl(path: Path) -> dict[str, Any]:
    meta = None
    records: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.endswith("\n"):
                raise ValueError(f"unterminated JSONL line {lineno}")
            row = loads(line)
            kind = row.get("kind")
            if kind == "meta" and meta is None:
                meta = row["value"]
            elif kind == "record":
                records.append({"key": row["key"], "value": row["value"]})
            elif kind == "event":
                events.append(row["value"])
            else:
                raise ValueError(f"unexpected JSONL row kind at line {lineno}")
    if meta is None:
        raise ValueError("JSONL snapshot missing meta row")
    return normalize({"meta": meta, "records": records, "events": events})


def _xml_value(parent: ET.Element, value: Any) -> None:
    if value is None:
        ET.SubElement(parent, "null")
    elif isinstance(value, bool):
        node = ET.SubElement(parent, "bool"); node.text = "true" if value else "false"
    elif isinstance(value, int) and not isinstance(value, bool):
        node = ET.SubElement(parent, "int"); node.text = str(value)
    elif isinstance(value, str):
        node = ET.SubElement(parent, "str", {"encoding": "base64-utf8"})
        node.text = base64.b64encode(value.encode("utf-8")).decode("ascii")
    elif isinstance(value, list):
        node = ET.SubElement(parent, "array")
        for item in value:
            child = ET.SubElement(node, "item"); _xml_value(child, item)
    elif isinstance(value, dict):
        node = ET.SubElement(parent, "object")
        for key in sorted(value):
            member = ET.SubElement(node, "member")
            key_node = ET.SubElement(member, "key", {"encoding": "base64-utf8"})
            key_node.text = base64.b64encode(key.encode("utf-8")).decode("ascii")
            value_node = ET.SubElement(member, "value")
            _xml_value(value_node, value[key])
    else:
        raise TypeError(type(value))


def _parse_xml_value(parent: ET.Element) -> Any:
    if len(parent) != 1:
        raise ValueError("typed XML value must contain exactly one type node")
    node = parent[0]
    if node.tag == "null": return None
    if node.tag == "bool":
        if node.text not in ("true", "false"): raise ValueError("invalid boolean")
        return node.text == "true"
    if node.tag == "int":
        if node.text is None or node.text == "":
            raise ValueError("XML integer text must be present")
        return int(node.text)
    if node.tag == "str":
        if node.attrib.get("encoding") != "base64-utf8": raise ValueError("unsupported XML string encoding")
        return base64.b64decode((node.text or "").encode("ascii"), validate=True).decode("utf-8")
    if node.tag == "array": return [_parse_xml_value(item) for item in node]
    if node.tag == "object":
        out = {}
        for member in node:
            if member.tag != "member": raise ValueError("invalid object member")
            key_node = member.find("key"); value_node = member.find("value")
            if key_node is None or value_node is None or key_node.attrib.get("encoding") != "base64-utf8":
                raise ValueError("invalid object member key/value")
            key = base64.b64decode((key_node.text or "").encode("ascii"), validate=True).decode("utf-8")
            out[key] = _parse_xml_value(value_node)
        return out
    raise ValueError(f"unknown XML value tag {node.tag}")


def write_xml(path: Path, data: dict[str, Any]) -> None:
    root = ET.Element("durable-workspace-snapshot", {"format": "DWSK-XML-1"})
    meta = ET.SubElement(root, "meta"); _xml_value(meta, data["meta"])
    records = ET.SubElement(root, "records")
    for row in data["records"]:
        rec = ET.SubElement(records, "record")
        key_node = ET.SubElement(rec, "key", {"encoding": "base64-utf8"})
        key_node.text = base64.b64encode(row["key"].encode("utf-8")).decode("ascii")
        value_node = ET.SubElement(rec, "value")
        _xml_value(value_node, row["value"])
    events = ET.SubElement(root, "events")
    for event in data["events"]:
        ev = ET.SubElement(events, "event"); _xml_value(ev, event)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def read_xml(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    if root.tag != "durable-workspace-snapshot" or root.attrib.get("format") != "DWSK-XML-1":
        raise ValueError("unexpected XML snapshot root/format")
    meta_node = root.find("meta"); records_node = root.find("records"); events_node = root.find("events")
    if meta_node is None or records_node is None or events_node is None:
        raise ValueError("XML snapshot missing required section")
    meta = _parse_xml_value(meta_node)
    records = []
    for rec in records_node:
        if rec.tag != "record": raise ValueError("invalid XML record")
        key_node = rec.find("key"); value_node = rec.find("value")
        if key_node is None or value_node is None or key_node.attrib.get("encoding") != "base64-utf8":
            raise ValueError("invalid XML record key/value")
        key = base64.b64decode((key_node.text or "").encode("ascii"), validate=True).decode("utf-8")
        records.append({"key": key, "value": _parse_xml_value(value_node)})
    events = [_parse_xml_value(ev) for ev in events_node]
    return normalize({"meta": meta, "records": records, "events": events})


def write_sqlite(path: Path, data: dict[str, Any]) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript("""
        PRAGMA journal_mode=DELETE;
        CREATE TABLE meta(key TEXT PRIMARY KEY, value_json TEXT NOT NULL);
        CREATE TABLE records(key TEXT PRIMARY KEY, value_json TEXT NOT NULL);
        CREATE TABLE events(seq INTEGER PRIMARY KEY, event_json TEXT NOT NULL);
        """)
        for key, value in data["meta"].items():
            conn.execute("INSERT INTO meta VALUES (?, ?)", (key, dumps(value)))
        for row in data["records"]:
            conn.execute("INSERT INTO records VALUES (?, ?)", (row["key"], dumps(row["value"])))
        for event in data["events"]:
            conn.execute("INSERT INTO events VALUES (?, ?)", (event["seq"], dumps(event)))
        conn.commit()
    finally:
        conn.close()


def read_sqlite(path: Path) -> dict[str, Any]:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        ok = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if ok != "ok": raise ValueError(f"SQLite integrity check failed: {ok}")
        meta = {k: loads(v) for k, v in conn.execute("SELECT key,value_json FROM meta ORDER BY key")}
        records = [{"key": k, "value": loads(v)} for k, v in conn.execute("SELECT key,value_json FROM records ORDER BY key")]
        events = [loads(v) for (v,) in conn.execute("SELECT event_json FROM events ORDER BY seq")]
        return normalize({"meta": meta, "records": records, "events": events})
    finally:
        conn.close()
