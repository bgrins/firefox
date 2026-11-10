# Animation-taint repair design

The reproduced failure has a clear substitution repair requirement, but a complete
fully conforming native patch needs an explicit taint-acquisition policy first. The current
specification taints custom properties mentioned in keyframes; a patch that only
marks winning animated values implements a narrower policy. CSSWG issue 13933
explicitly calls out this distinction and proposes changing inheritance behavior.
This capsule contains a source-authenticated design and proposed tests, not a fix.
`SCOPED-CANDIDATE.md` gives a concrete partial repair for the demonstrated active
CSS-keyframe intersection, preserving current-text inheritance without adopting a
global name registry or the proposed inheritance stripping.

## Evidence and scope

The neighboring `css-animation-taint-calibration-runtime-20261110-v1` capsule
records the same four-callback signature in the local browser and installed
Nightly: three failures and one passing ordinary-variable control. Active,
unregistered animated `--name` reaches `scroll-timeline-name` and `timeline-scope`
instead of selecting their `var()` fallbacks. An inherited value reaches a child's
`animation-name` instead of its fallback. Later assertions in that failing child
callback were not reached. These are observations of one missing animation-taint
mechanism, not three independently established bugs.

Animation taint is distinct from attribute taint. This finding does not establish
an attribute-exfiltration route, a crash, the separate proposed timeline-registry
invalidation failure, or novelty against existing Firefox reports.

`CHECK.json` authenticates 16 source copies against Git revision
`743ad7bca84a8488a1f5ae68e629d3658ebf1a55`, 28 named excerpts, and two CSSWG issue
snapshots. The final run also compared all 16 copies with live source. The
Searchfox discovery output is navigation evidence only: its indexed revision
differs from this locally modified branch. Source conclusions below use the
authenticated copies, not Searchfox line numbers.

Reproduce authentication from the repository root:

```sh
python3 artifacts/css-animation-taint-repair-design-20261110-v1/check.py
```

Add `--check-live` only when also checking the current checkout against the frozen
source. This checker verifies provenance and excerpt integrity; it does not prove
the CSS contract, completeness of call-site coverage, or correctness of a repair.

## Exact native dataflow

1. `Servo_GetComputedKeyframeValues` resolves a keyframe's custom properties with
   `KeyframeCustomPropertiesBuilder`. For non-universal registrations it reads
   the resolved value and constructs `CustomAnimatedValue::from_computed`.
   Other declarations use `AnimationValue::from_declaration`, which can call
   `CustomAnimatedValue::from_declaration`. Marking only the latter misses the
   typed path and risks confusing endpoint construction with effect provenance.
2. `get_animation_rule` receives a `CascadeLevel` and obtains an
   `AnimationValueMap` from `Gecko_GetAnimationRule`. It passes the map to
   `PropertyDeclarationBlock::from_animation_value_map` without the level.
   That function calls `AnimationValue::uncompute`, whose custom arm calls
   `CustomAnimatedValue::to_declaration` and then `ComputedValue::to_declared_value`.
3. Universal values become unparsed declarations; typed values become parsed
   declarations. The existing attribute-taint roundtrip explicitly copies a
   wrapper flag into a universal token value when necessary. Animation provenance
   would need an equivalent lossless representation if stored on values.
4. `Cascade::cascade_custom_property` applies rollback, exclusion and winner
   selection. Its unparsed, parsed and reference-free paths all eventually
   populate the custom-property substitution map. An acquisition mechanism must
   cover each relevant path and must specify whether losing declarations matter.
5. `VariableDeclaration::substitute_variables` already passes destination identity
   through `UnparsedValue::substitution_property_id` to
   `custom_properties::substitute`. For a pending shorthand this identity is the
   shorthand, not necessarily the currently expanded longhand.
6. `substitute_one_reference` reads the custom property, resolves an unresolved
   universal value recursively if needed, and serializes the resulting value.
   A missing or invalid primary falls through to the existing fallback evaluator.
   This is the narrow enforcement seam: a tainted reference in a forbidden
   destination must take that same invalid-primary route **before** substitution.
7. `Substitution`, `do_substitute_chunk`, `substitute_internal` and custom-property
   computation transport dependency results. A provenance flag cannot live only
   at the final ordinary-property reparse: a resolved alias has already lost its
   original `var()` references by then.
8. `CustomPropertiesMap::can_deduplicate_values` distinguishes attribute taint
   even though `Value::eq` and `VariableValue::eq` intentionally ignore it.
   Any new metadata affecting substitution must also participate in the map's
   semantic equality/deduplication; equal CSS text is not sufficient.

The direct nonanimatable-declaration filter in `get_animated_properties` does not
enforce this contract: the failing destination is an ordinary declaration that
consumes an animated custom property, not a timeline declaration inside keyframes.

## Policy gate before native implementation

The minimum shared contract is: once a referenced custom property is
animation-tainted, `var()` in a nonanimatable destination treats that primary as
guaranteed-invalid and uses its fallback if available. It must still permit the
same value in an animatable destination. This is not limited to `animation-*`.

The unresolved decisions concern how that premise is established and retained:

| Decision | Current text / evidence | Consequence for a patch |
| --- | --- | --- |
| Property name or selected value? | Current Variables text taints a custom property used in `@keyframes`; issue 13933 explicitly distinguishes this from Blink's selected-value behavior. | A winning-sample bit alone cannot claim the full current-text rule. An unused keyframes rule, an unrelated same-named property and an important override distinguish these policies. |
| Scope and lifetime of name taint? | The observed active-animation cases do not settle document versus tree scope, unused rules, removal, or keyframes replacement. | A name-based design requires a scoped tainted-name set plus invalidation and dependency closure. Do not infer a document-global permanent set from one sentence. |
| Inheritance? | Current behavior is tested as taint-preserving; issue 13933 proposes clearing it across inheritance. The snapshot contains no adopted resolution. | Storing metadata in inherited computed values and storing it only in per-element resolution state are different designs. Keep the disputed inheritance policy explicit. |
| Registered properties? | The parallel contract review found no current Houdini exemption; registration changes computed-value handling and interpolation, not an established blanket taint exemption. | Include universal registrations and typed registrations in the repair audit. Do not gate taint with `registration.is_universal()` or call the typed path out of scope. |
| CSS keyframes, Web Animations and transitions? | Generic animation-value and uncompute APIs are shared; issue 11102 discusses transitions. `CascadeLevel` distinguishes animation from transition levels but does not establish CSS-versus-script effect provenance. | If acquisition depends on the producing effect, preserve that information before effects are flattened. A generic `uncompute()` hook cannot infer it. |
| Unused fallback references? | Infectious property-name wording and selected-value dataflow can give different outcomes when a clean primary has a tainted unused fallback. | Define reference-based versus selected-result infection separately. Do not reuse attribute-taint propagation rules without establishing this contract. |

Primary policy snapshots: [CSSWG issue 13933](https://github.com/w3c/csswg-drafts/issues/13933)
and its captured comments in this capsule. The companion
`css-animation-taint-contract-review-20261110-v1` owns the broader current-spec,
registration, transitions and prior-art review. The snapshots here should not be
treated as a promise that no later CSSWG discussion exists.

## Smallest useful implementation plan, conditional on policy

### Shared substitution component

Introduce one explicit animation-taint query used by `substitute_one_reference`.
For a noncustom, nonanimatable destination and a tainted primary, return the
existing missing-primary result so the ordinary fallback path runs. Custom
properties must carry infection rather than reject the value. A missing
destination (`None`, for contexts such as queries) is not automatically a
nonanimatable property; audit those callers separately. Reuse the actual
noncustom-property animatability metadata, including shorthand/alias handling,
rather than an `animation-*` or timeline-name allowlist.

Rejecting the whole declaration after substitution is incorrect because it
would skip a valid fallback. Rejecting or deleting the custom property's stored
value is also incorrect: the same value may still be consumed by an animatable
property or observed through CSSOM.

### If selected-value taint is deliberately chosen

Preserve a distinct animation-provenance flag through computed custom values,
their universal token representation, declaration roundtrips, custom-property
resolution and map equality. A helper that marks a value should preserve its
existing attribute taint, URL data and tokens, and clone a shared `Arc` only when
the metadata must change. Do not place animation taint inside `AttrTaint` ranges;
the two restrictions have different destinations and purposes.

Prefer acquiring provenance at the sampled-rule publication boundary, with
origin supplied explicitly, rather than inside generic `AnimationValue::uncompute`.
`get_animation_rule` can pass its known cascade level to the map-to-declaration
conversion. A dedicated publication helper can mark custom values without
changing generic CSSOM/serialization conversions. This final publication seam
covers both constructors, including the typed `from_computed` bypass, but does
not by itself cover taint needed while resolving keyframe dependencies. Audit
`KeyframeCustomPropertiesBuilder` separately for that requirement.

Keep flags on declarations/values through winner selection: under selected-value
semantics a winning clean important declaration must not be tainted merely
because a lower-priority animated declaration was visited. Conversely, any
earlier shortcut or cached equality that elides a change from clean to tainted
must see the semantic difference.

| File | Conditional change |
| --- | --- |
| `servo/components/style/custom_properties.rs` | Universal token metadata; substitution flag propagation; invalid-primary guard; reference-free and recursive resolution paths. |
| `servo/components/style/properties_and_values/value.rs` | Typed/universal wrapper metadata; compute/uncompute preservation; explicit marking helper; composition propagation chosen from the contract. |
| `servo/components/style/custom_properties_map.rs` | Include animation provenance in semantic deduplication/equality. |
| `servo/components/style/gecko/wrapper.rs` | Preserve publication origin currently available to `get_animation_rule`. |
| `servo/components/style/properties/declaration_block.rs` | Separate sampled-rule publication from generic uncompute and mark only relevant custom values. |
| `servo/components/style/properties/mod.rs` | Destination-classification helper only if needed; preserve pending-shorthand semantics and cache correctness. |
| `servo/components/style/properties/cascade.rs`, `servo/ports/geckolib/glue.rs` | Change only where the chosen contract requires taint during keyframe pre-resolution or acquisition at cascade time. Inspect both typed and universal paths. |

Do not indiscriminately change `PartialEq` on interpolated values. Payload
equality, map semantic equality and sampled-effect suppression are separate
questions. Existing attribute-taint fixes already demonstrate why flags sometimes
need an explicit comparison beside payload equality; the native implementation
must audit suppression of metadata-only changes before claiming completeness.

### If current property-name taint is chosen

The shared substitution guard remains useful, but sampled-value provenance is
insufficient. First define a set of tainted names and its stylesheet/tree scope;
collect declarations from the relevant keyframes rules; compute infectious
dependencies according to the selected reference rule; and invalidate that set
when rules, registrations or applicability change. `stylesheets/keyframes_rule.rs`
and `stylist.rs` are candidate ownership seams, not an already-verified complete
patch surface. Then make the substitution query consult this state. Retain value
metadata only where the agreed inheritance/lifetime semantics require it.

Do not implement an ad hoc global name set as a shortcut. Its cross-element,
shadow-tree and dynamic-removal behavior would be observable and is not settled
by the reproduced fixture.

## Tests and next decision

`WPT-MATRIX.md` separates immediate regression cases from policy-discriminating
cases. They should become `testharness.js` computed-style tests; none of the
observed failures calls for a crashtest. Use independent callbacks so an earlier
failure cannot suppress evidence for another destination.

The scoped candidate can proceed as an explicitly partial repair after source
review, using the existing browser evidence and the focused test matrix. It must
retain the listed policy limitations and registered-property coverage. A claim of
full conformance additionally requires settling acquisition scope, lifetime,
effect-origin and unused-fallback infection. No live native source, WPT, index,
commit, build or browser was changed by this design task.
