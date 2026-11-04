# Memory Model

The operator uses three explicit project-visible memory classes.

| Class | Purpose | Persistence | Authority |
|---|---|---|---|
| Current Memory | Active working state and immediate directives | Volatile / replaceable snapshot | Descriptive |
| Durable Memory | Long-lived user/project decisions and preferences | Persistent project ledger | User-originated or explicitly promoted |
| System Memory | Stable effective boundaries outside project authority | Persistent boundary register | External/higher authority |

## Flow

```text
CURRENT observation/decision
        ↓ candidate for retention
DURABLE MEMORY
        ↓ constrained by
SYSTEM MEMORY
```

No memory class silently authorizes production. Production remains governed by `gates/PRODUCTION_GATE.md`.
