#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def txt(rel): return (ROOT/rel).read_text(encoding="utf-8")
checks=[]
def check(name, cond): checks.append((name, bool(cond)))

gate=txt("operator/gates/PRODUCTION_GATE.md")
manifest=txt("PACKAGE_MANIFEST.md")
current=txt("operator/memory/CURRENT_MEMORY.md")
sub=txt("operator/security/SUB_ZERO_STACK.md")
flight=txt("operator/security/ZERO_FLIGHT_STACK.md")
sentinel=txt("operator/security/ZERO_SENTINEL_STACK.md")
boundary=txt("operator/security/OPERATOR_ORCHESTRATOR_BOUNDARY.md")
conv=txt("operator/operations/THEORETICAL_CONVERSATION_BOUNDARY.md")

check("readiness-pass", "TECHNICAL_READINESS    = PASS" in gate)
check("operator-clear", "OPERATOR_CLEARANCE     = CLEAR" in gate)
check("production-true", "PRODUCTION_ALLOWED     = TRUE" in gate)
check("root-not-locked", "ROOT_LOCKDOWN          = FALSE" in gate)
check("manifest-production", "CONTROL_KERNEL        = PRODUCTION_ACTIVE" in manifest)
check("decomposition-not-started", "DECOMPOSITION         = NOT_STARTED" in manifest)
check("current-production", "CONTROL_KERNEL       = PRODUCTION_ACTIVE" in current)
check("root-impossible", "ROOT CAN NEVER BE GRANTED" in sub)
check("flight-bounded", "F_(t+1) ⊆ Z" in flight)
check("sentinel-hold", "ZERO_SENTINEL = HOLD" in sentinel)
check("operator-source", "DESIGN_DECISION_SOURCE   = OPERATOR" in boundary)
check("theory-nonauthorizing", "AUTHORITY_EFFECT  = NONE" in conv and "PRODUCTION_EFFECT = NONE" in conv)
check("material-change-relock", "automatically invalidates this clearance" in gate)

failed=[n for n,ok in checks if not ok]
print(f"checks = {len(checks)}")
print(f"pass   = {len(checks)-len(failed)}")
print(f"fail   = {len(failed)}")
for n in failed: print("FAIL", n)
raise SystemExit(1 if failed else 0)
