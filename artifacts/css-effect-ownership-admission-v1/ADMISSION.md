# Effect ownership companion admission

Read-only review on 2026-10-29 against canonical `css-spec-lean` HEAD `162b20fb7c53a0ab89b20875a965baee98fb66bb`. Companion `FILES.json` SHA-256: `654f1ff3e6382614a52a2ef6396d1d4d988ae199c1721af6e53bffddd1091005`; `Ownership.lean`: `27f54d3fb6f9c22d127786a3fdea9be38f3a8e65ca4a20bb65c344bb6825c369`. Imported `Dependency.lean`: `d49c2f91465f95ba9051d517acb805b32c19612abe8d76e219574fac1862add6`.

**Admit as a distinct standalone implementation-support companion.** Its material addition is the successful/rejected override protocol and arbitrary finite event-trace composition. It is not new native behavior, browser acceptance, a full CSS feature, or canonical coverage. No kernel replay was performed in this admission review; the existing eight audits and three rejected false controls remain producer evidence.

## Deduplication

All canonical names below are under `CssSemantics`; files have the corresponding module names.

| Existing module/declarations | Existing obligation | Ownership delta |
|---|---|---|
| `ImplementationSupport.KeyframeContext.shared_provider_current`, `literal_context_independent`, `midpoint_disagrees` | Common current provider versus endpoint-local exact-rational sampling | No owner state or API-call outcome |
| `ImplementationSupport.KeyframeGraph.complete_sample_correct`, `evaluation_order_independent`, `history_correct`; `KeyframeSchedule.constructed_sample_correct` | Finite DAG dependency scheduling and current caches | No CSS/script precedence |
| `ImplementationSupport.KeyframeEndpointDefaulting.dependency_agreement`, `advance_current`, `history_current`, `value_is_canonical_compute` | Token-list substitution, typed defaulting and context-dependent refresh | No override success/failure protocol |
| `ImplementationSupport.CommitRefresh.refreshed_prefix_current`, `scheduled_provider_prefix_current` | Ordered contributing-effect composition after covering refresh | Refresh obligations do not establish whether CSS may replace script-owned keyframes |
| `StepsOrigin.repaired`, `normalized_bounded`, `repaired_jump_none_at_one` | Literal/calculation step-count admission, normalization and clamping | No effect ownership or trace shielding |
| `TransitionMachine.run_iff`, `Runs.preserves` | Generic token-machine execution and invariant induction | Reusable machinery, not CSS transition or setKeyframes semantics |

`EffectOwnership.successful_override_shields` and `rejected_call_erases_from_trace` are the two substantive protocol results. `script_step_preserves` and `script_trace_preserves` are supporting composition lemmas. `css_refresh_uses_selection` and `new_transition_uses_css_selection` expose stipulated event branches; `rejected_then_refresh_remains_css` and `independent_consumer_witness` are concrete witnesses. Do not label eight audited declarations as eight independent discoveries.

The separate dependency artifact already proves `ContextualEasing.expr_locality`, `parameters_locality`, `cache_sound`, `field_support_does_not_identify_rule`, `context_changes_retain_capture`, `new_transition_captures_latest`, and `property_refresh_is_not_effect_refresh`. The ownership artifact imports its evaluator but does not use the locality/cache theorems to derive its ownership results. Its transition-start branch and retained-capture witness receive no additional independent transition-invariant credit.

## Minimal integration choice

Preserve this sealed companion and reference it as conditional implementation support. This is useful without modifying the canonical library, its imports, coverage counts, or current validation epoch. Record the two substantive protocol results and the six helpers/branch facts/witnesses separately in any later admission ledger; transfer adds zero proof-discovery credit.

There is no faithful drop-in canonical type for `ContextualEasing.Context = Field → Nat` and its arithmetic `Expr`. `KeyframeContext.Expression` has only exact-rational literal/provider cases. `KeyframeEndpointDefaulting.Expr` is `VariableExpr Token` with named optional token-list environments and typed defaulting. `StepsOrigin.Specified` is an already-resolved integer admission boundary. Replacing the imported types with any of these silently changes the subject. A later canonical transfer should import a single explicitly admitted contextual-dependency module, retaining its type/semantic limits, or first establish a concrete evaluator correspondence for a selected canonical fragment. Do not introduce a generic wrapper merely to manufacture a library connection. Existing `TransitionMachine.Runs.preserves` can discharge invariant induction if a later independent event relation is justified; adapting the runner alone adds no CSS coverage.

## Required claim boundaries

The companion's `MAPPING.md` and `SPEC-READ.json` map successful-only precedence to CSS Animations 2 `#animations`, and failure leaving effect keyframes unchanged to Web Animations 1 `#dom-keyframeeffect-setkeyframes`. This review inspected that recorded mapping, not a fresh exhaustive specification trace or C++ refinement.

* `setKeyframes (.error _)` is an already-processed, side-effect-free modeled event. Full-state erasure does not establish rollback of getters, iterators, reentrant calls, other author-script effects, or mutations outside this model. Native keyframe preservation on processing failure is weaker than arbitrary-world-state erasure.
* `refresh` always supplies a selected declaration and root. There is no absent-selection/removal event. The last matching `@keyframes` rule removal cancellation exception, animation-name changes, cancellation and effect replacement remain excluded. Shielding must never be extended across these lifecycle changes without new semantics.
* `NoSuccessfulOverride` restricts later accepted overrides; the finite event alphabet also excludes all lifecycle exceptions above. The theorem concerns only keyframe precedence, not every animation override bit.
* `Selection.root` and `Selection.declaration` are supplied natural-number identities, not canonical scope-root or cascade provenance proofs. Equality of support does not prove identity or equal expressions.
* Transition eligibility is stipulated. `startTransition` captures independently computed CSS parameters, not script frames; this does not identify actual animation/transition longhands or prove scheduling, reversal, progress, composition or rendering.

No canonical files, native files, build/browser state, Git references, indices or epochs were changed. This admission note is the only file written by this review.
