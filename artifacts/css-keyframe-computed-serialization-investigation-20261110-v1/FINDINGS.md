# CSS keyframe computed-value serialization investigation

The local browser returns specified expressions in CSS animation keyframes where the current Web Animations contract requires computed values. This is a reproduced API discrepancy, not a native repair or a new counted catalogue entry. Root source basis is ec467c0219d3d5daf70f42fcc53677cf8a262173; browser BuildID is 20261110181740, whose source relationship and binary identities are authenticated by the probe manifest and retained-build receipt.

## Observed boundary

The baseline-only probe completed lint and WPT with exit 0, seven PASS callbacks, one OK harness and eighteen unique observations. Those assertions validate setup and collection; the getter values are observations. Full browser restoration passed and was independently checked. No candidate native code was installed.

| Input and branch | Getter endpoint | Computed-value contract / control |
| --- | --- | --- |
| CSS, registered `<length>` `--kc-length: 2em`, 16px font | `2em` | `32px` |
| CSS, ordinary `margin-left: 2em`, 16px font | `2em` | `32px` |
| CSS, unregistered `--stored: var(--source)`, source `12px` | `var(--source)` | substituted `12px` |
| CSS, unregistered token `--kc-tokens: 2em` | `2em` | token value remains `2em` |
| WAAPI, registered length and ordinary margin authored `2em` | `2em` | specified-value branch remains `2em` |

CSS relative-length getter results remain unchanged at creation, quarter and three-quarter progress. Rendering resolves both registered length and margin to 15.5px / 26.5px for replacement and 18px / 34px for addition, with a 10px underlying value. The custom variable renders as 12px after its discrete switch. These observations delimit getter serialization from rendering; they do not establish global rendering correctness.

The original two expected-failure cases include the custom names, as the specification requires. Their first-failure property inventories are stale, but changing inventory alone is not a complete oracle audit. The overridden-variable case resolves ordinary color against the current animated custom-property context. The custom-only case retains the guaranteed-invalid underlying member as an empty string. Full frame values and metadata remain in the raw and parsed observations.

## Native repair constraints

`KeyframeEffect::GetKeyframes` uses `Servo_DeclarationBlock_SerializeOneValue` for non-null authored declarations. `single_value_to_css` substitutes ordinary `WithVariables` declarations when a style context exists and otherwise serializes the stored declaration. This explains the ordinary relative length and custom-property results. Generated null declarations instead serialize computed base values.

Two tempting substitutions are insufficient:

* `Servo_GetComputedKeyframeValues` is a rendering preparation path. It batches keyframe custom declarations into `KeyframeCustomPropertiesBuilder` before computing ordinary properties. A getter repair must preserve the specification's current element dependency context rather than silently substitute an endpoint-local dependency map.
* `AnimationValue::from_declaration` delegates custom values to `CustomAnimatedValue::from_declaration`. Its universal-registration branch explicitly retains the unparsed value without substitution. Calling this helper alone would leave the unregistered-variable discrepancy.

A narrow repair needs an explicit computed-value return path for untouched CSS animations, including real element/pseudo/parent/container/attribute context. Ordinary WAAPI effects and CSS effects whose keyframes were replaced must keep specified serialization. Preserve frame grouping, offsets, generated endpoints, easing/composite metadata and property-name conversion. Audit absent/invalid target handling and logical/shorthand mapping rather than broadening the current declaration serializer used by other consumers.

Custom-value computation must resolve references and registered syntax without mutating element computed style or sharing a changed dependency context between returned properties. Typed and universal properties need separate controls, as do self-reference/cycles, fallback, CSS-wide keywords and attribute taint. Reuse existing substitution machinery where its contract fits; do not introduce a second ad hoc evaluator. Rendering and getter computation may share lower-level helpers but have different assembly requirements.

## Next validation

Draft a small conformance WPT with full authored endpoints, a fixed font/source context, typed versus token custom values, ordinary relative units, and WAAPI / setKeyframes controls. Add a changing dependency context control to distinguish endpoint-local computation from the required current element context. Baseline assertions must demonstrate the exact gap before any candidate. Inspect the complete existing getter suite for expected serialization changes before removing metadata. Any native fix and WPT belong together in one standalone commit after its research evidence.

Bug 1391537 is historical context for the existing serializer TODO; its shorthand/authored-value scope alone does not establish that this current-spec discrepancy is a duplicate. This investigation changes no bug count and makes no security, release-browser or cross-browser claim. It was found by specification/source analysis and browser observation, not by a Lean theorem proving native behavior.
