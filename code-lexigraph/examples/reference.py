from enum import Enum
import json


class State(Enum):  # C01: local sentinel vocabulary
    READY = "ready"
    ERROR = "error"
    EXCEPTION = "exception"
    COMPLETE = "complete"


def decode_working_json(required_json):  # C02: JSON representation role
    return json.loads(required_json)


def make_report(state, required_json, response):  # C08: survivor exposure
    return {
        "state": state.value,
        "survivor": required_json,
        "response": response,
    }


def system_run(required_json, gate, operation):  # C03: system boundary
    try:
        if gate is State.ERROR:  # C04: mitigation before operation
            return make_report(State.ERROR, required_json, "operation skipped")
        if gate is not State.READY:
            raise ValueError("input gate must be READY or ERROR")
        working = decode_working_json(required_json)  # C05: independent tree
        operation(working)  # C06: mutable working reference
        return make_report(State.COMPLETE, required_json, "operation completed")
    except Exception as exc:  # C07: system-owned exception response
        return make_report(State.EXCEPTION, required_json, type(exc).__name__)
