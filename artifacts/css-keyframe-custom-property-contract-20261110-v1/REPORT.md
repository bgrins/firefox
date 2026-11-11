# Custom-property CSS keyframe contract audit

The two existing failures have stale **property inventories**: both custom names belong in the returned frames. Their complete value expectations should not yet be edited solely from those first failures. Source review also identifies a separate computed-value serialization gap worth a small diagnostic: declared custom values go directly to CSS serialization, including `var()` text and registered relative units. This capsule establishes the contract and source path; it does not claim a newly reproduced or newly counted bug.

Native/test basis is combined #172 tree `daaf9f0c4c9be813f693bf1401c5a4e33aca588e`. All reasoning uses pinned Git copies, including while the live animation files temporarily held the owned-generation experiment. No live source/test edit, browser/build execution, metadata change, or Git mutation occurred. The separate source extraction does not change this serialization path.

## Normative trace

**Question:** For an attached ordinary CSS animation whose keyframes have not been replaced, should `getKeyframes()` include custom properties and return their computed values?

**Scenario:** Connected ordinary element; successful CSS animation; no `setKeyframes()`, range offset, pseudo, or inactive-timeline ambiguity. Compare unregistered properties with a registered `<length>`; a separate WAAPI case is a control, not the same branch.

1. [Web Animations getKeyframes, step 2](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-getkeyframes) selects computed frames for the untouched CSS-animation case. The alternate branch returns specified frames with computed offsets.
2. [CSS Animations processing, steps 2–3](https://drafts.csswg.org/css-animations-2/#keyframe-processing) retains animatable declarations and fills missing endpoint properties. Both unregistered discrete properties and registered typed properties qualify.
3. [Computed keyframes, step 2.2](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes) computes each property; [value computation](https://drafts.csswg.org/web-animations-1/#computing-property-values) uses the element's computed dependency context. It does **not** substitute another declaration's endpoint value merely because both occur in one frame.
4. [Variables 1](https://drafts.csswg.org/css-variables-1/#defining-variables) requires substitution in unregistered computed values; guaranteed-invalid serializes empty. [Properties and Values 1 §2.4](https://drafts.css-houdini.org/css-properties-values-api-1/#computed-value-time) computes registered values according to their syntax, including canonical numeric units. Universal syntax retains token semantics; `<length>` resolves relative dimensions.
5. The API's step 3 serializes each resulting pair and keeps custom names unchanged.

**Verdict: REACHED.** Inclusion and computed-value return are required for the stated CSS branch. This is not a verdict that every current returned value is wrong: literal unregistered tokens can already be computed values. Raw specified values remain appropriate on the alternate WAAPI/replaced-keyframes branch.

The step graph returned no route at depths 9 and 18, without truncation. That is a graph representation limitation, not a negative normative result: the containing API section explicitly selects computed keyframes. The direct primary clauses above decide the trace. Captured current ED dates are CSS Animations 2 August 18, Web Animations October 8, Variables October 9, and Properties/Values October 31, 2026. Fresh primary HTML hashes match the indexed CSS/WA/Variables snapshots. The CLI rejects the Houdini ED domain, so that section was checked in the directly fetched official ED, not silently substituted with an older TR snapshot.

## The two existing fixtures: all fields to check

| Fixture/endpoint | Existing ordinary values and metadata | Required additional custom value |
| --- | --- | --- |
| Overridden variable, generated 0% | offset/computedOffset 0, `steps(2, start)`, generated default `replace`, underlying black color | `--end-color`: inherited underlying red token value |
| Overridden variable, authored 100% | offset/computedOffset 1, same easing, authored `auto`, `color: var(--end-color)` computed in current element context | `--end-color`: authored green token value |
| Custom-only, authored 0% plus filled property | offset/computedOffset 0, `ease`, authored `auto`, existing transform serialization | `--not-used`: guaranteed-invalid underlying value, serialized `""` |
| Custom-only, authored 100% plus filled property | offset/computedOffset 1, `ease`, authored `auto`, underlying transform `none` | `--not-used`: authored `200px` token value |

The first fixture's step timing is material. At the initial active step it can select the discrete property's green endpoint; its ordinary color then resolves against that animated computed custom value. A different timing function/current time can legitimately change the `color` serialized for the authored variable reference. It is incorrect to diagnose that phase dependence merely by expecting the declaration in the same keyframe to supply the value. Exact string whitespace and complete objects need the proposed capture; this table is a semantic audit, not an approved replacement WPT oracle.

The custom-only case does not omit a property because no ordinary declaration consumes it. Empty serialization here represents guaranteed-invalid, not an absent member or a claim that an authored empty custom value is invalid. The existing frames retain `auto` because they already exist; missing properties are appended to them. A wholly generated endpoint uses the captured CSS default composite, which is `replace` in these fixtures but can be `add` in a separate control. An implementation must not force every generated frame to replace regardless of the CSS default.

## Pinned native paths

`PropertyId::is_animatable` admits custom declarations. `Servo_StyleSet_GetKeyframesForName` keeps their declaration blocks. `CSSAnimationKeyframeEffect::GetComputedKeyframes` collects their names and fills absent endpoints using null declaration-block sentinels, with existing/default easing and composition matching. The ordinary generator doesn't compute all declared property values despite the method name.

`KeyframeEffect::GetKeyframes` flushes target style, generates endpoint records, and serializes each property. A non-null declaration block takes `Servo_DeclarationBlock_SerializeOneValue → PropertyDeclarationBlock::single_value_to_css`. That function substitutes ordinary `WithVariables` values using the element's current custom-property map; all other declarations, including custom declarations, take `d.to_css` directly. `SpecifiedValue::to_css` writes its stored CSS string. Registered type information is not used to compute this custom declaration on that return path.

A null endpoint declaration instead consults `mBaseValues`. `EnsureBaseStyle` fills needed bases using `GetBaseContextForElement` and computed-value extraction. `Servo_AnimationValue_Serialize` uncomputes that already-computed value before serialization. `CustomAnimatedValue::to_declaration` represents missing/invalid values as `GuaranteedInvalid`; the `ToCss` derive's `#[css(skip)]` variant emits no characters. If the map contains no base value, the C++ output string also remains empty. This explains the anticipated empty `--not-used` field without conflating membership and value.

The actual rendering path is different: `Servo_GetComputedKeyframeValues` uses `KeyframeCustomPropertiesBuilder` and registered/custom computation. Successful visual interpolation does not certify `getKeyframes`'s declaration serialization; conversely, a getter serialization discrepancy does not establish a rendering bug. No rendering-policy change is proposed here.

## Source-supported follow-up and prior bug boundary

Two small discriminators follow from the return path: a CSS custom keyframe containing `var(--source)` can serialize the unresolved token expression, and a registered `<length>` authored as `2em` can serialize `2em` instead of its computed px value. An unregistered `2em` control should keep its token value, while a WAAPI-created registered-property keyframe should follow the specified-value branch. These are source-supported hypotheses pending complete runtime observations, not evidence obtained from the two existing stale-inventory failures.

The source TODO cites [bug 1391537](https://bugzilla.mozilla.org/show_bug.cgi?id=1391537). Its retrieved record is NEW/S3, specifically about retaining shorthand/authored values, with 2017 rationale and a dependency on custom-property animation work. It does not by itself establish duplicate coverage for the current computed-value custom-property cases. The earlier short update calling this the broad known serialization bug was too strong; classification needs current-spec and runtime evidence, then a deliberate comparison with that historical issue. No bug count is changed.

## Smallest next experiment

`proposal/custom-keyframe-value-observations.html` has seven testharness callbacks: one registration setup and six scenarios. It emits eighteen `KCUSTOM-V1` JSON records, one per scenario at created/quarter/three-quarters phases. Each record retains full returned frames, pre-animation baseline values, current computed context, current time/progress and effect composite. The scenarios are the two original patterns, unregistered variable substitution, registered relative length with an unregistered token control, the same with additive CSS composition, and a WAAPI branch control.

Assertions check setup and a static registered relative-unit computation only. Getter outputs are observations, not guessed conformance assertions; root should require every unique case/phase record and complete harness results. The initial original patterns preserve their existing timing choices. Controlled seeks use paused animations to distinguish legitimate dependency context from unexpected serialization. The ordinary black base and 16px font are explicit. Registration is local to this isolated page; no network, URL-valued or security-sensitive payload is used.

Node syntax checking passes; WPT lint, browser execution and exact output review are pending. The next action is this baseline-only diagnostic on the restored combined browser. Only afterward should we draft a narrowly corrected existing WPT oracle or a separately justified serialization regression test. Do not remove either existing FAIL metadata stanza merely because the inventory is stale.
