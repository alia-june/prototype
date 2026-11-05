"""Normative DWSK-CJ-1 canonical JSON profile.

Profile rules:
- UTF-8 output, no BOM.
- Unicode strings and object keys are NFC-normalized.
- Object keys are strings and sorted lexicographically after NFC normalization.
- Duplicate keys introduced by normalization are rejected.
- Arrays preserve order.
- null, booleans, strings, and signed 64-bit integers are allowed.
- Floating-point values are rejected. Encode non-integral numeric values as strings
  using an application-defined decimal profile if they must be durable across languages.
- No insignificant whitespace.
"""
from __future__ import annotations

import hashlib
import json
import unicodedata
from typing import Any

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1

class CanonicalizationError(ValueError):
    pass


def normalize(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        if not (INT64_MIN <= value <= INT64_MAX):
            raise CanonicalizationError("integer outside signed 64-bit domain")
        return value
    if isinstance(value, float):
        raise CanonicalizationError("floating-point values are not permitted by DWSK-CJ-1")
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [normalize(v) for v in value]
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError("object keys must be strings")
            nkey = unicodedata.normalize("NFC", key)
            if nkey in out:
                raise CanonicalizationError("duplicate object key after NFC normalization")
            out[nkey] = normalize(item)
        return {key: out[key] for key in sorted(out)}
    raise CanonicalizationError(f"unsupported canonical type: {type(value).__name__}")


def dumps(value: Any) -> str:
    return json.dumps(
        normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def bytes_(value: Any) -> bytes:
    return dumps(value).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(bytes_(value)).hexdigest()


def loads(text: str) -> Any:
    # parse_int=int is exact; reject floats at parse time for the canonical profile.
    def reject_float(_: str):
        raise CanonicalizationError("floating-point values are not permitted by DWSK-CJ-1")
    return normalize(json.loads(text, parse_float=reject_float))
