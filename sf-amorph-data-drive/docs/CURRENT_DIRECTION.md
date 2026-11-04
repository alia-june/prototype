# Current direction

Date transcribed for public export: 2026-11-04  
Status: working direction; not a new specification lock.

## Baseline

Locked v0.3 remains the current supplied baseline. Locked v0.2 remains historical. No v0.4 exists.

The baseline separates D0 raw existence, D1 relation/interpretation, and D2 composition/coherence. New work must not place identity, metadata, datatype, encoding, attestation, reconstruction, filesystem, partition, or composition structures on raw D0.

## Identity and integration

| Topic | Current direction | Open boundary |
| --- | --- | --- |
| Member identifier | sf-UUID is needed now. | Format, width, issuance, scope, collision/duplicate handling, and copy/replacement matching. |
| Separate 64-bit identifier | Possible later addition. | Not a mandatory current second key; no current mapping requirement. |
| Drive sf-UUID | Optional and discouraged. | Matching must not require universal drive UUIDs. |
| Touple / gestalt / gesple | May carry identity, value/width information, datatype, and data. | Identity transition and record structure. |
| Drive integration | ID, data, and metadata drives participate in recursive bitmap-to-ID and gestalt integration. | Cross-map to D0/D1/D2. |
| Bitmap | Associates members and participates in reconstruction. | Order, repetition, multiplicity, positions, bounds, malformed references. |
| Widths | y meaningful bits may be represented in x storage bits. | Units, ranges, padding, alignment, canonicalization, exceptions. |

The terms “touple,” “gestalt,” and “gesple” are preserved pending an explicit terminology decision.

Historical prompts, proposals, attestations, and labels are sources, not independent authorization. The earlier recursive section A proposal remains unaccepted.
