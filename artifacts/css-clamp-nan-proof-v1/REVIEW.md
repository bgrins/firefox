# Preparation review

The model separates specification, implementation-shaped dispatch, and recursive simplification. `ClampRelation` gives a relational order specification independent of the selection implementation. `orderLaws` is proved rather than assumed. `simplify_sound_unconditional` quantifies arbitrary finite trees and arbitrary context functions; no numeric sampling premise appears.

The core simplifier conservatively retains unknown inputs and nonleaf operations. Its finite relative-unit theorem is a separate local commutation result and is not misrepresented as integrated coverage of the proposed native algorithm. The native design's mixed-unit fallback still needs a complete bridge; `guarded_early_return` states explicit universal semantic premises rather than inferring safety from a raw coefficient.

Mutation inventory reviewed from `discovery-v1/report.json`:

- Dropping an unknown upper child breaks fold preservation and the retained witness.
- Censoring upper NaN breaks binary selection, NaN propagation, and infinity controls.
- Censoring lower NaN breaks maximum equivalence and NaN propagation.
- Collapsing signed-zero order breaks order proofs and concrete zero controls.
- Censoring nested NaN breaks structural simplification preservation.
- Losing the zero-basis multiplication sign breaks scaling monotonicity.
- Accepting relative infinity at zero breaks the explicit NaN counterexample.

Every mutant has a valid changed definition and fails in theorem proof bodies. The expected diagnostics are frozen; the runner rejects unexpected errors, successful mutations, missing audits, compiler stderr, foreign paths, and source changes. Seven mutation failures do not prove mutation completeness.

Primary spec material is a subsection/excerpt of the already fetched reviewer snapshot, with source URL, retrieval time, full-document SHA-256, and excerpt hashes in `SPEC-v1.json`. This agent read that snapshot; it did not refetch it.
