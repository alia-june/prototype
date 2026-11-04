# Reference Inspection Views

## Shared referenced records

Both views reference the same occurrence holons. The occurrence holons in turn reference the same independently represented targets, relationship, and metadata. The views do not copy those bodies.

```text
relationship:R1 ----operation_ref----> target:T1
       |-------------input_ref--------> target:B0
       `-------------result_ref-------> target:B1

metadata:M1 <----metadata_ref---- occurrence:O0 ----target_ref----> target:B0
metadata:M1 <----metadata_ref---- occurrence:O1 ----target_ref----> target:T1
metadata:M1 <----metadata_ref---- occurrence:O2 ----target_ref----> target:B1

Each occurrence also has relationship_ref --> relationship:R1
```

The diagram shows references, not ownership. The single metadata record is deliberately reused to demonstrate reference identity; the pilot does not require all real occurrences to share metadata.

## V0 — chronological inspection

```text
view:V0
  [0] -> occurrence:O0 -> target:B0  "abc"
  [1] -> occurrence:O1 -> target:T1  append "!"
  [2] -> occurrence:O2 -> target:B1  "abc!"
```

This view follows source, transformation, result.

## V1 — reverse inspection

```text
view:V1
  [0] -> occurrence:O2 -> target:B1  "abc!"
  [1] -> occurrence:O1 -> target:T1  append "!"
  [2] -> occurrence:O0 -> target:B0  "abc"
```

This view starts at the result and walks backward for inspection. It does not mutate any record, erase the transformation, execute an inverse, or declare the transformation bypassable.

## What the comparison demonstrates

| Property | V0 | V1 |
| --- | --- | --- |
| Occurrence set | O0, O1, O2 | O0, O1, O2 |
| Array order | O0 → O1 → O2 | O2 → O1 → O0 |
| Referenced target bodies | unchanged | unchanged |
| Relationship | R1 | R1 |
| Metadata | M1 | M1 |
| History mutation | none | none |
| Rollback | none | none |

The change is a view-level permutation of references. The underlying records remain addressable and unchanged.
