# Theory inspector validation

Status: **focused PASS; full-project regression FAILED with two isolated reruns PASS**.

The inspected AUTH-18B index pins six JSON files totaling 32,598 bytes and 77 records. The package loaded the actual packet, resolved all structured links and traced `XW-ADJECTIVE-MARKER-A` across crosswalk, WordNet, theory-map, generic, source and sample catalogs.

Sixteen focused methods passed. They include rigid query/trace/CLI behavior, hardening against tamper, path escape, duplicate keys, duplicate IDs, executable fields and broken links, 120 fuzzy invalid controls, 200 loose search inputs, 500 deterministic repeated inspections and an explicit 128-link trace ceiling. Rejected operations did not change the copied packet; successful operations are read-only.

The dashboard rendered all 77 records at 1440×900 and 360×800 with zero page errors and exact viewport body widths. Data is packaged locally; the application makes no network request and displays catalog content using `textContent`.

The full 267-test project discovery run produced two errors in existing deadline/child-cleanup tests. Both exact methods passed on immediate isolated rerun. The failed full run is retained as evidence; no out-of-scope harness changes were made.

The validator establishes packet integrity against its local index and bounded behavior of this implementation only. It does not independently validate the source theory or permit decoding beyond `DECODE_BOUNDARY.md`.
