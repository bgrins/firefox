# Live-count and iterator composition

## Result and scope

This component closes the mathematical interface that the two predecessor components left open. The actual modeled cursor drain satisfies the count model's `RawEnumeration`, and arbitrary finite repaired constructor/COW histories derive the iterator getter's live-count premise. These are universal generic-key/payload theorems, not a finite matrix or an assumption that the desired enumeration already holds.

The complete final native source is identical in both imported capsules: `custom_properties_map.rs` SHA-256 `9ce38cf97e1ae93c134e80a1efc936f307d7311b8d7cf160331e9fa690ff5e9d`. `SOURCE-JOIN.json` authenticates the original and final whole-file identity. Both predecessor snapshots and checkers remain byte-for-byte unchanged.

## Composition

`Composition.lean` proves the correspondence of the independently written lookup definitions. Iterator `ownFind` returns an entry; count `ownFind` returns a nested Option. `own_find_entry`, `nearest_entry`, `owner_bridge` and `lookup_bridge` preserve keys and payloads exactly, including a present tombstone. `valid_bridge` equates per-node pairwise key inequality with key-list Nodup.

`emitted_membership` proves both directions: raw emitted membership iff the nearest count-model owner has that exact payload Option. It uses the actual source-shaped cursor traversal, its independent recursive reference and the per-node key invariant. `raw_enumeration` then derives the unique-key and exact-owner obligations. No cached/fresh enumeration equality is supplied as a premise.

`ready_live_count` applies the count model's independent key-roster cardinality theorem to that derived raw enumeration. `ready_reference_count` discharges the exact length premise of the iterator's final filtered getter. `getter_bridge` verifies that both source-shaped getter definitions are definitionally equal. Bounds, exact list indexing and present nearest-owner values follow.

`Histories.lean` composes the count constructor's `finite_history` with those results. For every finite sequence from the empty initial map, with arbitrary supplied unique/shared branch outcomes and comparison results:

- Stored count equals the length of the actual iterator's live projection, at every operation prefix.
- Each index below stored count returns an entry; an index at or above it returns None.
- Returned entries are live and come from the nearest owner. Two returned entries with the same key have the same index.
- The indexed result equals the independent nearest-owner reference's live projection.

No external live-count premise or RawEnumeration premise remains in these history theorems. No payload-comparison soundness premise is needed for readiness, count or index safety. Only `history_value_reference`, which compares resulting payloads with an independent sequence of requested updates, requires `CompareSound`. A witness shows why an unsound shared early-return comparison can preserve count/readiness while ignoring the requested value.

## Reachable counterexamples and discrimination

`CompositionWitnesses.lean` starts from the empty store and inserts nine live properties. The original algorithm then removes one through the unique-owner path and resurrects it through a shared expanding path. Its stored counts are 9 then 10 although independent live cardinalities are 8 then 9; the latter has a genuine two-node chain. These witnesses model the complete original old-count/COW branches rather than assuming an inflated initial counter.

The repaired history uses shared deletion after the nine-key threshold, retains the nearer tombstone, and then resurrects it. Count is 8 then 9 and all indices below count are proved present through the universal composition theorem.

The checker replays all eight predecessor semantic model mutants and three additional compiled wiring mutants: use flattened duplicate raw iteration, omit the live index filter, and collapse owned None into missing owner. The same finite observations distinguish them. The additional mutants validate the integration projections; they do not replace universal proofs or constitute compiled Rust mutation evidence.

## Native admissions retained

This is a manually source-bound model proof, not a verified Rust translation. It inherits the exact pinned full methods and source assumptions from both predecessors. In particular:

- Atom equality, unique IndexMap keys, replacement and iteration order implement the finite key/list interfaces. Native payloads are represented without discarding taint or URL-context data.
- Arc uniqueness/copy behavior and finite immutable parent snapshots supply the modeled branch and chain; allocation and reference lifetime safety are not proved. Actual ancestor metadata must match chain depth.
- Rust filter/nth/get and integer conversions implement their model operations. Native arithmetic needs representable finite rosters and faithful usize/u8 semantics; mathematical Nat theorems do not prove unbounded Rust arithmetic safe.
- Sound successful native value comparison is required only for the requested-update value semantics claim. Counter/index safety does not acquire that assumption through the join.
- Initialization and repaired histories are covered; no migration from an original corrupted live counter is proved.
- Two-map disjointness, inherited/noninherited registration routing, CSSOM concatenation, FFI/WebIDL, style invalidation and publication remain outside this per-map proof. Per-map index safety is not a whole-CSSOM correctness theorem.

Standard Lean axioms and the external pinned Lean runtime/library are audited as stated by the checker. Native Rust, browser and Firefox build execution are absent from this component. Root's browser receipts and independent source reviews remain separate.

## Replay

Authenticate the external freeze/manifest/checker pins, then run `check.py` with Python `-I -S` and a fresh external output directory. It authenticates the closed entire source closure before importing/executing either predecessor checker, replays both predecessor proofs/mutations, joins their freshly compiled modules, checks every new theorem's axioms and runs the wiring mutants. The 105 inherited theorem audits and 32 new audits are reported separately. Generated outputs never enter the sealed input root. Relocated replay and tamper receipts are separately sealed.
