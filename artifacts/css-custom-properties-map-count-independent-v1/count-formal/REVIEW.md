# Independent live-count formal review

Verdict: accepted as a conditional count/COW/history and filtered-index component. The separate iterator bridge, native representation and complete CSSOM lifecycle remain open; no whole-native correctness claim is accepted.

## Authentication and replay

Externally supplied FREEZE/MANIFEST/checker hashes were verified before execution. All 87 manifest inputs were checked for exact hashes, safe canonical paths, duplicate manifest keys, closed file roster and absence of symlinks by the reviewer. A manifest-only relocation plus both seals was created. Fresh `python3 -I -S capsule/check.py --lean ABSOLUTE_PINNED_LEAN --output NEW_EXTERNAL_DIRECTORY` completed five modules, 55 exact named axiom reports and 48 source bindings. The five modules are byte-identical to those fully read in the earlier static checkpoint; all final scope/mapping/checker/mutant files were also reviewed.

The 55 results comprise 46 general results and nine finite witnesses. Exact axiom reports contain only propext (50 results), Quot.sound (28), and Classical.choice (6), with no custom axioms/proof holes/native_decide. Axiom roster equality was checked by the producer checker and the retained logs were inspected independently.

Four mutation pairs differ only in the intended trialInsert expression: own-node-only old presence, inverted new presence, omitted decrement, and treating a tombstone's owned key as a present value. Both baseline and mutant definitions compile in every case. The identical correct proposition passes for baseline and fails for mutant with Lean's specific decide-proves-false diagnostic. Retained gate logs show the actual count proposition, not a syntax/import/infrastructure error. These gates exercise source-shaped TrialStore/nativeInsert transitions; the explanatory native.patch files were not compiled or run.

## Proof assessment

The independent projection enumerates a complete finite key roster and asks nearest-owner lookup, rather than trusting stored count. ownFind's nested Option distinguishes missing keys and tombstones. count_transition derives the separate old/new-presence counter update using single-key lookup update and an independent tally balance; it is not a definition of reference count in terms of the repaired counter.

Finite roster completeness is derived from initial stored keys and future operation keys. Unique per-node maps are preserved through replacement/append. Ready is preserved by initialization, unique mutation, shared skip, copy and empty-descendant expansion, then arbitrary finite histories. The old resurrection witness explicitly begins with the original algorithm's already-inflated tombstone count; it is not a Ready-state counterexample. The new correct history theorem does not migrate old corrupted counters.

Count/COW preservation allows arbitrary comparator behavior because skipping preserves the current count invariant. Requested-value lookup/history equivalence separately needs CompareSound. That premise concerns model payload equality and cannot be automatically identified with every native metadata field: VariableValue PartialEq compares CSS text, while taint and URL context have separate semantics. A caller/payload projection contract remains necessary; count correctness does not need it.

The filtered-index theorems derive length and below-count presence from Ready plus RawEnumeration. RawEnumeration requires exact unique nearest owners, including tombstones; count-only native iteration does not satisfy it. The source witness preserves that failure. The accepted iterator component must be connected by a separate theorem over the differing owner/lookup/validity definitions. No premise-label substitution is accepted as that composition.

## Source and machine boundaries

All complete original/count-only/combined map files are retained. Count-only and combined match the final formatted root pins. The checker regenerates 16 complete selected definitions for each of three variants (48 bindings) and verifies combined minus the two loop labels is exactly count-only. This binds source text, not Rust semantics. EMPTY and all fields/constants are present in the full snapshots; 48 does not mean every native method has a proof.

Actual IndexMap/atom equality, key uniqueness and replacement, immutable finite nonempty Arc chains, get_mut/make_mut cloning, successful allocation, native ancestor_count = chain depth, and compiler execution remain admissions. The model handles mathematical finite lists; decrement safety is derived, but increment uses finite-roster headroom. Actual u8/usize/u32 and CSSOM count conversions/sums are not globally discharged. Native borrowed iterators and capacity changes require their provider contracts.

CSSOM combines inherited/reset maps; disjoint live name domains and stable registration routing remain caller assumptions. Complete computed-value encoding, re-registration, cache invalidation and live publication are outside this component.

## Checker limitations and reviewer controls

The count checker authenticates its manifest and closed file roster, pinned Lean executable, exact audits and semantic mutation errors. It does not enforce Python -I/-S/no-optimization, reject output inside the source tree, pin the standard library, reject all symlinks/duplicate JSON keys, or close the directory roster as strongly as the iterator checker. Its README explicitly trusts the standard library/runtime. This review does not credit it with the iterator's eight negative guards.

For this replay the reviewer independently enforced isolation, no optimization, safe regular inputs and fresh external output, and verified all 5,092 library files against the accepted iterator toolchain inventory. That inventory is copied here. These are reviewer replay controls, not newly added behavior of the frozen producer checker. External authentication remains essential; no self-updated seal is an authenticity authority.

Own generated compiler outputs were removed only after all source/log/result receipts were retained. CLEANUP.json records the removed bytes. No production edits, Firefox/Rust builds, browser execution or Git operations were performed.
