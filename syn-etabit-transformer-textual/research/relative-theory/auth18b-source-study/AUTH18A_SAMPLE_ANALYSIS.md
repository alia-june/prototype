# AUTH-18A sample analysis

The inspected evidence is the retained AUTH-18A packet at `.docstream/etabit-map-tests/auth18a-vertical-composition-probe`.

- `source-records.jsonl`: SHA-256 `542d639812dd21764772dc569204e7b7f1abee5f81554b91aa319440f8663042`
- `relations.jsonl`: SHA-256 `6c915f82e1aed8e71b9ab10ea0e6b1237685f583c1b907af267955e447c1fa55`

The eight selected adjective records are `nonexempt`, `prismatic`, `attentional`, `headed`, `first-string`, `newfound`, the three-word `all-around(a)`/`all-round(a)`/`well-rounded` synset, and `aleuronic`. Their 19 retained pointers resolve to 17 one-hop target records.

The sample demonstrates:

1. source bytes and hashes can remain independently addressable;
2. WordNet pointer types can be catalogued without folding them into generic edges;
3. a source marker can be referenced by a replaceable syntax map without changing the source record;
4. a crosswalk can preserve a blocked theory comparison instead of inventing an interpretation.

It does not demonstrate linguistic completeness, a morphology decoder, Government-and-Binding validity, or corpus-scale ingestion. Exact sample records and aggregates are in `auth18a_sample_analysis.json`.
