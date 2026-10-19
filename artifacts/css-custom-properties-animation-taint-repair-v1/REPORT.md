# Retained custom-animation endpoint taint

## Status and recommendation

Propose the three-file `native.patch`: retain ordinary payload equality, then compare attribute taint on both endpoints of equal custom-property segments in `KeyframeEffect::UpdateProperties`. No live source, browser or build was changed by this worker. Compilation, generated C++ binding and candidate runtime remain root gates.

Root's original typed-endpoint diagnostic is reproduced in `evidence`: exactly two same-payload update cases fail, four different-payload/fresh-effect controls pass, and the harness is OK with stable pins. The failures occur at the final updated-effect URL-taint assertion after prior payload/raw-keyframe checks. This confirms the existing route on the combined project build. It is not an upstream runtime result.

`csswide-endpoint-taint.html` is a new six-case proposal, not an executed test. It avoids the earlier typed keyframe substitution repair by obtaining endpoints through existing CSS-wide `initial` and `inherit` providers. A separate one-site map prerequisite is necessary to address a publication obstruction on upstream; it is included only in the explicit standalone alternative. No claim of dependency-free upstream runtime is made.

## Normative trace

1. `setKeyframes` replaces the effect's keyframes. Their property values are computed before effect-value calculation. The replacement syntax is different even when the computed text is equal. [Web Animations](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-setkeyframes), [computing property values](https://drafts.csswg.org/web-animations-1/#computing-property-values)
2. Explicit `initial` selects the property's initial value; `inherit` selects the parent's computed value. Registration supplies the string initial value in the proposed fixture. [CSS Cascade explicit defaulting](https://drafts.csswg.org/css-cascade-5/#explicit-defaulting)
3. Attribute-derived values carry taint, including registered-property token equivalents used by substitution. A tainted URL makes the consuming declaration invalid at computed-value time. Literal equal text does not have that provenance. [CSS Values attr security](https://drafts.csswg.org/css-values-5/#attr-security)
4. Each effect has constant endpoints with identical taint, uses replace composition, and is sampled at a fixed interior time. Thus the test does not depend on a rule for interpolating different endpoint taints. A literal image reference calibrates the URL consumer. The observed `background-image` must change when the replacement changes taint while preserving text.

Verdict: **REACHED**, subject to the explicit fixture prerequisites. The proposed CSS-wide test checks parent computed text and tainted URL behavior, fresh effects, current computed text, raw replacement keyframes and final URL behavior. No if() syntax, external resource load or secret value is used. Novelty is not established; the prior audit retains related WPT-sync issue context.

## Actual source path and chosen boundary

`KeyframeEffect::SetKeyframes` first compares raw keyframes. The tested literal/attr and initial/inherit spellings differ, so it stores the new raw sequence and calls `UpdateProperties`. `BuildProperties` obtains computed values through `KeyframeUtils::GetAnimationPropertiesFromKeyframes` and `Servo_GetComputedKeyframeValues`. `AnimationProperty` equality compares property identity and segment arrays; `AnimationPropertySegment` equality compares offsets, both endpoint `AnimationValue`s, timing and composite operations.

C++ `AnimationValue::operator==` delegates to `Servo_AnimationValue_DeepEqual`. The generated Rust enum and derived `CustomAnimatedValue` equality reach `Value<Component>::PartialEq`, which compares payload and deliberately omits taint/URL metadata. Consequently the existing `propertiesChanged` can be false despite a changed endpoint taint. `EnsureBaseStyles` runs, but the early return then leaves old `mProperties` in place. The string type's non-interpolable path clones the selected endpoint. Subsequent substitution observes the retained taint.

The proposal keeps all these equality operators unchanged. A new read-only custom-value accessor returns the computed value's taint, or false for guaranteed-invalid `None`. A new FFI function returns this bit for custom animation values and false for other variants. The C++ lambda handles null endpoint values before the FFI call.

Only when ordinary property arrays compare equal does `UpdateProperties` inspect custom-property endpoints. Equality has already established matching array lengths, property identities, segment counts, offsets and endpoint nullness. The added indexed reads therefore use the same array shapes; a taint mismatch takes the existing changed-properties path. Both from/to endpoints are checked. Different payloads, non-custom property decisions and all unchanged endpoint bits preserve the original decision.

The normal replacement, compositor-state preservation, effect-set update, change notification and restyle code remains intact. No arrays are mutated while reading, no ownership is transferred by the accessor, and there is no allocation or callback in the new check. Generated FFI declarations are expected from existing geckolib cbindgen configuration; no generated header is manually patched. Actual compilation is still required.

## Equality consumers and scope limits

- Raw-keyframe equality is untouched. Changes to attribute content with identical raw keyframes involve scheduling/admission beyond this test; the proposal does not claim to repair every such path.
- Global `AnimationValue`/custom-value equality, transition-value comparisons, interpolation/addition decisions, segment equality and CSS-animation array equality retain their previous semantics. The extra bit check is local to retained property replacement.
- `EnsureBaseStyles` still uses ordinary AnimationValue equality for its change notification. It rebuilds its base-value map, but taint-only base-change scheduling deserves a separate audit; this proposal does not claim that route closed.
- URL metadata equality is not added. This repair addresses attribute taint; general observational substitutability of equal animation values is not proved.
- Numeric mixed-taint interpolation, additive composition, neutral endpoints, SMIL and transition creation are not tested or claimed repaired. Constant string endpoints avoid those questions.
- Equal arrays incur a second property traversal and, for custom properties, up to four constant-time taint queries per segment. Different arrays incur no extra traversal. No benchmark was run; unusually large equal custom animations are the relevant performance review case.

## Standalone dependency analysis

The original typed test uses the earlier fix70 branch in `Servo_GetComputedKeyframeValues`: typed unparsed declarations are taken from the computed keyframe map. Upstream instead attempts to parse the raw attr() text and can fall back to a universal value. Therefore that test cannot establish this repair's standalone behavior.

The proposed CSS-wide route uses `CustomAnimatedValue::from_declaration`'s existing initial-cache and inherited-map branches; fix70 applies only to typed Unparsed declarations and is bypassed. Initial cache and parent maps are selected by the registration. No missing-parent/root fallback, relative unit, namespace, cycle, invalid typed fallback or registration mutation is used. `inherits:true`, a distinct grandparent string and a fresh parent attr declaration ensure the parent computation replaces a different inherited payload. The test asserts parent admission rather than assuming it.

Unregistered/universal raw attr endpoints were rejected as an alternative: their preserved raw token text differs from a literal, so they do not independently exercise equal computed payload retention. Universal CSS-wide endpoints would still face publication metadata issues and add no useful independence.

There is a further publication dependency. `Cascade::init_custom_properties` starts the child's inherited map from the parent's map. The animation's parsed declaration enters `cascade_custom_property`, then `insert_var`/`CustomPropertiesMap::do_insert`. In upstream, the shared-map early return compares payload alone. With parent tainted A and an untainted initial endpoint A, this can retain parent taint even in a fresh effect. An explicit distinct underlying child B does not by itself fix this: higher-priority animation declarations are visited before lower-priority child declarations, and the latter are suppressed by the seen-name set. Do not rely on unspecified declaration ordering to force map ownership.

For this typed CSS-wide fixture, the minimal identified support is the already-known one-site `do_insert` change to `can_deduplicate_values`. The Parsed branch does not use the universal-value cascade early-out, so the second site from fix76 is not bundled. The standalone alternative does not include fix70, map count/iterator repairs or unrelated cascade changes. This is a source-derived sufficiency argument pending isolated runtime, not proof that there are no further platform/provider dependencies.

| Package | Contents | Meaning |
|---|---|---|
| `native.patch` | Three endpoint-comparison files | Stack repair with metadata publication fix already present |
| `stack-with-test.patch` | Above plus six-case CSS-wide WPT | Proposed normal landing package |
| `prerequisite-map-support.patch` | One existing map metadata comparison | Explicit standalone prerequisite; not a new defect |
| `standalone-native.patch` | Endpoint repair plus one-site support | Alternative for the old upstream source |
| `standalone-with-test.patch` | Above plus the same CSS-wide WPT | Independently reviewable source alternative; runtime still required |

`APPLICATION.json` records zero-fuzz exact application and reversal against captured current source and upstream, plus the five-file standalone alternative. Full standalone output snapshots are retained. Applying source is not an isolated build or runtime result.

The correct upstream revision is `976279105b2e78b8666a959eb3f25c9176cefaf8`. A historical sealed review printed a spurious trailing `a`, yielding an invalid 41-character identifier. That record is unchanged. Root independently confirmed its glue/value blob hashes at the correct revision and supplied the exact KeyframeEffect/map snapshots; `IMPORT-AUTHENTICATION.json` preserves the correction. Historical cascade/custom-property context from that closure is supplemental source evidence, not a newly queried Git identity claim.

## Remaining gates and useful formal target

Root should first run the new CSS-wide baseline, then pair the endpoint candidate on the current metadata-fixed tree. Retain the original six typed cases as project regression evidence. For a standalone claim, run the CSS-wide fixture on exact upstream with one-site map support, then with support plus endpoint repair, or document why an isolated runtime remains unavailable. All parent/fresh-effect prerequisites must execute; a different failure location is not a target pass.

Independent source review, generated-binding compilation, final formatting/patch identity, paired WPT identities and adjacent animation/attr-security regressions remain acceptance gates. No native edit or candidate runtime is claimed here. The checker authenticates the package, regenerates exact diffs, checks retained raw statuses and syntax, and applies/reverses patches in temporary artifact copies; it does not prove native semantics.

A subsequent compact formal component could model payload comparison separately from endpoint provenance, prove the added check preserves old decisions except equal-payload taint mismatch, derive both-endpoint retention invariants under array-shape equality, and exhibit omitted-from/omitted-to mutations. That theorem must retain the computed-provider/publication and scheduler premises. It must not turn this local cache check into a full animation or CSS taint theorem.
