# Static review of evolving draft

This is a read-only pre-seal review, not final authentication or execution. DRAFT-v2-PINS.json records the reviewed bytes. Final producer pins and replay remain required.

## Lean

The new planner_none_iff_unchanged proves both directions under unique identity: append changes length; move cannot preserve the list because the next element has a distinct ID; replacement cannot preserve the old unequal entry. changing_steps_are_actual and preparation_gate_actual_changes therefore connect the preparation label to actual modeled step inequality. The earlier label-only gap is closed.

planner_valid derives indexed split witnesses from the actual reverse scan, and planner_index_bounds derives in-range indices. raw_operation_representation handles separate declaration and priority lists and membership predicate; its move case intentionally preserves/reinserts the old target bit. concrete_storage_refinement ties this to the independently defined forward setter. The representation is mathematical lists plus an extensional membership function; allocation, actual SmallBitVec/ThinVec/hash storage and machine arithmetic remain source/runtime admissions. Raw operation validity permits generic appends, while uniqueness after a planner-produced append follows the separate planner/reference uniqueness result.

pair_expansion_convergence is substantive: after the later included pair member is set, the projection is [earlier,later], and subsequent unrelated setters preserve that projection. The unique action-list hypothesis supplies absence in the remaining suffix. Both directional opposition hypotheses are explicit. The result quantifies over arbitrary identities, values, priorities and relation, and does not assume a fixed physical-first convention. guarded_pair_expansion_convergence binds the same result to the actual modeled preparation gate.

The optional Nat-valued group map and Bool mapping-kind helper are a concrete relation instantiation; the main results quantify over any relation. Actual custom/non-group identities must instantiate no opposition. Stable metadata and expansion order still require source admission.

## Source/equality boundary

The model uses DecidableEq values, which is stronger than arbitrary generated PropertyDeclaration PartialEq. For all, each requested declaration is CSSWideKeyword or WithVariables, and UnparsedValue supports Eq. Old declarations of other variants cannot compare equal to either requested variant; this can admit the all comparison domain without globally assuming native payload reflexivity. However a global claim equating modeled state equality with native Vec<PropertyDeclaration>::PartialEq is unsupported. Unrelated float-containing declarations would also need an appropriate semantic/storage abstraction. Ordinary u16 payloads in the native facade do not establish general generated payload equality.

The ordinary planner helper has been factored from existing source; the formal result may cover ordinary declarations only under its stated equality/provider premise. The separate normal batching/rank-correction theorem remains open. Finite ordinary checks do not discharge it.

## Native extraction draft

build.py extracts full planner, prepare/update, push/extend/removal and participating all/lazy-iterator control flow. The facade substitutes Vec for ThinVec/SubpropertiesVec, Vec<bool> for SmallBitVec, BTreeSet for property sets, synthetic value variants and fixed symbolic equality. Real generator metadata is loaded for longhands/groups/expansion lists. Three pref profiles are synthetic subsets, not real pref values. These substitutions must remain explicit.

The driver independently applies forward set semantics to the source expansion and checks complete ordered rows, priorities and gate, then checks parallel-storage/set invariants. It also exercises ordinary source lists, removal, extend, and repeated setters. Final counts and semantic mutants have not yet been authenticated or independently executed.

The source expansion itself is shared between native and finite reference; provider uniqueness/exclusion/stability cannot be inferred from this agreement. They need separate metadata/source checks or explicit premises. The same applies to global generated payload equality and callback stability.
