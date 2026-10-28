This is the exact fallback-crossing counterexample found during source review of the scoped-cycle-bit provider proposal. Seven declarations pass Lean's kernel; three false claims are decisively rejected. The model reuses the previous outcome/default and guard models unchanged.

The normalized case is A=var(B,var(C)), B=var(A), C=var(missing). A's own initial is encoded as 3 (vertical-rl); B/C initials are 7 (vertical-lr); the outside consumer fallback is 11 (horizontal-tb).

| Evaluator | Outside consumer result | Meaning |
|---|---|---|
| Original recursive path, no new missing-provider default | 11 | Consumer fallback |
| Scoped-bit draft plus new acyclic registered defaults | 7 | C's default escapes through cyclic A |
| Participant-mark evaluator | 3 | A retains its own invalidation/default |

The scoped bit remains true in the incorrect result. It records that a cycle happened but cannot repair a value changed by a fallback descendant. The participant evaluator marks exactly B/A, not C. The missing C case in isolation still defaults correctly to 7; the defect concerns composition with the cycle.

Witness.lean is the small new model. scopedEvaluate mirrors the draft's save/reset/restore-OR cycle flag, success bypass on cycle-touched frames, and local missing-result defaulting. The no-default variant isolates the prior branch behavior. The existing participant evaluator provides the comparison. Fuel is sufficient for this finite trace; exhaustion remains pending, not CSS invalidity. The missing leaf abstracts a failed reference to an absent unregistered property; it is not a registered property's missing declaration.

The source review found this candidate defect first; Lean then checked the normalized counterexample. This is not automatic discovery from Rust, a proof of native equivalence, or evidence that a release binary follows this path. The actual partially resolved map, call order, registration lookup, full parser, inheritance, attributes, contextual-unit graph, taint and caching remain correspondence obligations. All atoms here are already admitted noninheriting registration values. Native V3 is a separately reviewed participant-mark proposal, not proven by this executable model. No accepted bug or canonical coverage credit is claimed.

Replay with an absent absolute output directory:

    python3 -I -S -B artifacts/css-registered-provider-fallback-cycle-witness-v1/replay.py --output /private/tmp/provider-fallback-witness-output

The retained output contains raw logs and the audit. Temporary compiler/module scratch is removed automatically. INPUTS pins the compiler and all imported/copied sources; REFERENCES binds the exact v2 body reviewed. Audited axioms are propext and, for scoped recursion proofs, Quot.sound. No custom axiom, sorry, native_decide or browser execution is used. validation-complete is successful; the earlier validation log is a corrected missing type annotation, not a successful negative control.
