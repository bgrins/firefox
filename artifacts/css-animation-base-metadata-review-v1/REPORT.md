# Base animation metadata change detection

## Verdict

**Confirmed separate defect; narrow candidate recommended for build and paired testing.** Root's eight-case run has four failures at the final captured immediate URL-taint assertion, four passing controls and harness OK. Every failing test reaches that assertion only after initial state, changed nonanimated twin, and forced-seek checks pass. This reviewer independently read the raw outcomes and probe; no browser was run by this worker. Novelty is not established.

The defect is in base-value change scheduling, not endpoint replacement. The probe never calls setKeyframes after creating its effect. It changes the underlying declaration while a paused effect retains the same time, endpoints and payload. EnsureBaseStyles stores the new base value, but its old equality suppresses the restyle needed to consume it. A seek causes consumption of the already-correct base and passes.

## Normative path: REACHED

1. Missing endpoint keyframes use the underlying value. Effect-stack application starts with the computed property value without animations. Discrete string interpolation selects the start before halfway and the end after halfway. Thus missing-start at 25% and missing-end at 75% select the changed base. [Web Animations effect value](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-effect), [applying the composited result](https://drafts.csswg.org/web-animations-1/#applying-the-composited-result).
2. Attribute-derived values carry taint through registered-property substitution. A tainted URL consumer is invalid at computed-value time. [CSS Values attr security](https://drafts.csswg.org/css-values-5/#attr-security).
3. An image-set string represents a URL. The fixture uses a literal image-set reference to calibrate its serialized image, and no competing background declaration. The tainted result therefore becomes none. [CSS Images image-set](https://drafts.csswg.org/css-images-4/#image-set-notation).
4. Model liveness requires dependent style updates; CSSOM exposes resolved style. Pausing time does not freeze the underlying cascade. The liveness section's following explanatory invariants are nonnormative; the preceding requirement and effect-value algorithm are the normative basis. [Web Animations liveness](https://drafts.csswg.org/web-animations-1/#model-liveness), [CSSOM getComputedStyle](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle).

Exact primary documents retrieved 2026-10-19 are retained in spec, with URL and content hashes. This is a source/spec adjudication of the fixture, not a formal mechanization of these specifications.

## Runtime isolation

The registered property is noninherited, syntax <string>, with initial payload B. Base payload A and the different-payload control C differ from B. This avoids equal-endpoint interpolation shortcuts. Explicit keyframes use CSS-wide initial, not a typed unresolved attr() keyframe. The value comes from the registration's initial provider. Only the underlying declaration is changed between literal and attr() forms.

| Configuration | Expected selected value | Observed |
|---|---|---|
| Missing start, same A, clean to tainted | A, tainted | Immediate image retained; seek correct |
| Missing end, same A, clean to tainted | A, tainted | Immediate image retained; seek correct |
| Missing start, same A, tainted to clean | A, clean | Immediate none retained; seek correct |
| Missing end, same A, tainted to clean | A, clean | Immediate none retained; seek correct |
| Missing start, changed A to C, either direction | C with new taint | Both pass |
| Both explicit initial endpoints, either direction | B, clean | Both pass |

The immediate observation is captured before twin/reference checks and before seeking. The final v2 fixture additionally reads the target after the control/reference flushes, before seeking, and asserts that both payload and image remain equal to the captured immediate result. Its repeated baseline again has exactly the same four failures at the final Immediate assertion; these new pre-seek checks pass. Both raw baselines are retained. All four failures are at that observation's URL-taint assertion, after its payload check. Root RUN.json reports stable source/config/binary pins, one suite end, and exit 1 from the four expected-to-pass failures. The checker verifies the exact eight names/statuses and failure locations against raw records. It does not independently recreate browser execution or verify all root pin acquisition logic.

## Source chain and repair

KeyframeUtils supplies null missing endpoints. AnimationPropertySegment::HasReplaceableValues therefore requires a base. EnsureBaseStyle resolves the base context without animation rules, extracts the animation value, and inserts it in mBaseValues. UpdateProperties invokes EnsureBaseStyles even when property arrays compare equal. Its unchanged-properties branch requests a Layer restyle only if baseStylesChanged is true.

AnimationValue::operator== handles outer nulls and otherwise calls Servo_AnimationValue_DeepEqual. CustomAnimatedValue derives payload equality; Value<Component>::PartialEq deliberately omits taint and URL metadata. The current EnsureBaseStyles predicate therefore misses same-payload taint changes. Servo_AnimationCompose obtains underlying values from prior effects or the base map; null endpoints select that underlying value. Noninterpolable string selection preserves the chosen value's metadata.

The retained caller context includes process_animations, Gecko_UpdateAnimations, EffectCompositor::UpdateEffectProperties, UpdateProperties, effect restyle enqueue/consume and composition entry points. These establish the source explanation alongside runtime; no complete scheduler/native refinement proof is claimed.

native.patch changes only the existing EnsureBaseStyles map predicate. It retains ordinary inequality, then compares taint for custom keys with two nonnull animation values, using the already-present accessor from repair 78. A mismatch takes the existing base-changed restyle branch. No global equality, endpoint array, notification call, map ownership, base acquisition, timeline selection or target handling changes.

### Nulls, keys and notifications

- Missing old key reads as null. A new nonnull value differs already; one-null cases short-circuit before calling Rust. Two nulls remain equal.
- A nonnull CustomAnimatedValue with internal None is a guaranteed-invalid custom value, not an outer null. Its accessor returns false. Existing payload equality still distinguishes it from a present computed value.
- Noncustom entries retain the old decision. Custom key/value consistency is an existing provider premise; this patch does not construct or relabel values.
- Only new entries are scanned. Old-only removed keys remain outside the predicate. This is explicit retained behavior, not a proof of general map equality. The fixture preserves its property and base requirement.
- If property arrays change, the existing changed-properties path already notifies and restyles; the optional base-change output is not requested. If arrays stay equal, the patch only restores the existing Layer restyle trigger. It does not add NotifyEffectPropertiesUpdated on that path.
- UpdateBaseStyle passes no change output and retains its existing behavior. Absent target still returns early; scroll-timeline base eligibility remains unchanged.
- At most two additional constant-time FFI reads per equal-payload, nonnull custom base entry are added. Both AnimationValue wrappers were already constructed for the old expression. No performance benchmark is claimed.

## Exact source binding and standalone packaging

The tested KeyframeEffect original is 02ffed21d1fbbce1bd58d0df9964fa23cf1d162f3bb74212bf9e4096296463bf. The scout's older whole-file snapshot differs in endpoint-loop formatting; the proposal uses the tested file, preserving repair 78. PROPOSAL.json pins original/candidate/diff. The candidate is root-formatted SHA cee5ea606d98c23cd609b9f09f87f97d871530de059ac7e31478c025fe87cc13; only whitespace changed from the proposed expression. Packaging uses final v2 WPT SHA 3c3f231171b914e38fc60bacdc967aa34605a6b545ee5e4f2b9818131564b5d6. Other retained caller snapshots are historical context, separately hashed; this report does not claim every context file is the current whole checkout.

The standalone alternative targets retained upstream 976279105b2e78b8666a959eb3f25c9176cefaf8. It contains three native files: base comparison, read-only CustomAnimatedValue accessor, and exported FFI accessor. It does not contain the endpoint comparison loop. standalone-with-test.patch adds only the eight-case WPT, making four files. stack-with-test.patch contains the base comparison and WPT only. Exact apply/reverse is checked against retained snapshots, not a Git checkout.

No map prerequisite is included. For this fixture, init_custom_properties seeds the noninherited map with initial B. The selected base A/C differs from B, so the upstream payload-only shared-map insertion shortcut cannot discard its taint on that basis. Parsed animation publication also replaces B with distinct A/C. The explicit initial control intentionally selects clean B. The fixture does not exercise inherited equal-payload map retention, universal shortcut publication, or typed unparsed keyframe conversion. Those remain separate repairs and must not be silently bundled. This is a source-derived prerequisite analysis, not an isolated upstream build/runtime result; any failing prerequisite assertion in an upstream run must be investigated rather than counted as the target failure.

## Gates and exclusions

Root completed formatting and still owns final build, candidate eight-case pair, neighboring animation/attr regressions, and final source/WPT binding. The parallel formal component is separate and not accepted by this review. General URL-data changes, removed-key scheduling, mixed-taint numeric interpolation, multiple effects, transitions, SMIL, registration mutation, pseudo disappearance and arbitrary scheduler histories are outside this fixture's conclusion. No release-browser or cross-engine claim is made.

Replay: python3 -I -S check.py. It authenticates a closed file/directory roster, checks source and runtime bindings, regenerates patches, applies and reverses both alternatives in temporary directories, and checks the expected outcome roster. It is an evidence-integrity and packaging check, not native execution or semantic proof.
