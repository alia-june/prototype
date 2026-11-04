# WordNet relation catalog

This catalog records what Princeton WordNet's own documentation defines. It does not reinterpret WordNet as a grammar theory.

## Relations present in AUTH-18A

| Symbol | Source-defined relation | Encoding in sample | Count |
| --- | --- | --- | ---: |
| `!` | antonym | lexical, non-zero word positions | 2 |
| `&` | similar-to | semantic, `0000` | 10 |
| `\` | pertainym | lexical, non-zero word positions | 3 |
| `+` | derivationally related form | lexical, non-zero word positions | 3 |
| `;c` | domain of synset — topic | semantic, `0000` | 1 |

The sample contains eight lexical and eleven semantic pointers. “Lexical” and “semantic” here describe the pointer tuple's scope; they are not statements about a project's internal grammar or theory drive.

## Source structures and markers

The machine catalog separately records adjective clusters, head synsets, satellite synsets, relational adjectives, participial adjectives, the attribute relation, and the `(p)`, `(a)` and `(ip)` adjective-position markers. Only `(a)` occurs in the eight-record sample, on `all-around(a)` and `all-round(a)`.

The exact 16 records, source IDs, locators, status and cross-catalog links are in `wordnet_relation_catalog.json`.
