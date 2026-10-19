# A: preserve font matching priorities

Status: proposal for review, 2026-10-18. No live native or WPT changes, browser run, Gecko build, or proof implementation. The frozen independent defect verdict remains unchanged.

## Repair

`lexicographic-proposal.patch` changes five files. Both `WeightStyleWidthDistance` and `WSSDistance` return `FontMatchDistance`. Its comparison key is `(presentation rank, width distance, style distance, weight distance)`. Presentation rank is 0 for unrestricted/matching presentation, 1 for a mismatch, and 2 for the default unmatched sentinel. Width, style and weight are separate doubles; no score multiplication or conversion to float remains. Existing coordinate helpers and assertions remain unchanged.

The sentinel must sort after a *mismatched* real candidate too. A tuple beginning with false and infinity would fail this condition if real mismatches begin with true. The proposed rank 2 avoids that error. `NotePresentationMismatch` changes only rank 0 to 1. `IsZero` requires rank 0 and three zero distances; a perfect style with the wrong presentation must not terminate the global search.

The five files are `gfxFontUtils.h` (score type), `gfxFontEntry.h` (accumulator), `gfxFontEntry.cpp` (three consumers), `SharedFontList.cpp` (two consumers), and `gfxPlatformFontList.cpp` (two exact-match early exits). No shared-memory face representation or IPC serialization changes. `GlobalFontMatch` is a stack accumulator, and its style reference still refers to the caller-owned style. The tuple owns its numbers; there is no temporary-reference adapter.

## Normative boundary and fallback

[CSS Fonts 4, Matching font styles](https://drafts.csswg.org/css-fonts-4/#font-style-matching) successively filters a family by width, style, and weight. A lower-priority property cannot compensate for a worse earlier property. Its final installed-font fallback step permits UA-dependent results. That latitude does not justify retaining the defective scalar mechanism here: `gfxFontGroup::FindFallbackFaceForChar` also calls both `SearchAllFontsForChar` implementations within an already selected family, and the shared native helper contract explicitly promises the same priorities. The repair therefore covers all score consumers.

Presentation preference is an existing Gecko policy above the three style coordinates, not a newly asserted universal CSS ordering across installed families. Common-font list order, platform fallback, font visibility, cmap availability/loading, and synthesis policies remain provider decisions. The proposed proof must distinguish the normative family filter from that installed fallback policy.

## Complete consumer audit

| Consumer/provider | Behavior retained or adjusted |
| --- | --- |
| `gfxFontFamily::FindAllFontsForStyle` | One-face/simple-family shortcuts unchanged. General loop iterates backward, clears the output on improvement, and preserves all equal-key matches in the same order. The existing adjacent duplicate-pointer suppression remains. |
| `fontlist::Family::FindAllFacesForStyleInternal` | Forward general loop; null mapped faces skipped. Equal-key entries retained in forward order. Shared pointer/descriptor checks and GTK non-scalable bookkeeping unchanged. |
| `fontlist::Family::FindAllFacesForStyle` | Existing bitmap-size filtering follows style selection, including tolerance and scalable fallback; no new size coordinate. |
| `gfxFontFamily::FindFontForChar` | Selects best-style entries first, checks skip/coverage and optional presentation; fallback to `SearchAllFontsForChar` for a nonnormal request remains. Removes its float narrowing. |
| `gfxFontFamily::SearchAllFontsForChar` | Reverse iteration over covered entries. Removes float narrowing. Equal complete keys still use the existing descending face-name comparison. |
| `fontlist::Family::SearchAllFontsForChar` | Forward iteration; strict improvement only. Optimistic comparison before lazy font creation/presentation is valid because adding mismatch can only worsen rank. Recheck after mismatch remains. Equal keys keep the earlier face. |
| `gfxPlatformFontList::GlobalFontFallback` | Platform-specific attempt and visibility/async cmap branches unchanged. Both loops now use `IsZero`; sentinel and mismatches cannot trigger early termination. Existing first exact-match stopping still limits later name-tie comparisons. |
| `gfxPlatformFontList::CommonFontFallback` | Uses the accumulator through the above family methods and its own ordered-family/presentation policy. No direct arithmetic. |
| `gfxFontGroup::FindFallbackFaceForChar` overloads | Shared/unshared calls use the new accumulator; async readiness and creation remain external. |
| `FindFontForStyle`, `FindFaceForStyle`, `gfxFontGroup::AddFamilyToFontList` | Consume selected lists/first face; no score arithmetic. |

Searchfox caller inventories are frozen in `evidence/searchfox-*.txt`. Full local definitions are in `original/` and the inherited survey snapshots. Searchfox's indexed revision differs in surrounding source positions; proposed bytes derive from the pinned local originals. No line-number correspondence is assumed.

## Ranges, ties, numeric bounds

Ranges are inclusive; a degenerate range is a single value. `FontPropertyRange` requires ordered endpoints. `FontFaceImpl::GetAttributesFromRule` passes computed weight/width/slant ranges into user font entries; `gfxUserFontFamily::AddFontEntry` preserves declaration order and asserts it is not a simple family. Thus downloaded range faces reach the general loop. Variation fonts with nonsingle ranges avoid the ordinary unshared simple-family shortcut. Shared-family construction also rejects nonsingle ranges. Variable-axis discovery/application and actual `fvar` interpolation are outside this repair.

Weight and width use unsigned 10.6 fixed point. Valid weight is 1..1000; width is clamped to 0..1000%. Slant uses signed 8.8 fixed point, angles -90..90, with italic encoded as 100; zero shares normal's encoding. `FromRaw`/deserialization still require valid-provider assumptions. Parsed finite CSS values and the normal constructors satisfy those assumptions; arbitrary malformed raw ranges are not a claimed domain.

Float conversion of these 16-bit fixed-point values is exact. Subtracting them and adding the helper's small integer penalties stays exact in binary64. Distances remain bounded by the existing 2000/900/1600 assertions. Tuple comparison therefore needs no epsilon and has no overflow/NaN for valid inputs. It does not require a proof that huge weighted sums preserve fractional lower coordinates.

The present weights already fail: one style quantum contributes only 39.0625 to a scalar score versus a possible weight penalty of 1200; one width quantum contributes 1,562,500 versus italic's 7,000,000. Float narrowing additionally loses differences at large scores: near 1e11 its ULP is 8192. Raising factors cannot repair those consumers. The proposed type accepts only internally produced distances; it does not claim a total IEEE order over NaN. A future formal bridge must explicitly establish finite valid inputs.

True component ties retain the original traversal and declaration-order behavior. Scalar collisions that previously looked like ties cease to be ties; that is part of the correction. Identical downloaded descriptors with overlapping coverage still prefer the last declaration. Disjoint `unicode-range` faces must remain in the selected list for later coverage selection. Bitmap filtering, skipped fonts, failed font creation, and duplicate identities need native controls, not merely a score-class test.

## WPT and native gates

`wpt-proposals/font-matching-lexicographic.html` is a concrete standalone proposed testharness file for `css/css-fonts/matching/`: 13 cases in both declaration orders, 26 subtests. It includes four reproduced singleton/range witnesses, mirrored negative fine-angle and expanded-width cases, coarse controls, fractional weight tie breaking, overlapping ranges, and a declaration-order tie.

Every subtest loads four explicit @font-face rules using `/fonts/Ahem.ttf`: two alternatives and two independent one-face calibration families. Four X glyphs at 20px must measure 80px for size-adjust 100% and 40px for 50%. The frozen Ahem has UPEM 1000 and X advance 1000. Descriptor/request parsing is checked; all faces must finish loading before measuring. The expected calibrated face is a literal case-table result of ordered filtering, not the candidate implementation. No canvas fallback or installed font is an oracle. No browser claim is made for these new proposed files yet.

WPT cannot portably force a particular system-font fallback registry, presentation glyph provider, shared-memory mapping, or GTK bitmap inventory. Before landing A, require a separate complete-native bounded harness (or Gecko gtest with controlled faces) covering both general family loops and all three fallback consumers. Include zero/one/multiple faces, ties/duplicate identities, missing maps, mapped-null faces, glyph absence, failed font creation, mismatch-only candidate, incumbent mismatch versus new matching candidate, `Any`, text and emoji preference, exact-zero termination, and both name-tie directions. Keep the complete methods extracted, with named owners and explicit provider observations. Do not present an extracted score class alone as coverage of those callers.

## Formal proposal

Universal Lean contract: for any finite ordered face list and total coordinate orders, successive minimum filtering (width, then style, then weight) returns exactly the same ordered identity sequence as a separately defined lexicographic scan. Prove preservation of ties, singleton/empty behavior, permutation invariance of the selected set, and first/last selection policies. Extend separately to `(presentation,width,style,weight)` for Gecko fallback and prove unmatched-sentinel ordering, optimistic-pruning soundness, and exact-zero lower-bound termination.

This contract is parameterized by coordinate ranks. It is not a proof that all current `StyleDistance` behavior implements Fonts 4. Width/weight helpers can receive their own piecewise fixed-point-to-spec rank proofs. For style, use the B contract plus explicit legacy cross-kind assumptions. Full native bounded connection must compare raw descriptors/provider results against an independent successive-filter oracle, then the actual extracted methods, including output identity order and provider call trace. State both universal Lean and finite native guarantees separately.

Required executable mutation gates (not executed in this design): restore weighted addition; swap width/style; swap style/weight; narrow score coordinates or the combined key to float; sentinel rank 0; drop presentation coordinate; treat mismatched zero as perfect; shared `<` to `<=`; drop equal-score entries; remove list clearing; reverse unshared ordering. Each must compile/run and disagree on a concrete independently expected output. Compiler errors, assertion failures, and a theorem rejection alone are not semantic mutation evidence. Also run randomized and boundary native score/caller cases against rational raw-input oracles. Any materially changed matching cost should be measured with controlled large face families before accepting the broader fallback repair.
