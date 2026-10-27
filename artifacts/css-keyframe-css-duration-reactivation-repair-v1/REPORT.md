# Rebuild effect properties after CSS animation updates

The native proposal adds one EFFECT_PROPERTIES task insertion beside the existing CSS_ANIMATIONS insertion in Gecko process_animations. It does not change the has_animations block, important-rule condition, display-change condition, task dispatch, or C++ code. The standalone patch contains only matching.rs and the exact existing six-case CSS duration WPT.

The original matching.rs body hashes d33ac615aec618d5b68f6b37a9d9b8eb8f35f2691ece88f757d433c78fca38ac. It matches sealed actual 66317 FINAL-PINS and the current follow-up diagnostic baseline/final source guards. SOURCE-BINDINGS joins six relevant archived bodies to that follow-up baseline. The follow-up terminal capsule and peer review were still pending while this proposal was prepared; PENDING-FOLLOWUP records only that limited provenance. No candidate build or browser result exists yet.

## Source argument

Let C mean needs_animations_update returned true, H mean the pre-task EffectSet query succeeded, I mean important_rules_changed, and D mean display changed from none. Before the patch, effect-property work is requested by H. Afterward, it is requested by H or C. CascadeResults remains H and I; DisplayChangedFromNone remains H and D. The complete native postimage differs by exactly one inserted statement, which the static checker verifies. The existing animation-only early return is unchanged.

The pre-task H query cannot cover an effect that becomes relevant during CSS manager work. Gecko_UpdateAnimations invokes AnimationManager::UpdateAnimations before its EffectProperties branch. The former can extend an old animation's duration, calling SetSpecifiedTiming and registering a previously irrelevant effect. The following SetKeyframes sees unchanged declarations and can return before UpdateProperties. EffectCompositor::UpdateEffectProperties then retrieves the current EffectSet, so the new task bit reaches the reactivated effect using the already-supplied current computed style.

This uses the existing sequential post-manager update route. It introduces neither a direct normal restyle from registration nor a recursive UpdateProperties call inside registration. When the manager creates a new effect, the extra update may repeat already-computed properties; the existing equality path handles unchanged values. When the manager removes all effects, UpdateEffectProperties returns for an absent set. Gecko_UpdateAnimations retains its null-computed-style early return. These source facts support the narrow scheduling change; a native debug build and browser comparison must still check assertions and unexpected restyle behavior.

No tree-counting v2 native change is required. The duration test initially computes sibling-count correctly on the original stack, then holds the effect outside its active interval, mutates and flushes siblings while it is irrelevant, and extends its CSS duration. The added task makes that CSS update rebuild the ordinary keyframe properties. All sensitivity flags, DOM mutation publishers, attribute handling and viewport paths remain exactly as before.

## Validation boundary

The WPT body is byte-identical to the measured draft (SHA 9ce483fa48f486af789ed436b73507103dde9364a8209b43a58cbb1d94a15d35). It contains width and transform reused-after-change targets plus fresh-effect and unchanged-context controls for both properties. It changes CSS duration, not JS timing ownership. First values are captured before later getters. Parent reports two calibrated target failures, 20 instead of 40, with all four controls passing; final terminal authentication remains separate.

Require an exact baseline, a candidate with all six cases passing, and original restoration, while retaining the existing tree/replay/attr/viewport observations and appropriate animation regression controls. A change in unrelated outcomes requires investigation. External replay without a CSS animation style update, named-timeline changes on other targets, effect retargeting, attribute initialization/invalidation and viewport updates are outside this patch's claim.

Static checks authenticated source/fixture references, applied the exact two-path patch in disposable scratch, compared both full postimages, removed scratch, checked JS syntax and registered six inert tests. There was no native compilation, callback execution, browser launch, live source/index mutation or acceptance decision.

Replay: python3 -I -S -B artifacts/css-keyframe-css-duration-reactivation-repair-v1/check.py --output ABSENT_DIRECTORY.
