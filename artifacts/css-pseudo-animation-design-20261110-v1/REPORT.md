# Missing-pseudo animation composition: current-source repair design

A CSSOM-only, request-local repair is viable in principle. The tracked implementation does **not** currently provide a safe drop-in helper: it needs scratch keyframe preparation, composition with explicit scratch state, and a pseudo-aware recascade entry point. Do not port D65652's broad `match_pseudo` hook or repair this by requesting a restyle for an absent pseudo-element. This is a source review and implementation plan, not a compiled candidate or an acceptance of the untracked prototypes.

## Evidence and scope

Native source is pinned at `2f8edd8effa87071d0576d488cb6cfa2fc65721c` in SOURCES.json; copies are under source/. Searchfox receipts are navigation evidence, not substitutes for these local branch bytes. The parent subsequently committed the nine-case fixture in `f07918bd8f5c`; it reports 6 PASS / 3 FAIL. The earlier target WPT reports 17 PASS / 7 expected FAIL: six related to bug 1615083, one separate unsupported `::placeHOLDER` case. No tests or builds were run for this design.

Inputs: `../css-pseudo-animation-admission-20261110-v1`, and `../css-pseudo-animation-repair-20261110-v1/D65652.md` plus its nine-case fixture. The old review identified missing underlying values for implicit keyframes and an unexpected transform-layer update during ordinary traversal. Those are distinct integration failures, both addressed by the boundaries below.

The normative basis is the captured [CSSOM getComputedStyle algorithm](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle) and [Web Animations applying the composited result](https://drafts.csswg.org/web-animations-1/#applying-the-composited-result). The latter requires an underlying base, ordered effect composition, and insertion at the appropriate cascade origin. The former exposes the requested pseudo's resolved properties subject to its document/flat-tree conditions. The proposed isolation and helper factoring are engineering conclusions, not requirements quoted from those specifications.

## Why existing entry points are insufficient

| Existing symbol | Actual behavior in the pinned source | Consequence |
| --- | --- | --- |
| `nsComputedDOMStyle::DoGetComputedStyleNoFlush` | Also called by internal animation style queries through static helpers | Composing here without an explicit caller mode risks recursion and changes internal contexts. |
| `UpdateCurrentStyleSources` / `ClearCurrentStyleSources` | Generation-based cache can retain lazily resolved style across property reads | Animated query results must not be cached solely by undisplayed restyle generation. |
| `ServoStyleSet::ResolveStyleLazily` / `Servo_ResolveStyleLazily` | C++ traversal guard and Rust document-data borrow span lazy resolution | Return from this call before invoking C++ animation preparation/composition. |
| `StyleResolverForElement::match_pseudo` | Uses empty animation declarations; generated pseudo animation handling occurs elsewhere | Keep ordinary matching unchanged. |
| `KeyframeEffect::EnsureBaseStyle` | Returns if `GetPseudoElement` yields no actual element | Cannot supply implicit/additive base values for this case. |
| `KeyframeEffect::BuildProperties` | Clones keyframes defensively but writes them back; can call virtual CSS keyframe preparation | Not a const scratch-preparation API. |
| `KeyframeEffect::UpdateProperties` | Publishes properties/base values, updates EffectSet, notifies and requests restyle | Do not call it merely to answer a missing-pseudo CSSOM read. |
| `EffectCompositor::UpdateCascadeResults` | Mutates masks/cascade status and may request restyles | Cannot be the refresh mechanism for query-local masks. |
| `ComposeSortedEffects` | Consults cached `PropertiesForAnimationsLevel` | Needs fresh masks derived from the query's fresh property arrays. |
| `KeyframeEffect::ComposeStyle` | Reads stored arrays/base map and updates overflow synchronization bookkeeping | Extract the segment/value computation from renderer bookkeeping. |
| `Animation::ComposeStyle` | Checks unresolved timelines and temporarily adjusts hold time for pending rendering | A new caller must deliberately preserve timing semantics; bypassing it blindly is insufficient. |

`RequestRestyle` is not harmless when the pseudo is absent: the compositor can update restyle maps and animation generation even when no generated pseudo can receive the eventual posted restyle.

## Proposed edit points and data flow

1. **CSSOM eligibility and lifetime: `nsComputedDOMStyle.cpp/.h`.** In `UpdateCurrentStyleSources`, after the existing flushes and pres-shell validation but before the generation-cache early return, identify an eligible absent pseudo with an effect set. Initially restrict this helper to the supported eager pseudo identities (`::before`, `::after`, `::marker`) and ordinary All-rules CSSOM reads. Keep non-pseudo, unsupported/nested identities, default-only queries, disconnected/flat-tree exclusions, and non-dynamic/printing behavior on their existing paths. Absence means no actual pseudo element; do not equate absence of a frame with absence of the pseudo.

   Bypass the generation cache for eligible reads even if the cached value predates animation creation. Resolve the raw pseudo style through the unchanged lazy path. Compose only after that call returns. Mark the resulting style as request-local and clear it in `ClearCurrentStyleSources`; also reset the marker in `ClearComputedStyle`. The early-return condition must also reject any previously query-composed style, even if the effect set has since disappeared; audit callers such as custom-property enumeration that may retain style sources differently. Cancellation/removal must not leave a previously composed cached result. Keep internal static `GetComputedStyle[NoFlush]` calls raw, or introduce an explicit mode defaulting to raw with only this CSSOM caller opting in. Preserve the later visited-style exposure gate.

2. **Snapshot preparation: `EffectCompositor.cpp/.h`, `KeyframeEffect.cpp/.h`, possibly `KeyframeUtils`.** Add a query-only orchestration method taking the exact owning target/pseudo, raw base style, and origin style. Snapshot strong effect and animation references in composite order before computing values. Snapshot the target and keyframe inputs, effect composite options, animation class/level and timing inputs. Build scratch property arrays using the existing lower-level `KeyframeUtils::GetAnimationPropertiesFromKeyframes` with owned keyframe copies and the current query context. Factor the CSS-keyframe-specific preparation if needed; do not call a virtual path that silently updates renderer-owned state.

   For each required underlying property, extract its current base animation value directly from the raw pseudo style using `Servo_ComputedValues_ExtractAnimationValue`. Store it in a request-owned table. This removes the dependency on `GetBaseContextForElement` finding a generated pseudo. The raw pseudo style must exclude its own animation/transition rules while still inheriting the origin's current style; do not strip ancestor animation effects. Assert/ensure this property at the boundary rather than assuming every lazy-style cache is suitable.

3. **Fresh masks and pure composition: `EffectCompositor`, `KeyframeEffect`, `Animation`.** Derive the animation-level property union from the freshly prepared arrays, not EffectSet's cached masks. Preserve current composite order and the special inclusion of transition effects when computing the animation-origin result for underlying values. Use separate animation/transition outputs and the existing skip semantics. A transition-origin rule must not accidentally acquire non-transition effects.

   Extract the existing selected-segment computation into a helper supplied with the scratch property array, base-value table, computed timing, iteration composite mode, property skip set, and result map. Keep `WillComposeStyle`, last-progress state, overflow-sync time, compositor flags and restyle generation changes in the existing rendering caller. `Servo_AnimationCompose` already supports an explicit base-value table and output map; reuse that value-composition primitive. Preserve unresolved/pending timing behavior via a shared timing-selection helper or an explicitly reviewed query equivalent. Snapshot once per query; do not tick/resolve pending animations as a side effect of the helper.

4. **Transient recascade: `ServoStyleSet.cpp/.h`, `servo/ports/geckolib/glue.rs`, and FFI declarations/bindings as required.** Introduce a narrow pseudo-query recascade call after C++ scratch composition finishes. Convert the two maps with `PropertyDeclarationBlock::from_animation_value_map`. Starting from the raw pseudo rule path, replace/add only Animation and Transition levels using `RuleTree::update_rule_at_level`; handle absent paths via the tree root and preserve visited inputs. Keep the ordinary declaration cascade responsible for important precedence; never overwrite computed fields directly.

   Cascade with the explicit originating primary style and explicit eager pseudo. `cascade_style_and_visited_for_pseudo_with_default_parents` supplies the correct pseudo inheritance and special layout-parent behavior for a `display:contents` origin. The ordinary-element `resolve_rules_for_element_with_context` is not an equivalent replacement. Use a fresh local thread context/rule cache and return an owned computed style. Rule-tree allocation/interning is expected; publishing ElementData, persistent pseudo caches, new frames, restyle hints or animation state is not. Recheck property restrictions, visited handling, existing skip-animation flags and printing gates.

The result is: CSSOM raw base → owned effect snapshot → fresh properties/base tables/masks → maps → transient pseudo recascade → one CSSOM read. The normal traversal retains its current entry points and bookkeeping.

## Remaining implementation gates

This is a viable prototype design, **not yet a safe full-property production patch**.

* **Preparation and reentrancy:** `BuildProperties` explicitly warns that computed-value preparation can trigger a subsequent restyle. The direct KeyframeUtils route avoids its write-back, but that alone does not prove the entire call chain is non-reentrant. The pinned `Servo_GetComputedKeyframeValues` uses an explicit supplied style, reads parent data, computes in a local context, and returns the local AttributeTracker's reference flag. The tracker itself records local references and reads attributes. Do not hold an EffectSet iterator, frame pointer, mutable Rust borrow or borrowed element data across C++ preparation calls. Either establish a no-flush/no-script preparation contract for the supported path, or use owning snapshots plus explicit invalidation/revalidation. An unbounded retry loop is not acceptable.
* **Current computation dependencies:** relative units, logical properties, custom-property providers and CSS keyframes cannot automatically be assumed correct merely because the base style is fresh. If an animated provider must affect endpoint computation in the same sample, a single base-only preparation pass may be insufficient. Start with the ordinary-length/transform/implicit-base controls, then test the provider cases before widening the conformance claim. Do not invent a fixed-point algorithm to pass the narrow bug test.
* **Timing factoring:** rendering pending-time overrides must be consciously retained or justified for CSSOM. End-point behavior for commitStyles is distinct; this helper must not reuse that endpoint-inclusive policy.
* **Pure recascade:** confirm that the selected recascade path performs only query-local/cache allocation work and preserves relevant flags. Current APIs have the building blocks but no ready-made absent-pseudo query contract.

If these extractions cannot be made without changing ordinary sampling semantics, stop the native candidate. The concrete missing architecture is a query-local prepared-effect snapshot and pseudo recascade, not a missing request to restyle the non-generated pseudo.

## Preexisting untracked work

PRIOR-WORK.json records exact observed hashes and confirms these paths are absent from the pinned Git tree; read-only copies are under prior-work/. `AnimationComposeResult.h` defines a borrowed map-or-sample sink. `animation_rule_sample.rs` and `deferred_animation_operations.rs` implement owned per-property operation roots and deferred value composition. `keyframe_endpoint.rs` retains declaration recipes and has a scoped registered-property resolver. The gtest/Rust files exercise these operation/ownership paths.

These are potentially reusable seams for an explicit composition sink and dependency-aware endpoints. They do not, by their existence, provide the CSSOM admission/cache policy, fresh missing-pseudo base values, timing snapshot, or pseudo recascade described here. They are untracked drafts, not accepted source or a validated native integration. No draft was changed or removed. Do not implement a second operation arena for this bug: first establish the drafts' provenance and compatibility if the candidate needs that machinery. The narrow fixed-value/implicit-base prototype can use the existing concrete animation-value map without adopting the deferred architecture.

## Bounded validation plan

Retain both existing fixtures: target identity/retargeting cases and all nine underlying-value controls. Keep the unsupported-placeholder failure separate. Add the focused groups in CONTROLS.md before claiming the repair complete. Debug-browser execution is necessary because D65652's transform-layer failure was an assertion during normal traversal, which a release-only numeric result does not cover.

No native source, WPT, browser, build or Git index/history was mutated by this investigation. check.py verifies captured source identities and prior-work preservation only; it does not prove the design or claim runtime correctness.
