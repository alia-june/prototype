# AUTH-18B source register

Status: **PARTIAL — GOVERNING SOURCE MISSING**.

This register distinguishes sources actually read from sources merely identified. It does not treat search results, bibliographic records, publisher descriptions or previews as substitutes for formal theory text.

## Governing WordNet material

- `SRC-WN31-ARCHIVE` — the retained Princeton WordNet 3.1 database archive. AUTH-18B reuses the eight-record AUTH-18A sample; it does not rescan or absorb the corpus.
- `SRC-WN-WNDB` — Princeton's database-file reference, governing pointer tuples and lexical-versus-semantic encoding.
- `SRC-WN-WNINPUT` — Princeton's lexicographer-file reference, governing pointer symbols, adjective clusters and adjective position markers.
- `SRC-WN-WNGLOSS` — Princeton's glossary, governing source-specific structural terms such as head, satellite and pertainym.
- `SRC-WN-LEXNAMES` — Princeton's lexicographer-category list, used as supporting documentation.

The Miller 1993 ACL record is retained only as historical context. The exact machine format is governed by the reference documentation above.

## Intended Government-and-Binding sources

- Chomsky's 1981 *Lectures on Government and Binding* was bibliographically identified and a publisher preview was checked, but substantive governing text was not available in the bounded study.
- Chomsky's 1982 *Some Concepts and Consequences of the Theory of Government and Binding* was identified through its MIT Press record. The publisher description confirms broad topics, not formal rules.
- Lasnik and Uriagereka's *A Course in GB Syntax* is registered as a companion source only.
- Marantz's 1981 MIT thesis is registered as a contrast source only; its institutional record was read, not mined for rules.

Consequently, the project may register topic names and the evidence gap, but it may not define government, binding, Case, ECP or empty-category relations from these descriptions. Exact structured records are in `source_register.json`.
