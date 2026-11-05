# Publication Decision

## Current state

Sanitation and private-repository publication are complete.

## License decision

On 2026-11-01, the user explicitly directed that the project-owned source be licensed as loosely as possible, published, and not made public. OpenSurface therefore applies the MIT License while retaining authorship as `dastardlyrat and OpenSurface contributors`.

The license grant is recorded in `LICENSE`. It applies to the sanitized project-owned source in this directory, not retroactively to omitted source payloads whose rights were not established.

## Separately licensed material

The omitted Heuristic Offload Engine v0.2 archive contains an MIT License naming copyright 2026 m.A.R.S. Its source is not bundled in this candidate. Any later inclusion must preserve that notice and be independently revalidated.

## Future visibility checks

- rerun the sanitized suite on at least Windows and Linux;
- retain the known portability defect or correct it in a separately versioned child;
- regenerate and verify `MANIFEST.sha256` after every release edit;
- expose only the sanitized tree, never the intake archive or private staging directory;
- require a separate explicit decision before changing repository visibility.

