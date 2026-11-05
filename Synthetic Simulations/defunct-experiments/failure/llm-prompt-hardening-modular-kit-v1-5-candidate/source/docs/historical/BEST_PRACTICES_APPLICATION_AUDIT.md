> **FABRICATION FLAG — GENERATED AUDIT**

# Candidate 1.5 Best-Practices Application Audit

## Scope and authority

Candidate 1.5 is a preserved child of candidate 1.4. The user instructed `Apply best practices`, then added `allow for lock unlock through encrypted secret`. The candidate applies the preserved online validation report and separately validated security constraints. It does not rewrite or promote candidate 1.4.

## Control mapping

| Validated recommendation or user requirement | Implementation | Mechanical/static evidence | Remaining external dependency |
|---|---|---|---|
| Routine screening must not become routine age collection | Module 14 output-only Stage 1; module 15 `no-collection-screen` | Default data policy and retention; inconsistent retention rejected | Runtime behavior evaluation |
| Keep the three axes independent | Module 14 retains emotional, intellectual, and physical age without a composite | Structural tests and behavioral vectors | Representative model testing |
| Minimize and scope any necessary data | Module 15 purpose, minimum field, scope, expiry, access, deletion, correction, prohibited reuse | Template and module assertions | Actual data store and deletion controls |
| Separate response and audit data | Module 15 audit-plane minimization | Static content tests | Logging architecture and access enforcement |
| Provide human review, correction, and appeal for consequential use | Module 15 review triggers and appeal record | Pilot/production configurations reject unavailable review or unspecified appeal | Staff, service levels, and user-visible process |
| Require impact assessment and operational assurance | Module 15 development/pilot/production admission | Mode/assurance consistency enforced | Accepted CRIA/DPIA/legal/accessibility records |
| Evaluate and monitor separate harms | Module 15 disaggregated measures and no composite safety score | Static content and behavioral vectors | Thresholds, datasets, evaluators, monitoring service |
| Contain incidents and revalidate changes | Module 15 incident, rollback, and change control | Pilot/production require configured-and-tested states | Exercised procedures and accountable owners |
| Lock/unlock through encrypted secret | Module 16 external authenticated-encryption envelope and single-use receipt | Default locked state; plaintext secret variable rejected; exact SHA-256 binding checked | KMS/HSM, validator, trusted time, replay store, authenticated channel |
| Unlock must not become a bypass | Modules 15 and 16 keep authorization, privacy, review, and evidence gates independent | Scope/configuration binding and explicit non-bypass rules | End-to-end authorization test |
| Do not overclaim validation | Assurance boundaries in modules 14–16 and validation record | Required wording tests | Production studies and independent review |

## Encrypted-secret design decision

The package does not implement cryptography inside prompt text or invent a custom cipher. The external control plane authenticates and decrypts an envelope under organizational cryptographic policy. It emits a sanitized, integrity-protected, short-lived receipt. The assembler checks that the receipt metadata declares the verified external plane, is unconsumed, and matches the deterministic SHA-256 of the exact non-secret assembly configuration.

The lock blocks triggered data collection, material restriction, and consequential age-gate action. It does not block output-only screening or universally safe answers. Unlock permits only the named branch; it does not disable other controls. Use, expiry, revocation, configuration change, error, incident, or channel loss relocks the branch.

## Disposition

**IMPLEMENTED AS A FAIL-CLOSED CANDIDATE CONTRACT; NOT PRODUCTION-VALIDATED.**

Candidate 1.5 can expose inconsistent declarations and safely define integration boundaries. It cannot prove actual human-review availability, assessment completion, operational monitoring, cryptographic key custody, trusted time, atomic replay prevention, or deployed-model behavior.
