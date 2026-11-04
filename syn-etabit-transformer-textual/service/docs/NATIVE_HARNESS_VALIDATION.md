# Native harness implementation and validation

Date: 2026-10-29 (America/New_York). AUTH-13.
Harness: `docstream.native-harness/1`.
Product: `docstream.native.safe-ascii/1`, package metadata 0.2.0.dev4.

## Outcome

**PASS for this bounded native workload.** No unexpected native product failure
was observed. Product source, existing tests, expectations, contracts and earlier
validation reports were preserved. The existing service/format harness FAILED
outcome and HF-01/HF-02/HF-03 remain unchanged.

| Mode | Passed | Failed | Submitted transformation attempts |
| --- | ---: | ---: | ---: |
| Hardening | 100 | 0 | 54 |
| Fuzzy error | 1000 | 0 | 730 |
| Torture | 8 scenarios | 0 | 736 |
| Combined | 1108 cases/scenarios | 0 | 1520 |

The fuzzy set has 800 expected invalid-input rejections and 200 valid controls,
not 800 product failures. All 20 error recipes receive 40 generated cases.
Every rejection checks its expected exception/code and complete state fingerprint.

Seventeen harness self-tests pass. Seventy-one relevant existing regression
methods pass: 30 native fixed checks, 35 CPU methods and six non-listening baseline
tests. Those regression methods retain the earlier 420 CPU generated sequences.
The old native generated/torture methods were not unnecessarily repeated in that
regression invocation; this new full run supplies its own larger error workload
and the retained-history stress scenario.

## Actual run and retained evidence

Primary run:
`C:/Users/<local-user>/Documents/Workbench/strmdocx/.docstream/native-harness-runs/auth13-20261029-validation/`.

REPORT.md and summary.json summarize the modes. RUN.json identifies the tested
source/harness files, Python environment and approved limits. Each mode retains
inputs, events, results and any failures. All 1108 original case inputs were
audited against their pre-execution file hashes and replay schema. No failed
case packets exist because this main workload had no unexpected failures.

The actual retained main-run footprint, including final reports, is 2,081,980
bytes, below 512 MiB. Mode supervisor durations sum to 10.655 seconds; this is
the sum of the owned mode durations, not an asserted end-to-end benchmark.
Worker durations are 0.078 seconds hardening, 0.781 seconds fuzzy error and
8.406 seconds torture. The largest observed Windows job committed peak is
77,774,848 bytes. Its scope includes the launcher and owned descendants, not
only Python heap or one process working set. No RAM ceiling or leak-absence
threshold is claimed. The main combined deadline is 900 seconds.

The 1520-attempt account applies to submitted native batch operations in the
three main modes. Constructor/definition cases have their own bounded case
counts. Harness self-tests, saved replays and the separately reported regressions
are not silently folded into that main-run metric.

## Observed torture results

- Wide retained history: 10,000 direct references per root; 500 transformations;
  501 streams/definitions, 500 batches and 5,010,000 stored reference slots.
  Every result and selected older streams matched their exact byte oracle.
- Deep sharing: eight layers, 200 shared occurrences and 32 selected-occurrence
  edits. Unselected uses and the original retained their content.
- Empty amplification: the accepted graph accounts for 1,990,200 expansion visits
  with zero bytes; the next over-budget definition rejects without mutation.
- Expansion boundary: exactly 1,000,000 bytes expand correctly; one additional
  byte is rejected with LIMIT_EXCEEDED and unchanged state.
- Resource exhaustion: eight configured boundary families reject atomically.
- Concurrent callers: four threads complete 40 edits each, retaining 161 streams
  and 160 batches. Branch content, 41-entry per-caller ancestry and gap-free
  stream ordinals are checked.
- Publication preparation: eight controlled fault points after retained work
  preserve state and allow subsequent valid work.
- Timeout cleanup: the stalled child reports readiness, then is deliberately
  terminated. Its own probe summary is INCOMPLETE; the parent scenario passes
  only after confirming that expected status and stopped owned child.

Every main mode supervisor records exit code zero and its owned child stopped.
No listener, browser or renderer was started. This tests in-memory consistency
and owned-worker cleanup, not filesystem crash recovery or service publication.

## Saved-case replay

Four separate fresh runs replay retained inputs successfully, retaining their
own reports. Each replay input is byte-identical to its source input:

| Replay run | Selected mode | Outcome | Attempts |
| --- | --- | --- | ---: |
| auth13-replay-invalid | hardening | PASS | 0 |
| auth13-replay-fault | hardening | PASS | 2 |
| auth13-replay-valid | fuzzy-error | PASS | 2 |
| auth13-replay-deep | torture | PASS | 32 |

These exercise malformed-surrogate rejection, a controlled publication failure,
valid byte edits and deep shared-assembly editing. No current failure was
invented merely to produce a product failure packet. Harness self-tests
separately verify synthetic failure recording and bounded reduction.

## Harness self-verification and development failure

The final 17 self-tests check deterministic generation, exact 800/200 coverage,
pre-execution retention/hashes, escaped invalid Unicode, replay family/schema/
size restrictions, specific error classification, complete state-change detection,
original and reduced failure packets, failure precedence during interrupted
shrinking, journal recovery, operation/evidence budgets, configuration rejection,
mode selection, non-overwrite behavior and actual supervisor timeout cleanup.

The first self-test run had one cleanup error, not a native product failure:

```text
PermissionError: [WinError 32] The process cannot access the file because it is being used by another process
... selftest-afjwgili ... child.log
Ran 17 tests in 1.370s
FAILED (errors=1)
```

NH-D01 in NATIVE_HARNESS_FINDINGS.md records the Windows descendant-handle race.
The fix is confined to the new native harness: stop_owned waits for its owned
Windows job's active processes to reach zero before closing/reaping. The old
process-owner helper and native implementation are unchanged. Final self-tests
and main/nested timeout execution confirm cleanup. The first failure is not
rewritten as a passing run.

## Evidence audit

```json
{
  "result": "PASS",
  "counts": {
    "hardening": 100,
    "fuzzy-error": 1000,
    "torture": 8
  },
  "fuzzy_families": {
    "error": 800,
    "valid": 200
  },
  "inputs_audited": 1108,
  "attempts": 1520,
  "retained_bytes": 2081980,
  "replays": [
    {
      "case": "invalid",
      "mode": "hardening",
      "status": "PASS",
      "attempts": 0,
      "input_sha256": "fce4832f7c4dbc967955461aa7b93c4bcb73bae3cbcddec453762f4732bd76c1"
    },
    {
      "case": "fault",
      "mode": "hardening",
      "status": "PASS",
      "attempts": 2,
      "input_sha256": "1a116d906ba9fd93ffb84a9b6c6e74c5687bc8041ead94fd367359589064e951"
    },
    {
      "case": "valid",
      "mode": "fuzzy-error",
      "status": "PASS",
      "attempts": 2,
      "input_sha256": "7fae49984fab09556b00313e23c912286a2c1883eb1c5fa46c10ac0cd6d45662"
    },
    {
      "case": "deep",
      "mode": "torture",
      "status": "PASS",
      "attempts": 32,
      "input_sha256": "ab485e8f1ed964396d8cda486068a18758b1b4fad69b28132fe4757967c4428f"
    }
  ],
  "worker_elapsed_seconds": {
    "hardening": 0.078,
    "fuzzy-error": 0.781,
    "torture": 8.406
  },
  "sum_supervised_mode_seconds": 10.655,
  "max_windows_job_committed_bytes": 77774848
}
```

## Preservation and implementation identity

All 60 pre-existing protected files match their initial hashes: 33
product/earlier-harness source modules, 18 old test modules, package metadata,
five lock files, the native fixture and the two original native contract/
validation documents. The three native implementation source files are
unchanged. Only the approved new harness, new fixed fixture/self-tests/reports,
new run evidence and planning indices were written.

The main run records the harness files used at execution. These new file
identities also cover its contract and findings:

```json
{
  "service/src/docstream_cpu/native_harness/cases.py": "362a098a10ba8551cf0e078deedf7295b3792cca1c08d868de9198a1ce240e2d",
  "service/src/docstream_cpu/native_harness/core.py": "c6aff4157c5f0ec3b7fd1fbc8a50ff2d357cad6aab699d2177d9d765d8ca8ccf",
  "service/src/docstream_cpu/native_harness/runner.py": "083c564cf293cd8df177156cd500ade6a3261df34542066b1e27cd550670fae3",
  "service/src/docstream_cpu/native_harness/worker.py": "ba551486df27ab0fc2d090ccb60e5d22c2e74e156fc67a964115d2f1ae97c597",
  "service/src/docstream_cpu/native_harness/workloads.py": "166334008b503abacf4587fccf8ce57eda4d9cbb7dc98ac5fdefd52748b3bfce",
  "service/src/docstream_cpu/native_harness/__init__.py": "62754ae393c72282f3d03342a20445c38acbe12af23ebef92181ef9535f78620",
  "service/src/docstream_cpu/native_harness/__main__.py": "3371e5aefb63db9d4dbf67dcf569ab0f9f9435e3611e63d907de91f7ba9ced77",
  "service/tests/test_native_harness.py": "2333e7b570a25f8c4ea8ccefabe8f0778f7ecd8b3bdbfdb705d5e3926286dfed",
  "service/tests/fixtures/native_harness/fixed-cases.json": "a254b1d2037b346da1c4c9c6a11d173d11250752e57478ed106ff3cebcd980bc",
  "service/docs/NATIVE_HARNESS_CONTRACT.md": "ef5294e5ad23798808030429265d2b0bb4219051852029fdd1ec96ed5518156f",
  "service/docs/NATIVE_HARNESS_FINDINGS.md": "e59d5623e3c609b32aacd7e248cc841c7f0ec5826fe5340720b39b599ac4927a"
}
```

Protected pre-change identities, all compared successfully after execution:

```json
{
  "service/src/docstream_cpu/artifacts.py": "b97776fe1a56caeb66916a9b67de262c864e642dd66936ea85d61e2c9c08d5e8",
  "service/src/docstream_cpu/assets.py": "86713c61144b2a89c616545858710c0803b93f2640a19a8f4ea0cbf2abbdd41c",
  "service/src/docstream_cpu/catalog.py": "d2f8117ca858bda3f37375588fe1eeaf149fd993307da766b5c1dc009da58e4a",
  "service/src/docstream_cpu/cli.py": "7e32dff0ea0933342828a943bfd9ff8f088977b0ccee85ead756a85c9a67223d",
  "service/src/docstream_cpu/docx_adapter.py": "bf73cf31492ac6b78e9bc91b163de87c5bb52ecc9c67d6e372c3c6f21f612fda",
  "service/src/docstream_cpu/errors.py": "f1d91402af159b813bc1fe7a0f863dc6cc3d536c01394103175ef0a0b58d247a",
  "service/src/docstream_cpu/executor.py": "733a3115ba314f3428410026b875e58bdea3cbe79c4a49aed0159c7dbcb133f5",
  "service/src/docstream_cpu/format_common.py": "5f5edf9b9696a4656b383a7f1252844fc0c5fbc2d6ec8528202afb3d08602ca7",
  "service/src/docstream_cpu/format_service.py": "ceeec2debd4b5be3d207b4f9ef7a78717e3a36c82f0a446470b79ac3109bd34b",
  "service/src/docstream_cpu/markdown_adapter.py": "db779b9788900188a7f7c019588d206354b9bc150624f936ec79c3ffb71d618b",
  "service/src/docstream_cpu/mcp_server.py": "5347fb41e3f2f45fae9a46dde5b6cafcd717d629d3c29f21cb01fccea8d8ebea",
  "service/src/docstream_cpu/models.py": "eb26679926f3ad7b0358c55b21709c556921b42738d0a0be52dedea11cb7b3b7",
  "service/src/docstream_cpu/operations.py": "24d1a9f65516140661a3a5e2f246837541e298fc5f4b76abe4d8b81207286c0b",
  "service/src/docstream_cpu/planner.py": "e139b205d3f66d8f11635942d182d1c04a627c31ea19bfe9c8ab644baec7ec10",
  "service/src/docstream_cpu/rendering.py": "c6ce66b710b8fd6fcbbce2924e8576acc65272b13825a50018480a526906d64c",
  "service/src/docstream_cpu/rich.py": "e6372a0ae31a9e60be2bc525826cc954fecd88dfabf52656ed9375bbec569cb3",
  "service/src/docstream_cpu/rich_rendering.py": "447740bed85e7c2c84d3bca542989b89ba30d34c9bb87d34c5d2bd42b61c9824",
  "service/src/docstream_cpu/service.py": "466243d741ffbe059d32c1c6f429bc79ab3e7bf37fdaf0a17834d6b9939c63c7",
  "service/src/docstream_cpu/storage.py": "7ce563ffe7585d36b755f67499afe24d17ab7da971ab8961a8ccdcde6f923142",
  "service/src/docstream_cpu/visual_service.py": "fc63fea12eecc673f89ca6a4f6b2f140fc1b8feb7f4a42e0d4bbea27bfd11e24",
  "service/src/docstream_cpu/__init__.py": "12bb14336aa4e662fd4fe0cd730e7528fae8170dbf90339c34f268ec9147f327",
  "service/src/docstream_cpu/__main__.py": "935a1c1166b0c1ea35a82256345000bf2c73ded718d77773bc27a71ecce28f7d",
  "service/src/docstream_cpu/harness/cases.py": "d567dda080cab25303c9d8da96c111a0f21abb97d72cabe82fa1174bbb4ad04c",
  "service/src/docstream_cpu/harness/core.py": "8a85f920771f08ea09b960bd09be7895a77373cc8dc9b89084036247d2b8f4c9",
  "service/src/docstream_cpu/harness/generate.py": "ff9d80da00c64c518f57a0985bfaa2eb42d4a1fae0fcbe3e0e8925576b73b614",
  "service/src/docstream_cpu/harness/runner.py": "313b9d44a6349d4bff857cfd88b6abdf63e58138deb6214b49602141a70ae4a9",
  "service/src/docstream_cpu/harness/worker.py": "d787bfbd566187892557805b8e2fb19dd8dcfe5c1dc3e547f4da9fc412a36c4f",
  "service/src/docstream_cpu/harness/workloads.py": "ffee4e5bd1d17a96ec62332dbb088b9d4c825bcc81bb802c972d7e1c53ea34df",
  "service/src/docstream_cpu/harness/__init__.py": "1a7813f8f9aacca6c17741ffedef0c1d26a9ae4008d4b4f23dca9f3fddbc3fff",
  "service/src/docstream_cpu/harness/__main__.py": "7adb715d3b1f79e5f4412da1481fb55ecaec8e461a6a71c316a66ded23198606",
  "service/src/docstream_cpu/native/model.py": "3dd8733f24d1ac3a0dbf3f29f7721003d6e065896f9c45140d061714dfd4a7ff",
  "service/src/docstream_cpu/native/values.py": "9f90988e19df662fd73ec72197342634f385712b804664138c6a24e01df0a787",
  "service/src/docstream_cpu/native/__init__.py": "c637ba0a89477abd5b2e14576051cac9fe444a1ab44ff8862d95f380d86062cc",
  "service/tests/confirm_harness_findings.py": "0c06bed47e9551b0e6b85539aac7b9f7128f6abe679e169ce8aa85e61427dcb6",
  "service/tests/crash_worker.py": "5d59f886f7eebe07bc339cf63c4b42d951c47dd17f402e136032793692057127",
  "service/tests/prepare_harness_fixture.py": "a38724afbd272247d35e2784eb1209ec187a286c83dedfd6996cc0225ad9135f",
  "service/tests/retain_harness_inputs.py": "265e260d0363cda0aedb1ad13fa060ab9cbf8974543fbcac0634910a92aeff52",
  "service/tests/run_m2_validation.py": "688c17f1ab97b02fa9b70a12648fc83ed58c313c9f9d767394bf859bd3e7ad5e",
  "service/tests/run_m3_validation.py": "8c834ed7438a2258a2219bfb3bd29e63e82b2813a5cfae1cdc1ed268467f8bf7",
  "service/tests/run_m4_validation.py": "3b9517326c67aa32833913dcd452a7d959a8edd2847044d3b444f596cc880819",
  "service/tests/run_validation.py": "6aa98a023b1cc4008296b2f6f9a4d09e396b92145b010c388b607abfa4b0180b",
  "service/tests/test_baseline.py": "d19b1520a66d8369eff8dfbb3842a64b59c0e5961cd50d3669e4108e4ecb70de",
  "service/tests/test_cpu.py": "6869905bed4caaab4699a0f00f5827bd38d32250ab281e997a1eb3fa28bdab15",
  "service/tests/test_formats.py": "f90fa1cdd5f09272c2177129e4a364e26acc5a40f42873a0a58b24c0693609fe",
  "service/tests/test_harness.py": "982da1c9620ef7bec25f22e057134401c5e27118fd7edee55a8d690fbe884ee2",
  "service/tests/test_mcp.py": "ff8f27f6633f1556841cde0c10bbc38059b754724d07ead0096491d67406cc4d",
  "service/tests/test_native.py": "2ab6fa288a80c0a983f563d565bd07ccc3d387bfa5935082df78ddba59332848",
  "service/tests/test_rendering.py": "dbedc676eb5b28bf380bae61497982b60e566c0ad07dfac5aa7a57241b4e5e1c",
  "service/tests/test_service.py": "9e9b78bb6bed901ac638a27d90ead1e2a2ecd1e198248c1eeef9477d210d62e1",
  "service/tests/write_harness_evidence.py": "2c0c8ab0773f872946eccae049ff6e5c5fa3213926b97fb40f4f67b7c4ce7c21",
  "service/tests/write_m4_evidence.py": "9ad0f22b2f3e9c0d750c452c4a2128a58d921c923114f249bb63a2140248b685",
  "service/pyproject.toml": "dd6f956b9b8432e72f2e743a5db5fea89cfe1abb1ad47a0b761fdf7ffc39f13b",
  "service/requirements-cpu.lock": "b5053694bd2d2389ddf5a384225c13580c981da73e04d96f30de2c52def94461",
  "service/requirements-m2.lock": "cf2a5e071cafdb34764afebe90b2945816721c7751deea1c58de9eef88eb2aca",
  "service/requirements-m3.lock": "84637b32bb9a8d4cb481197357270a87ffc1d471b9266840888255bd0a241774",
  "service/requirements-m4.lock": "97edf4f259f109f2d048f38b1ec169540e17749b788b73c1a032da7d60b4a8f1",
  "service/requirements-service.lock": "97edf4f259f109f2d048f38b1ec169540e17749b788b73c1a032da7d60b4a8f1",
  "service/tests/fixtures/native/assemblies.json": "55dfd5412298223d8973280452fb356066aee9477236677b4e3c0b1ea7e02b97",
  "service/docs/NATIVE_REFERENCE_CONTRACT.md": "0404c8193a1ea8613e912be3b263ffd4e9e3e7d16a6108cb8db7f1f2a46ae9db",
  "service/docs/NATIVE_REFERENCE_VALIDATION.md": "c062aa300db40697c92409cfcd69b3189e171aff45febfc7392f3a810f1c6f32"
}
```

Hashes establish byte identity, not authority, security, correctness or
independent attestation. There are no installed dependencies or external
datasets from this scope. Windows supervision uses the already available
process-management support also used by the earlier harness.

## Reproduction

From the workspace root in the prepared environment:

```powershell
& service/.venv/Scripts/python.exe -m docstream_cpu.native_harness all
& service/.venv/Scripts/python.exe -m docstream_cpu.native_harness hardening
& service/.venv/Scripts/python.exe -m docstream_cpu.native_harness fuzzy-error --seed 20261029
& service/.venv/Scripts/python.exe -m docstream_cpu.native_harness torture
& service/.venv/Scripts/python.exe -m docstream_cpu.native_harness all --replay <saved-input.json>
```

Normal runs create new IDs and refuse existing destinations. The retained
auth13-20261029-validation ID must not be reused. NATIVE_HARNESS_CONTRACT.md
defines fields, errors, counters, workload bounds and replay restrictions.

## Actual final harness self-test output

Command: `python -m unittest discover -s tests -p test_native_harness.py -v`
from the service directory. Exit code 0.

```text
test_attempt_budget_counts_rejected_submissions_without_publishing (test_native_harness.NativeHarnessTests.test_attempt_budget_counts_rejected_submissions_without_publishing) ... ok
test_changed_seed_changes_cases (test_native_harness.NativeHarnessTests.test_changed_seed_changes_cases) ... ok
test_configuration_and_mode_mismatch_are_rejected_before_run_creation (test_native_harness.NativeHarnessTests.test_configuration_and_mode_mismatch_are_rejected_before_run_creation) ... ok
test_evidence_budget_returns_incomplete_before_case_execution (test_native_harness.NativeHarnessTests.test_evidence_budget_returns_incomplete_before_case_execution) ... ok
test_failed_case_is_replayable_and_shrinking_preserves_failure (test_native_harness.NativeHarnessTests.test_failed_case_is_replayable_and_shrinking_preserves_failure) ... ok
test_generation_is_repeatable_and_has_exact_800_200_distribution (test_native_harness.NativeHarnessTests.test_generation_is_repeatable_and_has_exact_800_200_distribution) ... ok
test_input_is_saved_before_execution_with_exact_hash (test_native_harness.NativeHarnessTests.test_input_is_saved_before_execution_with_exact_hash) ... ok
test_interrupted_journal_does_not_claim_a_pass (test_native_harness.NativeHarnessTests.test_interrupted_journal_does_not_claim_a_pass) ... ok
test_invalid_unicode_is_retained_as_escaped_replay_data (test_native_harness.NativeHarnessTests.test_invalid_unicode_is_retained_as_escaped_replay_data) ... ok
test_observed_failure_keeps_precedence_when_shrinking_is_interrupted (test_native_harness.NativeHarnessTests.test_observed_failure_keeps_precedence_when_shrinking_is_interrupted) ... ok
test_real_supervisor_timeout_stops_its_owned_child (test_native_harness.NativeHarnessTests.test_real_supervisor_timeout_stops_its_owned_child) ... ok
test_replay_rejects_duplicate_keys_and_oversized_files (test_native_harness.NativeHarnessTests.test_replay_rejects_duplicate_keys_and_oversized_files) ... ok
test_replay_rejects_malformed_hex_and_expected_error_schema (test_native_harness.NativeHarnessTests.test_replay_rejects_malformed_hex_and_expected_error_schema) ... ok
test_replay_rejects_unknown_families_names_and_executable_fields (test_native_harness.NativeHarnessTests.test_replay_rejects_unknown_families_names_and_executable_fields) ... ok
test_smoke_run_replay_and_existing_run_refusal (test_native_harness.NativeHarnessTests.test_smoke_run_replay_and_existing_run_refusal) ... ok
test_state_change_is_detected_even_with_expected_exception (test_native_harness.NativeHarnessTests.test_state_change_is_detected_even_with_expected_exception) ... ok
test_wrong_exception_type_and_code_are_failures (test_native_harness.NativeHarnessTests.test_wrong_exception_type_and_code_are_failures) ... ok

----------------------------------------------------------------------
Ran 17 tests in 1.266s

OK
```

## Actual existing regression output

Command: `python -m unittest test_native.NativeRigidTests test_cpu test_baseline -v`
from service/tests. Exit code 0.

```text
test_all_128_symbols_have_distinct_exact_values (test_native.NativeRigidTests.test_all_128_symbols_have_distinct_exact_values) ... ok
test_branches_do_not_advance_an_implicit_head (test_native.NativeRigidTests.test_branches_do_not_advance_an_implicit_head) ... ok
test_case_whitespace_and_return_bytes_are_not_normalized (test_native.NativeRigidTests.test_case_whitespace_and_return_bytes_are_not_normalized) ... ok
test_catalog_and_values_are_immutable_through_public_views (test_native.NativeRigidTests.test_catalog_and_values_are_immutable_through_public_views) ... ok
test_children_reference_and_expanded_byte_budgets (test_native.NativeRigidTests.test_children_reference_and_expanded_byte_budgets) ... ok
test_definition_budget_failure_rolls_back_all_prefixes (test_native.NativeRigidTests.test_definition_budget_failure_rolls_back_all_prefixes) ... ok
test_detached_records_and_stats_cannot_modify_payload (test_native.NativeRigidTests.test_detached_records_and_stats_cannot_modify_payload) ... ok
test_duplicate_and_malformed_operations_are_rejected (test_native.NativeRigidTests.test_duplicate_and_malformed_operations_are_rejected) ... ok
test_each_layer_can_explicitly_reference_lower_layers (test_native.NativeRigidTests.test_each_layer_can_explicitly_reference_lower_layers) ... ok
test_empty_assembly_and_empty_batch_have_explicit_identity (test_native.NativeRigidTests.test_empty_assembly_and_empty_batch_have_explicit_identity) ... ok
test_equal_or_upward_edges_are_rejected_preventing_cycles (test_native.NativeRigidTests.test_equal_or_upward_edges_are_rejected_preventing_cycles) ... ok
test_fixture_has_fixed_external_expectations (test_native.NativeRigidTests.test_fixture_has_fixed_external_expectations) ... ok
test_full_alphabet_round_trip_including_every_control (test_native.NativeRigidTests.test_full_alphabet_round_trip_including_every_control) ... ok
test_hyphen_is_an_emitted_symbol (test_native.NativeRigidTests.test_hyphen_is_an_emitted_symbol) ... ok
test_identical_definitions_share_but_streams_do_not (test_native.NativeRigidTests.test_identical_definitions_share_but_streams_do_not) ... ok
test_insert_remove_replace_are_ordered_and_intermediates_addressable (test_native.NativeRigidTests.test_insert_remove_replace_are_ordered_and_intermediates_addressable) ... ok
test_invalid_late_operation_publishes_nothing (test_native.NativeRigidTests.test_invalid_late_operation_publishes_nothing) ... ok
test_invalid_paths_and_symbol_targets_reject_atomically (test_native.NativeRigidTests.test_invalid_paths_and_symbol_targets_reject_atomically) ... ok
test_limits_and_literal_size_are_strict (test_native.NativeRigidTests.test_limits_and_literal_size_are_strict) ... ok
test_missing_reference_does_not_publish_a_definition (test_native.NativeRigidTests.test_missing_reference_does_not_publish_a_definition) ... ok
test_noop_and_return_to_original_reuse_definition_keep_occurrences (test_native.NativeRigidTests.test_noop_and_return_to_original_reuse_definition_keep_occurrences) ... ok
test_publication_preparation_failure_publishes_nothing (test_native.NativeRigidTests.test_publication_preparation_failure_publishes_nothing) ... ok
test_reject_non_ascii_without_substitution (test_native.NativeRigidTests.test_reject_non_ascii_without_substitution) ... ok
test_replacement_cannot_change_parent_layer_or_leak_definitions (test_native.NativeRigidTests.test_replacement_cannot_change_parent_layer_or_leak_definitions) ... ok
test_shared_word_edit_changes_only_selected_occurrence (test_native.NativeRigidTests.test_shared_word_edit_changes_only_selected_occurrence) ... ok
test_stream_batch_and_operation_budgets (test_native.NativeRigidTests.test_stream_batch_and_operation_budgets) ... ok
test_strict_values_reject_coercions_and_mutable_containers (test_native.NativeRigidTests.test_strict_values_reject_coercions_and_mutable_containers) ... ok
test_unchanged_content_has_distinct_structural_layers (test_native.NativeRigidTests.test_unchanged_content_has_distinct_structural_layers) ... ok
test_unknown_stream_and_batch_are_explicit_errors (test_native.NativeRigidTests.test_unknown_stream_and_batch_are_explicit_errors) ... ok
test_zero_byte_graph_has_independent_traversal_budget (test_native.NativeRigidTests.test_zero_byte_graph_has_independent_traversal_budget) ... ok
test_competing_candidates_fail_stale_head_without_losing_candidate (test_cpu.CatalogTests.test_competing_candidates_fail_stale_head_without_losing_candidate) ... ok
test_empty_batch_still_has_new_stream_identity (test_cpu.CatalogTests.test_empty_batch_still_has_new_stream_identity) ... ok
test_history_and_out_of_order_materialization_do_not_change_head (test_cpu.CatalogTests.test_history_and_out_of_order_materialization_do_not_change_head) ... ok
test_invalid_batch_does_not_advance_head (test_cpu.CatalogTests.test_invalid_batch_does_not_advance_head) ... ok
test_noop_result_has_distinct_lineage_and_shared_payload (test_cpu.CatalogTests.test_noop_result_has_distinct_lineage_and_shared_payload) ... ok
test_original_bytes_bom_crlf_unicode_and_semantic_identity_are_separate (test_cpu.CatalogTests.test_original_bytes_bom_crlf_unicode_and_semantic_identity_are_separate) ... ok
test_removed_block_identity_cannot_be_resurrected_in_later_batch (test_cpu.CatalogTests.test_removed_block_identity_cannot_be_resurrected_in_later_batch) ... ok
test_unknown_identifiers_and_unsupported_encoding (test_cpu.CatalogTests.test_unknown_identifiers_and_unsupported_encoding) ... ok
test_300_generated_assignment_sequences (test_cpu.GeneratedConformanceTests.test_300_generated_assignment_sequences) ... ok
test_60_generated_invalid_sequences_preserve_first_error (test_cpu.GeneratedConformanceTests.test_60_generated_invalid_sequences_preserve_first_error) ... ok
test_60_generated_structural_sequences (test_cpu.GeneratedConformanceTests.test_60_generated_structural_sequences) ... ok
test_disjoint_grouping_red04 (test_cpu.ReductionTests.test_disjoint_grouping_red04) ... ok
test_document_properties (test_cpu.ReductionTests.test_document_properties) ... ok
test_empty_batch (test_cpu.ReductionTests.test_empty_batch) ... ok
test_exact_duplicate_assignment (test_cpu.ReductionTests.test_exact_duplicate_assignment) ... ok
test_font_return_to_original_executes_zero_writes (test_cpu.ReductionTests.test_font_return_to_original_executes_zero_writes) ... ok
test_mixed_fonts_restore_exact_inheritance_and_other_properties (test_cpu.ReductionTests.test_mixed_fonts_restore_exact_inheritance_and_other_properties) ... ok
test_modified_plan_and_optimizer_version_are_rejected (test_cpu.ReductionTests.test_modified_plan_and_optimizer_version_are_rejected) ... ok
test_move_and_remove_are_immutable (test_cpu.ReductionTests.test_move_and_remove_are_immutable) ... ok
test_only_final_font_is_executed (test_cpu.ReductionTests.test_only_final_font_is_executed) ... ok
test_partial_scope_supersession_preserves_other_target (test_cpu.ReductionTests.test_partial_scope_supersession_preserves_other_target) ... ok
test_plan_is_deterministic_and_bound_to_input (test_cpu.ReductionTests.test_plan_is_deterministic_and_bound_to_input) ... ok
test_restore_all_block_style_fields (test_cpu.ReductionTests.test_restore_all_block_style_fields) ... ok
test_same_effective_font_is_not_same_explicit_style_state (test_cpu.ReductionTests.test_same_effective_font_is_not_same_explicit_style_state) ... ok
test_structural_boundary_preserves_prior_assignment (test_cpu.ReductionTests.test_structural_boundary_preserves_prior_assignment) ... ok
test_text_preconditions_are_evaluated_in_original_order (test_cpu.ReductionTests.test_text_preconditions_are_evaluated_in_original_order) ... ok
test_block_id_cannot_be_reused_after_removal (test_cpu.ValidationTests.test_block_id_cannot_be_reused_after_removal) ... ok
test_duplicate_operations_and_batch_limit (test_cpu.ValidationTests.test_duplicate_operations_and_batch_limit) ... ok
test_failed_text_guard_survives_later_replacement (test_cpu.ValidationTests.test_failed_text_guard_survives_later_replacement) ... ok
test_inserted_block_cannot_restore_nonexistent_baseline (test_cpu.ValidationTests.test_inserted_block_cannot_restore_nonexistent_baseline) ... ok
test_invalid_position (test_cpu.ValidationTests.test_invalid_position) ... ok
test_json_and_dictionary_callers_have_same_scalar_strictness (test_cpu.ValidationTests.test_json_and_dictionary_callers_have_same_scalar_strictness) ... ok
test_snapshot_contract_and_deep_immutability (test_cpu.ValidationTests.test_snapshot_contract_and_deep_immutability) ... ok
test_unknown_target_cannot_be_hidden_by_later_reversal (test_cpu.ValidationTests.test_unknown_target_cannot_be_hidden_by_later_reversal) ... ok
test_unpaired_surrogate_cannot_enter_semantic_content (test_cpu.ValidationTests.test_unpaired_surrogate_cannot_enter_semantic_content) ... ok
test_new_inspect_and_guarded_edit (docstream_baseline_tests.DocstreamTests.test_new_inspect_and_guarded_edit) ... ok
test_inspect_ignores_headings_inside_code_fences (docstream_baseline_tests.DocstreamTests.test_inspect_ignores_headings_inside_code_fences) ... ok
test_match_guard_prevents_write (docstream_baseline_tests.DocstreamTests.test_match_guard_prevents_write) ... ok
test_capture_replacement_and_newline (docstream_baseline_tests.DocstreamTests.test_capture_replacement_and_newline) ... ok
test_native_round_trip (docstream_baseline_tests.DocstreamTests.test_native_round_trip) ... ok
test_service_root_containment (docstream_baseline_tests.DocstreamTests.test_service_root_containment) ... ok

----------------------------------------------------------------------
Ran 71 tests in 0.770s

OK
```

