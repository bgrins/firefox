# Scoped commitStyles pre-compose endpoint refresh proposal

**Exploratory one-file proposal, not a compiled or runtime-verified repair.** It targets commitStyles snapshot freshness without introducing public pending AnimationValues. It does not claim to solve general active dependency sampling, cycles or performance. No live native source was edited or patch applied.

Root reports terminal capture59678exit0 with two controls PASS and five calibrated snapshot FAILs. Root completion49563 also passed. The runtime/root seals are references, not an independent terminal review by this source audit. Source joins below use the already authenticated restored epoch96ca8; all six bodies match exact current archived roles. Searchfox discovery confirmed CommitStyles, ComposeServoAnimationRuleForEffect, UpdateEffectProperties and Gecko_UpdateAnimations. Searchfox's nsStyledElement::SetInlineStyleDeclaration definition calls SetAttrAndNotify for the style attribute; that additional discovery is not an archived current-epoch body pin.

## Exact missing step

CommitStyles flushes Frames, builds an animation-value map, serializes the concrete values into an inline declaration, then publishes the inline change. ComposeServoAnimationRuleForEffect holds the target's full post-flush ComputedStyle but calls only aEffect.UpdateBaseStyle(style). UpdateBaseStyle invokes BuildProperties and passes its temporary result to EnsureBaseStyles; it never replaces mProperties. Explicit replace endpoints usually require no underlying base value, so freshly computed endpoint segments can be discarded while composition still reads stale retained segments.

BuildProperties uses Servo_GetComputedKeyframeValues with the supplied style. The registered branch starts from style.custom_properties(), applies the existing keyframe custom-property builder/defaulting and extracts concrete values. Existing UpdateProperties retains those rebuilt segments, base styles and dependency state. No new parser, registration defaulting, attr namespace or public serialization contract is needed for this experiment.

## Proposed exact loop

The patch changes only ComposeServoAnimationRuleForEffect. It preserves the existing sorted prefix through the committed effect, snapshots strong references to every effect in that prefix, calls existing UpdateProperties against the same full target style, updates cascade bookkeeping again, reacquires EffectSet, then invokes unchanged ComposeSortedEffects. The earlier base-only call is removed because UpdateProperties itself calls EnsureBaseStyles. The committed effect remains included even when absent from EffectSet, preserving the finished/no-fill route.

Refreshing only aEffect would miss a lower contributing effect with stale dependencies. The prefix intentionally remains the existing global prefix used by this implementation; the patch does not introduce a different property filter or discard unsupported values. Higher provider animations remain outside that composition prefix but contribute through the full computed provider context. A higher consumer remains excluded from the committed partial result. No value is replaced with the target's final consumer (which is999 in the higher-consumer control). All refreshes and map composition occur before any inline write.

Strong references retain prefix effect lifetimes across UpdateProperties. Reacquiring EffectSet avoids retaining a stale raw set pointer across refresh calls. Updating cascade results afterward accounts for changed property sets. These are source-level precautions, not proof against all reentrancy. Existing UpdateProperties can publish dependency state, alter effect/cascade bookkeeping, notify its Animation and schedule a layer restyle; the proposed call is not a pure temporary evaluation. Review notification/reentrancy, transition-level and endpoint-inclusive behavior before treating it as landable. The frozen style must remain the dependency environment for this operation rather than recapturing a partially changed context mid-loop.

## Post-inline correction is an inference with a source chain

Matching's process_animations skips EFFECT_PROPERTIES during animation-only traversal with old style. Normal traversal with effects schedules it; Gecko_UpdateAnimations dispatches to EffectCompositor::UpdateEffectProperties, which calls UpdateProperties. Inline style notification followed by a computed-style query can therefore rebuild stale endpoints. This explains stale committed inline followed by corrected animated consumer and why the important-provider mutation can already repair the control. It is source-supported, not instrumented causal proof. The existing fixture does not export pre-inline endpoint caches or provider style, and calls getAnimations before collecting all after-values.

Another flush alone is not justified: no extra ordinary restyle may be pending. Dummy inline mutations would change observable behavior. The patch directly reuses the context-taking refresh seam instead of relying on those effects.

## Scope limitation and admission

For the measured literal independently sampled providers, the initial animation flush can update provider values while retaining a stale consumer cache. That makes the patch a concrete candidate for the seven cases. It is still necessary to verify that the held style contains current providers at the composition boundary.

A two-hop provider chain is a counter-boundary: if animated providerP itself retains stale endpoints depending on animatedQ, refreshing consumerC against a frozen staleP does not repair it. Composite order is not dependency order. The patch deliberately does not drop such rules, substitute initials/fallbacks or claim convergence; it preserves existing semantics outside what refresh establishes. Cycles, same-keyframe providers, multiple committed dependent properties, additive/accumulative and neutral endpoints remain explicit validation obligations. Existing cascade/defaulting/taint behavior is reused, not independently proved.

A temporary-properties composition seam could avoid retained-cache side effects but would require more code and a separate ownership contract. This small candidate is for testing the existing UpdateProperties route first, not a universal replacement for the active-sampling implementation.

Normative partial-stack/full-provider/snapshot requirements come from sealed commitStyles spec trace4415d178. No new normative cycle rule or bug count is claimed.
