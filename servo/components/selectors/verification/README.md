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

## Saturated ancestor clearing reproducer

The standalone harness compiles the production `style/bloom.rs` with a mock
element interface and vendored `smallvec` and `atomic_refcell` dependencies.
Its two regression cases cover recovery from a saturated ancestor chain,
clearing, and thread-local reuse.

The regression expectation is an empty filter after clear or reuse. The
original implementation can leave saturated counters when recovery shrinks
the current stack; a suitable repair must account for its earlier size.
The reproducers are initially ignored so this preparation commit keeps the
default suite passing. Run them explicitly to observe the original failure:

```sh
cargo test --offline --locked --manifest-path servo/components/selectors/verification/Cargo.toml --test style_bloom -- --ignored
```

A browser experiment uses 256 repeated class tokens on one ancestor and then
visits an ancestor with few hashes. The unpatched macOS arm64 debug build at
`976279105b2e` crashes; the candidate clearing repair passes three local runs
with Rust debug assertions enabled. Release builds do not expose the stale
counters to page script. No false negative has been demonstrated.

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
