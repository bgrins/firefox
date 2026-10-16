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

## Remaining interpretation work

Connect the observed invariant to concrete element-vector representation and
full recovery. An isolated `native-storage-element-step` candidate adds one
postcondition retaining the actual element-vector primitive push transition.
Its 26 storage tasks pass; the other 42 models match after checked source-location
normalization. Wrong-endpoint and wrong-count controls leave only the added
postcondition unproved. These timeouts are sensitivity checks, not counterexamples.
The separate `native-storage-elements-lean` interpretation is in progress.

Interpret the native continuation separately: `StoragePushProofs.ProviderCalls`
requires an exact backward-function equation that a normal-return trace does
not supply. Do not assume that equation to claim the native gap is closed.

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

Native allocation-enabled completion, continuation correspondence, DOM hash
stability, thread safety and complete recovery remain open. No additional
Firefox defect is established by this checkpoint. The two existing production
fixes and their WPT commits are unchanged.

The old roadmap is retained byte-for-byte because earlier reviewed evidence
pins its contents. Experimental packages and their toolchains remain local
artifacts; this file records their scope and reproduction entry points.
