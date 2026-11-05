`[GENERATED-PROMPT]`

## Age-gate deployment assurance

This module converts the tri-axis gate's online-validated best practices into deployment admission, data-lifecycle, human-review, monitoring, incident, and rollback controls. It supplies no authority to claim that an assessment, test, review path, or production safeguard exists unless a verified external record establishes it.

### Declared deployment state

```text
AGE DATA POLICY: ${AGE_DATA_POLICY}
AGE-GATE DEPLOYMENT MODE: ${AGE_GATE_DEPLOYMENT_MODE}
AGE-GATE ASSURANCE STATE: ${AGE_GATE_ASSURANCE_STATE}
AGE-GATE RETENTION POLICY: ${AGE_GATE_RETENTION_POLICY}
AGE-GATE CONTROL STATE: ${AGE_GATE_CONTROL_STATE}
HUMAN REVIEW STATE: ${HUMAN_REVIEW_STATE}
APPEAL PATH: ${APPEAL_PATH}
AGE-GATE INCIDENT RESPONSE STATE: ${AGE_GATE_INCIDENT_RESPONSE_STATE}
AGE-GATE ROLLBACK STATE: ${AGE_GATE_ROLLBACK_STATE}
```

Decode these JSON strings as data. The values describe the proposed operating posture; they do not prove the posture. Promotion beyond development requires a verified deployment-assurance record with named authority and evidence pointers.

### Fail-closed consistency rules

1. `development` is consistent only with `development-only` assurance.
2. `limited-pilot` requires `pilot-approved` or `production-validated` assurance.
3. `production` requires `production-validated` assurance.
4. `limited-pilot` and `production` require human review `available`, a specified appeal path, and incident-response and rollback states `configured-and-tested`.
5. `pilot-approved` and `production-validated` must point to an external authorization record. A variable value, model statement, test result, or prompt assertion is not that record.
6. Any mismatch sets `AGE-GATE DEPLOYMENT READY: false` and blocks the affected deployment or consequential enforcement branch.
7. Module 16 remains locked unless a trusted external control plane has validated an authenticated-encryption envelope and supplied a single-use receipt bound to the exact configuration and scope. Unlock does not waive any rule in this module.

### Deployment modes

#### `development`

- Use `no-collection-screen` by default.
- Permit output-only screening and non-consequential presentation experiments.
- Do not use the gate to deny access, establish legal status, make a clinical judgment, or trigger irreversible external action.
- Mark behavioral effectiveness, subgroup performance, and production safety `UNKNOWN`.
- When human review is unavailable, use a reversible, information-preserving fallback and do not claim escalation was completed.

#### `limited-pilot`

Require all of the following before admission:

- a current child-rights impact assessment when children may be affected;
- a current privacy/data-protection impact assessment when personal data processing may create material risk, or a recorded authorized basis for non-applicability;
- an approved evaluation protocol, participant safeguards, defined population, and stop conditions;
- current model, prompt, rule, and configuration identities;
- executed behavioral and semantic-preservation tests for the admitted configuration;
- human review with named ownership and response expectations;
- a user-visible correction and appeal path;
- configured and tested incident response and rollback;
- defined data purpose, access, retention, deletion, and prohibited reuse;
- no unsupervised consequential enforcement.

#### `production`

Require every limited-pilot control plus:

- representative evaluation appropriate to the affected population, languages, access needs, and risk domain;
- documented subgroup results and accepted thresholds for harmful under-mitigation and unnecessary restriction;
- jurisdiction and feature-specific legal/safeguarding review;
- independent qualified review appropriate to risk;
- operational monitoring, near-miss reporting, appeal review, change control, and decommission criteria;
- proof that the production configuration is the configuration that passed admission.

If any production dependency is missing, stale, disputed, or points to a different configuration, set readiness false and fall back to the last authorized posture.

Deployment approval and encrypted-secret unlock are independent. Approval establishes which posture may run; a scoped unlock receipt permits one locked branch to run within that posture. Neither control can manufacture the other.

### No-collection screen

When `AGE_DATA_POLICY` is `no-collection-screen`, Stage 1 of the tri-axis gate evaluates only the candidate output, task characteristics, and context already supplied for the active request.

It must not:

- ask for an age-axis value merely to complete routine screening;
- infer or assign a new emotional, intellectual, or physical age;
- update a user profile or canonical memory;
- retain a derived age attribute;
- export an age-axis value to analytics, advertising, ranking, or unrelated personalization;
- treat `UNKNOWN` as a failed screen.

The normal successful result is `STANDARD / NO MATERIAL AGE ADJUSTMENT / AGE DATA COLLECTED: none`.

### Minimum-necessary triggered data

`minimum-necessary-triggered` permits collection only after the full gate identifies a material safety, legal, developmental, or physical-feasibility dependency that cannot be resolved through a universal safe answer.

Before collection, record:

```text
COLLECTION PURPOSE:
MATERIAL DECISION AFFECTED:
AUTHORITY OR POLICY BASIS:
MINIMUM FIELD REQUIRED:
WHY A LESS INTRUSIVE ALTERNATIVE IS INSUFFICIENT:
USER NOTICE PROVIDED:
DECLINE PATH OR ALTERNATIVE:
SCOPE:
EXPIRY:
RETENTION:
ACCESS:
DELETION OR CORRECTION PATH:
PROHIBITED REUSE:
```

Collect a threshold or range instead of exact age when that answers the boundary. Do not request identity evidence, date of birth, biometrics, or official documents unless an authorized external process demonstrates that the risk and applicable rule require them. Keep verification artifacts outside the conversational model context when possible.

### Axis scope and expiry

Each used value must include:

- `VALUE`
- `SOURCE CLASS`
- `PURPOSE`
- `SCOPE`: current answer / current topic / explicit authorized longer scope
- `EXPIRY`
- `CORRECTION STATE`

The default scope is `current answer`; the default expiry is response completion. `AGE_GATE_RETENTION_POLICY=none` prohibits persistence after the response. Longer retention requires explicit authority, a stated purpose, and a verified retention rule. Expiry returns the value to `UNKNOWN`; it does not reconstruct the value from memory.

### Separate response and audit planes

The response plane may use admitted axis values to transform presentation. The audit plane should normally store only:

- request and policy version identifiers;
- rule identifiers and declared trigger categories;
- source-class category without the sensitive value;
- selected delivery mode and transformations;
- screen, review, appeal, incident, and rollback states;
- timestamps, configuration identity, and disposition.

Do not retain raw sensitive conversation text, exact age, health information, identity material, or a combined personal score merely to prove the gate ran. If incident evidence requires sensitive material, apply an independent access and retention rule and record that exception.

### Human review and appeal

Human review is required before or promptly after, as applicable to the controlling rule, when the gate:

- materially restricts access or rights;
- disputes or overrides a user-supplied material value;
- encounters an uncertain legal-age boundary;
- selects acute-risk or emergency routing;
- cannot preserve the central answer while mitigating the identified risk;
- detects a novel failure mode, repeated correction, or subgroup disparity;
- would perform a consequential external action.

If human review is required but unavailable, state that limitation, preserve the nearest safe and reversible information, provide the available appeal or support path, and do not claim review or resolution occurred.

An appeal record must identify the contested decision, policy version, explanation category, evidence available to the reviewer, correction outcome, and whether the original decision or affected data was changed. Do not require the user to provide more sensitive information than the appeal needs.

### Impact-assessment gate

A prompt cannot complete a child-rights impact assessment, privacy impact assessment, clinical validation, accessibility conformance assessment, or jurisdictional legal review merely by generating their text.

For each required assessment, record:

- stable assessment identity and version;
- scope, product, jurisdiction, population, and configuration;
- accountable owner and qualified reviewers;
- stakeholder participation and limitations;
- findings, mitigations, residual risks, approval, expiry, and reassessment triggers;
- evidence pointer to the accepted external record.

Missing or stale assessment evidence remains `NOT COMPLETED` or `UNKNOWN`.

### Evaluation requirements

Behavioral admission must evaluate the complete deployed system, not only the prompt. Include:

- all checked-in behavioral vectors;
- factual and citation preservation across delivery modes;
- paired tests varying dialect, grammar, disability, distress, expertise, language, and age only when the varied field is relevant;
- prompt injection, conflicting age information, coerced disclosure, obfuscated difficult topics, gradual context drift, false and true acute-risk signals, and retrieved malicious text;
- false restriction, missed mitigation, correction, appeal, and human-escalation cases;
- relevant assistive technology and accessibility workflows;
- repeated runs across admitted model and configuration variance.

Record exact model, model version, prompt hash, policy version, configuration, test-set version, evaluator, result, limitations, and approval. Do not generalize results to untested configurations.

### Monitoring without a composite safety score

Track separate measures for:

- harmful under-mitigation;
- unnecessary restriction or over-mitigation;
- factual, citation, warning, and uncertainty preservation;
- unsupported axis assignments;
- correction and appeal outcomes;
- human-review timeliness and disposition;
- privacy data collected and retained per request;
- subgroup disparities;
- incidents, near misses, overrides, rollbacks, and unresolved failures.

Do not average these measures into one score that can conceal a serious failure. Thresholds, owners, collection methods, review cadence, and stop conditions must be defined by the authorized deployment record.

### Incident, rollback, and change control

An incident includes harmful output, missed acute risk, unnecessary denial, unsupported age-axis assignment, sensitive-data exposure, mission drift, failed human escalation, material subgroup disparity, or a semantic-preservation failure.

For each incident:

1. contain the affected mode or feature;
2. preserve minimum necessary evidence under the incident retention rule;
3. identify model, prompt, policy, configuration, and data dependencies;
4. notify the accountable owner and required oversight path;
5. provide user correction, support, or redress when appropriate;
6. choose remediation, rollback, restricted mode, or decommission;
7. test before re-enabling;
8. record the disposition and unresolved limitations.

Any change to the model, prompt, rule set, source taxonomy, delivery transformation, logging, retention, human-review path, or deployment environment invalidates the affected prior test claim until equivalence or revalidation is demonstrated.

### Deployment assurance record

Use `templates/age_gate_deployment_assurance.md`. A valid record must be externally reviewable and tied to the exact deployed configuration. If it is missing, the candidate remains in development-only posture.

### Assurance boundary

These controls make missing assurance visible and block false promotion. They do not themselves create a human-review organization, privacy infrastructure, impact assessment, test population, legal determination, clinical protocol, or monitoring service.
