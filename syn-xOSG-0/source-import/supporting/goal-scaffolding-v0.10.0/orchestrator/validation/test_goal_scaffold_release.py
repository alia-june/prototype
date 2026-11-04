#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
checks=[]
def ck(n,v): checks.append((n,bool(v)))
def txt(rel): return (ROOT/rel).read_text(encoding="utf-8")
manifest=txt("PACKAGE_MANIFEST.md")
gate=txt("operator/gates/PRODUCTION_GATE.md")
current=txt("operator/memory/CURRENT_MEMORY.md")
release=txt("orchestrator/releases/GOAL_SCAFFOLD_RELEASE.md")
profile=json.loads((ROOT/"orchestrator/scaffolding/SYNTAX_PROFILE.json").read_text())
ck("release-version", "0.10.0" in manifest)
ck("production-active", "State:** PRODUCTION ACTIVE" in manifest)
ck("operator-clearance-recorded", "unlock production and emmit" in gate)
ck("final-gate-relocked", "GATE_STATE             = LOCKED_POST_RELEASE" in gate)
ck("future-promotion-blocked", "NEW_PROMOTION_ALLOWED  = FALSE" in gate)
ck("scaffold-production-active", all(x in current for x in ["GSP-001                    = PRODUCTION_ACTIVE","CAW-001                    = PRODUCTION_ACTIVE","RDP-001                    = PRODUCTION_ACTIVE","SYM-001                    = PRODUCTION_ACTIVE"]))
ck("release-no-privilege", "CORE_ACCESS != PRIVILEGE" in release)
ck("payload-preservation", "PAYLOAD_AFTER == PAYLOAD_BEFORE" in release)
ck("unknown-unresolved", "UNKNOWN_DESCRIPTOR -> UNRESOLVED" in release)
ck("core-access-profile", "core-access" in json.dumps(profile))
ck("decomposition-not-started", "Decomposition:** NOT STARTED" in manifest)
failed=[n for n,v in checks if not v]
print(f"checks={len(checks)} pass={len(checks)-len(failed)} fail={len(failed)}")
if failed:
    print("failed:",*failed,sep="\n- ")
    raise SystemExit(1)
