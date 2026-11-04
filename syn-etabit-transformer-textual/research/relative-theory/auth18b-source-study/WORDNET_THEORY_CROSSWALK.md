# WordNet-to-project/theory crosswalk

The crosswalk contains ten explicit comparisons. It is a map of possible representation links, not an equivalence table.

## Usable representation proposals

- WordNet lexical and semantic pointers can both be addressable references, provided the original symbol and source/target tuple remain present.
- An adjective position marker can be retained as an annotation and referenced from a replaceable syntax drive.
- A topic-domain pointer can have a project classification edge, provided the source relation remains separately identified.

## Non-equivalences

- `alternative_to` is not WordNet antonymy.
- `related_to` is not WordNet similar-to and supplies no similarity metric.
- project `derived_from` provenance is not automatically WordNet derivational relatedness.
- pointer direction, containment, order and topical domain do not imply Government-and-Binding government or binding.

The last two crosswalk entries are deliberately blocked. No WordNet relation was equated with GB government or binding. Exact loss guards are in `wordnet_theory_crosswalk.json`.
