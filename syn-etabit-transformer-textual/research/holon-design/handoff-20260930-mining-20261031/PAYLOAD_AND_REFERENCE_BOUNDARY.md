# Payload and Reference Boundary

## Boundary layers

| Layer | Purpose | Evidence/authority boundary |
| --- | --- | --- |
| Native Holon/reference model | Independently represented units and connections | Design incomplete; current direct rule requires references |
| Relationship/coordination model | Meaning and views over references | Broader than depth; final representation open |
| Resolved application view | Selected referenced material assembled for a use | Proposed concept; traversal and fidelity profile required |
| UPST v0.1 application packet | Strict nonrecursive JSON packet | Assistant-generated candidate, locally tested |
| UPTI v0.2 local staging | Preserve/validate bytes and prepare a candidate | No transfer, identity or delivery |
| Future accepted transport | Address/authenticate/deliver/receipt | Not supplied or implemented |
| Artifact reference | Metadata describing a separately obtained file | Does not open/copy/verify availability automatically |
| Protocol attestation | Future evidence role in larger Holon design | Contents and verifier unresolved |

## Reference-native versus nested payload

The v0.1 packet nests body objects. The current direct rule says everything is by reference. The sources support only this boundary conclusion:

- native model and packet need not share physical shape;
- a packet can be a resolved view if its source references and transformation/profile are recorded;
- nested packet data must not silently become owned native objects;
- the mapping must declare omissions, normalization and loss;
- packet IDs and hints do not become Holon identity or authority.

No resolver, mapper or packet profile is implemented here.

## Reference classes that future design must distinguish

1. Target reference: identifies a holon or other independent unit.
2. Occurrence reference: identifies participation in one composition/view, if adopted.
3. Relationship reference: identifies the meaning connecting units.
4. Metadata reference: identifies information about a unit, occurrence or relation.
5. Source reference: points to preserved original material.
6. Transformation reference: identifies an operation or transformation record.
7. Result reference: identifies produced bytes/stream/view.
8. Artifact reference: describes an external artifact without effect permission.
9. Catalog/sentinel reference: identifies a structural definition or represented special state.
10. Receipt/evidence reference: identifies an observation about processing, not authority by itself.

This is a mined classification proposal, not an accepted wire vocabulary.

## Authority checks before resolution

A future resolver should distinguish at least:

- syntactic reference validity;
- target availability;
- target byte identity;
- source authenticity claim;
- caller authority to resolve;
- caller authority to execute or mutate;
- supported target kind/version;
- freshness/replay state;
- recursion/cycle/resource limits;
- fidelity requirements;
- resulting evidence and failure state.

The v0.2 local candidate covers only a subset: local syntax/application validation, size/kind/version assumptions, byte mutation and session-local duplicate IDs.

## Null and sentinel boundary

The application packet's native null is not automatically acceptable inside the future native model. A future adapter must preserve that the source packet explicitly used JSON null in the declared interface, then map it to a cataloged sentinel occurrence only under an accepted profile. Reconstructing the packet may require restoring JSON null exactly.

## Receipt boundary

A local receipt may establish:

- local ID;
- message ID as parsed application data;
- input digest;
- local state;
- local validation outcome;
- byte-change observation.

It does not establish:

- trusted sender;
- remote receiver;
- delivery;
- acknowledgment;
- semantic acceptance;
- authorization;
- independent attestation.

## Safe conclusion

The candidate packages demonstrate that strict boundary packets and local staging can be built without granting them transport or authority. They do not decide the native reference model. Build the reference/relationship semantics first; derive boundary profiles afterward.
