# Selector collection extraction experiment

This directory contains a production-helper proof, conditional relative and
ancestor collector proofs, and their composition with Bloom rejection. It is
separate from `verify.py`. Deriving the collector premises from actual successful
matching and the corresponding DOM region remains open. Scoped extraction
diagnostics are retained alongside the checked results.

`lib.rs` imports production selector modules by path and includes the production
`parser.rs` inside its parser module. The inclusion permits a verification entry
point to call the private `simple_selector_hash` helper without copying its body.
`concrete.rs` supplies abstract atom identities and independent hash values for
concrete extraction experiments. It is not a CSS parser or a Gecko atom adapter.
The string conversion and serialization trait methods are unused by collection.

## Reproducible production-helper checkpoint

Run from the repository root:

```sh
python3 servo/components/selectors/verification/collection/verify_helper.py
```

This command checks the recorded native tool and patch hashes, extracts the
current production source with Charon, applies the exact unused-field
normalization below, invokes the patched Aeneas with native split-file output,
binds the external type models, and checks the Lean policy theorem. Generated
models are rebuilt rather than reused. `generated/helper-evidence.json` records
the Rust source, LLBC, normalization report, model and proof hashes.

`CollectionProofs.simple_component_policy` proves the exact behavior of production
`simple_selector_hash` for arbitrary distinct atom types. Its hypotheses specify
name inequality, three hash providers, and attribute collection policy. The
statement covers all component variants and quirks modes; it does not instantiate
the mock `identity > 3` policy. It is a helper policy theorem, not yet a theorem
connecting selector matches to an ancestor or relative-selector region.

The exact allowed axiom set is `propext`, `Classical.choice`, `Quot.sound`, and
`core.fmt.Formatter`. The last is an unused opaque type carried by `SelectorImpl`'s
`Debug` bound; no formatter behavior is assumed. Missing, duplicate, or unexpected
theorem audits fail the command. `test_audit.py` exercises those rejection paths.

The native Aeneas split-file interface supplies `lean/TypesExternal.lean` and
`lean/FunsExternal.lean`. Arc is a read-only logical value wrapper, HeaderSlice is
a header and finite list, and ArcUnion is a sum. These are positive Lean data
types, not assumptions of collector correctness. They do not model allocation,
reference counts, aliasing, or ownership. The helper uses no Arc accessor. Full
collector proofs must specify and check correspondence contracts for every
reachable dereference, slice, and union accessor before using this abstraction.
The only external function needed here is the identity `Borrow<T> for T` operation.

## Relative collector and iterator checkpoint

```sh
python3 servo/components/selectors/verification/collection/verify_relative.py
```

This separate command regenerates the actual relative collector and its recursive
singleton `:is()` / `:where()` calls, including the production `SelectorIter`.
Native unused-clause pruning avoids the unused trait witness responsible for the
full experiment's erased-lifetime projector failure. The verification entry point
is generic over `SelectorImpl`; its proof dependencies do not include mock atom
or formatter behavior. The collector bodies and generated Lean remain unchanged.

`CollectionIteratorProofs` proves that iteration starts at the backing slice's
first entry, returns each ordinary component, stops at a combinator while saving
its marker, and stops at slice exhaustion. These statements cover every component
variant and require no pending combinator. `CollectionStepProofs.simple_component_step`
proves the exact hash insertion behavior of every component other than `:is()`
and `:where()`, including masking, writing at the current length, and the fullness
return value.

`CollectionInvariantProofs`, `CollectionLoopProofs`, and `RecursiveCollectionProofs`
prove bounds, continuation flags, and preservation of an allowed-hash prefix through
the actual loop and singleton `:is()` / `:where()` recursion. The hypothesis `Good`
requires each simple emitted hash to be allowed and supplies a finite nesting depth
for relevant singleton selectors. The loop stops at the first combinator; its
termination measure is the remaining backing-slice length. These are conditional
collection and termination theorems. They do not establish that successful CSS
matching implies `Good`, or that every parsed selector has a suitable depth.

The three iterator theorems allow only `propext`, `Classical.choice`, and
`Quot.sound`. The component-step theorem and the actual generic collector functions
add only the unused `Formatter` opaque type. Nineteen exact axiom audits cover
sixteen theorems plus dependency audits of the verification wrapper and both
production collector functions. Native computation
axioms, missing audits, and additional dependencies are rejected.

The relative external models use bounded slices in `HeaderSlice`. The six explicit
function definitions model identity borrowing, the two `Option` try operations,
Arc dereferencing, header-slice contents, and `SelectorList`'s singleton-or-list
observation. These are contracts for finite, immutable content observation.
They do not prove Rust pointer layout, allocation, aliasing, reference counts,
ownership, or lifetimes, including the single-selector transmute in `SelectorList`.

`relative-boundary.json` pins both representation source files, the opaque slice's
source, and the complete generated external declaration signatures. Changes require
review of the representation contracts. The runner also checks the slice receiver
identity structurally in LLBC, rejects new opaque local methods and retained
`transmute`, and requires the production collector bodies. `test_relative_boundary.py`
exercises rejection paths. Evidence is written to `generated/relative/evidence.json`
only after all checks; a failed rerun removes the previous evidence.

`CollectionFrameProofs` also proves that length never decreases and writes leave
all positions below the initial length or at/above the final length unchanged.
The actual zero-initialized wrapper therefore leaves every unused slot zero,
including after singleton recursion and early fullness. This supplies the padding
condition required by the packing theorem.

The full matching-to-region theorem, exact emitted sequence, and ancestor
collector proof remain open. The required-hash premise must still
be connected to matching semantics and the DOM hash provider.

## Local-name matching bridge

```sh
python3 servo/components/selectors/verification/collection/verify_matching.py
```

This separate runner adds the actual `matches_local_name` and `select_name` bodies
to the relative extraction, sharing its production `Component`, `SelectorImpl`,
iterator, and collector definitions. `MatchingProofs.local_name_requires_hash`
connects a successful actual local-name match to every hash emitted by the actual
simple collector. `local_name_relative_collection` composes that result with the
actual collector and its zero-initialized verification wrapper: the returned
length is at most four and every live-prefix hash is allowed.

The supported matching subset is a rightmost compound containing local-name
components, ending at a combinator or exhaustion. `LocalNameMatch` requires the
actual local-name helper to return true for each component in that compound;
this is a semantic conjunction over the extracted iterator contents, not an
extraction of `matches_compound_selector` or the full CSS matcher. Singleton
`:is()` / `:where()` collection is verified separately, but their matching bridge
is still open. Attribute, ID, class, namespace, combinator-region, and ancestor
matching bridges are not covered by this theorem.

`HashAlignment` explicitly assumes correct atom equality/inequality, precomputed
hashes, borrowing, and that a successful `Element::has_local_name` observation
places the masked name hash in the chosen allowed set. This is the DOM-provider
contract; Gecko's FFI and hash insertion implementation are not proved here.
`MatchingContext` and `NonNull` are opaque types needed only by unused `Element`
dictionary fields. They add no behavioral correctness axioms. The exact twenty-three
audits permit these types only for the four matching bridge theorems.

`matching-boundary.json` pins the matching, element-trait, context, parser, and Arc
sources and the complete external declarations. The runner requires both matching
helper bodies, permits only the existing opaque `SelectorList::slice` function,
and writes fresh evidence only after all checks. Neither source bodies nor
generated collector or matcher bodies are rewritten.

## Collection, packing, and rejection

```sh
python3 servo/components/selectors/verification/collection/verify_rejection.py
python3 servo/components/selectors/verification/collection/test_rejection_boundary.py
```

`CollectionRejectionProofs.local_name_no_false_rejection` composes the local-name
matching conjunction with the actual collector, packing, and rejection functions.
Given `ValidHistory` for the filter and `HashAlignment` to the masked live hashes,
the composed computation terminates and returns true. The proof combines required
prefix membership with the recursive zero-tail theorem. Mask idempotence connects
the collector's already-masked output to `NormalizationProofs.pack_match_raw_history`.
This includes empty output, early fullness, collisions, and hashes whose low 24
bits are zero. The four array/history lemmas live in `PackingBridgeProofs.lean`
and are shared with the ancestor composition.

The runner regenerates the core Bloom model and matching model, running their
existing tests and audits. It then copies only Lean source files into a clean
combined directory and recompiles every required generated model and proof
dependency. The official Aeneas and Charon binaries must match the pinned release
archive; the collection extraction also retains its pinned native patches and
representation contracts. The matching source inventory and hashes are checked
before copying. Sixty-four exact dependency reports cover 61 theorems and three
collector definitions, with the same explicit opaque-type boundary as the matching
checkpoint.

`generated/rejection/evidence.json` records the core LLBC, tool, matching evidence,
boundary, and combined Lean source hashes. Old evidence and compiled output are
removed before provenance checks; core LLBC and generated source are removed
before regeneration. Evidence is written only after the final audit succeeds.
Ten boundary tests cover missing, extra, duplicate, and forbidden-axiom reports;
changed source inventories and hashes; archive and executable drift; and failed
provenance, extraction, or final compilation with stale artifacts present.

The supported selector subset remains the local-name compound conjunction
described above. Full matcher and region correspondence, singleton `:is()` /
`:where()` matching, other component matching, and Gecko's DOM hash-provider
contract remain open obligations. The theorem assumes a valid filter history;
it does not establish the cache's history for a browser traversal.

## Ancestor collection

```sh
python3 servo/components/selectors/verification/collection/verify_ancestor.py
python3 servo/components/selectors/verification/collection/test_ancestor_boundary.py \
  servo/components/selectors/verification/collection/generated/ancestor/collection.llbc
```

The ancestor runner regenerates the actual generic ancestor collector and its
iterator from current Rust source. It uses the same narrowly checked unused-GAT
normalization, native tool patches, and recursive-loop extraction as the relative
runner. Its separate boundary manifest checks the collector entry points and
subject-scanning helpers, source fingerprints, and complete external signatures.
The external models add only the standard `Option::is_none_or` behavior: `None`
returns true, while `Some` invokes the supplied predicate.

The iterator theorems establish exact skipping, total next-step behavior, source
positions, and strict progress for emitted components. The full collector theorem
then covers subject scanning, the ancestor region, recursive singleton `:is()` /
`:where()`, capacity limits, required-hash prefix preservation, and the array frame.
The zero-initialized `collect_ancestors` wrapper consequently returns only required
hashes in its live prefix and zeros in the remaining slots. Forty-nine exact
dependency reports cover 42 theorems and seven production collector definitions.
Fresh output and evidence are kept under `generated/ancestor/`. Nine boundary
tests cover root/body drift, exact audits, external declarations, source hashes,
and failed-run evidence cleanup.

`FullGood` is an explicit finite-depth premise. Its phase graph follows the actual
collector: a nested singleton on the subject invokes full ancestor collection,
while one in the ancestor region collects from the nested selector's subject.
Permitted-hash obligations apply to yielded ancestor components. Ordinary subject
hashes are not required to be present. The phase graph also retains the actual
handling of sibling, pseudo-element, slot-assignment, and part combinators.

These are collector contracts, not proofs of CSS matching or DOM ancestry. The
successful-match implication to `FullGood`, Gecko's hash-provider alignment, and
the browser traversal's valid filter history remain open obligations. Read-only
Arc and slice representations and source normalization remain explicit trust
boundaries. No ancestor collector body is replaced by a proof model or assumed
correct through an axiom.

## Ancestor collection, packing, and rejection

```sh
python3 servo/components/selectors/verification/collection/verify_ancestor_rejection.py
python3 servo/components/selectors/verification/collection/test_ancestor_rejection_boundary.py
```

`CollectionRejectionProofs.ancestor_collection_no_rejection` composes the actual
ancestor collector, packing, and filter query. It assumes `ValidHistory` and
finite-depth `FullGood` with permitted hashes equal to the masked live history.
The resulting computation terminates and returns true, including zero hashes,
collisions, empty collection, and a full four-slot prefix. This theorem adds no
successful-match or DOM-provider premise discharge.

The scoped runner freshly regenerates the core and ancestor models, checks their
exact source inventories, and recompiles only source files in a clean combined
model. It shares the archive/binary provenance checks and failure cleanup with
the local-name runner. The ancestor path uses its own generated types and external
contracts; it does not import the matching model or its opaque context types.
Ninety exact dependency reports cover 83 theorems and seven collector definitions.
Evidence is written to `generated/ancestor-rejection/evidence.json` only after all
checks pass. Seven boundary tests exercise missing/extra reports, behavior axioms,
source drift, failed provenance/regeneration/compilation, and stale output.

## Full collector gates

`extract.py --simple` preserves the direct generic extraction gate without
normalization. Omitting `--simple` also extracts the actual iterator-based
collection code. `--monomorphize` records separate monomorphized output; native
`--partial-monomorphize` can test the borrowed-type specialization pass.

The generic helper encounters an unused `SelectorImpl::ExtraMatchingData` GAT.
The separate default full-collector gate retains the unused GAT and can still
encounter extraction failures. The ancestor runner uses the reviewed source
refactor that separates subject scanning from final ancestor collection to avoid
the former outer-loop abstraction failure. `SelectorList::slice` and `servo_arc` operations
are opaque and need the representation contracts described above. No recursive
collector body or iterator is replaced with a hand-written proof model.

## Experimental unused-field normalization

`normalize.py` is an opt-in prototype, not part of the default extraction path.
It removes only the unused `ExtraMatchingData` associated-type slot from the
`SelectorImpl` dictionary declaration and corresponding implementations. It
requires the pinned LLBC schema, non-deduplicated input, the expected associated
type and its `Default` bound, and absence of references to that associated type
in every retained declaration and constraint. It refuses unexpected shapes.
The original file remains intact. A separate report records exact edits and
input/output SHA-256 hashes.

This transformation adds an extraction trust boundary. Its syntactic checks do
not constitute a proof of the transformation's semantics. Native Charon opacity
rules omit unused pseudo-class and pseudo-element method metadata, while the
attribute collection policy remains included. This avoids the unused visitor
trait cycle without removing method signatures in the normalizer.

The native trait-parent naming patch and positive external type models allow
Lean to check the normalized production helper. The normalized relative and ancestor scopes now extract the full production
collector bodies; the complete matching-to-region theorem remains open. The normalization itself remains an explicit extraction trust
boundary, even though the emitted helper theorem checks in Lean.

From the repository root:

```sh
python3 servo/components/selectors/verification/collection/normalize.py \
  servo/components/selectors/verification/collection/generated/simple/collection.llbc \
  servo/components/selectors/verification/collection/generated/simple/normalized.llbc \
  servo/components/selectors/verification/collection/generated/simple/normalization-report.json
python3 servo/components/selectors/verification/collection/test_normalize.py \
  servo/components/selectors/verification/collection/generated/simple/collection.llbc
```

The tests inject retained associated-type references into each declaration table,
check rejection of unknown schema fields and changed declarations, and verify
that the output differs only at reported slots.

## Pinned Aeneas preprocessing failure

`missing_trait_repro.rs` reduces the monomorphized extraction failure to an
identity function. Run:

```sh
python3 servo/components/selectors/verification/collection/tool_repro.py \
  --output servo/components/selectors/verification/collection/generated/repro-before
```

The unmodified pinned Aeneas fails while recognizing array `Default`
implementations because a trait implementation's declaration is absent in the
monomorphized input. `aeneas-array-default-missing-trait.patch` proposes skipping
that implementation during this recognition pass. It changes neither collector
code nor Lean axioms. The patch targets Aeneas `cd41995` with Charon source
`26abff028ced534ebf8e861f2d3dd1743e2aa318`. A native build of this patch extracts
the identity function successfully, and the pinned Lean compiler checks its
generated model. `tool_repro.py --aeneas PATH --output PATH` repeats both checks.

`tool-patch.json` pins the source archives and patch by SHA-256. The experimental
native build uses an isolated opam root under `artifacts/stylo-bloom-tools/`,
OCaml 5.3.0, Dune 3.20.2, and the upstream `bin_prot.v0.17.0` package. The later
`bin_prot.v0.17.0-1` packaging patch produced empty library metadata and prevented
its `gel` dependent from building. No global compiler or shell setup is needed.
Apply both recorded patches to a fresh copy of the pinned Aeneas source. After
installing the Aeneas and Charon source package dependencies in the `aeneas-5.3`
switch, build from the extracted Aeneas `src` directory:

```sh
OPAMROOT="$TOOLS/opam-root" AENEAS_VERSION=cd41995+collection-experiments \
  "$TOOLS/opam" exec --switch=aeneas-5.3 -- \
  dune build --profile release -j 4 main.exe
```

Here `TOOLS` is the absolute path to `artifacts/stylo-bloom-tools`. The resulting
binary is `aeneas-source/src/_build/default/main.exe`. Preserve that build as
`aeneas-collection-naming`; the helper runner verifies the recorded local binary
hash and version before use. The extraction experiment
accepts `--aeneas PATH --monomorphize`; monomorphized outputs use separate
`generated/simple-monomorphized/` and `generated/full-monomorphized/` directories.
The default verification runner continues to use the unmodified pinned tools.

The patch does not unblock monomorphized collector verification. `box_repro.rs` isolates the
next failure to a two-variant enum containing `Box<u32>`: Charon monomorphization
removes the built-in Box's type argument, which Aeneas requires. The same input
extracts and type-checks with the official tool when `--generic` is passed to
`tool_repro.py`. Use `--source .../box_repro.rs` to select this reproduction.

Full monomorphized collector extraction additionally retains calls to absent
generic `core::array::repeat` and `as_slice` declarations. Suppressing the
resulting Aeneas lookup failure would not supply those function bodies. These
are open native tool compatibility gates; no further LLBC erasure or full
collector theorem is claimed for this monomorphized extraction path.

`array_repro.rs` reduces the missing-call failure to returning `[value; 4]`.
It also passes extraction and Lean checking with `--generic` and the official
tool, while monomorphized extraction fails even with the preprocessing patch.

## Native naming and iterator reductions

`aeneas-trait-parent-names.patch` uniquifies colliding parent-clause field names
within a trait, leaving built-in field registrations unchanged. All projections
continue to use their clause IDs. `trait_names_repro.rs` fails Lean checking with
the official tool and passes with the patched tool. `tool-patch.json` records
both patch hashes and distinguishes the array-only binary from the naming-patched
binary retained at `artifacts/stylo-bloom-tools/aeneas-collection-naming`.

`associated_iterator_repro.rs` reproduces duplicate lifted associated types when
a generic iterator and its item type both constrain the same implementation.
`canonical_iterator_repro.rs` gives the iterator an associated implementation
type and passes extraction and Lean checking. The production refactor follows
that shape and still dispatches to the actual SelectorIter and AncestorIter.

`recursive_component_repro.rs` retains a small recursive traversal experiment.
Default extraction exposes a generated mutual-loop
universe mismatch in Lean; the native `--loops-to-rec` reproduction option
resolves it and both extraction and Lean checking pass. The separate ancestor checkpoint now extracts the actual generic production
collector with the reviewed source refactor. These smaller examples remain
extraction diagnostics, not replacement collector implementations.
