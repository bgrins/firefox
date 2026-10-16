# Native storage interpretation checkpoint

This checkpoint supplements the pinned [roadmap](ROADMAP.md). Milestones 1, 2,
3 and 5 retain their checked checkpoints; milestones 4 and 6 remain open.
The next target is native storage/recovery composition, followed by an actual
matching-to-rejection result for `section > span`.

## Reviewed storage trace adapter

The isolated package is
`artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-lean`.
Its `check-v3` run and independent `reviews/check-v1` replay pass:

- Eight exact Lean theorem/axiom audits.
- Seven rejected mapping mutations, including a changed native exit hash
  vector, `current` versus `final`, declaration origin, binder scope and width.
- Rechecked source, model, proof and output inventories for the prerequisite
  481-obligation, 43-model native storage checkpoint.
- Separate invalid-input checks that remove stale acceptance output.

The generated predicates retain all four typed vector alias definitions, the
complete provider trace, and all six storage endpoint/count equalities.
`providerSymbols` explicitly interprets the new symbols; Lean checks the
insertion-trace and readiness correspondence by definitional equality.
`witness_ready` derives provider readiness from the native entry hash conditions
and the storage witness's zero initial count.

`storage_hash_history` obtains extracted insertion calls, a representation of
exactly the native exit hash vector, and conditional hash/filter high-water
history. It does not identify native vectors from equal observed hash lists.

Evidence fingerprints:

| Record | SHA-256 |
| --- | --- |
| `check-v3/report.json` | `647c1bf24c4c91eda911d63809ca8938d6ec5362da9e2b5f74e129982f4a46b8` |
| `reviews/check-v1/report.json` | `7806a111d9923d31a86cb07dc374301943ca965f96c6abcd39b6f1263361be24` |
| `reviews/ADAPTER-FINAL-REVIEW.json` | `d8eab67b979148265a112f62a853c07e1507f8cd62bb0b66434782a88ff6799b` |

Reproduce using a fresh output directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-lean/check_adapter.py check-v4
```

## Reviewed storage observations

The second isolated package,
`artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-observations`,
exports the native function's five numbered entry conditions and ten numbered
exit conditions. Its `check-v1` run and independent `reviews/check-v1` replay
pass eight theorem/axiom audits and six rejection controls. Independent clause
review checks their original Why3 groups, binders, typed variables and record
constructor metadata.

`stored_high_water` identifies the actual stored value with the maximum of the
entry high-water value and the final hash count. `appended_record` identifies
an ordered append of the element and its policy-event count, under explicit
record-constructor and sequence interpretations. `stored_history` combines the
hash trace with the stored high-water observation. Record append and hash
history are still separate conditional results at this checkpoint.

The controls reject a changed AST fingerprint, missing clause, unsupported
borrow projection, reversed comparison, wrong record count and wrong final
record-vector endpoint. The last control retains its historical `record-order`
label; it mutates the endpoint, not sequence order.

| Record | SHA-256 |
| --- | --- |
| `check-v1/report.json` | `85096259d39a57a48581a183e840f4f4ac0c7712c928cefc7420fb6df3d2a26c` |
| `reviews/check-v1/report.json` | `a7d3ad4aa49e198082bc7c3be7848154fe143953d200b1b04ff91ad4b810c0de` |
| `reviews/OBSERVATIONS-FINAL-REVIEW.json` | `346217a9546562b6e47b3894c1f2771b1f53e8ee55c6907453f00b2c8e0109e9` |
| `reviews/CLAUSE-PROVENANCE-REVIEW.json` | `bd2b6233db38be93a67d52c2ee0a5189643d0f84d2d11602109d1f558d63597e` |

Reproduce using a fresh output directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-observations/check_observations.py check-v2
```

## Reviewed observed storage invariant

`artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-invariant`
combines the observations. Its `check-v2` run and independent `reviews/check-v1`
replay pass two exact theorem/axiom audits and six rejected mutations.

`observed_push_valid` preserves high-water history, the ordered concatenation
of each record's policy hashes, and each recorded hash count. The observed
record chain gains the pushed element at its head. The result retains a
representation of the exact native exit hash vector and a related extracted
sink with auxiliary count reset to zero, permitting another push. This reset
is a witness construction, not a native continuation interpretation.

`valid_lookup` proves lookup succeeds for a policy hash of an element in that
record chain. The proof uses only standard logical axioms. Actual DOM ancestry
and stability of the fixed element-hash policy remain separate obligations.

The controls cover reversed record flattening, a changed count, chain order,
wrong vector endpoint, missing count reset and missing hash membership. The
flattening mutation breaks both push preservation and lookup; the checker
requires both expected failures. Invalid manifest controls remove stale
acceptance output.

| Record | SHA-256 |
| --- | --- |
| `check-v2/report.json` | `fdc1a2d370a51b363fa63afde0c1631627eddf20f0e7e0f9e380d35d5e1fd607` |
| `reviews/check-v1/report.json` | `a50776428f0907e568642d71032fd630d8f9542cb8912266b7ee852c867fa9f0` |
| `reviews/INVARIANT-FINAL-REVIEW.json` | `964e12ff05038dca5a796be1199ddc64d1c962ff4513667e2334c5c3f6a7a776` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-invariant/check_invariant.py check-v3
```

## Reviewed element-vector interpretation

The isolated `native-storage-element-step` package adds one source postcondition
retaining the actual element-vector primitive push transition. Runtime bodies
and trusted primitive specifications are unchanged. All 26 storage tasks pass;
the other 42 models match after checked source-location normalization.
Wrong-endpoint and wrong-count controls leave only the added postcondition
unproved. These timeouts are sensitivity checks, not counterexamples.

`native-storage-elements-lean/check-v1` and independent `reviews/check-v1` both
pass 19 exact audits and six mutation controls. Fifteen definitional equivalences
preserve the earlier numbered source clauses. The new theorem consumes native
element-vector validity, spare capacity and the transition postcondition to
obtain an extracted push and representation of the exact native exit vector.
Count encoding is checked under the explicit 64-bit width.

The element primitive refinement includes native constructor correspondence;
this remains an explicit assumption. The result does not identify vectors from
observed lists or install a new aggregate native proof certificate.

| Record | SHA-256 |
| --- | --- |
| `native-storage-element-step/EVIDENCE-v1.json` | `0789419352af80e664e704a6fee0319efd13e115a908ba639071f58ba989f9ec` |
| `native-storage-elements-lean/check-v1/report.json` | `c0e49f5f934e37624b147b0aceeebe0fc430ec3af3d7ef3a0de9f87d4fd5b67d` |
| `native-storage-elements-lean/reviews/check-v1/report.json` | `f831ecbce9d087e7773c110409dd76d58b5b39bab9ba52c76a22532f7352c15f` |
| `native-storage-elements-lean/reviews/ELEMENTS-FINAL-REVIEW.json` | `7ceca9050ec12d5422f845069e752f72c809e3e777a0c613536f471b3dd9d5c8` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-elements-lean/check_elements.py check-v2
```

## Reviewed concrete storage representation

`native-storage-representation/check-v1` and independent `reviews/check-v1`
pass 20 exact audits, including freshly compiled existing recovery modules,
and six rejected mutations. `valid_iff` and `chain_eq` connect the observation
relation to the existing `StorageInvariantProofs.Valid` and `chain` definitions.

`push_representation` combines both vector witnesses, propagates initial
record-list compatibility through the native and extracted append results,
and constructs a related extracted storage state. It preserves the exact native
exit hash and element-vector representations, recovery validity and chain order.
No vector identity follows merely from equal observed lists.

The controls reject wrong vector endpoints, stored high-water, chain order,
missing record compatibility and changed counts. The existing `SequenceModel`
also contains pop, clear and dereference contracts; their native semantics
remain assumptions. This is a representation theorem, not proof that an actual
extracted storage call produced the constructed state.

| Record | SHA-256 |
| --- | --- |
| `check-v1/report.json` | `18468ebd76cbcd66a3d5306c835d6fa15afa6eae94a832375f93091f6e5746bb` |
| `reviews/check-v1/report.json` | `474d0f1505b0e549467a371f853c14eff58c938a0f9f45442c408fa1e876f660` |
| `reviews/REPRESENTATION-FINAL-REVIEW.json` | `58e8fc2d262d0f35790f46c5863020648da4c1b5062915c346f0efed3c65ddca` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-representation/check_representation.py check-v2
```

## Reviewed provider normal return

`native-provider-normal-return/check-v1` and independent `reviews/check-v1`
pass eleven exact audits and five rejection controls. All 23 proof outputs are
byte-identical between the producer and independent replay. Invalid manifest
controls remove stale acceptance output.

`actual_return_view` derives the actual returned enumeration view and the full
provider backward-function equation directly from a successful call to the
extracted provider. Its continuation restores the initial count while preserving
the future filter and hashes. No enumeration-behavior premise is needed for
this equation.

`actual_calls` derives the existing `StoragePushProofs.ProviderCalls` from a
success-only contract for the actual opaque enumeration return. A separate
proof shows that preservation of just the returned state's filter and hashes
suffices for the extracted storage push history; the record uses the actual
returned count. Controls reject a changed reset source, returned view, hash
frame, recorded count and missing enumeration premise.

The success-only enumeration contract remains an assumption. It does not prove
completion and may hold vacuously when enumeration fails. The theorem establishes
the extracted provider's continuation, not a general native backward-function
translation.

| Record | SHA-256 |
| --- | --- |
| `check-v1/report.json` | `7cc2521655423255efeaf2554d6711e9d9ff0f50091dabac43bf55fa57277f87` |
| `reviews/check-v1/report.json` | `b198cdbf7da1eb5975931c7d7646b079f5dde4de9c0714377f9033c08b3ce722` |
| `reviews/RETURN-FINAL-REVIEW.json` | `1459a1016d6cfd41ca25daddc43f8360858822621501cb7300f94d124d4c897e` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-provider-normal-return/check_return.py check-v2
```

## Remaining interpretation work

Connect the native enumeration trace to the exact successful return of the
opaque extracted enumerator, preserving its callback, ordered events and
initial/final endpoints. An existential represented state with equal observed
lists does not establish that correspondence. The actual provider continuation
equation is now proved separately and need not be assumed.

The retained enumeration extraction failure involves nested-borrow restoration.
Its proposed tool extension needs a justified association between symbolic
projections and future arguments before implementation. A separate native pop
experiment preserves the production body and debug checks; it is exploratory,
not an accepted recovery proof.

The matcher still has a preserved verifier limitation involving its borrowed
dynamic callback, associated data and mutable cache reference. The reviewed
runtime capability experiment remains separate from storage interpretation.

## Scope and assumptions

These are scoped interpretations of pinned generated predicates and conditional
Lean implications. They are not a general verified Why3 importer or an
end-to-end native execution proof. Applying the native storage result requires
its full source preconditions, including independent element-record capacity
and native type invariants. Sequence/counter meaning and primitive vector
refinement remain explicit. The imported extracted library retains opaque
SmallVec operations, recorded in the axiom inventory.

Native allocation-enabled completion, enumeration correspondence, DOM hash
stability, thread safety and complete recovery remain open. No additional
Firefox defect is established by this checkpoint. The two existing production
fixes and their WPT commits are unchanged.

The old roadmap is retained byte-for-byte because earlier reviewed evidence
pins its contents. Experimental packages and their toolchains remain local
artifacts; this file records their scope and reproduction entry points.
