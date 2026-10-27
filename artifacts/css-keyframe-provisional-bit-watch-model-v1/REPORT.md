# Conservative provisional attribute-watch bits

This successor proves that provisional true bits preserve the name-based watch model's admitted obligations. It replaces the earlier exact-map relation with matching effect identities and targets plus a sensitivity implication. This is one general simulation result with supporting lemmas, not a native verification or additional browser defect.

`PairRel fine coarse` requires equal effect identity, equal target, and `!fine.names.isEmpty = true` implying `coarse.sensitive = true`. `Rel` pairs the complete watch lists in order and requires membership inclusion from fine pending targets into coarse pending targets. Extra true bits and extra pending targets are permitted. The old exact-map relation implies this relation.

The independent coarse operations retain the earlier install/remove/change definitions. `strengthen` maps any selected identities to true, preserving all other bits, IDs, targets and pending obligations. A completed conservative install replaces one identity with sensitivity `extra || !names.isEmpty`; this covers either exact publication or an additional conservative bit without assuming a nonempty allocated tracker map. The supplied `extra` boolean is arbitrary. No transition takes its simulation conclusion as a premise.

The proofs establish named-hit preservation, preservation of an existing bit hit under arbitrary strengthening, removal and completed-install simulation, and mutation simulation. `finite_history_related` covers every finite history containing completed fine events, provisional strengthening steps, and conservative completed installations. Fine state stutters on provisional strengthening. `finite_history_published` reuses the existing publication invariant; together they derive that every surviving entry's supplied queried attribute is admitted by a coarse mutation after any such history. Pending inclusion concerns membership, not multiplicity, order or exact scheduling counts. Removal does not cancel already admitted obligations; no drain is modeled.

Five closed examples exercise `Some([])` with a true bit, the resulting intentional extra update, an initially absent query surviving another effect's removal, completed empty replacement clearing an obsolete provisional bit, and rejection of clearing a required true bit. The Some-empty example distinguishes allocation/presence from name-set nonemptiness; it does not assert that this particular state occurs in native execution. Three separately compiled false claims reject clearing a required bit, denying the provisional extra update, and losing the surviving absent query. They fail by kernel reduction to false, not syntax or missing imports.

## Source correspondence boundaries

The motivating source is the pinned eight-file attribute-effect publication proposal. Its tracker presence result and provisional true assignment can be conservative relative to a supplied completed dependency set. This model no longer needs the earlier exact-map requirement that a present tracker be nonempty. It still requires every actual query, including an absent result, to be represented in the supplied fine trace and any nonempty trace to yield a true native bit. No Rust/C++ execution, tracker-allocation invariant or FFI correspondence is proved.

A provisional event has a deliberately narrow meaning: the same active effect and target retain the same cached dependency association, while sensitivity may increase. It does not create an unavailable future query trace. Changing keyframe semantics before recomputation requires a separate argument identifying which cached trace remains relevant and when a completed new trace replaces it. Retargeting changes the target and therefore is not a fine stutter: a valid new target/semantic association must be supplied by a completed install or a future refinement operation. The proof does not infer that association from an unknown style. Native copy, equal-value early-return placement, base-style isolation, target/pseudo ownership, registration, and update ordering remain source obligations.

Only active watch publications participate in the aggregate. Dormant retained cache reuse is excluded. Attribute event discovery, qualified-name identity, pseudo routing, delivery to a normal update, same-flush timing, fairness and actual recomputation are unproved assumptions. A pending target is an admission obligation, not proof that a native scheduler fulfills it.

## Validation and accounting

The final replay compiles the three pinned dependency modules and the two new modules using pinned Lean 4.35.0-rc4 with two threads. It audits 15 support declarations and five closed examples, allowing only the standard `propext`, `Quot.sound`, and `Classical.choice` axioms; the closed examples use none. Imported results receive zero additional theorem credit. There is no canonical registration or normative CSS coverage claim.

Authoring compilation failures are retained separately. The final replay and all three false controls pass their expected checks. Owned scratch build products are removed. No live native/source/WPT/index/browser/canonical operation is performed.

Reproduce with `python3 -I -S -B artifacts/css-keyframe-provisional-bit-watch-model-v1/replay.py --output /absolute/absent/output`.
