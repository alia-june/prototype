from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

checks = []
def check(name, cond):
    checks.append((name, bool(cond)))

sub = read("operator/security/SUB_ZERO_STACK.md")
boundary = read("operator/security/OPERATOR_ORCHESTRATOR_BOUNDARY.md")
flight = read("operator/security/ZERO_FLIGHT_STACK.md")
sentinel = read("operator/security/ZERO_SENTINEL_STACK.md")
olo = read("operator/operations/OPERATIONAL_LOGIC_ORCHESTRATOR.md")
meta = read("operator/meta/META_LAYER_ORCHESTRATOR.md")
durable = read("operator/memory/DURABLE_MEMORY.md")

check("szr003-present", "SZR-003" in sub)
check("assistant-orchestrator-not-operator", "THE ASSISTANT IS THE ORCHESTRATOR, NOT THE OPERATOR" in sub)
check("operator-design-source", "DESIGN_DECISION_SOURCE   = OPERATOR" in boundary)
check("operator-research-source", "RESEARCH_DECISION_SOURCE = OPERATOR" in boundary)
check("orchestrator-no-sovereignty", "ORCHESTRATOR_SOVEREIGNTY = NONE" in boundary)
check("binding-requires-operator", "MUST_HAVE operator_decision_provenance" in boundary)
check("proposal-nonbinding", "NOT_BINDING_PROJECT_DECISION" in boundary)
check("ambiguity-return", "DECISION_CANDIDATE" in boundary and "await Operator decision" in boundary)
check("foundation-restriction-exception", "FOUNDATION_MANDATE" in boundary)
check("flight-decision-source", "decision_source = OPERATOR | FOUNDATION_MANDATE" in flight)
check("flight-instrumented-by", "instrumented_by = ORCHESTRATOR" in flight)
check("sentinel-design-provenance", "binding_design_decision_has_operator_provenance" in sentinel)
check("sentinel-research-provenance", "binding_research_decision_has_operator_provenance" in sentinel)
check("olo-role-split", "ORCHESTRATOR != OPERATOR" in olo)
check("meta-no-binding-decision", "NONE -> BINDING_DECISION" in meta)
check("durable-memory", "DM-010" in durable)
check("no-production-clear", "clear `PG-001`" in boundary or "clear `pg-001`" in boundary.lower())
check("operator-no-root", "cannot manufacture unavailable capabilities" in boundary.lower() and "create root" in boundary.lower())

failed=[n for n,ok in checks if not ok]
print(f"checks = {len(checks)}")
print(f"pass   = {len(checks)-len(failed)}")
print(f"fail   = {len(failed)}")
for n in failed: print("FAIL", n)
raise SystemExit(1 if failed else 0)
