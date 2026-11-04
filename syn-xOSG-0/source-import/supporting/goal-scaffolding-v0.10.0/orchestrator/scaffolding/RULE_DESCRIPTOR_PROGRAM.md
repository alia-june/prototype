# Rule Descriptor Program — RDP-001

**Purpose:** Deterministically resolve opaque references into bounded contextual descriptors without guessing from names.

## Resolution law

```text
reference token
  -> exact registry lookup
      -> FOUND: insert registered descriptor
      -> NOT FOUND: mark UNRESOLVED; do not invent
```

The program MUST NOT infer a descriptor from a namespace prefix, capitalization, punctuation, acronym, or apparent familiarity.

A reference such as `TES-518-3` is therefore just an opaque key unless the active registry contains an exact entry for `TES-518-3`.

## Descriptor record
Each admitted descriptor may contain:

```text
id
namespace
version
title
descriptor
source
status
sha256 (optional)
```

Descriptors supply context only. They do not grant rights, privileges, authority, agency, production status, or gate clearance.
