# Stylo Bloom filter verification experiment

This standalone Cargo wrapper includes the existing [Bloom filter](../bloom.rs)
and [ancestor-hash packing and rejection](../ancestor_hashes.rs) directly.
Charon extracts their Rust operations, Aeneas translates them into Lean, and
[BloomProofs.lean](lean/BloomProofs.lean),
[PackingProofs.lean](lean/PackingProofs.lean),
[NormalizationProofs.lean](lean/NormalizationProofs.lean),
[StyleBloomProofs.lean](lean/StyleBloomProofs.lean), and
[CoverageProofs.lean](lean/CoverageProofs.lean) check the filter operations.
[RecoveryProofs.lean](lean/RecoveryProofs.lean) checks the extracted recovery
algorithm under its stack and DOM contracts.
[ZeroedProofs.lean](lean/ZeroedProofs.lean) checks the debug zero-counter test.
The Firefox
build does not depend on this experiment.

[RelativeProofs.lean](relative/RelativeProofs.lean),
[CacheProofs.lean](relative/CacheProofs.lean), and
[RelativeBridgeProofs.lean](lean/RelativeBridgeProofs.lean) check relative-region
traversal, cache transitions, and their connection to the same Bloom operations.

See [ROADMAP.md](ROADMAP.md) for the six-milestone plan and current evidence.

## Run

From the Firefox repository root:

```sh
python3 servo/components/selectors/verification/verify.py --bootstrap
python3 servo/components/selectors/verification/verify.py
```

Bootstrap requires Python 3.11 or newer, rustup, Cargo, Git, curl, and a tar
implementation supporting Zstandard archives (GNU tar also needs `zstd`). It
downloads the releases pinned in [toolchain.json](toolchain.json), verifies their
SHA-256 checksums, and installs tools and proof-library dependencies under
`artifacts/stylo-bloom-tools/`. It does not change the default Rust toolchain.
Apple Silicon macOS has been exercised; Linux x86-64 and ARM64 download pins are
provided but have not been exercised.
The current macOS tool and library cache occupies approximately 13 GB.

Subsequent runs use the installed dependencies, run the Rust regression tests,
regenerate the model from the current source, and check the proofs. Generated
models and logs are ignored by Git. Logs are in `generated/`; setup logs are in
`artifacts/stylo-bloom-tools/`.

## Current guarantees

The core suite's seventy-three checked theorems cover:

- Construction and clearing produce an array of zero counters.
- A saturated counter stays unchanged for either adjustment direction.
- The hash mask is 4095, and both hash indices are less than 4096 for every
  32-bit input, including when the indices coincide.
- Reading a slot reports whether its counter is zero.
- Lookup returns true whenever both selected counters are nonzero.
- Insertion and valid removal preserve the relation between counters and live
  hash contributions, including when both indices coincide.
- Every live hash is found after any finite valid operation history, with no
  bound on the history length.
- Packing preserves the low 24 bits of each of the first three hashes and
  reconstructs the fourth when four hashes were collected. Inputs to this
  round-trip theorem are masked to 24 bits, as in the parser.
- Ancestor rejection returns true when each queried hash is live after a valid
  operation history, including the zero-sentinel early returns.
- Insertion, removal and lookup produce exactly the same result for raw hashes
  and hashes masked to 24 bits, for every filter state.
- Masking every hash in a valid history preserves that history's filter state.
  Packing and rejection composed after a raw-hash history cannot reject when
  the collected prefix is live and unused input slots are zero.
- Counters equal live contributions when the historical live-hash maximum is
  at most 127. The production clear helper terminates and returns an exactly
  empty filter, including its optimized removal path, under the append-history
  contract.
- Insertion preserves every nonzero slot and establishes both slots needed for
  its hash, even from arbitrary initial counters. Any finite sequence of actual
  insertions preserves prior hash coverage and covers every inserted hash.
- The extracted recovery algorithm terminates and reconstructs the target's
  ancestor path under the stack, navigation, depth and resource contracts below.
- Append-order high-water histories preserve every live hash's lookup even
  after saturation. A batch of actual insertions extends the recorded hash list
  in order and updates its historical maximum to the larger of its prior value
  and the final live length.
- The debug zero-check loop terminates and returns true exactly when all 4096
  counters are zero. This covers the debug implementation; the public method
  intentionally panics in release builds.

The proofs use the actual 4096-slot array and 8-bit counters, for all 32-bit hash
inputs. The Rust integration tests add concrete collision and saturation cases;
they are not formal proofs.

`Represents` relates each stored counter to the live contributions at its slot:
the counter is either 255 or equals that contribution count. A hash contributes
twice when its indices coincide. The insertion and removal proofs establish
preservation for the operations extracted from Rust, including arithmetic safety.

`ValidHistory` starts with an empty filter and tracks live hash occurrences.
Insertion adds an occurrence, removal selects an existing occurrence anywhere in
the list, and clearing resets the list. Each transition uses the corresponding
extracted Rust operation. `history_no_false_negatives` proves that lookup returns
true for every live hash after such a history. This does not prove that callers
always remove valid hashes or supply complete sets of ancestor hashes.

The packing and rejection proofs use the production Rust module, shared by the
selector parser/matcher and the verification wrapper. `pack_roundtrip` checks
the actual packing and decoding operations. `history_no_false_rejection` checks
the actual rejection loop, assuming every nonzero packed word's low 24 bits and
any nonzero decoded fourth hash are live. Its loop proof also establishes
termination. These assumptions do not prove that selector hash collection and
DOM hash production agree; the differential tests below exercise that boundary.

`pack_match_raw_history` closes the raw-versus-masked gap in that composition.
For inputs `[a, b, c, d]`, the prefix selected by `len` must be live, and the
remaining suffix must be zero padding. The theorem covers all collection
lengths from zero through four, including collected zero-valued hashes. It uses
the extracted packing and rejection operations, with no extra decoding step.
The collector's ability to supply those inputs remains a separate obligation.

The experiment currently covers `BloomStorageU8`. It does not verify
`BloomStorageBool`, arbitrary `BloomStorage` implementations, full
selector-matching callers, or probabilistic false-positive rates.

## Caller clearing proof

[StyleBloomProofs.lean](lean/StyleBloomProofs.lean) adds an exact-counter relation
and an append-order `HighWaterHistory`, matching the hash stack's insertion
order. A hash contributes at most two counts per slot, so a historical maximum
of 127 live hashes keeps counters below 255. The production helper's threshold
of 25 is therefore within that bound. The actual extracted removal loop is
proved terminating and exact; both clear paths return the zero filter, and the
optimized clear establishes a new empty history with high-water zero.

[StorageHistoryProofs.lean](lean/StorageHistoryProofs.lean) connects that same
append-order history to saturated-counter coverage without restricting the
historical maximum. It also checks batch insertion and the exact resulting
high-water value. These lemmas support the production adapter proof; they still
require its storage operations to establish the logical history.

The helper lives in `style/bloom_filter.rs` and is called by `StyleBloom`.
Its contract still requires the supplied hash slice and high-water mark to
correspond to the recorded history. The broader `StyleBloom` recovery and
container-adapter proof is in progress; this is not yet a proof of all callers.

## Recovery algorithm proof

The production rebuilding and recovery loops live in `style/bloom_recovery.rs`.
Twelve principal declarations check finite parent-path collection, depth trimming,
common-parent search, pending-stack reversal, and complete recovery. The theorem
covers Gecko's separate-root behavior and the other configuration's common-root
requirement. It assumes correct element depth, stable parent links and equality,
a valid initial ancestor chain, an empty pending stack, and sufficient bounded
stack capacity. Each push must follow the current parent, including pushing a
root when the stack is empty. These proofs use only standard logical axioms.

`StackContract` states how the production adapter must implement its operations.
The separate [production storage checkpoint](recovery/README.md) connects the
actual storage and recovery operations to this contract under explicit library,
hash-provider, DOM and resource assumptions. The algorithm proof alone does not
discharge those assumptions; actual DOM hash enumeration remains open.

## Relative traversal and cache proofs

The relative suite checks another 42 theorems and two concrete witness
definitions. Together with the core suite, the runner audits 117 declarations.
Its wrapper includes the production `relative_selector/filter.rs` and extracts
the traversal, entry update, target selection, cache lookup, and Bloom operations.
An LLBC metadata check rejects any retained mock selector collector or matching
types; only the copied match-hint enum may remain, and its variants are checked
against the production enum.

Under a finite forest, stable navigation, and terminating callbacks, the
extracted traversal terminates. On success it visits exactly the direct children
or strict descendants of its root, once each; on failure it stops at the first
unsuccessful callback. A concrete branching-and-chain forest inhabits the
navigation contracts.
Target-selection and key proofs cover child/subtree distinctions and sibling
anchors. The cache proof checks first lookup without construction, successful
publication, retry after an unavailable hash provider, and reuse. An unsuccessful
construction never publishes a partial filter.

The bridge proves equivalence between the relative and core extractions of
actual Bloom insertion and lookup. If a successful element callback performs
exactly the insertions in a fixed hash list, every hash from the requested
region is present in the built filter. The list retains ordering and duplicate
hashes; for Gecko it describes the masked hashes supplied by
`each_relevant_element_hash`. Failed callbacks may change their temporary
filter, which is discarded. Callbacks must terminate.

`get_filter_no_false_negatives` composes this with cache lookup: every returned
filter accepts every supplied region hash, and all cached entries retain their
coverage. This assumes a fixed cache epoch with stable tree links, hashes, and
injective element identities, and sound preexisting entries. It does not prove
that a matching selector's collected hashes belong to that region; milestone 6
addresses that separate obligation.

The wrapper substitutes opaque standard-library map operations for hashbrown's
matching entry API. `MapContract` explicitly assumes successful map calls,
entry selection, updates to only the requested key, and the generated borrow
return behavior. It also specifies the boxed filter borrow. These library
semantics, allocation success, and Gecko's navigation/hash providers are outside
the checked implementation. The source audit below supports the cache lifetime
assumption; it is not a machine-checked concurrency proof.

## Operation-history exploration

The Rust tests also compare the production code with independent models:

- [tests/histories.rs](tests/histories.rs) explores 148,602 prefixes of valid
  insert/remove/clear histories, up to five operations from each of five initial
  states. The hashes exercise shared slots, coincident indices, and ignored high
  bits; initial states include counters just below and above saturation.
- [tests/style_bloom.rs](tests/style_bloom.rs) checks 60,000 recovery histories
  across the 120 five-node forests whose parents precede their children. Each
  history visits three targets, with optional pushes after the first two visits.
  Another 1,536 histories exercise deep and shallow branches around saturation
  boundaries. The oracle checks depth, current parent, slot occupancy, clearing,
  and thread-local reuse.

The wrapper enables the production `gecko` recovery branch by default, including
transitions between separate roots. Its atoms and DOM interface remain mocks.
`--no-default-features` tests the common-root branch instead. Both debug and
optimized runs pass; this exploration has not found an additional defect.
These are bounded checks, not formal proofs of `StyleBloom` or its callers.

## Differential selector matching

The separate [differential crate](differential/tests/matching.rs) links the real
`selectors` crate, including its CSS parser, ancestor-hash collection, matcher,
and relative-selector filter cache. The verification runner builds it against
Firefox's vendored dependencies and runs it in release mode.

It compares matching with filters disabled against ancestor-only, relative-only,
and combined filtering. Its 2,668 generated selectors run over all 24 four-node
forests whose parents precede their children, four label assignments, all three
quirks modes, every element, and three repeated lookups: 27,661,824 comparisons.
The grammar includes combinators, namespaces, attributes, case differences,
`:is()`, `:where()`, and `:has()` with nested selectors and sibling traversal.
Failures report the selector, forest, labels, element, and filtering mode.

An additional 5,788,800 comparisons exercise five hash profiles (ordinary,
colliding, zero low bits, mixed zero low bits, and shared low bits with different
upper bytes), 24-node chains, branching trees and separate roots, and nested
selectors through depth 16. The total is 33,450,624 comparisons. Mismatches are
replayed and greedily reduced by removing nodes, selector text, labels and cache
setup probes while retaining the failure. Controlled faulty hash providers
validate reduction for both ancestor and warmed-cache relative failures. Reduced
cases retain consistent class/ID attributes; reduction does not promise a
globally minimal case.

Additional checks exercise shared filters across different selectors and retries
when an element cannot provide hashes. A targeted check counts hash-provider and
class-matching calls to establish that repeated lookups build, reuse, and reject
through the relative filter. The selector-result cache is reset between passes
so it cannot bypass those checks.

Both debug and optimized runs pass. These are bounded comparisons using a mock
DOM and deterministic string hashes. They do not cover Gecko's atom hashing,
shadow DOM, mutation/invalidation, or every selector grammar production, and are
not a formal proof of selector matching.

## Bugs found in callers

### Saturation survives clearing

`StyleBloom::clear()` selected its removal fast path from the current hash-stack
length. After a deep ancestor chain saturated counters, recovering to a shallow
element could shrink that stack below the threshold. Removing the remaining
hashes then left saturated counters behind. Debug builds failed the zeroed-filter
assertion; release builds retained stale counters across thread-local reuse,
allowing additional false positives. No false negative was demonstrated.

The fix records the largest stack since the previous clear. A stack that has
always held at most 25 hashes cannot saturate a counter: even with coincident
indices, it contributes at most 50 to any slot. Larger stacks use the full reset.

[tests/style_bloom.rs](tests/style_bloom.rs) compiles the actual
`style/bloom.rs` with a minimal mock element interface and the vendored
`smallvec` and `atomic_refcell` crates. It exercises depth recovery, clearing,
and drop/reuse, including threshold and saturation boundaries. Both tests fail
against the original caller and pass with the fix. This is a Rust regression
reproducer, not a Lean proof of the caller or an end-to-end browser test.

Run the local tests independently of the proof tools:

```sh
cargo test --offline --locked --manifest-path servo/components/selectors/verification/Cargo.toml
cargo test --offline --locked --release --manifest-path servo/components/selectors/verification/Cargo.toml
```

### Subtree construction consumes stack proportional to DOM depth

The relative-selector filter's `add_to_filter()` recursively visited descendants.
The production function aborts with stack overflow on a 100,000-element mock
chain in a thread with a 128 KiB stack, in both debug and optimized builds.
The fix walks child, sibling, and parent links iteratively, stopping at the
requested root. It uses constant auxiliary space.

[tests/relative_filter.rs](tests/relative_filter.rs) includes the production
filter source with mock element and selector interfaces. The selector adapter
supplies a hash directly; it does not exercise parsing or CSS matching. The
deep-chain check runs in a subprocess so a stack-overflow abort becomes a test
failure. Additional cases check sibling branches, children-only traversal,
subtree boundaries, cached reuse, and retry after unavailable element hashes.
These tests do not establish reachability through a browser page or constitute
a formal proof of the traversal.

## Browser regressions

Two Web Platform Tests exercise the production callers through the DOM and style
system:

- [ancestor-filter-saturation-crash.html](../../../../testing/web-platform/tests/css/selectors/ancestor-filter-saturation-crash.html)
  uses 256 repeated class tokens on one ancestor, followed by an ancestor with
  few hashes. It detects the clearing assertion in builds with Rust debug
  assertions enabled; release builds do not expose stale counters to the page.
- [has-deep-subtree.html](../../../../testing/web-platform/tests/css/selectors/has-deep-subtree.html)
  matches two `:has()` selectors against the same direct child while a deep
  subtree is hidden from layout. Firefox metadata dispatches style work to
  workers to exercise their smaller stacks. The test also checks the resulting
  computed color.

After building Firefox locally, run:

```sh
./mach wpt --headless --no-pause-after-test testing/web-platform/tests/css/selectors/ancestor-filter-saturation-crash.html testing/web-platform/tests/css/selectors/has-deep-subtree.html
```

Use a debug build, or add `ac_add_options --enable-rust-debug` to a local build
configuration, to exercise the clearing assertion.

Both tests crash an unpatched macOS arm64 debug build at `976279105b2e`.
With the fixes applied and Rust debug assertions enabled, both pass three
consecutive local runs. A control using only one `:has()` selector also passes
on the unpatched build with the same deep DOM and worker preference.

### Mutation and tree-boundary coverage

Three additional WPTs check independently expected computed styles after DOM
mutations, with style flushes between transitions:

- `filter-dynamic-mutations.html`: class/ID/attribute changes, subtree moves and
  removal/reinsertion, child-versus-descendant regions, namespace and case rules.
- `filter-shadow-mutations.html`: shadow boundaries, named slot reassignment,
  moves between shadow roots, and host removal/reinsertion.
- `filter-quirks-mutations.html`: class/ID case folding and mutations in a real
  quirks-mode document.

All 33 checks pass over three local repetitions. These tests use actual style
and query lifetimes, not retained caches mutated in place. They have no internal
filter hit counters or filter-disabled browser oracle; the instrumented Rust
checker supplies direct filter-execution evidence.

After the caller extraction refactors, a fresh native build with Rust debug
assertions also passed all five browser tests for three repetitions: 42 checks,
with no unexpected results.

## Cache epoch boundary

`SelectorCaches` owns the relative filter map. The DOM entry points
`element_matches`, `element_closest`, and `query_selector` in `style/dom_apis.rs`
each create a fresh local cache. `ThreadLocalStyleContext::new` also creates a
fresh cache; `driver::traverse_dom` owns its thread contexts through a local
`ScopedTLS`, which releases them at traversal completion. The direct style
resolution entry points in `ports/geckolib/glue.rs` create local thread contexts.
`match_relative_selectors` bypasses relative matching when
`matching_for_invalidation_comparison` is set, before accessing these caches.

This source audit supports using a query or traversal as the cache epoch. The
relative proof assumes that DOM links, relevant element hashes, and opaque
identities remain stable within that epoch. It does not prove Gecko's exclusion
of concurrent DOM mutation or make a retained map safe across mutations.

## Selector collection checkpoint

The separate [collection experiment](collection/README.md) checks the exact
production simple-component hash policy for generic atom types, equality,
hash functions, and attribute-policy contracts. Its runner regenerates the
model from current Rust source. It uses an isolated patched extraction tool,
a checked-shape removal of an unused associated-type slot, and explicit
read-only Arc representations; those additional trust boundaries are documented
there. This theorem is outside the 117-declaration default suite. A second
isolated runner checks the actual relative iterator, collector loop, and singleton
recursion with sixteen theorems and three collector dependency audits, including
preservation of untouched array slots and zero padding. A third
runner adds four local-name matching bridge theorems. They connect the actual
local-name helper to collected hashes under explicit atom and DOM-provider
alignment contracts; they do not extract the full CSS matcher. The ancestor
collector contract is checked separately below; deriving its premises from
actual successful matching remains open.

The combined rejection runner freshly rebuilds the core and matching models and
checks 64 exact dependency reports. It composes local-name collection with actual
packing and Bloom rejection under the existing matching, hash-alignment and
history premises. Ten negative tests cover audit and freshness failures.

The ancestor runner checks 49 exact dependency reports after extracting the
production collector through a borrowing helper. These establish iterator
behavior and whole-collector termination, required-hash inclusion, preserved
array contents and zero padding under explicit finite-depth component policies.
Nine tests check the extraction boundary. The combined ancestor rejection runner
checks 90 reports, composing this contract with actual packing and Bloom lookup.
Seventeen guard tests cover both rejection runners. Actual successful matching
must still imply the component policies, and DOM enumeration must supply the
corresponding region hashes.

## Production storage checkpoint

The isolated [recovery experiment](recovery/README.md) extracts shared production
storage alongside the existing core model and checks all 73 core theorems
unchanged. Eighty-three additional theorems cover storage operations, coherent
element/hash histories, finite insertion resources, and actual rebuild/recovery
composition. The rebuild theorem establishes the ancestor chain and successful
lookup of its enumerated hashes, including after saturation, with exact borrow
restoration. Seventeen provider theorems connect the actual insertion callback
to its finite trace, establish completion under count/capacity/allocation bounds,
and instantiate rebuild/recovery with the concrete provider. One further theorem
checks exact insertion behavior against the preserved original Rust method,
including the result and future borrow restoration. Together the runner checks
174 theorems.

Both opaque DOM enumeration callbacks must still emit the same finite hash list
for an element; the actual enumeration body has not yet discharged that contract.
Library semantics, allocation and DOM/forest contracts remain explicit
assumptions. Recovery also requires the exact supplied depth, coherent equality,
a valid initial chain, and the shared-root condition when separate roots are
disallowed. The provider cleanup passes a native build, 42 browser checks and
ten Rust regressions in each of four configurations.

The [roadmap](ROADMAP.md) records subsequent isolated native-provider work:
conditional enumeration and provider checks, a typed trace interpretation, and
a conditional history application. Those results do not yet discharge this
runner's complete enumeration contract or native backward-function
correspondence. They remain separate from the 174-declaration checkpoint.

## Trust and checks

The connection to Rust depends on the pinned compiler, Charon/Aeneas extraction,
and Aeneas's standard-library models. Lean checks the proofs. This is not a proof
of the native compiler or the resulting machine code.

The zero-check implementation uses an explicit early-exit loop so extraction
can use the modeled slice iterator operations. Its exact predicate and
termination are checked; no opaque iterator `all` operation remains in the
core or relative proof dependencies.

The runner checks the exact set of reported declarations. All 73 core theorems
allow only Lean's standard logical axioms. Relative proofs additionally permit
precisely listed opaque map,
hashing, and boxed-borrow declarations where the library contracts require them.
Those allowances apply only to the designated cache and bridge theorems. The audits reject
`sorryAx`, unlisted axioms, missing or duplicate reports, and Lean warnings.

The pipeline uses Charon's generic extraction. Full monomorphization currently
hits an Aeneas array-default prepass failure with the pinned release. The
included source is not rewritten to work around this limitation.

Tool documentation: [Charon](https://github.com/AeneasVerif/charon),
[Aeneas](https://github.com/AeneasVerif/aeneas),
[Lean](https://lean-lang.org/).
