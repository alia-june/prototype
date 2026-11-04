# Relative and replaceable map probe validation

Validation date: 2026-10-30 (America/New_York)  
Authorization: AUTH-18A  
Final result: **PASS / COMPLETE**

## 1. Implementation

New maintained package: `service/src/docstream_cpu/relative_maps/`  
Focused tests: `service/tests/test_relative_maps.py`  
Existing service, native, native-vocabulary and persistence modules were not
modified by AUTH-18A.

Final implementation hashes:

| File | SHA-256 |
| --- | --- |
| `values.py` | `bda5f5ae9d6081055f4d58c1a3d850f3880136493a60676d89574f736f1926dd` |
| `model.py` | `c38d5eacf286a190863952478be9462bc511a941e61b3ae3cdbd72b56c733b0c` |
| `wordnet_pull.py` | `784e23f02031c0b16398d7f6381911771fa4a8d69644ea7c88d188f8c7cb3b1c` |
| `probe.py` | `86ffa5c5cf60326999c5942cc50f27cb3126550e6df5dab59808baea60611256` |
| `artifacts.py` | `626005f706013639b70bf2b1a38d9bcce9d9fb9b630bae59ac4cc5fd5fc4c0fd` |
| `__init__.py` | `8fa51d7a38db1463945c382cfba87b324dd42e2547fb39a37fa920f911fe9f2f` |
| `__main__.py` | `4dec1005df79788007cbd3af40e3d0dfb7ad4c7e688d7139fc6e4e9c847d6ca5` |
| `test_relative_maps.py` | `19d8545695b21249e6aaebece79e78cec95ddbb11126bacdb735c07351537b06` |

These hashes identify locally validated bytes; they are not independent
attestation.

## 2. Focused test result

Command:

```text
service/.venv/Scripts/python.exe -m unittest -v tests.test_relative_maps
```

Result: **17 methods passed in 0.157 seconds**. The methods include:

- canonical immutable entry identity and detached payloads;
- identical recipe reuse and identity changes caused by different order maps;
- Context A replacement without Context B change or prior-map deletion;
- acyclic lineage and 500-map addressability;
- missing inputs, duplicate draft keys, cycles, bad order positions, bad context
  selections and capacity failures rejecting without publication;
- read-only snapshot behavior;
- deterministic synthetic WordNet selection and relation preservation;
- source digest and byte-budget enforcement;
- explicit unresolved relations when target resolution is capped;
- changed seeds selecting different samples while the same seed replays;
- strict scope/type limits;
- evidence replay and deliberate tamper rejection;
- 200 seeded malformed batches with exact expected codes and state preservation;
- a 500-map chain/alternative torture case completed in under 30 seconds.

The 200 fuzzy submissions cover missing symbolic inputs, dependency cycles,
duplicate local keys and absent external digest inputs. All four families were
selected at least once; all 200 rejected without changing store statistics.

The torture method published 500 maps and 500 entries in five atomic batches,
then traversed all 500 reachable identities from the final map.

## 3. Real-source pull and composition

Evidence directory:
`.docstream/etabit-map-tests/auth18a-vertical-composition-probe/`

| Measure | Observed |
| --- | ---: |
| Status | `COMPLETE` |
| Candidate adjective records | 18,185 of 50,000 allowed |
| Selected adjective records | 8 |
| Retained pointer relations | 19 |
| Resolved unique target records | 17 of 32 allowed |
| Unresolved target keys | 0 |
| Source records retained | 25 |
| Logical source bytes | 3,169,936 of 4,194,304 allowed |
| Published maps | 21 |
| Published entries | 101 |
| Atomic publications | 1 |
| Map input references | 65 |
| Runtime | 3.954387100005988 seconds of 120 allowed |
| Peak process working set | 131,297,280 bytes of 134,217,728 allowed |
| Python allocation peak | 41,787,809 bytes |

The deterministic sample included both adjective (`a`) and satellite adjective
(`s`) source records, single- and multi-word records, and a record containing
the source marker forms `all-around(a)`, `all-round(a)` and `well-rounded`.
Those tokens and markers remain raw source data; no final decoding was adopted.

The peak working set passed but was only 2,920,448 bytes below the ceiling. This
is a material finding, not a comfortable capacity margin.

## 4. Context result

- Context A v1 resolves adjective composition A:
  `4d6bcafb4290f22967ff7606dca1e1daca160cbda43f803e08be4fa864c6f60c`.
- Context A v2 resolves adjective composition B:
  `a1e4ac1582dd4e64bd8d08bbe16d115dccc0f537f01b665bcd236af61d4298ab`.
- Context B v1 still resolves composition A after Context A v2 exists.
- Both compositions and all prior contexts remain in the catalog.

## 5. Evidence verification

The maintained replay verifier passed:

- five payload hashes verified;
- five deterministic payload/summary products verified;
- 65 map input references verified;
- 25 retained source records verified;
- 19 relation records verified; and
- all three context resolutions rechecked.

Evidence payload hashes:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `aliases.json` | 1,834 | `2e3c582716930a3d8c8885a3a62753e9dcb98800b86100c5e7b2c79d7a8e914a` |
| `maps.jsonl` | 84,204 | `a1e6f3ab7d5c59a5562c68a69a5d5c9bc84fd3e08ee965343287b158a4e15c7c` |
| `relations.jsonl` | 7,680 | `6c915f82e1aed8e71b9ab10ea0e6b1237685f583c1b907af267955e447c1fa55` |
| `result.json` | 1,195 | `df14bd2910af3bb92d40fae0dc9c657a6e41ebf48804a02002db57cf86c139f0` |
| `source-records.jsonl` | 39,091 | `542d639812dd21764772dc569204e7b7f1abee5f81554b91aa319440f8663042` |

## 6. Existing regression result

Seventeen native-vocabulary methods and 60 native/native-harness/meta methods
also passed: **77 methods in 9.804 seconds**. The unchanged native torture case
retained 501 streams across 500 transformations and 5,010,000 reference slots in
7.199 seconds.

Including the 17 focused relative-map methods, 94 verification methods passed in
the final selected validation set.

## 7. Proof boundary

This validates an isolated in-memory mechanical map graph and retained packet.
It does not validate a live Etabit drive, durable recovery, concurrent writers,
real grammar/syntax sources, Government and Binding Theory, linguistic accuracy,
complete WordNet decoding, whole-service behavior, GPU lowering or agentic
integration.
