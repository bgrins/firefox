# Proposed exact client integer conversion

The retained eight-case browser diagnostic calibrated every row and phase. Its two large-plus-17 width/height cases returned 16777218 instead of 16777217; first/repeat/restored reproduced the error and reset recovered. That was a restored mixed working build before installing 112, not a clean-upstream or release comparison. The native input was not traced. This proposal is uncompiled, uninstalled and unaccepted.

`native.patch` changes only `dom/base/Element.h`: four existing inline client getters call a private in-class static helper instead of converting through binary32. The helper is implicitly inline, preserves the existing script-running annotations and calls the same `GetClientAreaRect()` field exactly once. Its three statements promote before bias addition, then divide by the existing 60-app-unit scale. No new include, class state, generic graphics conversion, geometry query, scrollbar handling or zoom operation is introduced.

All four adapters have exactly the same source policy. Applying the full signed32 conversion to all four keeps that policy consistent without introducing a positivity assumption. The large browser witnesses concern Width/Height only; Left/Top remain unproven large-origin cases. The earlier scope audit recommended a two-getter out-of-line alternative. Root subsequently selected this private inline alternative for review: it avoids changing call shape, and all-four coverage is conditioned on the origin/border/zoom/scrollbar preservation gates below. No four-bug claim follows.

## Exact policy and source mapping

The old client path is float division followed by floor(value + 0.5), whose negative half ties go toward positive infinity. The exact helper uses bias +30 for nonnegative inputs and -29 for negative inputs, then C++ truncation toward zero. It must not use fix 112's -30 negative bias.

| Actual helper operation | Existing `CSSOMClientRounding` proof |
| --- | --- |
| `int64_t(aCoord) + bias`, with scale 60 | `bias_domain`, `bias_fits64`: [-2147483677,2147483677] fits signed64 for every signed32 input. |
| Truncating division by 60 | `source_matches_floor`: equals mathematical floor((a+30)/60). |
| Final int32 cast | `quotient_domain`, `result_fits32`: [-35791394,35791394] fits. |
| Integral input and existing ties | `native_integral_identity`, `half_tie`, `negative_half_tie`; -30→0, -90→-1. |
| Difference from offset policy | `offset_policy_difference`: only negative exact half ties differ in the ideal integer conversions. |

The sealed 14-theorem model is reused by reference, with no duplicate Lean module or new theorem count. This is manual correspondence to C++ semantics, not compiler verification or proof of the preceding frame/zoom calculations. The source intentionally corrects float misroundings rather than preserving every historical large output.

The standalone header patch is independent of 112 and earlier rectangle repairs. HEAD90 and retained upstream976279105b2e have the same original header bytes; the checker verifies unique textual applicability and reversal on both. `GetClientAreaRect` remains wholly unchanged in Element.cpp, including root viewport, scroll-container, non-scrolling padding rectangle, no-box and existing branch-specific unzoom behavior.

The normative integral-size oracle follows CSSOM View section 6's client padding-edge dimensions, excluding scrollbars and ignoring transforms. The new test uses an empty non-root block, no borders or scrollbars, and unit zoom, so content plus end padding is the expected client size. It does not select a new fractional rounding policy. Getter algorithm branches are not rewritten; only final numeric publication changes. [CSSOM View](https://drafts.csswg.org/cssom-view/)

## Tests and independent/composed variants

`client-size-integer-precision.html` has eight independently named tests: clientWidth/clientHeight × content size 16/16777200 × padding 0/17, each collecting first/repeat/reset/restored values. It asserts constituent computed sizes and the client value directly; no offset/scroll metric or DOMRect supplies its oracle. Strict independent geometry calibration remains in the retained research diagnostic. Expected baseline 6 pass/2 fail and candidate 8 pass are pending paired WPT results, not execution results here.

`gecko-wpt.patch` contains only this header change and its own WPT. `combined-112-client-gecko-wpt.patch` concatenates the exact accepted 112 patch with this independent patch: Element.cpp, Element.h and two WPT files, 32+8 main cases. It is a proposed superseding landing scope, not an edit to the sealed 112 acceptance or its installed files. The helpers remain distinct because their negative half-tie policies differ.

Before accepting all-four scope, preserve exact keyed results for the selected client zoom, fractional-zoom sibling, subpixel, root, input, outer-SVG and scrollbar-width tests. Their initial pinned inventory is `css-cssom-client-scope-audit-v1/TEST-PINS.json`; root's runner must add ancestor metadata/support closure and the additional `client-props-input.html` control. Do not assume all pass: retain prior failures and macOS scrollbar intermittency as observed. The subpixel test's clientTop-labelled border assertions call clientLeft, so that file alone is not independent clientTop coverage. Actual Top coverage comes from client-props-input, client-scroll-props-input, outer-SVG and the zoom test. No broad geometry-branch migration is implied.

`differential.cpp` is prepared but unrun. It includes the exact helper extraction and actual nsCoord/AppUnits headers, checks an independent quotient/remainder oracle, ties, signed endpoints, integral identity and ordinary-domain equality with a source-shaped old float/floor expression. It does not compile the Element class or prove the whole old gfx adapter. Root should run it under integer/UB sanitizers, then compile and compare the full candidate. `check.py` only authenticates artifacts, reverses the header edit, verifies upstream text applicability, syntax-checks JS and registers eight names with inert callbacks. No browser/native/index action occurred.

## Counting and commit scope

Because 112 is unsigned, I recommend one eventual integer-geometry precision report/commit if the expanded client scope passes its own validation. Describe the two explicit rounding policies and the two float-loss mechanisms, and retain both independent WPT files. This would extend 112 rather than automatically create 113. Until then, 112's narrower accepted scope remains the only accepted claim; the client proposal must not borrow that acceptance. If the client gates block, retain independently landable 112 and defer this header patch. Research/proofs stay in preceding commits, not the native/WPT commit.
