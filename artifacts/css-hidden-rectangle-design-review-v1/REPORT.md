# Rectangle/provider observation design review

**GO for a small implementation, with the scope details below made explicit. No design blocker.** This reviews the proposed mathematical interface, not checked Lean code or a native correctness theorem. The sealed design and all eleven referenced input hashes authenticate.

Returning the whole provider state and resolving the target against that state captures the missing observation dependency. Admission alone cannot establish ancestor-position correctness. Observation-only erasure retains ancestor state and therefore supports a useful commutation law without pretending a Size-valued frame describes the whole world. The existing transition runner is sufficient.

The implementation should enforce these details:

- Session mutation, admission and forcing depend on the preserved world and event, not on the emitted observation log. Otherwise an arbitrary non-injective observation erasure cannot commute with histories. State and failure outcomes must agree exactly; only the accumulated observations are mapped.
- A stable target denotes an identity that cannot be silently reused for a different object. Re-resolve after forcing; deletion or failed resolution produces none. Include a small target-disappearance witness. The Option runner terminates on failure and exposes no post-failure state; it proves neither native rollback nor continuation after partially mutating failures. No expanded failure framework is needed for this capsule.
- Make the selected-size-only counterprovider clear eligibility just as the reference provider does while leaving ancestor translation stale. This isolates the positional defect from readiness and demonstrates a wrong first and repeated rectangle despite successful admission and completion. The pre-force-observation counterexample should finish in the corrected world while returning the stale rectangle.
- Hidden.Size names logical inline/block axes. Mapping physical width/height directly to i/b is restricted to this horizontal-writing-mode witness, not a generic writing-mode conversion.

The c3 witness is substantive: retained measurements have first/repeat [70,25,40,16] and visible reference [30,10,40,16], so equal widths and heights do not imply equal geometry. An aggregate offset is enough to disprove selected-size sufficiency; assigning the y offset to a particular native ancestor would exceed the evidence. The reference provider's correction remains stipulated arithmetic, not a proved Gecko algorithm.

The design correctly separates unconditional observation-erasure laws from conditional compatibility with Hidden.geometryQuery. Keep explicit admission, identity, provider-output and cache/completion correspondence premises; MathML output publication is not automatically a Hidden cache-miss step. Target lifetime, coordinate-space composition, fragmented boxes, transforms, scrolling and the native ancestor repair remain outside this initial model.

No compiler, browser, build, production source or Git/index operation was performed. Only this review artifact was written.
