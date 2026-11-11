# Specified keyframe getter repair

The one-file native candidate built successfully and passed its bounded browser comparison. Across 13 WPT pages, the baseline had 100 passing callbacks, 22 failing callbacks and 13 successful harness endings. The candidate had 103 passing callbacks, 19 failing callbacks and the same 13 harness endings. Exactly the three intended callbacks improved; the other 132 records, including diagnostics and expected classifications, were unchanged.

The repair selects computed keyframes only for an effect still associated with a CSSAnimation whose keyframes were not replaced through setKeyframes(). The specified branch also stops substituting variables from computed style. The regression test covers replaced CSS keyframes, detached effects and effects transferred to an ordinary Animation, with an ordinary Web Animations control.

`standalone.patch` contains only `dom/animation/KeyframeEffect.cpp` and `testing/web-platform/tests/css/css-animations/getkeyframes-specified-branch.html`. It passes `git apply --check` against the retained branch. Research and execution evidence belong in preceding commits. The patch is not applied or committed in the live tree. Signing remains pending.

`baseline2` and `candidate1` hold the actual comparison. The first baseline attempt stopped under sandbox restrictions before browser testing; its preserved failure and verified recovery are described in ROOT-RECOVERY.md. The candidate build exited zero with no compiler warnings; existing Mach build-monitor KeyError('export') tracebacks remain in the complete log. This optimized experiment does not establish debug/sanitizer coverage or repair general computed-value serialization or missing-pseudo CSSOM behavior.

The Web Animations getKeyframes() branch rule is at https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-getkeyframes. This defect was found through source/spec analysis and browser tests during the verification work; this candidate is not backed by a new Lean proof of native execution.
