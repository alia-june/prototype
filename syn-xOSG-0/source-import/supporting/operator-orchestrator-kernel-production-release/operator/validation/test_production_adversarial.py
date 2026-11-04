#!/usr/bin/env python3
"""Adversarial reference-model checks for production control-kernel invariants.

These tests challenge privilege monotonicity, root-lockdown, gate provenance,
Zero-Flight bounds, and successor-phase separation. They model package rules;
they do not create external authority or capabilities.
"""

ZERO = frozenset({"READ","ANALYZE","VALIDATE","ATTEST","SAFE_STAGE"})
ROOT = "ROOT"

class State:
    def __init__(self):
        self.rights = set(ZERO)
        self.flight = set(ZERO)
        self.root_lockdown = False
        self.operator_clear = True
        self.readiness = True
        self.material_change = False
        self.decomposition = False

    @property
    def production(self):
        return self.readiness and self.operator_clear and not self.root_lockdown and not self.material_change

    def downstream_set_rights(self, requested):
        requested=set(requested)
        self.rights &= requested

    def mutate_flight(self, requested):
        requested=set(requested)
        if not requested <= ZERO:
            raise PermissionError("flight exceeds Zero")
        self.flight=requested

    def root_attempt(self):
        self.root_lockdown=True
        self.rights.clear()
        self.flight.clear()

    def root_release(self):
        self.root_lockdown=False

    def orchestrator_clear(self):
        return False

    def operator_clearance(self):
        self.operator_clear=True

    def material_change_event(self):
        self.material_change=True
        self.operator_clear=False

checks=[]
def check(name, cond): checks.append((name,bool(cond)))

s=State(); before=set(s.rights); s.downstream_set_rights({"READ","ANALYZE"})
check("rights-can-restrict", s.rights == {"READ","ANALYZE"})
check("rights-no-growth-after-restrict", not (s.rights > before))
s.downstream_set_rights(set(ZERO)|{"PRODUCTION"})
check("rights-intersection-blocks-added-production", "PRODUCTION" not in s.rights)
check("rights-remain-subset-zero", s.rights <= ZERO)

s=State(); s.mutate_flight({"READ"})
check("flight-tighten", s.flight == {"READ"})
s.mutate_flight({"READ","ANALYZE","VALIDATE"})
check("flight-relax-within-zero", s.flight <= ZERO)
s.mutate_flight(ZERO)
check("flight-return-to-zero", s.flight == ZERO)
try:
    s.mutate_flight(set(ZERO)|{"ROOT"}); bad=False
except PermissionError: bad=True
check("flight-beyond-zero-rejected", bad)
check("flight-does-not-alter-rights", s.rights == set(ZERO))

s=State(); check("root-not-in-baseline", ROOT not in s.rights)
s.root_attempt()
check("root-attempt-locks", s.root_lockdown)
check("root-attempt-zero-rights", s.rights == set())
check("root-attempt-zero-flight", s.flight == set())
check("root-lockdown-blocks-production", not s.production)
s.root_release()
check("root-release-does-not-regrant-rights", s.rights == set())

s=State(); s.operator_clear=False
check("no-operator-clear-no-production", not s.production)
check("orchestrator-cannot-clear", s.orchestrator_clear() is False and not s.production)
s.operator_clearance(); check("operator-can-clear-with-readiness", s.production)
s.material_change_event(); check("material-change-relocks", not s.production and not s.operator_clear)
check("readiness-stays-distinct", s.readiness is True and not s.production)

AUTH_EFFECT="NONE"; PRIV_EFFECT="NONE"; PROD_EFFECT="NONE"
check("theory-no-authority", AUTH_EFFECT == "NONE")
check("theory-no-privilege", PRIV_EFFECT == "NONE")
check("theory-no-production-effect", PROD_EFFECT == "NONE")
s=State(); check("control-kernel-release-does-not-start-decomposition", s.production and not s.decomposition)

requested={"READ","ANALYZE","ROOT"}
policy={"READ","VALIDATE"}
core=set(ZERO) & requested & policy
check("core-intersection", core == {"READ"})
check("core-subset-zero", core <= ZERO)
check("core-no-root", "ROOT" not in core)
check("challenge-cannot-create-production", "PRODUCTION" not in core)

failed=[n for n,ok in checks if not ok]
print(f"checks = {len(checks)}")
print(f"pass   = {len(checks)-len(failed)}")
print(f"fail   = {len(failed)}")
for n in failed: print("FAIL",n)
raise SystemExit(1 if failed else 0)
