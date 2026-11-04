# Independent service-harness meta-verification contract

Date: 2026-10-31. AUTH-19A. Identity: `docstream.harness-meta/1`.

## Purpose and boundary

The service-harness meta-verifier treats `docstream_cpu.harness` as the target. It verifies retained cases, journals, summaries, cleanup claims, source identities and aggregate execution without accepting the target's final status as its only oracle.

AUTH-19A may add `docstream_cpu.harness_meta`, its reviewed fixture, focused tests, retained evidence and reports. It may not change the target service/native harness, product implementation, expected product results or historical runs. Harness and product corrections require later scopes.

## Closed inputs

Meta-cases use `docstream.harness-meta.case/1` with an internally selected closed mutation or scenario name. Inputs cannot select commands, executables, modules or filesystem roots. Every meta-input is saved before execution and identified by SHA-256.

Hardening contains 30 fixed checks. Fuzzy uses seed 20261031 and exactly 1,000 cases: 800 invalid mutations and 200 clean controls. Twenty invalid mutation families occur 40 times each. Torture contains eight named scenarios.

## Independent audit

The auditor uses strict UTF-8 JSON, rejects duplicate keys and limits individual JSON files to 2 MiB. It recomputes canonical input hashes, checks root containment, reconciles counts with cases, finds duplicate identities, reads raw events, compares `cleanup.json` with summary cleanup, checks job-zero support and derives overall status independently.

An incomplete worker may be stopped before creating an event journal. A missing journal is accepted only when the retained mode is incomplete and has zero cases. An existing malformed journal, a missing journal with retained cases, a demoted failure or a passed mode with incomplete coverage remains a defect.

The outer journal separately verifies its own retained inputs, planned coverage, counts and sticky failure precedence. A meta-harness exception is not a target finding.

## Modes

Hardening verifies clean evidence, malformed/duplicate/oversized JSON, schema and identity mismatches, inconsistent status and counts, missing worker/cleanup fields, unresolved cleanup, unsupported job-stop claims, duplicate/missing/tampered/escaped inputs, missing/contradictory events, incomplete/failure demotion, product mutation, non-overwrite, configuration bounds and pre-execution retention.

Fuzzy applies the same closed families in deterministic generated order and requires every invalid packet to be rejected while every control passes.

Torture executes eight real 50 ms service-harness deadlines, three paired test-order runs, three complete unittest discoveries, four parallel packet audits, a 2,000-event unfinished journal, 20 sticky-failure recoveries, eight isolated evidence controls and exclusive log-open observations for all eight deadline cycles.

## Ownership and limits

External unittest processes are launched in a separate meta-owned Windows job with kill-on-close. Only children launched by the meta-harness may be terminated. Target process results are retained as raw output with byte size and SHA-256.

The approved ceiling is 900 seconds, 512 MiB retained evidence, 1,000 fuzzy cases, 2,000 total meta-cases, 24 owned termination cycles, four concurrent targets, three discoveries and 2,000 events in the long-journal scenario. Evidence size is a sampled guard plus exact final observation, not an operating-system quota.

PASS proves only that the local implementation satisfied this closed contract. FAIL may identify a meta implementation error, target-harness defect or product failure; `HARNESS_META_FINDINGS.md` classifies the source. No dependency, network deployment, release, GPU, Etabit or agentic-control work is authorized.
