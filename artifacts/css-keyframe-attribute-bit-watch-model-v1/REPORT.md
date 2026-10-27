# Conservative boolean watch simulation

The new result is a general forward simulation from the reviewed name-based AttributeWatches model to per-effect boolean watches. It proves the representation can over-invalidate without losing a named dependency's admitted update. This is separate research; no C++/Rust refinement, scheduler liveness, browser outcome, canonical registration, or additional bug is claimed.

## Operational definitions and result

A BitWatch retains the target and sets `sensitive = !names.isEmpty`. BitState stores watches keyed by effect identity and a pending-target list. Installation replaces only that identity; removal removes only that identity. Change ignores the attribute name and admits a target if any remaining watch for that target is sensitive. No transition requires a safety predicate or the desired simulation result as its admission premise.

`Simulates fine coarse` means:

- `coarse.watches = fine.published.map abstractPair`;
- every target occurring in `fine.pending` also occurs in `coarse.pending`.

`named_watch_implies_bit` derives a sensitive target watch from a matching named watch. `install_simulates`, `remove_simulates`, and `change_simulates` prove preservation for the independently defined coarse operations. `finite_history_simulates` inducts over an arbitrary finite list of the existing install/remove/change events, starting from both empty states. The proof is not restricted to the closed examples.

Combining this simulation with the existing fine model's arbitrary-history query coverage derives `queried_mutation_admitted`. The absent-result specialization retains a queried name whose value is none. `survivor_mutation_admitted` proves that removing a different effect still admits a surviving effect's queried mutation. Endpoint values are not consulted during either watch representation's installation, so equal numeric values cannot skip dependency replacement in these transitions.

The pending relation is inclusion of target membership, not equality of list ordering, multiplicity, or exact event counts. Both models retain obligations through removal and installation; draining is outside this simulation. Conservative extra obligations remain allowed.

## Witnesses and false controls

Four kernel-checked examples cover an initially absent query, two effects sharing a target with one removed, a mutation of an unqueried name, and equal-valued replacement with a query-free entry. The different-name example derives fine pending `[]` but coarse pending `[7]`: the extra update is intentional. A separate false claim asserting exact pending equality is rejected. Two additional false controls assert that missing reads are ignored or removal clears a survivor's obligation; both are rejected for reducing to false.

There are 14 support declarations and four closed examples in the axiom audit. They support one simulation and its coverage consequences, not 18 independent discoveries. Imported Obligations/Watches proofs receive zero additional credit. The earlier author's failed compilation log is retained; the final replay compiles without warnings and audits only the standard Lean axiom set.

## Native correspondence and remaining assumptions

The proposed native query-presence bit and live EffectSet scan motivate this abstraction. The fine model still assumes complete supplied query traces, correct target/effect identity, and correctly delivered mutation events. Qualified-name encoding and pseudo-element owner mapping remain external. Rust correspondence additionally requires that the tracker is None exactly before any query and that its allocated reference map is nonempty after a query; this Lean model does not parse Rust or prove that heap invariant.

The exact watch-map relation concerns completed publication. The native proposal also sets a provisional conservative true bit when changed keyframes or retargeting cannot yet obtain style. That extra sensitivity is not represented as a fictitious completed empty query trace here. Extending the relation to arbitrary strengthened/provisional bits is a separate, small overapproximation obligation; no proof of that native path is claimed by this exact-map theorem.

This model does not establish publication timing around native equal-value returns, isolate native base-only computations, or verify clone/retarget implementation. Those are source-review obligations of the linked repair. Active registration and dormant retained caches remain distinct; an absent effect cannot receive mutations through the active aggregate, and replay freshness is not repaired by this simulation. Scheduler delivery, same-flush timing, fairness and actual recomputation remain conditional as in the parent watch/animation models.

## Reproduction

`python3 -I -S -B artifacts/css-keyframe-attribute-bit-watch-model-v1/replay.py --output /absolute/absent/output`

The replay authenticates both dependency capsules and their module hashes, the pinned Lean compiler, model source pins and references. It compiles Obligations, Watches, Bits and Witnesses in an owned two-thread temporary workspace, audits all 18 declarations, rejects the three false claims for the intended reason, and removes scratch build products. It does not read live Gecko sources, invoke a native/browser build, mutate an index, or integrate into the canonical library.
