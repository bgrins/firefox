# Borrowed storage extraction experiment

This directory preserves a native Aeneas/Charon tool correction needed to
extract the concrete Stylo recovery adapter. It is a local experiment using
pinned Apple Silicon macOS binaries. It does not replace the default toolchain
or complete the StyleBloom adapter proof.

## Reproduce

From the Firefox checkout root, with the existing local tool cache:

```sh
python3 servo/components/selectors/verification/recovery/check.py
```

The runner checks the executable and patch hashes in `tool-patch.json`, extracts
the Rust cases, checks generated Lean, and audits three `invoke_exact` theorems.
Logs and generated files go to
`artifacts/stylo-bloom-tools/recovery-binder-check/`. The expected stage results
are recorded in `expected-results.json`.

The native binaries were built from the source archives and prerequisite
patches recorded in `tool-patch.json`, with OCaml 5.3.0 and the
`aeneas-5.3` opam switch. Apply `fuse-region-binders.patch` at the Charon source
root and `instantiated-trait-names.patch` at the Aeneas source root, then run
`dune build main.exe` from Aeneas's `src` directory. The binary hashes describe
the retained builds in this checkout; builds on other platforms require their
own recorded provenance. The runner currently uses the pinned macOS ARM64 Lean
installation.

## Corrected behavior

`Substitute.fuse_binders` shifted method region indices by the number of outer
outlives predicates. It must shift by the number of outer region parameters.
Otherwise independently bound lifetimes can collide: ending a method's receiver
borrow also ends the lifetime stored inside the receiver.

The naming patch distinguishes trait declarations carrying `PeInstantiated`
metadata and their implementations. Such declarations can have no remaining
`Self` type parameter. The patch changes extracted names only; explicit impl
rename attributes retain their existing behavior.

| Case | Outer regions / outlives predicates | Original borrow check | Corrected borrow check | Corrected Lean |
| --- | --- | --- | --- | --- |
| `repro.rs` | 1 / 0 | Fails | Passes | Passes |
| `two_regions.rs` | 2 / 0 | Fails | Passes | Passes |
| `two_regions_outlives.rs` | 2 / 1 | Fails | Passes | Unsupported backward output |
| `two_regions_equal.rs` | 2 / 2 | Passes | Passes | Passes |

The three successful `invoke_exact` proofs check the actual generated concrete
trait dictionary and generic invocation. Given successful checked additions,
they establish both the updated values and the exact returned borrow functions:
independent lifetimes propagate their respective borrowed fields, equal
lifetimes propagate both fields together, and each function restores the
original owned field. Their audits allow only the standard logical axioms.

A one-way outlives relation still reaches an unsupported backward-abstraction
output in `SymbolicToPureExpressions`. The ordinary unmonomorphized borrowed
`Self` dictionary also remains ill typed. These are separate remaining tool
limitations.

## Production provider and recovery verification

```sh
python3 servo/components/selectors/verification/recovery/verify_storage.py
```

The combined runner checks 174 declarations: 73 existing core proofs, 83 storage
and recovery adapter proofs, 17 concrete provider proofs, and one exact equivalence
theorem against the preserved original insertion method. The default verifier
and its tools remain unchanged. This runner uses the separate local binaries
pinned in `provider-tool.json` on Apple Silicon macOS.

`crate/lib.rs` includes the production Bloom, storage, recovery, and DOM-provider
sources in one extracted namespace. The DOM shim preserves the used `TElement`
bounds and the shared receiver of `traversal_parent(&self) -> Option<Self>`.
It models `SendElement` as its transparent element wrapper. Parent/equality
correspondence remains an explicit contract; this is not extraction of the full
Gecko DOM trait, its internals or the unsafe thread-transfer justification.

The production callback captures `HashInsertBorrowed`, whose private fields
reborrow the filter, hash buffer, and count. Its checked operation increments
the count, inserts into the filter, and appends to the hash buffer, in that order.
The verification-only `storage_hash` wrapper calls these production operations
through `sink.borrowed().push_hash(hash)`. No duplicate insertion algorithm or
unused production wrapper is maintained for the proof.

`baseline/old_bloom_storage.rs` is the immutable pre-refactor source, with its hash
recorded in `baseline/source.json` and pinned by `provider-tool.json`. Each run
extracts that original method alongside the current production borrowed methods.
`WrapperEquivalence.exact_behavior` proves equality of the complete results and
returned restoration functions for arbitrary future states, including failure
and divergence. Updating production must not replace or repin this original
source as its own equivalence baseline.

### Proved connection and remaining assumptions

`HashInsertProofs.Calls` uses successful calls to the actual extracted
`storage_hash` wrapper. It establishes the exact appended hash list, insertion
history, count increment, and restoration of the owned count. The provider
proofs connect the actual callback and returned restoration function to this
trace. The expected-hash callback is also extracted and checked.

`ProviderCompletionProofs` proves successful completion under explicit finite
count/hash bounds and library allocation assumptions. `ProviderModelProofs`
instantiates the existing adapter contract with the actual extracted `DomHashes`
dictionary. The per-element hash bound and element capacity imply the necessary
hash-buffer bound. `ProviderRecoveryProofs` then specializes the existing rebuild
and recovery hash-retention theorems to that concrete provider.

The production `each_relevant_element_hash` enumeration is still opaque.
`Enumeration` assumes that its two callback instantiations execute the specified
finite folds over the same stable list. This is an unresolved behavior proof,
not a claim that DOM primitives alone have been abstracted. The known generic
trait-method callback specialization limitation prevents extracting the complete
enumeration today. In particular, the checked provider composition does not yet
prove the actual local-name, namespace, ID, class, and attribute enumeration
policy or its stability during a recovery epoch.

Other explicit premises remain: coherent SmallVec/Vec sequence and allocation
contracts, DOM parent/equality correspondence, a finite ancestor forest, valid
initial history/ancestor contents, empty pending stack, exact supplied depth, and
sufficient capacity. Recovery permits separate roots only under its stated
configuration; otherwise the theorem requires the shared-root condition.
Complete caller verification is not claimed.

### Isolated tool corrections and reproduction

`provider-tool.json` pins the native binaries, patch files, original Lean backend
inventory, immutable baseline, compiler executables, and original elaborator
source. Its native prerequisites are recorded in `tool-patch.json` and
`storage-tool.json`.

To rebuild the native snapshots:

1. Use the pinned Charon source revision
   `26abff028ced534ebf8e861f2d3dd1743e2aa318`, Rust nightly `2026-09-17`, and its
   locked dependencies. Apply `provider-tools/captured-lifetime-inference.patch`
   at the Charon root. Build `charon` and `charon-driver` with
   `cargo build --locked --no-default-features --features rustc --bin charon --bin charon-driver`.
2. Start from the Aeneas source archive and prerequisite patches in
   `tool-patch.json`, including the recovery binder/naming corrections and the
   ordinary-function naming patch in `storage-tool.json`. Apply
   `provider-tools/specialized-fn-traits.patch` and
   `provider-tools/specialized-fn-unit-output.patch` at the Aeneas root. Build
   `dune build main.exe` from its `src` directory using the recorded OCaml 5.3.0
   `aeneas-5.3` opam switch.
3. Retain rebuilt executables under separate cache paths and record their hashes
   before use. The recorded binary hashes identify the reviewed local builds;
   other builds/platforms require their own provenance and validation.

The Charon correction infers closure-region mutability from captured fields,
including nested closures, without changing ordinary ADT metadata or the original
infection predicate. Unused lifetimes remain shared; residual unknown metadata
is not claimed to be fully classified. An earlier experiment that treated every
unknown lifetime as mutable was rejected because it broke shared/noncapturing
closures. The Aeneas changes use specialized `FnMut`/`FnOnce` signatures and
preserve unit outputs when the originating generic trait requires them.

The runner rebuilds a fresh isolated Lean import overlay for every invocation.
It applies `provider-tools/normalize-caseson-type.patch` to the pinned original
`Aeneas.Do.Elab` source and recompiles it. That one-line correction normalizes the
scrutinee type before selecting constructor-eliminator universe levels. The
original backend stays untouched. Its complete file inventory is checked before
and after the run; the generated overlay inventory, including compiled companions
and symlink destinations, must also remain unchanged. Other installed Lean
packages and the Lean sysroot remain explicit toolchain trust.

Seven tracked controls in `provider-tools/controls/` exercise mutable ownership,
nested mutable captures/closures, shared captures, noncapturing/inherited
lifetimes, and generic unit returns. Each is freshly extracted and checked in
Lean against `expected.json`. The preexisting ordinary-function naming regression
also remains checked. These tool controls supplement the actual production
proofs; they do not verify the extraction tools themselves.

### Evidence and guards

Each run deletes previous generated models, overlays, and success evidence before
checking prerequisites. It rejects Charon embedded errors, mismatched embedded
source, opaque production functions, missing entry points, and unexpected theorem
or axiom reports. Provider enumeration is the explicit opaque exception. Source,
proof, metadata, and tool hashes are checked again before recording success.

Fresh output is written under `generated/combined/`; `evidence.json` records the
174-proof result, native control results, source/model hashes, baseline equivalence,
and generated overlay inventory. No scratch experiment model or compiled proof
is imported.

```sh
python3 servo/components/selectors/verification/recovery/test_storage_audit.py \
  servo/components/selectors/verification/recovery/generated/combined/stylo_bloom_verification.llbc
python3 servo/components/selectors/verification/recovery/test_provider_tools.py
```
