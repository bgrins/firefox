# Null-progress transition origin review

The ordinary-element probe observed Firefox 158 rendering opacity 0.8 while a real CSS transition remained paused at progress 0.5 and an overlapping WAAPI animation had null progress. Removing the non-filling effect restored 0.5. All 53 setup/identity checks and all 36 reads were retained by root; this review independently checked their JSON. Active overlap behaved as the intentional Animation-origin control, and transition-only as Transition origin. This establishes release-browser behavior, not a specification violation or a new counted bug. The exact release binary was not built from the pinned source revision; the source trace is a compatible causal explanation rather than instrumented release provenance.

## Native route

SOURCES.json authenticates ten files at ec467c0219d3d5daf70f42fcc53677cf8a262173. Searchfox discovery preceded exact Git reads. The relevant route is:

1. AnimationEffect::IsCurrent accepts the positive-rate before phase; IsInEffect is false for the unresolved progress. KeyframeEffect::UpdateTargetRegistration retains IsCurrent OR IsInEffect through animation relevance. Registration has legitimate future-playback and API uses and should not be removed.
2. EffectCompositor::UpdateCascadeResults unions every property of each registered Animation-level effect, without an in-effect test, into PropertiesForAnimationsLevel. This remains true when the cache is freshly recomputed; no stale-cache premise is needed.
3. ComposeSortedEffects excludes that union from the Transition-origin composition and includes it in the Animation-origin composition. GetServoAnimationRule includes transitions in the latter stack, to support underlying values. Thus the transition can supply opacity 0.5 at Animation origin.
4. KeyframeEffect::ComposeStyle returns on null progress, so the higher WAAPI effect contributes no replacement sample. Important author opacity 0.8 then overrides the transition contribution routed through Animation origin.
5. Removing the animation changes the union, requests the Transition-origin rule again and restores the transition sample at its own origin.

This is a static causal trace matching the measured values. No native instrumentation or candidate run was performed here.

## Existing intent and known issue

[Bug 1606176](https://bugzilla.mozilla.org/show_bug.cgi?id=1606176), still NEW/S3 in the retrieved snapshot, audits stale EffectSet cascade information during no-flush paths. Comments 6–8 explain intentional circular priorities: transitions override ordinary/important rules, important overrides animations, and overlapping animations override transitions. This confirms the active-overlap control. It does not expressly address current-but-not-in-effect membership. Its referenced regression, dom/animation/test/mozilla/test_cascade.html, adds and removes an active CSS animation and contains neither delayed fill:none nor an important declaration.

[Bug 1228229 comment 5](https://bugzilla.mozilla.org/show_bug.cgi?id=1228229#c5) treats a change of in-effect status as a cascade-changing event and explicitly generalizes the mechanism to script animations; comment 7 introduces that dirtying. Current KeyframeEffect still marks cascade information dirty when IsInEffect changes. The retained historical attachment 8697695 gates winsInCascade and animatedProperties through inEffect. It is a reviewed historical draft, not proof of the final landed bytes or an identified regressing commit. Comments 40 and 42 separately affirm the important-versus-active-overlap policy. [Bug 1339704](https://bugzilla.mozilla.org/show_bug.cgi?id=1339704) discusses the transition-rule filtering and pre-traversal update mechanism; its retrieved discussion does not resolve this null-sample case. The historical Web Animations issue 97 concerns transitions detached from markup, not non-filling membership. No exhaustive novelty search is claimed.

## Specification boundary

[Applying the composited result](https://drafts.csswg.org/web-animations-1/#applying-the-composited-result) establishes a property stack, calculates its result, then inserts it at the origin of the highest-order effect. [The effect-value algorithm step 1](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect) aborts on unresolved iteration progress. The stack definition itself orders targeted effects without explicitly spelling out exclusion of non-sampling effects. The initial phases/states summary and the combining-effects introduction are non-normative; neither is promoted to a normative membership premise here. Normative current/in-effect definitions establish the distinct states but do not by themselves resolve the origin-selection question.

**Verdict: INCONCLUSIVE** for a mandatory 0.5 result in the delayed fill:none overlap. The unresolved point is whether an effect producing no effect value can still determine the origin of another effect's composited value. A CSSWG clarification or an independent complete normative trace is needed before claiming conformance. The observed result is real even if the specification ultimately permits it.

Correction to frozen earlier documentation: the effect-value anchor is `the-effect-value-of-a-keyframe-animation-effect`. The shorter `the-effect-value-of-a-keyframe-effect` link used in the earlier probe/combined report does not resolve in the current index. This review retains the corrected section and anchor check without rewriting those frozen inputs. Two failed section queries are retained as empty outputs; no evidence is derived from them. Current spec snapshot hashes appear in every successful query output. Scoped web searches found no directly deciding CSSWG issue; this is not evidence of absence.

## All direct union consumers

| Consumer | Role and consequence of filtering |
| --- | --- |
| ComposeSortedEffects | Selects complementary animation/transition masks; also serves commitStyles including its endpoint-inclusive exception. |
| UpdateCascadeResults | Publishes the union and compares its previous value to request transition restyles; membership-only changes must invalidate that rule too. |
| KeyframeEffect::IsEffectiveProperty | Combines union membership with important-rule presence. Used by GetEffectiveAnimationOfProperty and HasEffectiveAnimationOfPropertySet. |
| AnimationInfo::AddAnimationsForProperty, through GetEffectiveAnimationOfProperty | Accepts relevant effects, not just in-effect effects; asserts every admitted Animation-level property is not important-overridden. Filtering the shared union alone can violate this assertion for a delayed animation. |
| KeyframeEffect::IsMatchForCompositor / GetPropertiesForCompositor | Uses effective-property filtering while allowing relevant delayed effects; cannot silently switch the shared union to sampled-only semantics. |
| nsLayoutUtils::HasEffectiveAnimation | Uses the same effective-property predicate for relevant effects. |
| KeyframeEffect::ShouldBlockAsyncTransformAnimations | Uses union/intersection with important rules for whole-transform blocking and per-property exclusion. Preserving that classification avoids an unrelated async change. |
| EffectSet field/accessors | No other direct-field accesses were found in the scoped Searchfox identifier inventory. |

The separate copied candidate keeps the all-relevant union for these compositor/layout consumers and experiments with a second in-effect mask for normal style composition. It remains held: pending Animation::ComposeStyle can temporarily use a wallclock-selected hold time, unlike ordinary IsInEffect, and endpoint-inclusive commitStyles has distinct eligibility. The candidate preserves the inclusive legacy path but does not prove a general pending-time equivalence. No registration, timing advancement, transform side effect, or event change is proposed. Any acceptance must keep current registration distinct from sampled-origin membership, retain active-overlap/important controls, and test transition-mask invalidation when entering/leaving effect.
