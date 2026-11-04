# Native vocabulary pilot validation

Validation date: 2026-10-30 (America/New_York)  
Authorization: AUTH-17  
Final bounded result: **PASS / COMPLETE**

## 1. Implementation under test

The implementation adds the side-effect-free
`service/src/docstream_cpu/native_vocabulary/` package and
`service/tests/test_native_vocabulary.py`. Existing native-model source was not
modified. The source archive is the acquisition-manifest-bound Princeton
WordNet 3.1 database archive.

Implementation file SHA-256 values at final validation:

| File | SHA-256 |
| --- | --- |
| `values.py` | `2e31d60f40d3427fc231b484cc6e713d1b780b678715c21f4ea2fdde1b8f20d3` |
| `pilot.py` | `734834af9a093550314bdc6435855892bc0b5086a3fd900e4973a6f942c9710f` |
| `artifacts.py` | `9f80727da94f8815f0375475d11e5830bae4f57c5a7191a2a007e0273f60ecef` |
| `__init__.py` | `6ca16d1557379959e354db656fe22b2103387d0a734c93050a737605ea28d3ac` |
| `__main__.py` | `8ea337c67d9df11705e922e4c3a12db689460cefbb0d7c9d28d6521406505426` |
| `test_native_vocabulary.py` | `c0f97c2e0cac496fa6ed7dd6fcf9e6acf01cf71a74318247309e340e5f25f3eb` |

These hashes identify the locally validated bytes. They are not independent
attestation.

## 2. Focused test result

Command:

```text
service/.venv/Scripts/python.exe -m unittest -v tests.test_native_vocabulary
```

Final result: **17 methods passed in 0.346 seconds**. Coverage includes:

- the exact 11-entry explicit fragment registry and distinct `ette`/`-ette`;
- literal fallback preserving case, punctuation and digits;
- no inferred root for the `marionette` construction example;
- balanced source parsing, syntax-marker separation and exact locators;
- duplicate occurrence retention with shared native definition identity;
- collocation exclusion without underscore-to-space conversion;
- deterministic replay;
- natural source exhaustion versus budget-caused partial status;
- exact evidence hashing, overwrite refusal and tamper rejection;
- source digest mismatch, missing members, malformed hexadecimal fields,
  non-ASCII source, malformed archives and missing paths;
- exact-type and approved-ceiling enforcement;
- record/byte truncation returning `PARTIAL` without exceeding the limit; and
- a synthetic maximum run of 1,000 forms plus 100 exception pairs below the
  existing native capacity.

## 3. Final real-source run

Evidence:
`.docstream/native-vocabulary-runs/auth17-20261030-final/`

| Measure | Observed |
| --- | ---: |
| Status | `COMPLETE` |
| Form occurrences | 1,000: 250 noun, 250 verb, 250 adjective, 250 adverb |
| Exception pairs | 82: 25 noun, 25 verb, 25 adjective, 7 adverb |
| Source records read | 721 of 10,000 allowed |
| Selected source bytes | 158,405 of 8,388,608 allowed |
| Collocation tokens excluded | 203 |
| Explicit fragment definitions | 11 |
| Unique word constructions | 1,003 |
| Total native definitions | 1,014 of 4,096 allowed |
| Native reference slots | 7,519 |
| Execution time | 1.4052358000189997 seconds of 600 allowed |
| Peak process working set | 40,853,504 bytes of 536,870,912 allowed |
| Python allocation peak | 2,217,880 bytes |

The seven adverb exception pairs are all eligible single-token pairs available
before natural end-of-file in `dict/adv.exc`; the approved cap was “up to 25”
per part of speech. No byte or source-record budget caused the lower count, so
the final status is `COMPLETE` with no shortages.

Retained payload manifest:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `constructions.jsonl` | 810,100 | `42c6e2ffad4c8c3f7fdfe8dffc070a0f90e6dc9d0a321232a352093c48bc1aed` |
| `exceptions.jsonl` | 37,691 | `fea684d29bbd5ff200a2bfd2cde3ecba367e87e6c426c96d4feb5279d6b5cc95` |
| `forms.jsonl` | 528,603 | `7a3ea296bde5fb23274afefcadc703afc47f6f7ff774901f7cf4f1a0dd2b890a` |
| `fragments.json` | 3,791 | `236a6a416dc7ed9f77dce35b02917a479ccb03cb796169155564cce01853d0c7` |
| `result.json` | 1,188 | `0de9d5db01910980de88b5bda4d98c1266a4757509d84f938ee44c217e27d91e` |

## 4. Maintained evidence verification

The `--verify` command passed. It checked five retained payload hashes, replayed
and byte-compared five deterministic payload/summary products, validated 1,082
source locators and checked 2,167 exact native expansions or occurrence links.
Replay produced the same counts, definition IDs and construction traces.

## 5. Existing native regression result

Command:

```text
service/.venv/Scripts/python.exe -m unittest -v \
  tests.test_native tests.test_native_harness tests.test_native_harness_meta
```

Result: **60 methods passed in 10.146 seconds**. This includes the pre-existing
200-case generated native oracle, the 10,000-reference/500-transformation native
torture test, the native hardening/fuzzy/torture harness checks and the harness
meta-checks. The torture test reported 501 retained streams and 5,010,000
reference slots in 7.543 seconds. No existing native source was changed.

## 6. Retained development observations

The first real invocation attempt did not start Python because its command used
`service/.venv` while already operating from `service`; no source or evidence
was produced. The corrected initial implementation run was retained at
`.docstream/native-vocabulary-runs/auth17-20261030/`. It selected the correct
records but labeled natural `adv.exc` exhaustion `PARTIAL` and could not obtain
the process peak through its first low-level probe. Focused logic was corrected
to distinguish natural end-of-file from budget truncation, and peak working set
is now read through the installed Windows API binding with a low-level fallback.
The initial directory was not overwritten or presented as final evidence.

## 7. Proof boundary

This is local bounded validation of one CPU pilot. It establishes neither the
correctness of WordNet itself nor an external source signature. It does not
validate complete-corpus capacity, persistence/recovery, the existing document
service, Markdown/DOCX or rendering behavior, GPU representation, release, or
agentic-control integration.
