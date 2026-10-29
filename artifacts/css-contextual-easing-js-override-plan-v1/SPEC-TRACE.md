# Successful script overrides and rejected calls

**Question:** Can a contextual CSS easing restyle replace keyframes supplied by a successful script call, and does a rejected call disable later CSS updates?

**Scenario:** An existing paused CSSAnimation retains its owning element and matching keyframes rule. The script supplies literal easing and valid keyframes, or an otherwise comparable array with offset 2. Later changes affect sibling context or inherited font size. No matching rule is removed, effect replaced, animation name changed, or context-dependent easing passed through the script API.

1. [CSS Animations2, Animations](https://drafts.csswg.org/css-animations-2/#animations) gives successful setKeyframes calls precedence over subsequent matching-rule and resolved animation-timing-function changes. The explicit qualification is “After a successful call”. Removing the last matching rule remains a cancellation exception; this fixture never removes it.
2. [Web Animations, setKeyframes](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-setkeyframes) replaces keyframes with the processing result. Its deciding failure rule is “If that procedure throws an exception, this effect’s keyframes are not modified.” An offset outside [0,1] requires TypeError. The fixture uses 2, independent of unresolved contextual API policy.
3. Therefore the valid literal override remains authoritative across the later context changes. The rejected call does not satisfy the successful-call condition, leaves prior keyframes intact, and does not exempt the existing CSS effect from ordinary CSS updates.

**Verdict: REACHED** — successful-only override precedence and rejected-call atomicity are directly specified. This does not establish a new browser defect.

Primary drafts were retrieved on 2026-10-28 (CSS Animations2 dated 18 August 2026; Web Animations1 dated 8 October 2026). Both anchored sections resolved. The webspec-index executable was unavailable (cfa216/127), so this is a direct normative-section trace, not an automated exhaustive route enumeration. The ordinary CSS easing cases do not depend on the open CSSWG14246 proposal restricting element-dependent script easing.

| Native boundary | Saved-source finding |
|---|---|
| CSSAnimationKeyframeEffect::SetKeyframes | Argument processing failure returns before both mIgnoreKeyframesGeneration and the owning animation override flag. Success records CSSAnimationProperties::Keyframes. |
| CSSAnimation::PropertiesWillSetFromJS | ORs the override property into mOverriddenProperties; PropertiesOverridenByJS returns it. |
| UpdateOldAnimationPropertiesWithNew | Replaces keyframes and default timing only if the Keyframes bit is not overridden. BuildAnimation passes the existing animation's actual override flags. |
| Candidate matching.rs | Contextual keyframes request an animation update after normal restyle. This does not remove the downstream C++ override gate. |

Searchfox discovery/definition reads: c51633, 9ce21d, 98cb1a, e3842b, b0a95d, 24813b, 1dac0b, dc1092. The first lookup used the conventional double-d spelling and returned zero matches (b1664d); the actual API spelling is PropertiesOverridenByJS. Additional SetDefaultTimingFunction caller search eaa7b6/8e15f6 found the guarded old-effect setter and new-effect initialization. Immutable HEAD source joins and excerpts are in SOURCE.json. These bounded paths look correctly guarded; actual candidate behavior remains to be measured.
