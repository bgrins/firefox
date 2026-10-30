# Masked-font admission isolation

The final masked-font update is independent of the disputed own-versus-base timing policy: after the authored font becomes 32px, both underlying and animated font are 32px, so duration is 2s and paused 750ms opacity is .375. Frozen original 61482/249ad8/0 instead retains effect 1000ms/.75 for all four samples, while its computed duration list stays 2s,2s before and after the mutation. The literal control reaches 2000ms/.375. This package does not read or replace the active four-source trial.

## Smallest isolation patch

native.patch changes one fallback in accepted matching.rs 41e95acc: eligible Gecko normal traversals request CSS animation updates. Non-Gecko fallback stays false. The original animation-only early return and preceding no-CSS, missing-old-style, rule-change, display, writing-mode and scroll checks remain intact. Manager 3b24 and the original boolean EffectCompositor are unchanged.

The source argument is concrete but not an executed prediction. The recorded old/new composed animation lists are equal. If the preceding admission reasons are false, needs_animations_update reaches its false fallback; the completed run did not trace that branch. Existing EFFECT_PROPERTIES work does not select new CSS timing through the manager. The isolation queues CSS_ANIMATIONS together with EFFECT_PROPERTIES; unchanged manager then reads composed 2s. StyleDocument already calls compositor PreTraverse after the first traversal. Original PostRestyleForAnimation explicitly retains requests made inside Servo for that follow-up. This path can therefore repair the case without tri-state; only an isolated build can establish that it actually does. Literal PASS does not prove the contextual task's exact scheduling location.

## Why this is not yet a landing fix

Unconditional normal admission with the composed manager can also retime after an unrelated outline or same-value style mutation while underlying font remains 16px and animated font is 32px. It would select composed 2s although original Firefox and Chrome initial effects use 1s. Testing only the final masked 2s can conceal that input-policy change. Manager-only pre-own timing likewise cannot fix a missing CSS_ANIMATIONS task.

No complete hidden-base-change predicate follows from old/new composed lists or composed font metrics. Rule-node identity misses inherited/root-input changes with identical child rules; it is not a historical value-generation certificate. important_rules_changed is also insufficient: MatchAndCascade sets it, but ordinary style-attribute replacement returns the important-rule change result, so a normal inline font mutation can escape it. Neither proxy is proposed as a complete invalidation condition.

The precise value-level condition is a freshly resolved selected CSS animation input list differing from the previous selected list actually supplied to the manager, with all existing keyframe/display/writing-mode/timeline update reasons retained. That needs a separate input snapshot or a proved generation certificate and an explicit timing-source policy. Effective timing cannot substitute: a script-owned updateTiming override may intentionally differ from CSS input.

A conservative implementation may check selected input on every already-recomputed eligible CSS-animation target, then skip expensive updates when that list and all other update reasons are unchanged. It still needs target invalidation for hidden inherited font/lh, global rem/rlh/device metrics, variables/registration/taint, rule edits and pseudo lifecycle. Fresh evaluation after admission does not prove every affected target was admitted. The current one-line patch implements neither that cache nor a general safe selective invalidation scheme.

## Standalone candidate WPT

tests/css/css-animations/animation-duration-masked-font-update.tentative.html has one callback, standard testharness resources and no private receiver, run ID, browser helper or preference override. It keeps the original ready/paused 750ms acquisition and three setup frames, then changes the inline font exactly as the diagnostic did. This deliberate CSSOM mutation tests the style-attribute replacement path. The first getter reads opacity before timing or membership; captured first opacity cannot be repaired by later getters. Final duration/progress, retained animations/effects/currentTime/paused state are asserted. Initial animated font 32 is calibrated, but no initial opacity or contextual duration is asserted.

This is an unexecuted reduction: removing diagnostic collection and initial numeric assumptions may affect reproduction. It is not a measured PASS/FAIL and is not installed in the WPT tree. It intentionally tests synchronous first-read behavior, so the style flush is part of the regression oracle rather than application performance advice.

Fresh Searchfox declaration a6c1be/0 says typed arithmetic defaults true. Root's exact capture fc64e6/0 additionally joins StaticPrefList whole-body 5e4d6ed4 to both HEAD ecfe and original build 20ab and records value: true. No enabling WPT metadata is needed for this branch's declared default. This does not claim a separately executed release-browser default or that arbitrary external profiles cannot override it. The test explicitly asserts syntax support. The original research runner's inherited preference alone was not used as evidence.

## Required isolation tests

- Run the exact masked diagnostic and standalone test with only this matching change, original manager and original compositor. Preserve initial and final observations; predicted final 2s/.375 remains untested.
- Keep underlying 16 masked by 32 and apply unrelated outline/same-value mutations. Any opportunistic 1s→2s retiming exposes the composed-input risk, not a justified repair.
- Exercise normal inline, class/rule, inherited font/lh and root rem/rlh changes with literal controls. These falsify pointer-only or important-rule-only admission.
- Preserve script-owned timing/currentTime, inactive-but-specified CSS animations, no-CSS targets and pseudo identity. Output PASS cannot establish dispatch counts.
- If matching-only corrects effect timing but not first output, compare the identical patch with tri-state and inspect actual pending/consumption evidence. Do not add a drain loop or a guessed pass budget.

No native checkout, browser, build, index or canonical state was changed. The patch is an experimental decomposition, not an accepted fix or general completion policy.

Offline check 637652/0 applies and reverses the exact one-line patch in owned scratch, registers the one callback inertly, generates a genuine WPT manifest, and passes WPT path/content lint. Repository-wide and Git-ignore lint scans were deliberately not invoked; a process audit rejects Git execution. All 14 referenced bodies authenticate and scratch is removed. This does not execute the callback or compile native code. Independent review904352 found no source/test blocker; its requested qualification that the untraced admission branch is a hypothesis is incorporated.
