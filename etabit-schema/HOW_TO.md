# How to review an Etabit descriptor

Use the v0.2 example to check what the Etabit draft can describe and what its offline validator can reject. This exercise does not mount a drive, run a constructor, or grant access to metadata.

## Start with the matching files

1. Read the [architecture guide](ARCHITECTURE.md) for source and referential drive roles, constructor-scoped metadata, and the unresolved reader and authority boundaries.
2. Open the [v0.2 schema](schema/etabit-project.v0.2.schema.json) and the [v0.2 four-symbol example](examples/four-symbol-source.v0.2.json) together. The earlier v0.1 descriptor is a separate record; do not mix the versions in this check.
3. In the example, follow a reference from its source drive ID to the destination drive and object ID. Also inspect how codepages name referential drives and how the descriptor keeps stored symbols separate from operational result states.

Use a checked-out revision for a repeatable review. The schema's `$id` points to a moving branch and is not a substitute for a commit or release identifier.

## Run the existing offline checks

From `etabit-schema/`, with Python and `jsonschema` already available, run:

```sh
python -B tests/test_v0_2.py
```

If `jsonschema` is missing, the check cannot start. See the [README's dependency and validation instructions](README.md#validation-and-how-to-run-it) for preparation. Do not treat an import error as a result about the descriptor.

The [test program](tests/test_v0_2.py) validates the supplied example, checks selected local graph relationships, and changes copies of the example to exercise negative cases. It does not edit the tracked example. Its expected success marker is `ETABIT_SCHEMA_V0_2_TESTS=PASS (draft shape + local reference tests only)`.

| Check | Example | What to conclude |
| --- | --- | --- |
| Descriptor shape | The supplied v0.2 example satisfies the v0.2 schema. | The document meets those declared constraints. |
| Local graph checks | An unknown target drive or a codepage referencing a nonreferential drive is flagged. | The additional checker catches those local relationship errors. JSON Schema alone does not perform all these checks. |
| Forbidden settings | The tests reject runtime activation, reader metadata access, automatic disclosure, and codepage execution permission. | The draft descriptor refuses those settings; a real process is not being constrained by this test. |
| Non-normative ordering | Reversing the five Cypher responsibilities remains valid. | Array order does not establish authority or precedence. |

Record the revision, whether the validator ran, and any failure message separately. The [audit reconciliation](docs/V0_2_AUDIT_RECONCILIATION.md) explains why successful descriptor checks do not establish constructor behavior, reader isolation, live storage, or admission of the draft.
