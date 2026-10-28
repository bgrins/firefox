# Provider demand readiness and retry obligations

This artifact checks a small owner protocol for the inactive demand transport API. It is not a native refinement, a Tarjan proof, a CSS conformance model, or a completed provider repair. The existing registered contextual-initial admission question remains unresolved; no theorem decides that policy.

`Demand.lean` contains 13 kernel-checked declarations and seven decisive rejected false claims. It imports byte-identical `Independence.lean` and `Admission.lean` from the sealed selected-independence artifact. The new general result uses that model's normalized nested/list expression evaluator: a complete context footprint, readiness for every key, and agreement of each ready key with its final context imply equal computed values now and at completion. Completeness is an explicit semantic premise, not established by checking a prioritary bitset or by observing one value.

The executable owner abstraction retains an actual list of active owner tokens. Suspension requires the token to remain present, clears provisional effects, and preserves committed effects, published output and stack. Publication requires Applying, a retained owner and the same generation; the next publication fails, preventing duplicate effect commitment. Lookup never exposes Pending/Applying stale cache entries and accepts a Ready value only in the matching generation. These are separate obligations: the model does not prove every sequence of native operations maintains them, nor that the native context is immutable within a generation.

False controls reject unknown-as-ready, an empty footprint for a context-dependent value, cached Applying reads, retry after owner retirement, stale-generation reuse, duplicated effects and conflating a reverse scheduling request with a semantic dependency edge. The two-node edge example illustrates a false cycle if a scheduling edge is added to the semantic graph; it does not implement SCC traversal.

The concrete 800 versus 200 witnesses are abstract values motivated by the observed provider/default mismatch. They are not a normative assertion about admitting a contextual @property initial value.

## Actual interface and driver boundaries

The sealed v1 `substitute_one_reference` checks provider pending status before cached lookup and requests raw nonuniversal registered providers even if a readiness implementation incorrectly calls them ready. `PreparedRegisteredDefault::try_compute` blocks Unknown and Pending cycle classification. These are useful local properties, but the inactive API has no authoritative readiness caller yet.

The captured `traverse` retires the SCC stack entries and takes their variable names before calling `apply_prioritary_property`. `ensure_prioritary_property` inserts its ensured bit before applying dependencies or the declaration. Consequently enum-only Applying→Pending cannot provide a correct resumable traversal: the owner may already be gone, and the ensured bit may already suppress retry. Retain a suspended continuation before retirement, or reconstruct an equivalent owner transaction with a separately justified protocol. Merely adding the demand as a Tarjan edge is also unsafe: conservative prioritary scheduling prerequisites are not actual CSS read dependencies.

`AttributeTracker` reads may accumulate before a Demand. A retry needs either restoration or a documented idempotent accumulation policy; the model chooses discarded provisional effects and does not prove tracker operations satisfy that abstraction. Seen flags, cascade priority/revert state, shorthand cache, style-builder mutations, taint and inheritance effects must share the real commit boundary. A finalized provider and its consumer must use the same registration, parent snapshot and target generation. The current readiness trait does not carry those identities.

A further caller obligation is classification/plan coherence. V1 treats Acyclic and InvalidatedParticipant identically after the Pending guard. A plan prepared for CSS-wide inherit can therefore return the parent even when passed InvalidatedParticipant. For a non-inheriting registration with initial3 and parent5, that API combination returns5 rather than the invalid default3. This is a constructible invalid caller combination, not evidence that live code reaches it: the owner must select/rebuild the Invalid plan when participant classification requires it. The model does not certify this separate default-selection rule.

## Replay and limits

Run `python3 -I -S -B replay.py` from a fresh copy without its `check` directory. The script pins Lean4.35.0-rc4, compiles imported modules and the new model, prints all new axioms, and requires each negative to fail because its proposition is false. Temporary compiled outputs are removed. The checked audit contains no sorryAx or native reduction axiom.

The first draft failed on record-update syntax; the second reached all positive declarations but a negative lacked a Decidable instance. Their logs are retained as failed preparation, not successful false controls. Final `check/RESULT.json` records13 declarations and7 actual false-proposition rejections.

No browser, build, live source/index/epoch mutation or native typecheck was performed. This artifact supplies review obligations and counterexamples, not acceptance evidence. A v2 integration still needs the actual driver, transaction and context-completeness correspondence checked against its source and observed provider/consumer regressions.
