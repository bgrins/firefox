# Conditional offset and scroll precision consolidation

This proposal treats the four offset metrics and two scroll dimensions as one final-conversion defect, conditional on the separate scroll calibration probe confirming the predicted result. It is not accepted or installed. The active offset-only candidate and all earlier sealed artifacts remain unchanged. No additional bug is counted.

`native.patch` changes one file, `dom/base/Element.cpp`, against explicit revision `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`. A file-local `AppUnitsToRoundedCSSPixels` replaces the offset lambda and the two final `nsPresContext::AppUnitsToIntCSSPixels` calls. The standalone landing patch contains only that native patch and one WPT. Research tooling and this proof mapping are separate artifacts.

## Scope and source correspondence

| Consumer | Existing geometry and zoom boundary | Proposed final conversion |
| --- | --- | --- |
| `Element::GetOffsetRect` | Existing frame/parent/shadow geometry, then one `EffectiveZoom().Unzoom(rect)` | Convert x, y, width and height independently with the shared helper. No endpoint subtraction or rounding-after-union policy is introduced. |
| `Element::ScrollWidth` | Existing `GetScrollSize()` returns app-unit size after its existing `EffectiveZoom().Unzoom(size)` | Convert returned width with the shared helper. |
| `Element::ScrollHeight` | Same size producer and unzoom | Convert returned height with the shared helper. |

`GetScrollSize()` retains its `nsSize` return type and exact body. Its scroll-container range/port addition, overflow-visible padding/child union, no-frame return and unzoom are unchanged. Other internal callers continue receiving app units. `GetScrollOrigin()` and `GetClientAreaRect()` are byte-identical; `Element.h` is not part of the patch. Client metrics retain their existing float conversion and floor(value + 0.5) policy, including negative ties. No generic gfx, nsPresContext or CSSPixel converter is changed.

The helper's three arithmetic statements are identical to the reviewed offset lambda after indentation removal. Promotion precedes the signed bias; division truncates toward zero with divisor 60; the final cast is representable. The helper preserves ideal nearest rounding with half ties away from zero. It intentionally corrects old float-induced misroundings, so it does not claim bitwise preservation of all historical outputs. Both prior unzoom operations remain exactly once on their respective paths, with their existing precision/clamp behavior.

## Existing proof reused

`Rounding.lean` is a byte-identical copy of `css-cssom-integer-rounding-model-v1/Rounding.lean`: the same 21 results, zero new theorems. Its sealed independent replay is referenced, not rewritten. This task did not run another Lean compiler or C++ build.

| Actual shared-helper operation | Existing result |
| --- | --- |
| Signed32 `aCoord`, promoted sign-dependent ±30 addition | `bias_domain`, `bias_fits64`: numerator [-2147483678, 2147483677] fits signed64. |
| C++ signed division by 60, truncating toward zero | `source_matches_magnitude`, `source_matches_remainder`: source-shaped rounding equals independent quotient/remainder rounding. |
| Final signed32 cast | `quotient_domain`, `result_fits32`: quotient [-35791394, 35791394]. |
| Exact integral scroll/offset input `60*k` | `native_integral_identity`, `integral_identity`: exact integer k is preserved within the native input domain. |
| Existing ideal fractional tie/sign policy | `positive_half_tie`, `negative_half_tie`, `native_pair_symmetry`, `nearest_error`, `monotone`. |

The same domain applies to all six scalar call sites because each supplies an `nscoord`. This is a manual semantic correspondence to the helper, not extracted C++ or a proof of earlier native geometry, unzoom, browser branch reachability, compiler correctness, or CSS fractional-rounding policy. The previously executed actual-header sanitizer helper exercises the identical arithmetic statements in lambda form; it is not a compilation receipt for this new static-function placement or its new consumers.

## Test proposal and acceptance gate

`offset-scroll-integer-precision.html` preserves the previous 24 test bodies and their names verbatim, then adds eight independent tests: scrollWidth/scrollHeight × content size 16/8388600 × end padding 0/9. No scroll assertion is hidden behind an offset assertion. Each new case collects first, repeated, reset-padding and restored-padding values from the same empty target, with its own cleanup and assertions. New styles use classes; the previous offset fixture bodies are unchanged.

The landing cases check constituent sizes, padding, parent, box count, overflow, transform and unit zoom. They intentionally do not use an offset size or DOMRect value as the expected scroll result. The separate research probe `css-cssom-scroll-client-proposal-v1` supplies stricter independent rectangle/style/parent calibration and unchanged client controls before these hypotheses can be classified. Test registration and syntax checks here execute no browser test body.

Conditional predictions, not observations from this artifact:

| Source role | Offset 24 | Scroll 8 | Total 32 |
| --- | --- | --- | --- |
| Normalized old source | 18 pass / 6 fail | 6 pass / 2 fail | 24 pass / 8 fail |
| Offset-only candidate | 24 pass | 6 pass / 2 fail | 30 pass / 2 fail |
| Consolidated candidate | 24 pass | 8 pass | 32 pass |

The two predicted scroll failures are the large-plus-nine width/height cases: expected 8388609, old converter predicted 8388610. Reset to 8388600 should pass. These predictions require calibrated layout and should be replaced by exact paired raw results before acceptance. Preserve all existing offset/zoom gates and add relevant scroll dimension, overflow-visible, scrolling-container and zoom preservation coverage; root must choose and pin those rosters before running. A wider caller migration or the separately hypothesized larger client conversion loss is outside this patch.

If the scroll reproduction confirms while the offset repair remains open, this is a compact single-fix scope: six consumers of the same final arithmetic, one file-local helper, one 32-case WPT. If offset acceptance has already frozen its landing scope, keep the scroll addition separately reviewable and cross-reference the same cause rather than inflate the defect count.

## Spec boundary

The official CSSOM View editor's draft dated 8 October 2026 was read on 23 October 2026: section 6's scrollWidth/scrollHeight getters return the corresponding scrolling-area dimension; section 2's rightward/downward scrolling-area edges include the padding edges and eligible descendants. For this active-document, non-root, non-body, empty block target, the selected dimension is content size plus end padding. The fixture uses exact integer sizes and does not select a fractional tie policy. [CSSOM View](https://drafts.csswg.org/cssom-view/)

The patch changes final numeric publication only; it does not reimplement the numbered getter algorithms or their special root/body/no-box branches. Existing implementation placement and all those branches remain intact. The current unzoom behavior is preserved rather than justified anew by this narrow integral-identity argument. `webspec-index` was unavailable in the earlier retained audit; the official document was read with the web fallback. Fragment navigation was normalized by that tool, so no independent anchor-validation claim is made.

## Reproduction of artifact checks

Run `python3 artifacts/css-cssom-offset-scroll-consolidation-v1/check.py`. It authenticates referenced seals, reconstructs the entire one-file change, checks unchanged producer bodies and exact arithmetic/model reuse, syntax-checks the scripts, and registers all 32 names with inert `test` callbacks. It does not install a WPT, run a browser, compile native code, modify the index or touch native source. No generated compiler products or target directories exist.
