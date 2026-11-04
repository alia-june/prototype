# v0.3 Evidence — Reconstruction Status

The exact historical v0.3 archive is not currently available in the supplied source set.

This directory therefore contains **reconstruction evidence**, not a recovered original binary.

## Documented developmental role

v0.3 is the deterministic hardening stage between the v0.2 actualized runtime and the v0.4 loose/fuzzy hardening stage.

Documented hardening targets include:

- state-transition validation;
- corruption handling;
- persistence consistency;
- transaction-journal recovery;
- runtime locking and bounded timeout;
- symlink refusal on protected paths;
- bounded task/history sizes;
- verification-state consistency;
- deterministic regression tests.

## Available reconstruction evidence

The consolidated v0.5 package contains a later reconstructed runtime and deterministic hardening suite that embodies these requirements. It is useful evidence of the intended v0.3 pressure and solutions, but must not be represented as the original historical v0.3 binary.

## Publication rule

Any code copied here from the consolidated package must be labeled:

```text
RECONSTRUCTION_EVIDENCE
SOURCE = xOSG-0_complete_chat_artifact_v0.5.0
NOT_ORIGINAL_V0.3_BINARY
```
