# How to grow a living tooling workspace

## Start here

This guide explains how to set up a workspace in which a person and an agent can begin useful tool work, retain what happened, and grow the system carefully as it operates.

A **living tooling workspace** is not a finished universal platform. It is a working place with a purpose, operating rules, source material, known capabilities, current tasks, and retained results. It can gain a capability, but that growth must be visible, bounded, and reviewed. It does not silently replace the tools it already depends on.

This is a setup and operating guide, not an exported runtime, controller, orchestration service, installer, Seed package, or bare-metal shell. A local workspace owner must choose and adopt their own rules; this document cannot transfer another project's approvals, source identity, or authority.

## The working cycle

```text
purpose
  → working rules
  → source and available capabilities
  → one approved piece of work
  → retained result and evidence
  → informed decision about the next small improvement
```

A successful run does not become automatic authority for the next run. A source folder does not become a usable tool merely because it is present. A proposed feature does not become part of the environment until its requirements, change, and validation have been explicitly approved.

## 1. Decide what the workspace is for

Begin with a plain statement of purpose. It should name the work the owner wants completed, not merely a collection of software or an aspirational architecture.

> This workspace helps the owner and agent inspect, use, and gradually instrument selected tools while preserving source, decisions, failures, and evidence. The immediate goal is to make one declared tool easier to operate without hiding its authority or state changes.

The purpose can change later, but record the change and its reason. Do not infer it from a folder name, a past experiment, or newly discovered code.

## 2. Establish the working areas

You do not need a large installation or a complex folder standard to begin. You do need to make different kinds of material distinguishable.

| Working area | What belongs there | Why it stays distinct |
| --- | --- | --- |
| Instructions and mode | Purpose, working rules, approvals, and operating limits | A tool result does not decide what an agent may change. |
| Source and reports | Original material, source identities, and governing reports | Source evidence is not a generated output or proposal. |
| Capability catalog | What is present, checked, required, and limited | Presence does not prove readiness. |
| Active work | Current question, inputs, outputs, and acceptance conditions | The next task remains understandable. |
| Runs and evidence | Outputs, receipts, logs, validation, failures, and corrections | A later result can be inspected without rewriting an earlier one. |
| Shared guide and roadmap | How the workspace works and what may be considered next | The system grows without silently widening a task. |

The names and layout are the owner's choice. What matters is that fixed source, new task output, authority records, and historical evidence are not confused.

## 3. Separate use from growth

| Activity | Meaning | Normal authority boundary |
| --- | --- | --- |
| Discussion | Clarify an outcome, inspect a small sample, or compare options | No production change follows from discussion alone. |
| Use | Perform an approved task through an existing declared capability | New task outputs and evidence stay in the approved location. |
| Documentation maintenance | Correct the shared account of approved work | It must not misrepresent evidence or weaken the rules. |
| Environment growth | Add/change a controller, dependency, source component, toolchain, wrapper, service, schema, or shared runtime | It needs its own concrete proposal and explicit approval. |

Write this boundary down in the workspace instructions. It is an operating rule for people and agents, not a technical read-only switch. A request to use a tool does not also approve installing software, patching that tool, adding a scheduler, or building a general orchestrator.

## 4. Ask for one useful piece of work

An owner does not need to know a command, class, or controller name to start. State the desired human result first.

```text
I want:
The material to use is:
The result is for:
It is correct when:
Constraints or things that must not change:
```

For example:

> I want to know whether one existing validator can check this declared batch without changing source. Use the current validator documentation and this named batch. The result is for me to decide whether to use it again. It is correct when the output, evidence location, and limits are clear. Do not install dependencies, change the validator, or promote anything.

Before a production task writes, runs, builds, publishes, or changes anything material, the agent should make a concrete proposal. The proposal names the source basis, exact outputs and destinations, limits, validation, and known uncertainty. Approval applies to that stated scope, not unrelated work.

## 5. Begin with one declared tool

Do not start by designing a universal control plane. Select one tool that has a real useful job. Read its declared interface and governing reports before deciding whether to use or instrument it.

For that one tool, identify:

1. The human outcome it is meant to produce or verify.
2. The source files and declared interface that define it.
3. Inputs, authority requirements, possible state changes, outputs, and refusal behavior.
4. The evidence it leaves behind, including the difference between a process exit, tool-reported result, structural verification, and human acceptance.
5. Its recovery boundary: what must stop and be retained if work is partial, failed, or uncertain.
6. A new, non-overwriting location for task output and evidence.

This makes the first operation small enough to understand. It also gives the workspace an honest basis for deciding whether repeated interpretation of that tool is a candidate for deterministic support later.

## 6. Instrument only the burden you can name

Tooling is useful when it removes a repeated well-defined burden without pretending to decide what still needs a person. Candidate deterministic work can include parsing declared input, comparing identities, checking a known path, retaining a receipt, or running one named command.

The following remain outside an ordinary controller or expert-system rule core unless a separately approved design says otherwise:

- The owner's intended outcome and scope.
- Whether authority is real and sufficient.
- Whether evidence is truthful or semantically adequate.
- Acceptance, promotion, legal meaning, and the next material decision.
- A recovery decision when the retained state is incomplete or unclear.

Use this sequence when a repeated burden may be worth support:

```text
inspect → map burden → propose the smallest fitted support → approve
→ validate → retain evidence → document the boundary
```

The word **fitted** matters. A writer, validator, gate recorder, importer, and decision tool can have different authority, evidence, failure, and recovery conditions. Reusing a pattern is good; forcing every tool into one imagined universal receipt or controller is not.

For the next step, read [How to Instrument a Tool](README.md). It explains how to inspect one real tool before proposing narrowly fitted deterministic support.

## 7. Treat every run as a record, not just an answer

When approved work runs, preserve enough information for someone to understand what was attempted and what the result actually establishes:

- Run identifier and time context.
- Declared input and applicable source identity.
- Request, admission, or authority boundary when one exists.
- Process observations and tool-reported result.
- Validation performed and its stated scope.
- Output location and hashes when byte identity matters.
- Next permitted action, or a clear stop-and-retain state.
- Failure and correction evidence, without overwriting the original attempt.

Do not claim more than the record supports. A clean process exit does not prove semantic correctness. A structural validator does not grant acceptance. A SHA-256 value proves byte identity of named material, not its truth, authority, ownership, or meaning.

## 8. Keep the system alive by maintaining its map

After a useful task, update the smallest record that helps the next person or agent orient themselves.

| If this changed | Maintain this kind of record |
| --- | --- |
| What a component can actually do | Capability catalog |
| How one tool should be inspected or used | Shared how-to or tool guide |
| What was learned from a retained task | New run report, preserving prior runs |
| What should be considered next | Roadmap or decision list |
| What an agent may change | Instructions/mode, only through their own approved scope |

Do not rewrite a past failed run into a later success. Link the correction to the retained failure and use a fresh run identity. Do not turn a temporary task script into an undeclared reusable system component. If a missing shared capability is needed, stop the affected task and present an environment-growth proposal instead of building it by implication.

## 9. Grow in stages, not by accumulation

| Stage | Question to answer | Deliverable |
| --- | --- | --- |
| Orient | What is here, what applies, and what is safe to use? | Instructions, catalog, and small source inspection. |
| Use | Can an existing declared tool perform this approved task? | Retained task result and bounded validation. |
| Instrument | Is there a repeated named burden worth moving out of an LLM or manual process? | Separately approved, tool-fitted support. |
| Harden | Does the support behave within chosen normal, failure, fuzzy, or contention cases? | Retained bounded test evidence and limits. |
| Connect | Is there a justified need for contracts, an orchestrator, a harness, or a hypervisor? | Separate architecture and implementation decision. |
| Export | Does another owner need a starting guide or selected retained state? | Approved guide-only seed or selected snapshot procedure. |

Later stages are not automatic rewards for finishing an earlier one. An instrumented controller does not by itself justify a scheduler, general runtime, compiled package, network service, or bare-metal shell.

## 10. Prepare a seed or snapshot carefully

A **guide-only seed** is a reusable starting description of how to set up a workspace. It does not automatically carry original work history, tool source, installed dependencies, runtime state, or old approvals.

A **selected snapshot** is deliberately chosen retained state that an owner wants to preserve or hand off. Its contents, privacy review, restore expectations, identity records, and validation must be proposed before it is made.

Neither term proves portability, recoverability, compatibility, or authority. The receiving owner or harness still has to check compatible inputs, interfaces, and permitted effects.

## First-tool readiness checklist

| Question | Ready when |
| --- | --- |
| What human result is wanted? | The outcome and correctness condition are stated. |
| What source governs the tool? | The relevant interface and reports are named. |
| What may change? | Existing source and new task-output locations are distinguished. |
| Who decides? | Human authority and controller-side assertions are not confused. |
| What happens on uncertainty? | The task has a stop-and-retain boundary. |
| Where is evidence kept? | A fresh, non-overwriting output location is named. |
| How is the result checked? | Validation is bounded and its limits are stated. |
| What is next? | Use, review, correction, or separate growth proposal is explicit. |

If a question has no answer, keep the task in discussion or bounded inspection until it does. Do not fill the gap with an invented controller, installation, authority claim, or automatic workflow.

## Continue through the public method

Use this guide to establish a working place and one honest tool boundary. Then read [How to Instrument a Tool](README.md). Read the [existing-controller guide](HOW_TO_USE.md) only after a specific controller has already been inspected, approved, and validated. The [ES-xOSG-0 working example](es-xosg-0/README.md) is a separate non-executing receipt-classification example, not a generic orchestration runtime.
