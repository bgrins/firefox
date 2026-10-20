# Animation metadata after successful interpolation

## Result

No additional observable metadata defect established in this bounded static audit. The examined error, discrete, list, iteration and publication branches do not supply a new taint-loss counterexample beyond repairs 76, 78, 79 and 80. This is negative source evidence, not a universal native proof or a browser result. No native changes or executable browser probe were produced.

Complete current files and hashes are retained in `source/` and `SOURCES.json`. Indexed Searchfox discovery was checked against local changed code. Two final global caller searches failed with DNS errors; their scope is explicitly left open.

## Normative oracle

The [attribute security rule](https://drafts.csswg.org/css-values-5/#attr-security) requires provenance to survive a substitution when an attribute-derived value contributes, including registered custom values; using that provenance in a URL invalidates the declaration. This does not by itself require combining provenance from every unsuccessful attempted operation.

[Web Animations](https://drafts.csswg.org/web-animations-1/#animating-properties) selects one endpoint for discrete interpolation, and falls back to discrete behavior when corresponding computed components cannot combine. [Registered property animation](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior-of-custom-properties) uses simple lists, with separate transform exceptions. [CSS Values combination rules](https://drafts.csswg.org/css-values-4/#combining-values) define unsupported addition as the second value, with accumulation defaulting to addition. These distinctions matter when assessing an error fallback; blanket OR over every attempted input would not be an independently established exact provenance rule.

## Actual path findings

| Path | Exact source behavior | Assessment |
| --- | --- | --- |
| Successful scalar/list/enum combination | `Value<Component>::animate` invokes the payload provider with `?`, then constructs the result with outer taint OR. | Repair80 is outside the scalar payload, so successful registered lists and enum variants receive it too. |
| List mismatch / partial failure | `ComponentList::animate` requires the same multiplier and invokes `lists::by_computed_value::animate`; that requires equal lengths and collects a `Result` from each pair. | A partially built list is not published on error. The unrelated with-zero and repeatable-list algorithms are not the registered list provider. |
| Different enum variants / explicit error variants | The complete `style_derive::animate::derive` emits a discriminant check and propagates field errors with `?`; String, Url, Image, CustomIdent and Universal are marked error. | No clean replacement value is manufactured here. This reading is of the generator source, not independently compiled macro expansion. |
| Optional invalid values | `Option<T>::animate` delegates Some/Some, accepts None/None, and rejects mixed pairs. | No implicit Some-zero or clean placeholder. |
| Discrete failure | `compose_animation_segment` clones the chosen complete from/to value according to progress; equal-offset segments clone according to total-progress sign. | Selected endpoint metadata is retained. The unselected endpoint's taint is not automatically required. No new oracle-backed bug. |
| Add / accumulate endpoint failure | `composite_endpoint` returns None on payload failure; the caller then uses the explicit endpoint. A neutral endpoint clones the underlying value. | For nonadditive values this follows replacement behavior; unsupported provider error versus normative nonadditivity must remain a type-specific admission. |
| Iteration failure after successful endpoint composition | `accumulate_endpoint` retains `Some(endpoint)` if accumulating onto it fails. If it began with None, the caller falls back to the explicit endpoint. | Crucially, failure does not discard a previously composed endpoint and its taint. Positive iteration is the only branch that invokes this helper. |
| Effect stack / underlying provider | `Servo_AnimationCompose` first checks the already-composed property map, then cached base style when needed; missing required underlying data returns without publishing. | A lower-priority successful value is used whole. Freshness of the supplied map/base and resampling are external here, including prior repair79. |
| Animated zero | `AnimationValue::Custom` explicitly returns Err with bug1869185; the FFI returns null. | Unsupported operation, not a successful taint-clearing custom zero. Global native consumers were not fully retraced after Searchfox DNS failure. |
| Distance | Custom is outside supported builtin match arms; FFI maps failure to -1. | No custom value or metadata is published by distance. This does not prove all pacing callers correct. |
| Uncompute / cascade publication | Custom delegates to `to_declaration`; typed values use derived computed-to-specified conversion. Universal conversion explicitly preserves outer taint in the inner raw value when needed. | No missing bit identified. Generated conversion, whole cascade and prior map metadata fix remain separate native admissions. |
| Raw serialization helper | `to_variable_value` does not embed outer taint, but the ordinary var caller passes `v.attr_tainted` separately. Recursive unresolved var ORs it after success. Both attr callers ultimately force true. | The three callsites in current `custom_properties.rs` are not laundering paths. Inspecting this helper alone would have produced a false lead. |

## Rejected or unresolved extensions

- The transition endpoint equality lead remains INCONCLUSIVE as recorded in `css-animation-equality-frontier-v1/CHECKPOINT.md`. Payload-insensitive provenance changes do not independently establish a required restart.
- First-operand `url_data` in successful `Value::animate` is not a demonstrated URL-base bug. URL/image payloads are explicit error variants; discrete fallback clones a whole selected value. A claim involving numeric/string serialization requires a complete URL resolution/base context argument. That argument was not established here.
- Transform-list special behavior and `none` handling already cite bug1884606. This audit does not reclassify that known limitation as a new metadata bug.
- Scalar arithmetic is not proved. In particular the color provider builds weighted mixtures for Procedure values and cites CSSWG issue7324; the broader color addition/spec-policy question is outside this metadata conclusion. No claim that every payload provider implements the current combination specification was made.
- Zero-weight OR remains the conservative policy already documented for repair80. No provenance-clearing requirement is inferred from a zero numeric coefficient.

## Next formal obligation

Prove **outcome-sensitive provenance preservation through complete segment composition and publication**, rather than another isolated OR identity:

1. Model actual optional endpoints, neutral values, composite operations, previously composed map/base source, positive iteration and the three complete glue helpers. Keep original endpoint and already-composed endpoint distinct.
2. Supply an independent contribution reference: successful admitted payload combination combines contributors; normative replacement selects the second value; discrete interpolation selects an endpoint; failed iteration retains the previously composed endpoint. A payload error is not assumed equivalent to normative nonadditivity without a named provider premise.
3. Derive that output taint includes every reference contributor through all branches. Do not require exact equality where conservative taint is allowed. Preserve property identity and Some/None validity in the theorem.
4. Join typed/universal `to_declaration`, map publication and var substitution to the URL rejection observer. Explicitly admit decoded payload conversion, URL context, map/base readiness, scheduling, generated macro correspondence, Arc lifetime and compiler behavior.
5. Mutants should independently erase the right operand on success, clear a selected discrete clone, replace the retained composed endpoint after failed iteration, and omit the separate taint argument at var serialization. These distinguish branch composition from the already proved wrapper identity.

The strongest new counterexample search enabled by this obligation is a **successful endpoint addition followed by failed iteration accumulation**, then discrete final selection. A naive fallback to the original explicit endpoint would lose provenance contributed by the underlying value. The current inspected `.or(Some(endpoint))` branch prevents that specific mistake. Constructing an actual type combination with those outcomes is a provider admission task; no speculative browser failure is asserted.

## Coverage boundary

Inspected complete files: value wrappers, animation derive generator, generated animation template source, animated Option/procedure/list/color providers, glue composition/FFI, and custom substitution implementation. Read earlier equality frontier and interpolation proposal to exclude duplicates. Primary specs were fetched through the web tool on 2026-10-19. Not executed: source extraction, Lean, browser, WPT, or builds. Not exhaustively inspected: every scalar/transform provider, macro expansion, all C++ distance/zero callers, transition scheduling, external URL-base histories, every declaration-map publisher, or full consumer geometry. No novelty, formal acceptance, or whole-animation correctness claim.
