# Owned CSS keyframe generation prerequisite

The four-file copied candidate makes CSS endpoint generation consume an owned specified-keyframe array and captured CSS defaults. It adds explicit offset refresh on that array. Completed endpoints are local results, never cached in the snapshot, so a later property build after refresh cannot select the snapshot's stale completed endpoints.

This is a prerequisite for bug 1615083, not its repair. No CSSOM hook, live source edit, native build, browser run, metadata change, or Git mutation was performed. The patch is cumulative against `d825b3e46700b1378820a591ff8f5a5c15bbc811`. It **replaces**, rather than stacks on, the earlier completed-output snapshot patch in `css-pseudo-animation-next-candidate-20261110-v1`. The separate composition extraction is not included.

## Interface and ordering

| Operation | Inputs and effects |
| --- | --- |
| `CapturePropertyInputs()` | Clones specified keys once, captures optional CSS generation defaults/opt-out, then captures the strong element and pseudo request together with the effect composite. |
| `PropertyInputSnapshot::RefreshComputedOffsets(timeline, range)` | Calls existing `KeyframeUtils::ComputeMissingKeyframeOffsets` on the private owned array. Does not mutate the effect, sample the timeline, rebuild live properties, or publish style. |
| `BuildPropertiesFromInputs(snapshot, style, timeline, attributes)` | Generates CSS endpoints afresh from the snapshot array, then computes per-property values in the supplied context. No completed array survives this call in the snapshot. Resets and forwards the attribute-dependency output. |
| ordinary `BuildProperties()` | Preserves null-target admission, one specified clone, no offset refresh, debug specified-key equality check, and unconditional array move-back. |
| `GetComputedKeyframes()` | Retains its boolean/output-array API. Captures generation defaults virtually, returns false without touching output when absent, otherwise generates directly from live keys. No new specified-array clone for `getKeyframes()`. |

The intended future request sequence is capture, explicit owned refresh using a coherent timeline/range context, then property build using the corresponding style/timeline. The API does not enforce that refresh was called, because ordinary rendering must preserve its existing no-refresh call order. It does enforce that property build cannot reuse completed endpoints stored before refresh: there are none. Previously returned property arrays remain previous results and must not be reused as fresh output after a later refresh.

## Source preservation and dispatch audit

`searchfox-generation-callers.txt` records discovery; `pinned-generation-callers.txt` and the twelve Git-authenticated source copies establish branch-specific details. The only `GetComputedKeyframes` override is `CSSAnimationKeyframeEffect`; the only callers are `KeyframeEffect::BuildProperties` and `KeyframeEffect::GetKeyframes`. The former is routed through the owned array. The latter's body is unchanged and calls the retained wrapper.

The virtual seam intentionally changes from generation into a caller-provided output to `CaptureCSSGenerationOptions`. Base effects, including transitions, return no CSS options. The CSS override preserves `mIgnoreKeyframesGeneration`: JS-set keyframes are not regenerated, even while the object remains the CSS subclass. Captured CSS `mDefaultComposite` is distinct from the effect's `mEffectOptions.mComposite`; both retain their original roles. Default easing and the generation algorithm, including implicit endpoints and null declaration sentinels, are retained.

The generator moved within `CSSAnimation.cpp`; its body differs only by replacing live `mKeyframes` with the explicit array and removing the boolean return. Existing helper functions remain in that translation unit. `GetKeyframes`, live range refresh, all external property-building callers, and effect bookkeeping outside the extraction are unchanged. Named-range ordering is not repaired here; concurrent range-group work is a separate candidate.

The original `BuildProperties` cloned specified keys, invoked virtual generation, then read target/effect composite. This candidate clones, virtually captures defaults, captures target/composite, then runs the extracted value-only generator. Its current implementation manipulates arrays and declaration references; no effect publishing or script invocation is introduced. Preservation is scoped to this current synchronous path, **not arbitrary reentrant overrides**. The existing defensive copy/debug/write-back behavior is retained. Capturing target/pseudo intentionally stabilizes the request's value as well as extending element lifetime; the old borrowed pseudo reference could observe hypothetical retargeting.

## Ownership, freshness, and cost

The snapshot owns the specified array, generation-default values, effect-composite value, and `OwningAnimationTarget`. Declaration blocks within keyframes remain shared references, not deeply immutable copies. It owns no computed style, animation/effect timing, provider state, animation range, or timeline. Callers must keep those objects alive and establish the appropriate coherent context. This extraction does not prove a general no-script/reentrancy contract for all downstream value conversion.

Owned refresh uses the existing offset algorithm, including unresolved and zero-attachment-range handling. `ViewTimeline` mapping reads cached timeline data; refresh does not tick or otherwise make that data current. Capturing defaults is therefore independent of establishing offset/timing freshness. The supplied computed style must also be appropriate for custom properties, font/relative units, and implicit underlying endpoints.

Ordinary property builds still make exactly one explicit full specified-keyframe clone, subsequently moved back. The existing CSS generator still creates its percentage/range arrays. New costs are the captured target's strong reference and the copy/move of default easing/options; complex timing functions may have owned or reference-counted storage. No allocation-count or performance equivalence is claimed for those value copies. `getKeyframes()` adds the options copy but no full specified clone.

## Checks and remaining gates

`check.py --check-git` authenticates source/test pins, replays the patch forward and backward in scratch files, checks unchanged exterior code, checks the generator's normalized body, and checks ordinary admission/write-back, single clone, opt-out/default forwarding, and absence of stored completed arrays. These are structural/source checks, not a C++ proof or compilation. `FORMAT.json` records actual repository-filename clang-format commands and idempotence. Known preexisting untracked prototypes were hash-checked and neither consumed nor changed.

`TEST-PLAN.md` provides the bounded existing test inventory. A real build and baseline/candidate callback comparison are still required. In particular, ordinary WPT coverage does not directly exercise the new explicit owned-refresh call sequence before a future caller uses it.

The final missing-pseudo repair still requires owned coherent timing/effect order, pending/unresolved behavior, fresh provider-dependent endpoint context, base values and property masks, CSSOM-only admission/cache handling, pseudo-aware transient recascade and cascade levels, and debug validation of the historical transform-hint failure. Neither this seam nor its eventual optimized preservation experiment closes those gates.
