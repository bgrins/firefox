# Other-engine timing-source review

The pinned Blink and WebKit paths select CSS animation timing before applying the element's own effects. Neither inspected path distinguishes a self-cycle from an acyclic dependency between two effects on the same element. This is material contrary implementation evidence for treating the same-element 1375 ms expectation as an already interoperable oracle. It is not a browser result or a normative exception. Descendant dependencies remain a separate question.

Primary-source snapshots: Chromium `e9e6ab5f300882766d96610c34a026eacb25c88e` (upstream commit time 2026-10-30 06:38:45 UTC) and WebKit `4f16e9eb385db3ca1460ca1ed97cc16823e190fc` (06:43:26 UTC). `SOURCES.json` records exact URLs, captured bodies and hashes; two follow-up hooks are explicitly excerpts with separate full-response hashes. `SOURCE-TRACE.json` supplies checked ranges and commit-pinned links. These are upstream sources, not installed browser versions, compiled artifacts, or Gecko applicability evidence. Initial moving-main web responses differed in age/signature; final conclusions use only the consistent commit-pinned captures.

## Blink

1. `StyleResolver::ResolveStyle` calls `ApplyBaseStyle` before `ApplyAnimatedStyle`. The latter snapshots base data and calls `CSSAnimations::CalculateAnimationUpdate` before adding effect interpolations.
2. `CSSToStyleMap::MapAnimationDuration` computes seconds with the current resolver's length-conversion data. `CalculateAnimationUpdate` gets animation data from its incoming style builder and calls `ConvertToTiming`; changed specified timing reaches `update.UpdateAnimation` on the ordinary update path.
3. After adding interpolations, `ApplyAnimatedStyle` calls the cascade with `CSSProperty::kNotAnimation`. The captured property metadata marks `animation-duration` as an animation property; the flag definition covers animation/transition longhands. Thus this second cascade excludes duration. Other font-dependent values can respond to animated font values.
4. Separately, the non-DCHECK animation-only update path returns after calculating active interpolations, without rebuilding CSS timing. The DCHECK path verifies the optimization and asserts that a timing-changing update is not an animation-only style change.
5. This is not simply cache reuse: `CanReuseBaseComputedStyle` rejects the shortcut when font-affecting animations coexist with font-relative units, and similarly for animated line-height with `lh`. The rebuilt base style still precedes own-effect composition; the later animation-property filter remains.

These functions support an architectural pre-effect timing boundary. They do not establish the complete set of invalidation paths, historical design intent, expression admission in a shipping build, or a universal once-per-frame policy. The unrelated cyclic-variable handling comment in `StyleCascade::Resolve` concerns cyclic custom-property values and is not evidence about this direct `em` timing dependency.

## WebKit

1. `TreeResolver::styleForStyleable` may clone the last pre-effect style for animation-only resolution, but only when there are no properties overridden after animation.
2. `createAnimatedElementUpdate` calls `Styleable::updateCSSAnimations` with `resolvedStyle.style` before invoking its `applyAnimations` lambda. `updateCSSAnimations` compares that style's animation list with the stored list; equal lists can return early. Otherwise matching CSS animations receive `setBackingStyleAnimation`.
3. `CSSAnimation::syncPropertiesWithBackingAnimation` assigns the numeric backing duration to the effect unless the duration field was overridden through the API. It does not read the rendered font at that point.
4. The lambda saves the pre-effect style, clones it, applies keyframe effects, then runs `applyCascadeAfterAnimation`. `PropertyCascade::shouldApplyAfterAnimation` includes declarations with font/line-height dependencies when those metrics are animated. It has no corresponding blanket exclusion of animation longhands. The duration type is a numeric time-or-auto; calc conversion evaluates with builder state, and the captured dependency collector records `em` as font-size-dependent.
5. This dependent recascade marks properties overridden after animation, which prevents the simple animation-only base clone next time. That does not itself supply a second timing synchronization: the inspected function returns the newly animated style after the earlier update call. The inspected post-cascade effect-stack hook deals with accelerated-property overrides; it is not another CSS-duration update. No whole-engine caller census or guarantee about later invalidations is claimed.

Consequently WebKit's path can plausibly produce a post-effect computed CSS duration while the applied effect retains the pre-effect backing duration. That is a source-based hypothesis, not an observed mismatch or proof that the specification permits one.

## Relation to the exact authored diagnostic

The existing fixture and all actual observations remain unchanged. Its fixed values are conditional on which metric feeds timing:

| Case | Fully animated metric interpretation | Consequence of the inspected pre-effect timing path, if no other path intervenes |
|---|---|---|
| Same element: fixed 2000 ms font effect at 750 ms, separate opacity held at 750 ms | Font 22 px; contextual duration 1375 ms; opacity 6/11 | With underlying font 16 px, opacity timing remains 1000 ms and opacity .75. Blink may retain CSS duration 1 s as well; WebKit may recascade CSS duration to 1.375 s. |
| Same element: stepped self-font, duration `1em / 32px * 1s`, held at 750 ms | Conditional transfer 16→32→16; no fixed endpoint | Underlying 16 px supplies 500 ms; font output can remain 32 px. Blink's duration filter and WebKit's backing-vs-post-cascade distinction can break feedback without iteration. |
| Animated ancestor supplies a descendant's inherited metric | Parent's composed metric is available before the descendant's own effects | The same-element pre-effect boundary does not imply freezing the inherited metric. WebKit's resolution context explicitly uses the current parent-stack style. This review does not establish descendant query freshness in either engine. |

The same-element two-effect case is mathematically acyclic, yet that alone does not make the inspected engines perform a second timing update. Conversely, this source evidence does not excuse Gecko's captured late descendant Pending work or establish any engine's first-read completion behavior. `SPEC-BRIDGE.md` states the remaining normative question. Keep current tests as authored evidence; qualify a landing claim until that timing-source distinction is resolved. A narrowly targeted cross-engine run of the existing fixture would distinguish the hypotheses without changing its oracle or rewriting historical FAIL/PASS results; none was run here.

No native change, browser, build, Git/index/canonical operation, model claim, or acceptance increment occurred. Shell networking was used only to retrieve immutable upstream files into this artifact. The initial sandbox DNS failure and missing `webspec-index` are recorded in `CHECK.json`; no bootstrap/install was attempted under the read-only task boundary.
