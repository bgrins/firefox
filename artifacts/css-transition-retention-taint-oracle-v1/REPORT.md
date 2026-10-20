# Running transition endpoint provenance: oracle unresolved

**Verdict: INCONCLUSIVE.** The source-supported retention behavior is not sufficient to justify a bug, repair or asserted WPT. No browser was run. Primary documents were retrieved on 2026-10-20 UTC (19 October local). No Lean proof or global equality change is proposed.

## Question and scenario

A registered `<string>` property has a running, paused, `allow-discrete` transition from A to B. At 75% progress its stored destination B is selected. Replace the underlying declaration with an equal string B whose source changes between a literal and `attr()`. Observe transition identity, serialized payload and `image-set(var(--property))`. The disputed question is whether attribute provenance participates in the transition algorithm's value equality. This is separate from how interpolated numeric values acquire taint; that investigation belongs to `css-animation-interpolation-taint-oracle-v1`.

## Current primary-spec trace

1. Registered `<string>` values compute as specified; registered custom-property animation uses its type. The registration and parsed value must be valid. [Properties and Values API, computed values and animation behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior-of-custom-properties).
2. `allow-discrete` admits discrete transitions and selects the second value after the midpoint. [Transitions 2 §2.1](https://drafts.csswg.org/css-transitions-2/#transitionable).
3. At transition creation, Transitions 1 §3 stores the after-change property value as the end value. On later style changes, §3 step 4 enters cancellation/replacement processing only if the stored end value and new after-change value are unequal. Merely changing the declaration is insufficient. [Starting transitions](https://drafts.csswg.org/css-transitions-1/#starting).
4. The current transition value is computed from its stored start/end values and progress. No reviewed step refreshes just the provenance of an otherwise retained endpoint. [Application of transitions](https://drafts.csswg.org/css-transitions-1/#application).
5. Attr-derived values carry taint through substitution, including registered-property equivalent token sequences; tainted URL use is invalid at computed-value time. This makes provenance observable, but does not explicitly define equality for the transition-retention decision. [Attr security](https://drafts.csswg.org/css-values-5/#attr-security).

**Unresolved branch:** if equality includes provenance, step 4 may cancel or replace according to its other guards. If equality is payload-only, the prior transition retains its previously captured destination. Requiring the old transition identity *and* freshly substituted metadata would introduce a third, hybrid rule not found in this trace. A metadata difference alone does not prove that a restart is required; even on the unequal branch the current-value and transitionability guards matter.

Keeping an older literal B while a new attr() also produces B does not alone show information disclosure: the retained literal was already present. Conversely, an older tainted B can remain tainted under the captured-endpoint interpretation after the underlying declaration becomes literal. Both observations can distinguish interpretations; neither settles which interpretation is normative.

## Exact source path

`SOURCE-PINS.json` binds complete current glue/value snapshots and the complete transition manager. Searchfox discovery of `nsTransitionManager.cpp` exactly matches the local file; the locally modified Rust snapshots are kept separately from the earlier indexed code.

- `ExpandTransitionProperty` admits custom names. `ConsiderInitiatingTransition` supplies `oldTransition->ToValue()` to `Servo_ComputedValues_ShouldTransition`.
- The Rust routine computes the new animation value, compares the old end value by `PartialEq`, and returns `old_transition_value_matches` before constructing replacement endpoints. C++ returns without replacement on that result.
- `DoUpdateTransitions` has a subsequent cancellation sweep. `Servo_ComputedValues_TransitionValueMatches` uses the same payload equality, so the proposed equal-string metadata flip passes that sweep too.
- `Value<Component>::PartialEq` explicitly omits `url_data` and `attr_tainted`; `CustomAnimatedValue` includes the property name and optional value. Different property names are not silently equated by this witness.
- `DoCreateTransition` constructs stored keyframes through `GetTransitionKeyframes`/`AppendKeyframe`. String animation reports an error; `compose_animation_segment` then clones the selected endpoint. Thus this probe avoids the numeric `Value::animate` provenance-combination question.

**Static prediction, not browser evidence:** same-payload changes retain the original transition and its prior endpoint taint; explicit seeking does not change that. Different-payload controls replace the transition; removing transition-property exposes the new underlying value. Ordinary opacity transition identity remains stable when its destination is unchanged.

## Existing tests and issue search

The spec links `attr-security-transition.html`: it creates a transition to an attr-derived string and checks its selected destination is tainted. `attr-security-transition-interpolated.html` tests numeric/length interpolation into `if(style())`. Neither changes the provenance of an already stored same-payload destination. Complete upstream files are retained in `spec/`; they are supporting prior tests, not normative definitions.

Two scoped web searches on 2026-10-19 (`site:github.com/w3c/csswg-drafts attr taint transition equality` and `site:github.com/w3c/csswg-drafts "attr" "transition" "equal"`) found no resolving issue. Search results included issue 13933 about **animation-taint on inheritance**, a different mechanism. This bounded negative search is not an exhaustive prior-art search or a novelty claim.

## Small diagnostic for possible root execution

`diagnostic.html` is standalone and **unexecuted**. `await runTransitionRetentionProbe()` returns four rows: both taint directions, each with equal or different destination text. It records old transition identity, play state, payload/URL observations, keyframe serialization, explicit resampling and transition removal.

Assertions cover only prerequisites/controls: both transitions exist; literal URL calibration; stored start/end selection before mutation; changed nontransitioned declaration; unchanged ordinary opacity transition identity; and the new underlying value after transition removal. Disputed post-mutation URL/identity results are records, not assertions. Passing this diagnostic would not resolve the equality oracle. It is not a WPT proposed for submission.

The next substantive step is a specification clarification of equality for provenance-bearing computed values, ideally with this minimized retained-endpoint scenario. No repair should be implemented until that obligation is justified. No issue was filed or message sent externally.

Interpolation-oracle coordination: its proposed both-contributing arithmetic taint contract creates no transition equality, restart or retained-endpoint refresh obligation. This investigation does not import such a conclusion.
