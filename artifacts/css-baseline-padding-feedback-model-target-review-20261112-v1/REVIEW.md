# Feedback model target review

No false clause or target-strength blocker was found. The ten obligations are useful as a scalar history-composition result, provided native realization of the transitions remains separate as the contract states. No target amendment is requested. Target.lean and CONTRACT.md here are exact reviewed draft snapshots; INPUTS.json pins them. No compiler or proof was run.

| Obligation | Review |
| --- | --- |
| parent_consistent | Replacement sets used to raw plus adjustment for arbitrary integers. No restriction on the previous cache is needed. |
| step_consistent | A parent resets all components; a child preserves the state. The initial consistency premise is sufficient. |
| history_consistent | Finite lists admit arbitrary ordering, length and integer payloads, including repeated parents or no events. This is closure of the declared step relation, not an assumption that every history already satisfies the invariant. |
| repeated_child | Full record identity, not just used equality, is asserted for arbitrary initial states and all natural repetition counts, including zero. It does not claim an inconsistent initial state is repaired. |
| old_repeated_child | Used grows by exactly n times adjustment; raw and adjustment stay fixed by oldStep. The Nat-to-Int conversion is appropriate for List.replicate. |
| old_nonzero_drift | A single old child event adds nonzero adjustment to an initially consistent record. Both positive and negative values violate consistency; no positivity assumption is needed algebraically. |
| reset_independent | The first parent overwrites all state. Subsequent identical events therefore yield identical records regardless of either initial state. No preceding consistency premise narrows this claim. |
| zero_adjustment_control | With a correctly initialized zero adjustment, arbitrary repetitions preserve the full record under the old transition. |
| concrete_old_witness | Parent 3 18 has used 21. Two old child steps yield 57, which differs from raw plus adjustment 21. |
| concrete_fixed_witness | Two fixed child steps retain 21. Child, parent 4 8, child yields 12. The explicit refresh occurs between children. |

The corrected child transition is identity by definition, and the parent transition performs correct replacement by definition. The proof will establish consequences and arbitrary finite composition of those selected operations. It will not establish from first principles that the native patch realizes them. This is not circular as a model theorem, but would be circular if used as the sole evidence of native child/parent correctness. The contract keeps that distinction explicit.

The integer domain is wider than native baseline acquisition. In particular, a selected native side receives a nonnegative magnitude, whereas the algebra permits negative adjustment. This is a stronger mathematical domain, not evidence that negative selected contributions occur in the browser. Unbounded integers also avoid both prior padding overflow and later geometry rounding; no machine range claim follows.

The witness uses CSS-pixel-scale numbers matching the described probe. It is not an app-unit/C++ execution witness, does not include the 2px border, and does not equate used with a DOMRect coordinate. The source/probe correspondence must bind units, side selection and actual measured state separately. The existing contract appropriately disclaims that refinement.

The scalar state deliberately omits theme/SVG override precedence, both axis suppression flags, cache property presence, relative-size flags, input aliases and all other geometry. Full record preservation here covers only raw/adjustment/used, not those native fields. Parent replacement must not be cited as solving the separate peer-font invalidation discrepancy; the modeled parent always supplies the newly correct values.

No native execution, universal C++ correctness, overflow repair or compiler acceptance is supplied by this review. A later proof audit should require all ten original field theorems plus aggregate, unchanged definitions and standard-only axioms, with failed attempts kept distinct.
