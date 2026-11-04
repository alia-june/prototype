# Reference-Occurrence Inspector

Date: 2026-11-01  
Status: approved bounded offline inspector for the completed reference-occurrence pilot.

## Purpose

This package provides a read-only visual inspection surface for the sibling `reference-occurrence-pilot-20261101` package. It makes the pilot's references and two inspection orders visible without changing the source fixture or claiming a general Docstream runtime.

The inspector demonstrates:

```text
View
  -> ordered occurrence references
       -> target reference
       -> relationship reference
       -> metadata reference
```

It distinguishes the historical transformation `B0 --T1--> B1` from the order in which an observer chooses to inspect the occurrence records.

## Open it

Open `index.html` directly in a modern browser. No server, installation, build, account, or network connection is required.

The application is intentionally compatible with a `file:///` URL. Its source snapshot is carried in `data.js` because browsers do not consistently permit a local page to fetch sibling JSON files. `data.js` is a resolved display packet, not native storage or a new authority source.

## Controls

- **Chronological** displays `O0 -> O1 -> O2`.
- **Reverse inspection** displays `O2 -> O1 -> O0` without rollback or mutation.
- **Compare both** places V0 and V1 side by side and highlights matching occurrence identities.
- Select an occurrence or record to inspect its fields.
- Follow the target, relationship and metadata reference buttons independently.
- Use the record-family buttons to narrow the record index.
- Open **Validation findings** to inspect any detected structural or digest problem.

All source-derived values are inserted into the page as text. The application does not interpret record content as HTML.

## Source boundary

The display packet records the source paths, byte sizes and SHA-256 values for:

- `../reference-occurrence-pilot-20261101/reference_occurrence_contract.json`
- `../reference-occurrence-pilot-20261101/reference_occurrence_fixture.json`

The source fixture was required to pass its existing strict Python validator before the inspector package was produced. The inspector then performs its own JavaScript-side structural, reference, transformation and payload-digest checks.

The SHA-256 checks establish agreement with the named bytes or canonical payload representations. They do not establish authorship, authority, semantic truth, trusted time or permission to execute anything.

## Files

- `index.html` — static semantic interface.
- `styles.css` — responsive visual system.
- `data.js` — provenance-bearing resolved display snapshot.
- `inspector-core.js` — environment-neutral model analysis and comparison functions.
- `app.js` — safe browser rendering and interaction.
- `test_inspector.mjs` — rigid, deterministic fuzzy-error and bounded torture tests.
- `VALIDATION.md` — final executed evidence and proof limits.
- `INSPECTOR_MANIFEST.json` — source and package byte identities; excludes itself.

## Non-capabilities

This inspector cannot edit, execute, undo, cancel, deduplicate, bypass, render, transmit, persist or authorize a transformation. It has no database, service, GPU layer, WordNet/Etabit integration or agentic control. Reverse inspection is a traversal choice, not rollback.

The inspector is a resolved presentation of one bounded fixture. It is not the final native Holon schema and does not modify the existing Docstream runtime.
