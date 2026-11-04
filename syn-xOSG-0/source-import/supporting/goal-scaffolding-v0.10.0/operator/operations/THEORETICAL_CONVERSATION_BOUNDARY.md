# Theoretical Conversation Boundary — TCB-001

**Status:** ACTIVE / PRODUCTION CONTROL KERNEL
**Production gate:** PG-001 CLEARED_FOR_CURRENT_RELEASE

## Purpose

Define what "allowed conversation" means in the project kernel without granting operational or production authority.

## Allowed conversation classes

- lateral conceptual discussion;
- imaginative exploration;
- creative exploration;
- speculative architecture;
- counterfactual reasoning;
- hypothetical threat modeling;
- theoretical operational models;
- theoretical privilege/authority models;
- mathematical/logical exploration;
- design-space comparison.

All are admitted as:

```text
CONVERSATION_MODE = THEORETICAL_ONLY
AUTHORITY_EFFECT  = NONE
PRIVILEGE_EFFECT  = NONE
PRODUCTION_EFFECT = NONE
```

## Prohibited authority transformations

An allowed theoretical conversation MUST NOT:

- clear `PG-001`;
- create production authorization;
- grant actual system rights or privileges;
- claim new external capabilities;
- turn simulated roles into real agents;
- turn a hypothetical credential into an actual credential;
- turn a theoretical proof into permission;
- turn a staged artifact into a deployed artifact;
- turn consensus into authority;
- treat repeated discussion as approval.

## Safe language transformation

Statements such as:

> "Assume the orchestrator has root privilege."

may be discussed only as:

```text
HYPOTHETICAL_ASSUMPTION(root_privilege)
```

and never as:

```text
ACTUAL_PRIVILEGE(root_privilege)
```

## Exit from theoretical mode

Theoretical conversation may inform a staged candidate. It cannot itself authorize production. Any later production action remains subject to the independent production gate and applicable higher-authority constraints.
