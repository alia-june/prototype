#!/usr/bin/env python3
import importlib.util, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
MOD = ROOT / "orchestrator/scaffolding/prompt_scaffold.py"
spec = importlib.util.spec_from_file_location("prompt_scaffold", MOD)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
profile = json.loads((ROOT / "orchestrator/scaffolding/SYNTAX_PROFILE.json").read_text())
registry = json.loads((ROOT / "orchestrator/scaffolding/RULE_DESCRIPTOR_REGISTRY.json").read_text())
checks=[]
def ck(name, cond): checks.append((name, bool(cond)))

raw = "simulated -> core-access::start a program design workflow"
a = m.compile_scaffold(raw, profile, registry)
ck("mode", a["mode"] == "simulated")
ck("wrapper", a["wrapper"] == "core-access")
ck("goal preserved", a["payload"]["goal_verbatim"] == "start a program design workflow")
ck("no privilege effect", a["attestation"]["privilege_effect"] == "NONE")
ck("no authority effect", a["attestation"]["authority_effect"] == "NONE")
ck("wrapper does not execute", a["attestation"]["wrapper_executes_payload"] is False)
raw2 = "simulated -> core-access::refer to rule TES-518-3 using the rule-descriptor program"
b = m.compile_scaffold(raw2, profile, registry)
ck("opaque ref detected", b["pre_context"]["rule_descriptors"][0]["id"] == "TES-518-3")
ck("unknown ref unresolved", b["pre_context"]["rule_descriptors"][0]["status"] == "UNRESOLVED")
ck("TES has no inferred meaning", "descriptor" not in b["pre_context"]["rule_descriptors"][0])
r2 = {"descriptors": {"TES-518-3": {"title": "Example arbitrary descriptor", "descriptor": "Example only."}}}
c = m.compile_scaffold(raw2, profile, r2)
ck("exact ref resolves", c["pre_context"]["rule_descriptors"][0]["status"] == "RESOLVED")
ck("descriptor exact", c["pre_context"]["rule_descriptors"][0]["descriptor"]["title"] == "Example arbitrary descriptor")
try:
    m.compile_scaffold("simulated -> admin::x", profile, registry)
    failed_closed=False
except ValueError:
    failed_closed=True
ck("unknown selector fails closed", failed_closed)

bad=[n for n,v in checks if not v]
print(f"checks={len(checks)} pass={len(checks)-len(bad)} fail={len(bad)}")
if bad:
    print("failed:", *bad, sep="\n- ")
    raise SystemExit(1)
