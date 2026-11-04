# Native vocabulary pilot findings

Findings date: 2026-10-30 (America/New_York)  
Authorization: AUTH-17  
Approved pilot status: complete

## Result

The pilot demonstrates that bounded WordNet word-form occurrences can be mapped
to exact safe-ASCII native `WORD` definitions while keeping source semantics,
relations and provenance outside the definition payload. Identical
constructions deduplicate by definition ID, while duplicate source occurrences
remain separately locatable. The final run and maintained verifier pass within
all approved resource ceilings.

No open implementation defect was observed within AUTH-17 after the two
development corrections documented in validation. The following are design
findings and scope limits, not claims of full vocabulary completion.

## NV-F01 — The exception cap is not a promised count

The selected Princeton source provides only seven eligible single-token adverb
exception pairs in `dict/adv.exc`, so the complete final pilot has 82 pairs
rather than 100. This confirms that quota caps and source availability must stay
distinct. Future reports should not manufacture padding or relabel natural
end-of-file as a resource failure.

## NV-F02 — Collocations need a separate native decision

Two hundred three collocation tokens containing `_` were encountered before the
four form quotas were filled. They were deliberately excluded. Treating `_` as
a literal underscore, a space, a phrase boundary or an encoded source separator
changes native structure and therefore requires a separate proposal. The pilot
does not silently choose among them.

## NV-F03 — Explicit fragments are structurally useful but sparse

The established 11 definitions are reused whenever their exact lowercase bytes
occur; all other bytes pass through literal `SymbolRef` fallback. This is
deterministic and lossless, but it is not a useful morphology engine by itself.
Growing the fragment registry should be an explicit curated operation with
provenance and conflict handling—not an inference derived from WordNet spelling
or exception relations.

## NV-F04 — WordNet does not provide the requested root construction

Synsets, lemmas and exception form/base relations do not identify the project's
meaning-free glyph/component/root decomposition. AUTH-17 therefore creates no
`ROOT` definitions. For example, the presence of `marionette` does not license
an etymological `mario` or `marion` root. Root declarations need their own
governing source or direct project decisions.

## NV-F05 — The current native capacity is sufficient only for a pilot

The final run used 1,014 of 4,096 definitions for 1,003 unique constructed word
strings plus 11 fragments. A complete WordNet load would exceed this catalog
ceiling and also needs durable persistence, indexing, reload, migrations and
resource policies. Those are not authorized by AUTH-17. “Absorb WordNet” should
not proceed as a larger loop over the current in-memory model.

## NV-F06 — Provenance is durable evidence; the native catalog is still ephemeral

The retained JSONL artifacts preserve selected source occurrences, relations,
construction traces and definition IDs. The in-memory `NativeModel` is rebuilt
deterministically during verification, but there is no durable native vocabulary
store or service operation yet. A next production proposal must decide whether
the source records and native catalog belong in the existing SQLite service, a
separate immutable catalog, or another bounded store before expanding intake.

## NV-F07 — WordNet semantics remain useful but orthogonal

The source contains synset and pointer information that could later support
lookup or agent assistance. Embedding that information into the meaning-free
native construction payload would conflate spelling structure with lexical
semantics. If used later, it should remain a separately versioned annotation
layer linked by explicit provenance.

## Recommended next move

Do not absorb the rest of WordNet into the current in-memory catalog. The next
useful scope is a storage-and-query design review based on these retained
records: immutable catalog identity, source-occurrence tables, explicit fragment
registry ownership, deterministic rebuild or snapshot rules, capacity/index
budgets and atomic publication/recovery. A concrete proposal and fresh approval
are required before implementing or bulk-loading that store. GPU and
agentic-control integration remain later; agentic control remains last.
