# Stylo Bloom filter verification experiment

This standalone Cargo wrapper includes the existing [Bloom filter](../bloom.rs)
directly. Charon extracts its Rust operations, Aeneas translates them into Lean,
and [BloomProofs.lean](lean/BloomProofs.lean) checks properties of that generated
code. The Firefox build does not depend on this experiment.

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

The ten checked theorems cover:

- Construction and clearing produce an array of zero counters.
- A saturated counter stays unchanged for either adjustment direction.
- The hash mask is 4095, and both hash indices are less than 4096 for every
  32-bit input, including when the indices coincide.
- Reading a slot reports whether its counter is zero.
- Lookup returns true whenever both selected counters are nonzero.

The proofs use the actual 4096-slot array and 8-bit counters. These are universal
local properties, without a bound on sampled inputs. The Rust integration tests
add concrete collision and saturation cases; they are not formal proofs.

The full no-false-negatives theorem for arbitrary operation histories is **not
proved yet**. The next step is to relate the array to a multiset of live hashes:
for each slot, the stored counter is either 255 or equals the number of live
hash contributions to that slot. A hash contributes twice when its indices
coincide. Removal requires that the hash is currently present; clearing resets
the multiset. Proving preservation under insertion and valid removal will allow
induction over operation histories and use of the checked lookup theorem.

The experiment currently covers `BloomStorageU8`. It does not verify
`BloomStorageBool`, arbitrary `BloomStorage` implementations, selector-matching
callers, or probabilistic false-positive rates.

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

## Trust and checks

The connection to Rust depends on the pinned compiler, Charon/Aeneas extraction,
and Aeneas's standard-library models. Lean checks the proofs. This is not a proof
of the native compiler or the resulting machine code.

Extraction retains the unused `is_zeroed` trait method, whose slice-iterator
`all` operation is an uninterpreted external function in the generated model.
Construction, clearing, and lookup reference the trait dictionary, so Lean
reports that symbol transitively in their theorem dependencies. None of those
operations calls it, and no behavioral property of the external function is
assumed. `is_zeroed` itself is outside the verified scope.

The runner checks the exact set of reported theorems and allows only Lean's
standard logical axioms, plus that external function for those three theorems.
It rejects `sorryAx`, additional axioms, missing reports, and Lean warnings.
Resolving the unnecessary external dependency remains follow-up work.

The pipeline uses Charon's generic extraction. Full monomorphization currently
hits an Aeneas array-default prepass failure with the pinned release. The
included source is not rewritten to work around this limitation.

Tool documentation: [Charon](https://github.com/AeneasVerif/charon),
[Aeneas](https://github.com/AeneasVerif/aeneas),
[Lean](https://lean-lang.org/).
