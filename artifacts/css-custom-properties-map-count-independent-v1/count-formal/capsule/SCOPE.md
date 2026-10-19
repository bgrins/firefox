# Live-value count: scope and admissions

This component proves the mathematical state transition selected by the count repair in `servo/components/style/custom_properties_map.rs`. It does not prove Rust execution, the raw iterator implementation, CSSOM publication, or the entire custom-property system.

## Proved contract

A node is an ordered finite list of unique keys, each with `Option V`. The parent chain is finite. `ownFind` returns `Option (Option V)`: a present tombstone stops parent lookup. `Some` values are arbitrary, including an empty string; no serialization-based validity test is used.

The independent reference enumerates a finite, unique key roster, performs nearest-owner lookup, and includes exactly successful values. The roster is constructed from the initial chain and future operation keys. It is not assumed to omit uncounted keys. The counter update is separately defined by the native old/new-presence match.

`count_transition` proves that inserting into the first node changes reference cardinality by precisely that match. Existing-key replacement, absent-key append, tombstone shadowing, and parent resurrection are covered. `decrement_headroom` derives positive count before subtraction. `increment_headroom` derives representable addition from a bound on the finite roster; it does not assume successful native allocation implies that bound.

`Ready` combines stored-count equality, roster coverage and unique keys within each node. It is preserved by initialization, unique-owner insertion, shared no-op, copy-on-write and new-parent-chain insertion. Arbitrary finite operation histories preserve it. `history_lookup` separately proves agreement with a function-update reference, assuming only that a successful value comparison implies semantic equality. Counter coherence and index safety do not need this comparator assumption.

`RawEnumeration` is an explicit bridge: raw entries have unique keys and contain exactly each nearest owner, including tombstones. Under this bridge, filtering present values has the proved count and every index below stored count returns an entry. An unconditional theorem shows that any returned filtered entry is present. A kernel witness shows why the count-only source's still-buggy iterator cannot discharge this bridge.

## Native representation and API admissions

1. Atom equality corresponds to `DecidableEq K`; IndexMap has unique keys, replaces an existing key without creating a duplicate, and preserves other entries. Container internals are not verified.
2. A finite, acyclic, nonempty parent chain represents the actual `Arc<Inner>` graph. Shared parent snapshots remain stable. Clone/make_mut/get_mut and allocation normal completion supply the modeled branch outcome and logical copy. Actual refcounts, aliasing and allocation failure are not modeled.
3. The initial singleton empty node corresponds to `EMPTY`. For threshold correspondence, `ancestor_count = chain.length - 1`; the native threshold constants are 8 and 4. The model proves expansion's depth bound under this representation, not a Rust graph construction theorem.
4. Native `usize` arithmetic agrees with mathematical arithmetic when the finite roster fits its bound. Decrement headroom is derived. Native `u8` increment follows the expansion check with faithful ancestor metadata. Compiler, memory, execution-stack, allocation and integer representation semantics remain trusted.
5. The semantic payload equality used for an early shared no-op is sound when true. Reflexivity or completeness is unnecessary. Actual `ComputedRegisteredValue` equality, taint and URL-context semantics are outside this component. Counter preservation remains true even without this payload premise.
6. Shrinking capacity and cloning preserve logical contents. External callers construct or retain states satisfying `Ready`; there is no migration theorem for a preexisting corrupted original counter.
7. The separate iterator component must establish `RawEnumeration` for its actual modeled drain. The present package deliberately does not import an unaccepted checkpoint. Combined source is retained for exact later composition; no correctness claim is made for original/count-only raw iteration.
8. CSSOM combines inherited/noninherited maps and observes their iterators. Those callers, registration selection, style scheduling and browser lifecycle are outside the theorem. Browser discovery preceded this proof.

## Source versus theorem

The retained full files and 48 complete function bindings authenticate the selected source. A handwritten abstraction maps native methods to the Lean definitions. Textual binding and source review are not a verified Rust-to-Lean translation. The source ledger identifies this admission rather than promoting a model theorem to an all-input native theorem.
