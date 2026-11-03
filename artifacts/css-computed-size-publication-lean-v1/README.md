# Computed-size publication and effect safety

The final run2 audited 13 Lean theorems and rejected five genuine false propositions. The tool session was 37357, launch455fe9, terminal26ae3d, exit0. The first run preserves a proof elaboration failure; it is not counted as a pass.

The model addresses a specific native review obligation: a dependent registered value can consume an early computed FontSize before the whole font pipeline finishes. A later family, text-scale, or inherited-zoom operation must not change that consumed size. Detecting a mismatched readset afterward cannot repair the already-computed consumer.

`State.size` is an opaque value label, represented by Nat; it is not a CSS numeric evaluator. `published` records a single publication within one cascade, `consumers` records copied values, and `effects` records named effect invocations. The four names illustrate separate family, text-scale, size, and inherited-zoom operations; they are not a complete inventory of native effects. Applying an effect supplies its result, rather than deriving it from CSS or native inputs.

`step` checks compatibility of the proposed resulting value before mutation, rejecting repeated effect execution and any size-changing effect after publication. Native integration must establish that compatibility before an effect runs. The model permits a distinct later effect that preserves the published size. A consumer requires a publication. The invariant additionally requires that unpublished states have no consumers: otherwise a state with stale consumers could evade the write guard merely by clearing publication.

`step_preserves_safe` checks every transition. `accepted_trace_preserves_safe` extends that result to arbitrary finite accepted event lists. The two corollaries establish that all recorded consumers equal the resulting size and that named effects remain unique. This is derived from the executable transition guards and initial invariant, rather than assumed as a property of every trace.

`late_invalidation_is_unsafe` shows why writing 30 after a consumer copied 20, then clearing the certificate, is insufficient. The controls reject claims that this updates the consumer, that a later size-changing hook is acceptable, that an effect may run twice, that consumption may precede publication, or that publication can precede a changing hook. The positive ordered trace finishes four distinct effects and a consumer; it also shows that a value-preserving later effect need not be forbidden.

This proves safety, not progress. The ordered trace is an example, not a theorem establishing native prerequisite order or a complete readset. Unique effect names assume at most one occurrence of each named effect per modeled session; mapping native loops and hooks to those occurrences remains external. A machine that rejects valid CSS inputs would not satisfy the intended implementation. Native integration must establish the actual ordering and stability of every relevant later write before publishing, so valid cases finish. Readset equality checked after consumption is only a misuse detector. Neither pointer equality nor this abstract model proves immutability of device, root, viewport, font-metric, or parent inputs.

No native refinement, native effect inventory, correct CSS conversion, full dependency graph, general liveness, or browser result is claimed. No new Firefox bug or specification-coverage increment follows. The source correspondence below is a review map, not a verified extraction.

| Model obligation | Native review point |
|---|---|
| Publication remains stable under future effects | `ComputedSizeCertificate`, `Context::computed_size_ready`, `Context::prepare_computed_size` |
| Selected operations precede consumption | Retained FontSize/XTextScale selection; family/keyword ordering |
| An applied operation is not replayed | `Cascade::ensure_prioritary_property` and the proposed applied-effect ledger |
| Omitted inherited size receives the native conversion once | `Cascade::recompute_zoom_dependent_inherited_lengths` |
| All later writers are accounted for | `Cascade::did_apply_prioritary_property` and keyword/family/language hooks |

References pin the previously sealed selection source and native hook analysis. The actively edited nonabsolute successor is deliberately not frozen here. Its construction and correspondence must be reviewed and tested separately.

The runner uses the pinned Lean 4.35.0-rc4 binary, audits every named theorem, rejects `sorryAx` and `Lean.ofReduceBool`, and permits only the standard propext/Classical.choice/Quot.sound axioms. Both owned scratch directories were removed. Run `python3 -I -S -B replay.py NEW_RUN_NAME` to reproduce without touching live native sources or Git.
