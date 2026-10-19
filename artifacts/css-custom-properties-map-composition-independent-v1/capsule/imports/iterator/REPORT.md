# Nearest-owner iteration and live indexed enumeration

## Scope

This component proves a generic finite-chain iterator model with arbitrary key type `K`, decidable key equality and arbitrary payload type `V`. It models the corrected iterator and the combined candidate's live-value filtering. Full original, iterator-only candidate and combined native map files are retained under `source/`.

It is a source-shaped Lean proof with an explicit native correspondence review, not a proof of compiled Rust, IndexMap internals, memory safety, count-maintaining constructors or all CSSOM behavior. The prior source/browser audit remains separate. Parent-owned runtime receipts are not imported as proof.

## Proved contracts

`Iterator.lean` represents the mutable current full node, its remaining iteration suffix, the parent chain and all visited descendant nodes. `step` consumes one entry, advances to a parent, yields an entry, or finishes. Shadow rejection consumes the entry and resumes traversal. The rank strictly decreases on every transition. `walk` follows those branches; `Runs` relates complete small-step executions to its output.

The independent reference recursively concatenates a node with the ancestor reference filtered by that node's owned keys. It does not inspect the iterator's mutable cursor or its output. `walk_reference`, `initialized_enumeration` and `traversal_reference` equate the complete source-shaped traversal to that reference. The theorem allows arbitrary finite chains, including empty nodes and more than the native four-ancestor optimization bound.

`CursorHistory.lean` proves that reachable cursors retain the original chain as visited descendants, current node and remaining parents, and that the current suffix is genuinely a suffix of its full node. A single `Next` invocation follows zero or more silent transitions until yield/end. It terminates, preserves cursor coherence and exposes the exact remaining drain. This connects the internal loop to successive public iterator calls. The `None` return abstracts the exhausted mutable cursor; it proves no remaining output and termination, not an exact terminal heap representation. Native descendant membership loops are modeled by finite `any`; their element comparison and list-iteration interface remain admitted below.

`Contracts.lean` proves globally unique emitted keys from per-node key uniqueness, exact nearest-owner lookup, and agreement with the native recursive `get` model. Ownership uses `Option (Option V)`: no owner differs from an owned `None`. A nearer tombstone blocks every ancestral value and remains in raw iteration. `emitted_nearest` binds each yielded entry to its nearest owner.

The final `getIndex` first enforces the stored bound and then indexes the raw iterator filtered by `value.isSome`. `get_index_exact` and the in/out-of-range laws require:

```
stored = (live (reference chain)).length
```

The live projection retains uniqueness and contains only valued entries. The earlier raw-index contract is explicitly named `getIndexRaw` and uses raw enumeration length; it is historical iterator-only behavior, not the final native getter. Neither contract proves that insertion/removal/COW establishes its length premise. A separate count-constructor component must supply the live-count invariant before whole-map indexed access is accepted.

## Counterexamples and mutation gates

Kernel witnesses preserve the original duplicate-ancestor result, corrected one/deep-chain shadowing, tombstone non-resurrection, raw/live indexing difference, empty-node termination and incorrect-count cases. The last cases show why iterator correctness alone cannot establish stored length.

Four semantic mutants alter extracted complete model definitions: discard the shadow decision, omit a visited node on parent advance, ignore tombstones as owners, and remove the live filter. Each mutant's definitions must compile first; the same independently specified finite observations then discriminate it. These are model mutations, not native Rust mutations. Universal proofs and finite semantic discrimination are separate evidence.

## Native bridge and boundaries

`SOURCE-BINDINGS.json` contains every complete method from each retained map file, including the four central definitions: `Iter::next`, `Inner::iter`, `Inner::get` and `CustomPropertiesMap::get_index`. The checker verifies whole-file identity, exact method spans and the iterator-only two-line change. Combined `Iter::next` equals the iterator candidate, while combined indexed access filters `None`. The final combined source is root's formatted `css-custom-properties-enumeration-fix-v2/source/combined.rs`, SHA-256 `9ce38cf97e1ae93c134e80a1efc936f307d7311b8d7cf160331e9fa690ff5e9d`; its historical predecessor differs only in getter line wrapping. The retained insertion and COW methods are context, not silently credited to this proof.

Required native admissions:

- Each IndexMap node has unique keys, `contains_key` and `get` use the same equality, and its iterator traverses the exact immutable ordered entries once with forward progress. The Lean model proves consequences of that interface, not its implementation.
- Borrowed node identities, parent links and entry storage remain valid and immutable during iteration; the admitted chain is finite. Arc/reference lifetimes, SmallVec allocation, allocator failure and compiler semantics are not proved here.
- Rust's `filter`/`nth` and `usize` indexing implement the finite-list operations on representable lengths. Count arithmetic and update history remain obligations of the separate count proof.
- Payloads are opaque: all values and their equality/taint/URL metadata pass through unchanged. This model does not assert that two native payloads with different metadata are equivalent.
- CSSOM invalid-value exclusion additionally needs complete computed values, host gates, registered-property rules, count/FFI/WebIDL and live publication. `None` is the map's removed-value representation, not a proof of every possible CSS invalid-state encoding.

The source bridge is manually reviewed and mechanically pinned; there is no Rust-to-Lean semantic translator. Standard Lean axioms are audited separately. No raw-map uniqueness theorem is advertised as unconditional native or whole-CSSOM correctness.

## Replay

Authenticate the externally supplied freeze, manifest and checker hashes, then follow README. The sealed source root is closed and never receives compiler output. The checker rejects altered or unlisted inputs before creating its fresh output directory, compiles all four modules, audits every listed theorem, checks source correspondence and executes the four model mutants. Historical checkpoint files are explicitly obsolete evidence and are not imported by the proof.

## Validation result

The development source-only replay passed all four modules, 50 exact theorem axiom reports and four compiled model mutants. The first preformat checker invocation failed before compilation because Lean required its input inside the working root; the corrected checker copies authenticated modules into the fresh output. Separate replay receipts preserve that failure and final relocated validation. No native execution is attributed to this capsule.
