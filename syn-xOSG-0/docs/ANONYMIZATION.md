# Anonymization Policy

This repository publishes technical structure, not personal identity.

## Default publication rule

Publish:
- architecture;
- schemas;
- runtime code;
- tests and harnesses;
- validation reports;
- invariants;
- technical manifests;
- version/growth documentation.

Do not publish raw by default:
- personal memory;
- chat/prompt history;
- response logs;
- account metadata;
- email addresses;
- local usernames;
- hostnames;
- personal filesystem paths;
- opaque account/profile identifiers;
- access tokens, credentials, or secrets;
- incidental personal narrative not required to understand the system.

## Transformations

When encountered in publishable technical material:

```text
PERSONAL NAME        -> [PERSON]
EMAIL ADDRESS        -> [EMAIL]
ACCOUNT / PROFILE ID -> [ACCOUNT_ID]
LOCAL USERNAME       -> [USER]
HOSTNAME             -> [HOST]
PERSONAL HOME PATH   -> <LOCAL_PATH>
SECRET / TOKEN       -> [REDACTED]
```

Generic test strings such as `/etc/passwd`, `C:\\Windows\\System32`, or fictional shell/path payloads may remain when they are clearly test corpus data and contain no identifying information.

## Semantic preservation

Anonymization must not change:
- control semantics;
- invariants;
- version lineage;
- test expectations;
- failure classifications;
- code behavior, except where a personal path or identifier must be parameterized.

If redaction would change behavior, the file should be withheld and replaced by a technical summary until a behavior-preserving sanitized version exists.

## Provenance

Original uploaded archives remain source evidence outside the publicized/sanitized tree. Sanitized copies are derivative publication artifacts and should be labeled accordingly.
