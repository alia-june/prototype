# Harness findings and replay cases

Date: 2026-10-29. Product tested: docstream-cpu 0.2.0.dev4.

The harness is delivered; its combined product result is **FAILED**. The rigid
checks pass and the bounded torture scenarios pass. The 500-case fuzzy run has
24 failed cases in three reproducible groups. These are 24 cases, not 24
independent defects. Product code and pass criteria were left unchanged.

| ID | Failed fuzzy cases | Classification | Observed behavior |
| --- | ---: | --- | --- |
| HF-01 | 5 | Open conversion-policy/fidelity finding | A carriage return becomes a line feed after a successful DOCX export/reimport; no conversion-loss diagnostic |
| HF-02 | 10 | Confirmed format error-handling defect | NUL text enters the semantic model but DOCX export raises a raw adapter exception; the service returns generic INTERNAL_ERROR |
| HF-03 | 9 | Confirmed direct ingestion error-handling defect | A dictionary request containing an unpaired surrogate raises UnicodeEncodeError before typed validation can reject it |

## HF-01 carriage return conversion

The reduced case contains one paragraph/span whose only text is `\r`.
The round-trip value is `\n`. The export and reimport both succeed without
diagnostics. The old source stream remains intact; this is a difference in the
newly converted representation, not observed rewriting of stored history.

This is deliberately retained as an unresolved policy finding. The document
library documents that newlines and carriage returns become Word line breaks,
and that line breaks read back as newline characters. That explains the
observed mapping; it does not independently decide Docstream's source-fidelity
policy. See the [python-docx text API](https://python-docx.readthedocs.io/en/latest/api/text.html#docx.text.run.Run.text)
and [paragraph creation API](https://python-docx.readthedocs.io/en/latest/api/document.html#docx.document.Document.add_paragraph).

The current harness comparator keeps text codepoints significant. Resolving
this finding requires an explicit choice: preserve/reconstruct the distinction,
reject/report it as a conversion loss, or approve and document CR/LF
normalization for that conversion. The harness did not silently broaden its
equivalence rules to make this case pass.

Replay: `.docstream/harness-runs/final-validation/fuzzy/failures/minimized-0013.json`.
Code location: docx_adapter.py export_docx/add_runs, where span text is passed
to paragraph.add_run. The confirmed observed service path in the earlier
verified run exported and reimported successfully with `input_text: "\r"`,
`output_text: "\n"`, empty loss diagnostics and original head revision zero.

## HF-02 NUL in DOCX export

The reduced case contains a single U+0000 character. It is a valid UTF-8 scalar
and is accepted by the semantic model. DOCX construction raises ValueError
because that text cannot be placed directly into XML. The direct adapter fails
without a conversion diagnostic. Through FormatService, the export returns
INTERNAL_ERROR, retryable false and committed false. The source head stays at
revision zero and no successful export is claimed.

This is an error-classification/format-boundary defect. A future correction
should identify unsupported text before document construction, provide an
explicit validation/conversion diagnostic and apply the chosen loss policy.
This report does not authorize dropping or replacing the character.

Replay: `.docstream/harness-runs/final-validation/fuzzy/failures/minimized-0021.json`.
Code location: docx_adapter.py export_docx/add_runs and its caller in
format_service.py. The retained service confirmation observes the generic
failure at the public application-service layer, not just a direct helper call.

## HF-03 malformed surrogate at dictionary ingestion

The reduced input is an invalid dictionary ingestion request containing an
unpaired U+D800 character. Expected behavior is the declared VALIDATION_ERROR
with no document. Actual behavior is UnicodeEncodeError from UTF-8 serialization
before Pydantic validation. No document was created in the confirming store.

The path is service.py parse_request -> storage.dumps -> models.canonical_bytes.
It encodes the dictionary before the model's valid_unicode validator executes.
The existing direct model tests still pass; they enter through a different
validation boundary. This is why the old 117-test result and this new failure
can both be accurate.

Calling the transport invocation wrapper directly with this library request
produces generic INTERNAL_ERROR, retryable true and committed unknown. This
confirmation does not establish that a real MCP SDK request can bypass its
own earlier typed validation. The direct dictionary API is the verified failing
boundary; HTTP/SDK exploitability is not claimed.

A future correction should make invalid Unicode a stable validation error
before encoding/reserving the request. Valid Unicode source bytes and existing
stream hashes must retain their current behavior.

Replay: `.docstream/harness-runs/final-validation/fuzzy/failures/minimized-0014.json`.

## Evidence and unchanged scope

The final run saves every input before execution. Its 500 cases are distributed
as 189 batch cases, 63 equivalent-Markdown cases, 62 Markdown round trips,
62 DOCX round trips, 62 invalid requests and 62 malformed packages. The three
minimized groups were replayed individually under the replay command and each
failed again with its original signature.

Earlier service confirmations are retained under
`.docstream/harness-runs/approved-verified/service-confirmation-verified/observations.json`.
They are supplementary observations, not replacements for the final run's
immutable inputs/results. The earlier development run recovered its 624 case
inputs by regeneration and verified every input hash; its RECOVERED_INPUTS.json
records that provenance. Final runs save inputs directly and need no recovery.

No product behavior was modified to address these findings. No renderer
baseline was changed, no failed expectation was loosened and no failure was
converted into a pass. Harness completion is separate from product acceptance.
These corrections and the HF-01 policy decision require a subsequent scoped
proposal/clearance. Agentic-control integration remains last.
