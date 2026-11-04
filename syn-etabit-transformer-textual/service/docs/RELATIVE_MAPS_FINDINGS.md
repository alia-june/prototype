# Relative and replaceable map probe findings

Findings date: 2026-10-30 (America/New_York)  
Authorization: AUTH-18A  
Status: completed bounded probe

## Result

The mechanical architecture works within the approved slice. Objects, orders,
structures, processes, grammar, syntax, theories, relations, composed drives,
contexts and replacement ledgers can be represented as immutable maps whose
identities change with their exact inputs and recipes. Replacement is contextual
and non-destructive rather than a mutable global head.

No open implementation defect was observed within the final AUTH-18A tests. The
following findings define the boundary for a future design.

## RM-F01 — Relativity needs qualified references

A bare object or category ID is insufficient. Interpretations must bind to exact
map identities, versions and contexts. The probe achieves this through
content-addressed input-map IDs; a durable Etabit design must retain those
qualifiers across storage and reload.

## RM-F02 — Replacement is a new context, not mutation

Context A v2 selects composition B while Context A v1 and Context B v1 continue
to select composition A. The prior composition remains addressable. This is the
minimum behavior needed for “everything is relative and replaceable” without
losing history or making rollback the only recovery mechanism.

## RM-F03 — Order is identity-bearing

The same underlying objects arranged by different order maps produce different
relation and adjective-composition identities. Order must therefore remain a
first-class referenced map, not an incidental array order hidden inside another
record.

## RM-F04 — Theory replacement is proven mechanically, not linguistically

The Government-and-Binding and alternative theory drives are placeholders. The
probe proves that either can be referenced and replaced. It does not establish
their rules or their suitability for WordNet. Actual theory construction needs
designated governing sources and a source-mining/standardization report before
parsing or derivation rules are adopted.

## RM-F05 — Source parsing and theory projection remain separate

WordNet byte offsets, hexadecimal word counts, pointer tuples and raw tokens are
decoded according to the source record form. Theory maps consume the resulting
objects; they do not redefine the archive format. This separation allows source
decoders and theory projections to be replaced independently.

## RM-F06 — The deterministic arbitrary pull is useful

Hash-ranking all 18,185 adjective candidates produced a reproducible sample with
both adjective types, different pointer counts and source marker forms. It is
arbitrary with respect to lexical meaning but replayable. It is not a statistical
or linguistic representative sample.

## RM-F07 — Memory margin is too narrow for expansion

The real probe peaked at 131,297,280 bytes against a 134,217,728-byte ceiling.
It passed, but only by 2,920,448 bytes. The current selection implementation
retains parsed candidates while ranking them. Before increasing record count or
adding more WordNet members, use a streaming fixed-size top-k selector and avoid
retaining every candidate object. Do not treat this pass as capacity evidence
for a full transmigration.

## RM-F08 — The retained packet is not Etabit

The JSON/JSONL evidence packet proves portable identities and references. It
does not prove Etabit path access, map APIs, filesystem semantics, atomic durable
publication, locking, recovery or multi-writer behavior. Those require the real
Etabit locator and interface contract.

## Recommended next decision

Before another implementation, decide which uncertainty to reduce:

1. **Etabit substrate contract:** supply the mounted path and map API, then test
   durable publication/reload of this exact packet without adding linguistic
   semantics; or
2. **Decoder/theory source study:** designate governing grammar, syntax and
   Government-and-Binding sources, then produce a source-grounded relation and
   decoding catalogue without loading the full archive.

Do not combine both into a full WordNet transmigration yet. The memory finding,
real-source rule uncertainty and untested Etabit persistence should be resolved
in bounded stages. GPU and agentic integration remain later; agentic integration
remains last.
