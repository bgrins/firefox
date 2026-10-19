# Animation composition preserves property identity

## Result and boundary

The Lean model proves that endpoint composition, iteration accumulation and segment interpolation preserve the owning property identity and have the option values required by their unwrap/expect sites. Readiness follows from the actual map-wrapper underlying-value guard. Finite map updates from empty preserve unique keys and key/value identity coherence. A separate constructor proof establishes unique declaration identities, membership agreement, aligned normal-importance bits and mutable storage.

This is a conditional universal model theorem. It is not a whole-program source-interpretation theorem, native compiler proof, animation arithmetic proof or browser conformance result. No defect, production patch, native execution or new browser test is claimed.

## Independent obligations and definitions

`Value` has an arbitrary identity and arbitrary payload. The general theorems require no payload equality. Its derived equality instance is available only when the component types supply equality, and is used for concrete examples; general proofs never assume it.

`Preserves arith` requires only that a successful arithmetic operation on equal-identity operands returns that identity. It does not require success, expected payloads, or final output/map coherence. Arithmetic may depend on procedure, accumulation count, both payloads and an opaque interpolation progress bit encoding. Providers are pure functions in this model; effectful/native execution correspondence is an external obligation.

`OptId key option` constrains only present values. `Ready key option` additionally proves presence. The two-level result of `composite` and `accumulate` distinguishes outer `none` (an unavailable native unwrap/expect value) from `some none` (valid arithmetic failure or unchanged endpoint selection). Failures are therefore not erased by assigning an expected result.

For admitted actions, the supplied `ActionId` premise relates the segment's optional endpoints, last endpoint and optional base value to the owning property. Rejected identities place no coherence constraint on their unused values. It does not assume the composed result. Proving segment grouping and the base/FFI provider relation remains a separate component. Map lookup derives its relation from the inductively established map invariant.

## Source-shaped composition

The authenticated complete source bindings cover:

- `composite_endpoint`: replace retains the original; add/accumulate use the underlying value; absent endpoints clone underlying; arithmetic failure is a valid absent composited value.
- `accumulate_endpoint`: a present composited endpoint survives arithmetic failure; otherwise failure leaves selection to the original endpoint. Its missing-original unwrap is proved ready.
- `compose_animation_segment`: both endpoint compositions, optional iteration accumulation, last-or-underlying fallback, final endpoint selection, zero-length selection using total-progress sign, interpolation and half-progress fallback.
- `Servo_AnimationCompose`: invalid/nonanimatable identity skip, exact need-underlying disjunction, current-map-before-base lookup, missing-base skip, and final insert.
- `Servo_ComposeAnimationSegment`: the direct wrapper. Its caller must establish the readiness guard; this wrapper does not perform the map wrapper's missing-base check.
- `from_animation_value_map` and the generated/custom identity providers listed below.

`Composite` has exactly replace/add/accumulate, as in the retained WebIDL. The unrelated keyframe `auto` enum is not a segment mode. `active` is iteration-accumulate AND count greater than zero. `need` includes either absent endpoint, either non-replace mode, or active iteration accumulation with absent last endpoint. `guard_endpoints` and `guard_last` derive the readiness premises from this disjunction and successful missing-base guard passage. `compose_ready` proves complete presence and identity, including arithmetic failures.

Numerical decisions are represented by the actual branch results: equal keys, negative total progress and segment progress below one half. The interpolation provider additionally receives an opaque progress-bits natural number. The identity theorem holds for arbitrary branch results; it does not prove floating comparisons, timing, easing, IEEE arithmetic or a concrete bit encoding. Native count/progress-width correspondence remains external. In particular this does not eliminate the non-NaN premise needed by the upstream segment-grouping loop.

The model's `selected` combines each endpoint's iteration update and final selection. The source updates both endpoint options before either final selection. These pure computations have the same value dependencies; no theorem of operation trace, side effects or evaluation timing is claimed. Every possible missing-value path is still represented and excluded by the derived readiness theorem.

## Map and constructor composition

`lookup` searches a finite unique association list. `insert` replaces the key by filtering its old entry and adding the new pair. These are abstract finite-map operations; no native HashMap iteration order or hash-table implementation proof is claimed. `step_ready` proves that admitted coherent inputs either retain the map through an early return or insert a coherent result. `finite_updates` permits arbitrary finite action lists, duplicate update keys and arbitrary payloads. `from_empty` initializes without an assumed nonempty invariant. `missing_base_retains` and `inadmissible_retains` state the early-return behavior exactly.

`ConstructorIdentity.pushEntry` separately appends an uncomputed declaration and inserts the **map key** into membership. `build` executes this loop and then creates an independent false importance vector of map length. `loop_storage` derives the loop result for arbitrary initial storage. `constructor_ids` uses the map coherence and uncompute identity premises to connect actual declaration IDs to keys; it does not define them to agree. `constructor_representation` proves unique declarations, matching importance length, bidirectional membership agreement, all-normal importance and mutable state (`mutable` models the inverse of native `immutable`, initialized false). `map_history_constructor` composes the arbitrary finite update theorem with that representation result.

The membership list represents set insertion by prepending keys; native set semantics, allocation, vector capacity and bit-vector implementation remain source admissions. No constructor enumeration order is asserted beyond the chosen native enumeration, and a unique enumeration is required. Counterexamples show why coherence, uncompute preservation and uniqueness cannot be omitted.

## Generated/custom provider evidence

The copied static capsule is externally authenticated by its original FREEZE and MANIFEST hashes. Fifteen complete function bodies are retained with source path, context anchor, start position, body and hash, and re-extracted during checking. Complete source files remain in the closure. The historical whole-file glue.rs SHA-256 is `f850eec636e6740d5582c1dcea66f69f8b50c59f8f576167e2bcab6fb080cf9a`. This is not a claim that later live glue.rs bytes are identical. The selected composition functions have their own body pins. A separately investigated change to `Servo_GetComputedKeyframeValues` must receive a new caller/source binding; that function is an upstream admission here, and this proof establishes neither its value representation nor custom-property interpolation correctness.

Generated `AnimationValue::animate` checks discriminant equality and writes the first input tag on successful arithmetic; unequal longhand tags panic. `CustomAnimatedValue::animate` checks the custom name, propagates arithmetic failure and copies the name on success. The arbitrary `Preserves` contract represents these successful paths, conditional on generated representation and compiler correctness; it does not promise arbitrary mismatched native inputs return safely. Generated clone and uncompute retain the longhand tag, or use the corresponding typed variant; custom uncompute retains the name even when its payload is absent and emits an initial declaration. The latter payload absence is distinct from an absent animation endpoint.

`from_declaration` physically normalizes logical properties before the computed keyframe provider derives its identity. `from_computed_values` constructs the requested physical variant or the requested custom name, or returns absent. The complete generated templates and custom methods are pinned, but code generation, unsafe layout/tag correspondence, custom atoms, Rust/C++ identity conversion and cloning are not proved here. The frozen static report retains the upstream computed-entry, segment-building, transition-replacement, base-cache and selected-segment caller chain. Segment grouping, nonempty arrays, bounds, non-NaN offsets, scheduling, FFI aliasing, allocation failure, layout and machine arithmetic remain explicit external obligations.

No AllOrder or PublicStorage theorem is imported; this component gives its own small independent constructor-storage proof. It can be composed with the public storage representation later through a separately reviewed mapping.

## Validation and limitations

There are 49 theorem declarations: 26 general lemmas, two contract proofs for concrete universally failing/successful providers, and 21 concrete kernel examples. The examples cover representative selection, failure and missing-base branches, priority of existing map values over base, nonempty histories and construction, plus counterexamples to removed arithmetic, readiness, endpoint, constructor coherence, uncompute and uniqueness assumptions. They are kernel witnesses, not compiled semantic mutants or native/browser experiments.

All source modules compile in order into a fresh external directory. Each theorem receives an axiom audit accepting only Lean's standard `propext`, `Quot.sound`, and `Classical.choice`; custom axioms, sorry, admit and native_decide are rejected. The source binding checker verifies all 15 complete records and the three-value segment enum. The retained static audit is a source argument, not executable native correspondence.

The complete input roster is authenticated before local source execution. The checker rejects shadowing files/packages, symlinks, nonregular files, unexpected empty directories, duplicate JSON keys, path escapes and output inside the capsule. Nine corruption controls exercise these rejections. Python isolated mode and a fresh Lean output path exclude accidental repository imports. Compiler/standard-library correctness and the pinned executable remain trusted.

The retained recorded source replay passed all 49 theorem audits and all nine integrity controls. Final handoff requires fresh canonical and manifest-only relocated replays, exact result/axiom receipt agreement and repeated integrity controls. Commit only the manifest roster plus MANIFEST.json and FREEZE.json; generated objects and execution outputs stay outside the capsule. Independent review remains a separate gate.
