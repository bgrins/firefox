# Independent base metadata proof review

Status: **ACCEPT the scoped mathematical component**, with native/provider/scheduling admissions retained. Fresh externally authenticated, manifest-only relocated replay passed. No proof or source-correspondence blocker found.

## Reviewed theorem boundary

The new model scans only entries present in the rebuilt base map and obtains each old value using that same entry's key. Its nested Option domain distinguishes an absent outer AnimationValue from a present custom AnimationValue with no computed custom value. The latter guaranteed-invalid value has no attr bit, but differs from outer absence in ordinary equality. Custom classification is a function of the key, not an independent per-row bit.

Entry decomposition is sound for arbitrary payload comparators, including nonreflexive comparators. A null/non-null mismatch is already detected by ordinary comparison, which justifies removing the null guards only in the derived Boolean characterization. The new native expression itself retains those guards. The scan theorem distributes existential disjunction across the finite list. The added-decision theorem identifies the exact cases newly detected over the old scan; it does not assume taint equality.

The unchanged-selected-metadata theorem derives equal taint for a selected custom entry from a false changed flag. Its selection and custom-key hypotheses are essential. Old-only removed keys are outside the scan; the explicit counterexample prevents interpreting this as full map equality. List uniqueness is not required for the Boolean theorems; actual hashmap key/value coherence and unique iteration remain native/provider correspondence premises.

## Request versus delivery

baseFlag reflects target presence and whether the output pointer was requested. requestsRestyle summarizes reaching the request call from the two UpdateProperties branches. It does not prove that the request survives KeyframeEffect's target/context/animation guards or EffectCompositor's context/pres-shell guards.

The synchronous tick model publishes a supplied base and replaces the retained sample exactly when notify or force is true. This is a definition of an admitted scheduling episode, not an extraction or proof of Gecko's scheduler. selected_sample_metadata_after_request additionally assumes the prior sampled taint agrees with the old selected base. That premise concerns the starting state, not the desired next result. The proof derives next taint in the skip branch and obtains it by admitted delivery in the request branch. It proves neither fresh payload equality nor arbitrary multi-effect/timeline histories.

Seven independent kernel challenges are retained in Review.lean to demonstrate the relevant domains and counterexamples. They add no native conformance claim.

## Source and imports

The imported TaintValue and EndpointModel files provide types and definitions, not imported proof counts. No inherited whole-CSS or native scheduling claim is accepted. Native source bindings retain complete UpdateProperties and EnsureBaseStyles before/after, EnsureBaseStyle, ComposeStyleRule, RequestRestyle, C++ equality, Rust deep equality/taint accessor, composition entry and null-endpoint provider, plus EffectCompositor request logic.

These source bodies explain the abstraction boundary. They are not compiled by this capsule. The formal comparator is an admitted projection of native value equality; native custom-key/value identity, publication, URL-data observational quotient, allocation/FFI and scheduling remain open. The actual getter returns false for guaranteed-invalid custom values and noncustom variants; a false taint bit does not establish general URL validity.

I authored the independent native proposal, not this Lean model/proof. The source/oracle review is frozen separately at css-animation-base-metadata-review-v1. This review independently checks the formal component and does not substitute its model executions for the root's browser/build evidence.

## Executed checks

Authoritative producer FREEZE, MANIFEST, checker and report hashes in PRODUCER-PINS.json were checked before any producer code executed. All 49 input hashes and the closed file/directory roster were authenticated, then only manifested inputs and the two seal files were copied into a fresh directory. Isolated Python ran the copied checker with fresh external output and a cleaned Lean/Python environment.

The fresh replay compiled five model modules, checked all 23 named results and their exact axiom inventory, verified 14 source-body bindings, and ran the baseline plus the one compiled omission mutant. The baseline produces ten true checks. The omission mutant produces four false metadata/sampling observations while preserving six controls. This is a Lean model mutation, not a compiled C++ mutation. Producer axiom inventories use only propext and Quot.sound, or neither; the exact per-name list is retained in the producer AUDITS.json.

All seven independent witness theorems compiled. The first six use propext and the final request/delivery witness uses no axioms. They show that conservative nonreflexive comparison remains allowed; an always-true primitive comparison cannot hide a custom taint mismatch; lookup identity and custom classification matter; prior sampled coherence is necessary for skip observations; and GIV is distinct from outer absence despite sharing a false taint bit. The delivery witness is about the modeled transition, not native dispatch.

Six genuine corruptions were rejected before any output directory was created: modified model bytes, an extra shadow Lean module, an extra empty directory, symlink, duplicate manifest key and FIFO. The unmodified copied capsule authenticated again afterward. All temporary compiled outputs were removed by the owned temporary-directory cleanup. RESULT.json retains exact command receipts, mutation outputs, independent axiom output and guard outcomes.

The first independent run reached successful producer replay and compiled all seven witness theorems, but my harness expected no axioms for every witness. Actual by-decide elaboration used propext for six. DEVELOPMENT.json records this reviewer expectation error; the corrected exact inventory was followed by a second complete fresh replay. No producer artifact was changed.

## Reproduction and conclusion

Integrity review: `python3 -I -S check.py`.

Fresh independent replay, including all producer gates and independent challenges: `python3 -I -S review.py --producer ../css-animation-base-metadata-proof-v1` (from this directory). Output is JSON on stdout and all compiled files use a fresh temporary directory.

Accept the local arbitrary-finite-new-entry comparison theorem and the explicitly admitted one-step sampling model. Do not promote it to detection of removed keys, arbitrary native histories, URL validity, or unconditional request delivery. Full native rendering/scheduler refinement remains open; final browser/build acceptance belongs to its separately pinned gate.
