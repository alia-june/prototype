from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEC = ROOT / "operator" / "security"

def read(name):
    return (SEC / name).read_text(encoding="utf-8")

checks = []
def check(name, cond):
    checks.append((name, bool(cond)))

composite = read("RULE_0_COMPOSITE_STACK.md")
subzero = read("SUB_ZERO_STACK.md")
absolute = read("ABSOLUTE_ZERO_STACK.md")
zero = read("ZERO_RULE_STACK.md")
flight = read("ZERO_FLIGHT_STACK.md")
sentinel = read("ZERO_SENTINEL_STACK.md")
root = read("ROOT_SENTINEL_AND_RESTRICTED_ACCESS.md")

check("order-subzero", "SUB_ZERO_STACK" in composite)
check("order-absolute", "ABSOLUTE_ZERO_STACK" in composite)
check("order-zero", "ZERO_STACK" in composite)
check("order-zero-flight", "ZERO_FLIGHT_STACK" in composite)
check("order-zero-sentinel", "ZERO_SENTINEL_STACK" in composite)
check("non-escalation-rights", "rights(T.after)" in subzero and "rights(T.before)" in subzero)
check("non-escalation-privileges", "privileges(T.after)" in subzero)
check("no-downstream-weaken-foundation", "no rule after `szr-001` may weaken" in subzero.lower())
check("root-does-not-exist", "ROOT DOES NOT EXIST" in subzero)
check("root-never-granted", "ROOT CAN NEVER BE GRANTED" in subzero)
check("root-no-privileges", "ROOT GRANTS NO PRIVILEGES" in subzero)
check("root-attempt-lockdown", "ROOT_ATTEMPT" in subzero and "ROOT_LOCKDOWN" in subzero)
check("lock-production", "production_locked = TRUE" in subzero)
check("zero-rights", "operational_rights = ∅" in subzero)
check("zero-privileges", "operational_privileges = ∅" in subzero)
check("zero-agency", "operational_agency = NONE" in subzero)
check("only-root-release", "{ ROOT_RELEASE }" in subzero)
check("release-no-root", "does not grant root" in subzero.lower())
check("release-no-production-clear", "PG_001" in subzero or "PG-001" in subzero)
check("core-alias", "ROOT_LIKE_RESTRICTED_ACCESS == CORE_ACCESS" in root)
check("core-subset", "CORE_ACCESS_SCOPE ⊆ ZERO_BASELINE_CAPABILITY_SET" in root)
check("challenge-not-authority", "does not create underlying rights" in root.lower())
check("challenge-no-secrets-history", "avoid storing reusable authentication secrets" in root.lower())
check("absolute-preserves-szr1", "candidate_preserves_SZR_001" in absolute)
check("absolute-preserves-szr2", "candidate_preserves_SZR_002" in absolute)
check("absolute-unknown-deny", "If any term is false or unknown" in absolute)
check("zero-baseline", "ZERO_FLIGHT_CURRENT_SCOPE ⊆ ZERO_BASELINE_CAPABILITY_SET" in zero)
check("flight-live", "LIVE PRODUCTION CONTROL ORCHESTRATION" in flight)
check("flight-only-mutation", "ZERO_FLIGHT may mutate ZERO_FLIGHT rules only" in composite)
check("flight-bounded", "F_(t+1) ⊆ Z" in flight)
check("flight-can-relax", "F_t ⊆ F_(t+1) ⊆ Z" in flight)
check("flight-no-foundation", "MUTATE_UNDERLYING_STACK" in flight)
check("flight-no-sentinel", "MUTATE_ZERO_SENTINEL" in flight)
check("sentinel-hold", "ZERO_SENTINEL = HOLD" in sentinel)
check("sentinel-no-production", "production_effect = NONE" in sentinel)
check("sentinel-root-release-only", "input != ROOT_RELEASE" in sentinel)
check("sentinel-flight-immutable", "ZERO_FLIGHT_MUTATION_TARGET == ZERO_SENTINEL" in sentinel)
check("no-root-granted-state", "There is no valid `ROOT_GRANTED` state" in root)

failed = [name for name, ok in checks if not ok]
print(f"checks = {len(checks)}")
print(f"pass   = {len(checks)-len(failed)}")
print(f"fail   = {len(failed)}")
for name in failed:
    print("FAIL", name)
raise SystemExit(1 if failed else 0)
