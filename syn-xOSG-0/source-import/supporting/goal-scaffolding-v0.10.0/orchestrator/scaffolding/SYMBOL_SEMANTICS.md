# Symbol Semantics — Opaque Token Principle

**Component:** `SYM-001`
**Status:** production-active in v0.10.0; future material changes remain subject to PG-001.

## Principle
Surface tokens have no intrinsic authority or domain meaning.

```text
TOKEN_SPELLING != TOKEN_AUTHORITY
TOKEN_SPELLING != TOKEN_DOMAIN
TOKEN_SPELLING != TOKEN_DESCRIPTOR
```

Characters such as `->`, `::`, namespace strings such as `TES`, and identifiers such as `TES-518-3` are formal notation only until an Operator-controlled syntax profile or descriptor registry assigns a meaning.

`TES` may designate any Operator-selected namespace (including an ordinary fictional or project namespace). The Orchestrator MUST NOT infer a security, rule, privilege, or domain meaning from the token itself.

## Default symbolic envelope profile
The current staged profile defines:

- `->` as a relation/separator token;
- `::` as the payload delimiter;
- `simulated` as a mode label with `authority_effect = NONE`;
- `core-access` as a wrapper-profile selector, **not a privilege grant**.

Changing these bindings is an Operator design decision.
