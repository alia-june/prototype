# Actualization Notes — revision 0.2.0

The original xOSG-0 artifact defined the architecture but left runtime state implicit.
This revision makes the design inspectable and locally executable.

## Added
- explicit runtime state machine;
- persistent five-register store;
- capability/claim boundary in runtime behavior;
- provenance conventions;
- behavioral change-control classification;
- machine-readable runtime schema;
- repeatable validation command;
- atomic local state writes;
- explicit distinction between requested and completed actions.

## Deliberate non-features
The runtime does not spawn hidden agents, alter the underlying model, elevate privileges,
access external accounts without an available integration, claim unsupported completion,
or silently change xOSG-0 behavior.

This is an actualized workflow engine for the documented overlay, not autonomous hidden
multi-agent infrastructure.
