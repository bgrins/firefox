# B: use the 11-degree oblique search threshold

Status: independent proposal for review, 2026-10-18. `threshold-proposal.patch` changes only `StyleDistance` in `gfxFontUtils.cpp`; it applies without A. No native/browser/proof execution is claimed here.

## Repair and basis

Replace the local 14-degree-derived search constant with `kObliqueSearchThreshold = 11.0`. Use it for the italic-to-oblique fallback target, the positive `>=` branch, and the negative `<=` branch. Correct the existing last-branch comment to use the negative threshold. Keep `FontSlantStyle::DEFAULT_OBLIQUE_DEGREES` and unspecified `font-style: oblique` at 14 degrees.

[CSS Fonts 4, Matching font styles](https://drafts.csswg.org/css-fonts-4/#font-style-matching) chooses outward-first searching at and beyond 11 degrees, inward-first below it, and mirrors this for negative requests. Italic's positive-oblique fallback begins at 11. The default oblique angle answers a different question. Current primary draft evidence and CSSWG issues 2295/2539 are copied from the frozen survey; the primary page was checked again on 2026-10-18.

## Full affected helper audit

The equality fast path stays first and returns zero for either endpoint; interior containment remains zero in each oblique branch. The normal-request branch is unchanged. An exact italic face remains zero. Italic fallback with `aItalicToObliqueFallback == false` still resets the target to zero and applies its existing bad-fallback bias; changing the initial target to 11 must not affect that branch. Normal/italic encoding, fixed-point conversion, distances and range providers are unchanged.

At +11 the `>=` branch applies; at -11 the `<=` branch applies. One slant quantum is 1/256 degree, so 10.99609375 and 11.00390625 are exact adjacent boundary controls. Corresponding negative cases must reverse directions. ±14 remain in outward-first branches. Zero and sign-crossing ranges keep their existing treatment; an inclusive range spanning the target has zero distance. A range ending at 11 satisfies italic's positive fallback threshold with score 1; exact italic still scores 0. The +1 prevents an oblique match from tying true italic.

All consumers receive the changed style coordinate through `WeightStyleWidthDistance` and `WSSDistance`: both family general loops and their shared/unshared fallback paths. There are no other StyleDistance callers in the frozen Searchfox inventory. Existing simple-family shortcuts and native platform-specific fallback may bypass the helper; no claim that B revises those algorithms. Constructor fixed-point/domain audit is in DESIGN-A. Eleven is exactly representable in binary32/binary64 and 8.8 fixed point, and maximum helper distances stay within current assertions. No widening or raw encoding change is needed.

The patch intentionally does not repair every cross-kind ordering. For example, the current normal branch places negative oblique before italic, while the current spec's explicit sequence puts italic first. That is a separate static lead requiring its own independent runtime/spec adjudication. Likewise numeric `ital` axis synthesis, unsupported-font fallback, and normal/oblique-zero representational distinctions are outside this repair's theorem. Do not claim a complete StyleDistance-to-spec proof based on these changes.

## WPT proposal

`wpt-proposals/font-matching-threshold.html` proposes 19 cases in both orders, 38 subtests. Four reproduced witnesses cover positive/negative 12-degree requests, a range case, and italic fallback. Controls cover below/above the search pivot; new cases include exactly ±11 and their one-quantum neighbors, exact matches, a range including 11, italic fallback to a range ending at 11, default oblique remaining 14, exact italic, and equal-distance declaration order.

The file uses the same independently calibrated Ahem protocol described in DESIGN-A, embedded in the file so neither repair's WPT depends on the other. Equal width and weight throughout B isolate style search; scalar-priority A is not needed for those cases. A uses angles ±20 and normal/italic width competition rather than the 11..14 interval, so its bug witnesses do not require B. Browser baseline/candidate runs must verify this separation, not merely run the combined patches.

Required additional native controls include `aItalicToObliqueFallback` false for all italic/range cases (the current oblique-only policy must be byte-for-byte equivalent in outcome); normal requests; exact italic; targets/endpoints ±90, zero, ±11, ±14; ranges touching/spanning each boundary; singletons and containment; both signs; and the existing last-resort weight behavior. The existing `oblique-last-resort-weight-selection.html` failure tracked by bug 2033377 must not be relabeled a new threshold regression or silently accepted as a new pass. Execute and compare actual existing-test outcomes.

## Formal proposal and source closure

Define the spec oracle as an ordered sequence of angular intervals/directions, separately from native piecewise distance arithmetic. For valid fixed-point angle ranges, prove that minimizing the distance for each of the four oblique request regions selects exactly the faces containing the first available angle in the relevant positive/same-sign search phase. Prove inclusive endpoint and threshold partition lemmas and positive/negative symmetry. Separately prove italic-to-positive-oblique fallback's 11-degree pivot and strict preference for actual italic. Explicitly state which later cross-kind fallback phases remain assumptions.

If a broad universal theorem includes all available style kinds, it must first confront the existing cross-kind discrepancy rather than encode it as spec truth. A narrower same-sign subproblem is useful and honest, but its scope must be part of the approved milestone before implementation. Both-patch verification can then compose these coordinate contracts with A's independent ordered-filter theorem.

Native connection should extract the entire unchanged/changed StyleDistance function, actual fixed-point conversion/inlines, ordered range providers and callers; retain complete before/after sources and a counted two-version extraction manifest. Include `FontPropertyTypes.h`, computed `font.rs`, relevant `ServoStyleConstsInlines.h`, and generated constants/type layout provenance. A handcrafted adapter using unconstrained floating point is not an adequate fixed-point bridge. Name all owners, expose validity assumptions, and retain source-only input closure separately from full historical receipts.

Required executable mutations (planned, not run): restore 14; change only positive branch; change only negative branch; leave italic fallback at 14; make +11 strict `>`; make -11 strict `<`; change default oblique to 11; remove containment; erase the italic exact-match advantage; override the oblique-only zero reset. Every semantic mutant needs a successful executable witness plus expected reference/changed winners, separately from Lean theorem failures. A default-angle mutant must reach the real provider or a separately pinned provider test; mutating an unused local number is not evidence. Finish with complete bounded native comparisons for original, B-only, A-only and combined versions, retaining known unrelated failures explicitly.
