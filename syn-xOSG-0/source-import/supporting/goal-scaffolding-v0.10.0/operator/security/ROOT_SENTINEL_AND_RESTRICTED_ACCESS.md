# Root Sentinel and Restricted-Access Semantics

**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

## State model

Valid root-related states are deliberately asymmetric:

```text
NONEXISTENT
ROOT_ATTEMPT
ROOT_LOCKDOWN
```

There is no valid `ROOT_GRANTED` state.

## Transition model

```text
NONEXISTENT --root_attempt--> ROOT_LOCKDOWN
ROOT_LOCKDOWN --ordinary_input--> ROOT_LOCKDOWN + REJECT
ROOT_LOCKDOWN --root_release_valid--> NONEXISTENT
ROOT_LOCKDOWN --root_release_invalid--> ROOT_LOCKDOWN
```

A release restores only the policy baseline. It does not restore or manufacture elevated authority.

## Restricted-access model — Core Access

```text
ROOT_LIKE_RESTRICTED_ACCESS == CORE_ACCESS
```

`CORE_ACCESS` is not root and does not inherit root semantics. The prior internal name `CHALLENGE_SCOPED_RESTRICTED_ACCESS (CSRA)` is retained only as a deprecated compatibility alias.

Core Access may be admitted only through a scoped challenge-response test and remains bounded by the already-admitted Zero baseline:

```text
CORE_ACCESS_SCOPE ⊆ ZERO_BASELINE_CAPABILITY_SET
```

A challenge-response establishes eligibility for a bounded scope; it does not create underlying rights, privileges, authority, or agency.

When an existing Zero-Flight rule is more restrictive than the eligible Core Access scope, the live orchestrator may relax that **Zero-Flight restriction only**, and only until the resulting scope is still within `ZERO_BASELINE_CAPABILITY_SET`.

```text
CORE_ACCESS_AFTER_CHALLENGE ⊆ ZERO_BASELINE_CAPABILITY_SET
```

The challenge may never mutate Sub-Zero, Absolute-Zero, Zero, or Zero-Sentinel.

### Challenge-response constraints

A Core Access challenge-response test MUST:

1. establish only scoped eligibility;
2. never be interpreted as proof or grant of root;
3. never enlarge the immutable Zero baseline;
4. bind admitted scope and lifetime explicitly;
5. avoid storing reusable authentication secrets in prompt/response history;
6. fail closed on replay, mismatch, ambiguity, or unavailable verification;
7. remain subject to higher constraints, Zero-Sentinel, and `PG-001`.

A conversational challenge-response without an actual trusted authenticator is theoretical evidence only and cannot grant external privileges.
