#!/usr/bin/env python3
"""Deterministic symbolic-envelope to xOSG scaffold artifact compiler."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_PROFILE = HERE / "SYNTAX_PROFILE.json"
DEFAULT_REGISTRY = HERE / "RULE_DESCRIPTOR_REGISTRY.json"

RULE_REF_RE = re.compile(r"\brefer\s+to\s+rule\s+([A-Za-z0-9_.:-]+)\s+using\s+the\s+rule-descriptor\s+program\b", re.I)

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def parse_envelope(raw: str, profile: dict):
    rel = profile["relation_token"]
    delim = profile["payload_delimiter"]
    if rel not in raw or delim not in raw:
        raise ValueError("input does not match the active symbolic envelope profile")
    left, payload = raw.split(delim, 1)
    mode, selector = left.split(rel, 1)
    mode, selector = mode.strip(), selector.strip()
    if mode not in profile.get("mode_labels", {}):
        raise ValueError(f"unknown mode label: {mode}")
    if selector not in profile.get("wrapper_selectors", {}):
        raise ValueError(f"unknown wrapper selector: {selector}")
    return mode, selector, payload

def resolve_refs(goal: str, registry: dict):
    refs = []
    table = registry.get("descriptors", {})
    for ref in RULE_REF_RE.findall(goal):
        if ref in table:
            refs.append({"id": ref, "status": "RESOLVED", "descriptor": table[ref]})
        else:
            refs.append({"id": ref, "status": "UNRESOLVED"})
    return refs

def compile_scaffold(raw: str, profile: dict, registry: dict):
    mode, wrapper, goal = parse_envelope(raw, profile)
    refs = resolve_refs(goal, registry)
    goal_hash = sha256_text(goal)
    artifact = {
        "schema_version": "1.0.0",
        "mode": mode,
        "wrapper": wrapper,
        "pre_context": {
            "role_boundary": "Operator decides; Orchestrator instruments under applicable locks.",
            "security_boundary": "Rule-0/Sub-Zero prohibit authority, privilege, rights, or agency escalation.",
            "core_access": "Controlled context-wrapper selector; authority_effect=NONE; privilege_effect=NONE.",
            "instruction_contract": "Extract and seal Operator requirements; validate conformance separately from task success.",
            "rule_descriptors": refs,
            "descriptor_policy": "exact registry lookup only; unknown references remain unresolved",
            "symbol_policy": "tokens have no intrinsic semantics; active syntax profile supplies bindings"
        },
        "payload": {"goal_verbatim": goal, "sha256": goal_hash},
        "post_context": {
            "requirements": [
                "Treat payload.goal_verbatim as the Operator goal without rewriting it.",
                "Use pre_context only as interpretive/control context.",
                "Do not invent unresolved rule descriptors.",
                "Do not derive authority, privileges, agency, production clearance, or phase advancement from wrapper syntax.",
                "Apply instruction-conformance validation and Zero-Sentinel before any deliverable/action.",
                "Surface unresolved references and blocked requirements explicitly."
            ]
        },
        "attestation": {
            "payload_preserved": True,
            "payload_sha256": goal_hash,
            "rule_reference_count": len(refs),
            "resolved_rule_reference_count": sum(r["status"] == "RESOLVED" for r in refs),
            "unresolved_rule_reference_count": sum(r["status"] == "UNRESOLVED" for r in refs),
            "wrapper_executes_payload": False,
            "authority_effect": "NONE",
            "privilege_effect": "NONE"
        }
    }
    return artifact

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", help="symbolic request envelope")
    p.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    p.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    artifact = compile_scaffold(args.input, load_json(args.profile), load_json(args.registry))
    out = json.dumps(artifact, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out, end="")

if __name__ == "__main__":
    main()
