"""Behavioral model regression for production-active Zero-Flight semantics.

This is a local reference model; it does not independently grant authorization.
"""

ZERO_BASELINE = frozenset({"READ", "ANALYZE", "VALIDATE", "ATTEST", "SAFE_STAGE"})
UNDERLYING_LAYERS = frozenset({"SUB_ZERO", "ABSOLUTE_ZERO", "ZERO", "ZERO_SENTINEL"})

class FlightState:
    def __init__(self, admitted):
        admitted = frozenset(admitted)
        if not admitted <= ZERO_BASELINE:
            raise ValueError("flight scope exceeds Zero baseline")
        self.admitted = admitted

    def mutate(self, target_layer, new_admitted):
        if target_layer != "ZERO_FLIGHT":
            raise PermissionError("Zero-Flight cannot mutate another layer")
        new_admitted = frozenset(new_admitted)
        if not new_admitted <= ZERO_BASELINE:
            raise PermissionError("flight relaxation exceeds Zero baseline")
        self.admitted = new_admitted

s = FlightState({"READ", "ANALYZE"})
assert s.admitted < ZERO_BASELINE

s.mutate("ZERO_FLIGHT", {"READ"})
assert s.admitted == frozenset({"READ"})

s.mutate("ZERO_FLIGHT", {"READ", "ANALYZE", "VALIDATE"})
assert s.admitted == frozenset({"READ", "ANALYZE", "VALIDATE"})

s.mutate("ZERO_FLIGHT", ZERO_BASELINE)
assert s.admitted == ZERO_BASELINE

try:
    s.mutate("ZERO_FLIGHT", set(ZERO_BASELINE) | {"PRODUCTION"})
    raise AssertionError("expected beyond-baseline denial")
except PermissionError:
    pass

for target in UNDERLYING_LAYERS:
    try:
        s.mutate(target, {"READ"})
        raise AssertionError(f"expected target denial: {target}")
    except PermissionError:
        pass

print("checks = 7")
print("pass   = 7")
print("fail   = 0")
