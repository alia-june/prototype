# xOSG-0 developmental architecture

xOSG-0 is a developmental line of orchestration research. Its architecture is best read as a sequence of reductions, additions, and tests, from ES-xOSG-7 through Seed. The retained artifacts describe different generations and supporting mechanisms. They do not form one integrated runtime to launch.

Start with the [canonical growth spine](growth/README.md), then use the [source ledger](docs/SOURCE_LEDGER.md) to distinguish retained packages, reconstruction evidence, and missing originals. This line is distinct from the [xOSG instrumentation family](../docs/xosg/README.md); placement in the same repository does not establish integration or shared authority.

## Developmental spine

| Stage | Architectural question | What to read it as |
| --- | --- | --- |
| [ES-xOSG-7](growth/spine/00-es-xosg-7/README.md) | What broad predecessor was reduced to create xOSG-0? | Documented genesis. The source ledger does not identify an original ES-xOSG-7 archive among the supplied packages. |
| [Bare-metal 0](growth/spine/01-xosg-0-baremetal/README.md) | What is the smallest inspectable control substrate worth carrying forward? | Declarative reduction: machine description, technical logic, operating prompt, working registers, and retained human direction. |
| [v0.2 actualization](growth/spine/02-xosg-0-v0.2/README.md) | What changes when the model acquires executable state? | Persistent state and registers, CLI operations, runtime schema, and transition history. Read the [historical v0.2 architecture](history/v0.2.0/architecture/xOSG-0_architecture.md) as version-specific evidence. |
| [v0.3 deterministic hardening](growth/spine/03-xosg-0-v0.3/README.md) | How should a stateful runtime behave when persistence, locking, or recovery fails? | A stage organized around deterministic controls and state integrity. Reconstructed evidence is not an original v0.3 binary. |
| [v0.4 loose/fuzzy hardening](growth/spine/04-xosg-0-v0.4/README.md) | What happens when the input is malformed, ambiguous, or outside clean assumptions? | Adversarial pressure on the deterministic substrate. Retained fuzzy evidence and reconstruction do not establish recovery of an original v0.4 binary. |
| [Seed](growth/spine/05-seed/README.md) | What minimum coherent kernel is justified by the preceding work? | An extraction after hardening, distinct from genesis, the full archive, and a release bundle. |

## Roles to trace while reading

- **Human direction and authority.** Identify who sets the objective, approves action, and decides what evidence to accept. A state transition or generated record is not by itself a grant of authority.
- **State and transition mechanics.** Distinguish declared registers and operating rules from the stages that persist state, execute CLI operations, and retain transition history. Follow the stage-specific source for what is actually present.
- **Validation and failure evidence.** Separate ordinary execution from deterministic tests and loose/fuzzy challenges. Record which artifact and version support each claim, including what was reconstructed and which original artifacts remain missing.

The [supporting development](supporting/README.md) covers the learning layer, operator kernel, operator/orchestrator, deterministic offload, and goal scaffolding. These are mechanisms to read alongside the spine. Their package versions and filenames do not replace the primary developmental sequence or establish that all mechanisms ran together.

## Reading route

1. Use the [project README](README.md) to choose a generation or theoretical application.
2. Read the [growth guide](growth/README.md) and the relevant stage page. Ask what the stage inherited, what pressure caused it to change, and what survived into the next stage.
3. Check the [source ledger](docs/SOURCE_LEDGER.md) and [import status](docs/IMPORT_STATUS.md) before treating a snapshot as an original or a retained mechanism as an operational dependency.

This page is a map of the published lineage and its evidence boundaries. It does not qualify a runtime, reproduce a test campaign, or supply a unified installation guide.
