# Cross-registration taint: bounded caller review

No new reachable taint-loss case is established. The two suspicious function-level paths remain distinct. Exact e86 keyframe handling bypasses the empty-taint typed parser for Unparsed custom declarations; the other path still needs evidence that an older universal computed endpoint is recascaded under a different, typed registration. No new browser probe was prepared because that missing lifecycle handoff has not been established.

This review uses root-created immutable `git show` snapshots of e86b64866cdc5e2260ba9be08c45756fd96e21bb, not live Stylo owned by the diagnostic run. REFERENCES authenticates the three snapshot closures and the saved capacity cascade candidate (832d). Searchfox caller discovery guided the bounded reads; conclusions below use the exact saved definitions. This is neither an exhaustive callgraph proof nor a security noninterference claim.

## Existing negative coverage

The earlier deep-v2 browser receipts cover six stylesheet-registration phases: unregistered, universal, string, universal, string, unregistered. Each phase checks direct static attr(), a paused CSS-animation inherit endpoint, and a paused var(--source) endpoint. Both animations use fill mode `both` and a negative delay placing the sample at progress 0.5; the inherited/var source is an attribute-derived parent custom value. In both recorded browsers (Firefox 158 and development 160), all 18 image-set sinks remained `none`; animated progress was 0.5. The registration control changed between 17px and the typed initial string. The saved runtime checker also records positive image requests and unchanged binaries/removed profiles. This review independently re-counted the 18 blocked values and animation progress from each raw receipt; it did not repeat the browser experiment or reauthenticate current application files.

These negatives do not cover every registration history, transition endpoint, or engine path. Their source snapshots predate the e86 snapshots used here. Repeating these three mechanisms with the same six phases would not resolve the present unknown.

## Path A: explicitly tainted universal value into typed substitution

`ComputedValue::to_declared_value` preserves a universal wrapper's taint by cloning a reference-free inner value and setting `explicitly_attr_tainted` when necessary. `CustomAnimatedValue::to_declaration` and the custom arm of `AnimationValue::uncompute` provide the animation-to-declaration route.

`Cascade::cascade_custom` can send reference-free Unparsed declarations directly to `substitute_references_if_needed_and_apply`. Its no-reference shortcut preserves a universal value under a universal registration. A typed registration instead reaches `apply_substituted_value` and `substitute_internal`. The latter passes CSS, token boundaries and reference records to `do_substitute_chunk`, without passing the explicit-taint bit. The no-reference branch constructs a substitution with default taint. Thus the source-level loss mechanism remains real **if** an explicitly tainted reference-free Unparsed value reaches this typed-registration route.

The unresolved prerequisite is concrete: identify a reachable animation/transition or other internal producer that retains a computed universal value from registration R0, then uncomputes and recascades that same value after current registration becomes typed R1, without first recomputing/replacing it or rejecting the mismatch. An internally fabricated value/registration mismatch does not establish this. This review has not proved that transition endpoints survive that switch; transitions are a follow-up source question, not a newly justified probe or a claimed bypass.

## Path B: CustomAnimatedValue::from_declaration with empty AttrTaint

The typed Unparsed branch really calls `SpecifiedValue::compute` with default AttrTaint. A successful typed parse is the suspected loss branch; failed parsing falls back to a universal value retaining the original variable value, so a parse failure alone does not demonstrate loss. Three inspected entry routes constrain its reachability:

| Entry route | Exact saved behavior | Consequence for the alleged loss |
| --- | --- | --- |
| `Servo_GetComputedKeyframeValues` | Builds the keyframe custom-property map. For Unparsed custom declarations under a nonuniversal current registration, retrieves the computed map value, calls `CustomAnimatedValue::from_computed`, and continues before `AnimationValue::from_declaration`. | The suspect typed-Unparsed parser is bypassed on this route. This does not independently prove map construction safe against Path A. |
| `AnimationValue::FromString` → `Servo_AnimationValue_Compute` | Obtains computed style, then freshly parses the supplied authored string into a declaration before computing it. | This inspected route does not supply an older computed universal value carrying a hidden explicit-taint bit. Serialized text alone is not that internal object. |
| `SMILCSSValueType::ValueFromStringHelper` → `Servo_GetAnimationValues` | Accepts `NonCustomCSSPropertyId` and freshly parses the string. | The inspected SMIL wrapper cannot supply the custom-property declaration required by this branch. |

These are per-caller exclusions, not a claim that `CustomAnimatedValue::from_declaration` is unreachable in general. Parsed custom values and CSS-wide inherited/initial values follow different arms; the latter clone computed values rather than perform the suspect typed Unparsed parse.

`KeyframeEffect::UpdateProperties` rebuilds properties and, even when ordinary property comparison reports equality, explicitly compares old/new custom endpoint attr-taint bits. It also updates base styles. `EffectCompositor::UpdateEffectProperties` calls this for the effect set. These definitions rule out a simple claim that this update always ignores equal-token taint changes. They do not establish when every registration change triggers the update, or that every transition endpoint is rebuilt before sampling.

## Next action and limits

Do not claim a new accepted defect or attribute-data disclosure. Keep both function-level concerns as source proof obligations. The smallest useful next step is to establish an actual producer/consumer edge for the R0 universal → R1 typed endpoint handoff, including update/cancellation ordering. Only then should a distinct browser probe retain and verify that endpoint across the switch, with a typed-registration positive control and same-registration taint controls. Absent that evidence, no new probe is warranted.

No live source/application reads, browser execution, native build, Git/index/canonical mutation, patch or registration experiment was performed by this review. Native diagnostic work and previous browser results retain their separate authorities.
