# Accumulated flex margins corrupt flex growth

Status: browser-reproduced native candidate, not an accepted or committed fix. A separate signed-wrap build is in progress; this candidate has not been applied to the native worktree.

## Reproduction

Use a 1000px-wide nowrap flex container. Each item has flex:1 1 Bpx, margin-inline-end:-Bpx, min-width:0, and no border, padding or gap. Each outer base/hypothetical main size is zero, so the 1000px of free space should be distributed among the items. All sampled item widths should be B+1000/N, allowing layout/CSSOM rounding.

| B in pixels | N immediately below failure | Observed below | N at failure | Observed at failure |
|---|---:|---|---:|---|
| 1,000 | 35,791 | widths about 1000.03px; final outer end about 1000px | 35,792 | sampled widths zero |
| 100,000 | 357 | widths about 100002.8px | 358 | sampled widths zero |
| 1,000,000 | 35 | widths about 1000028.6px | 36 | sampled widths zero |
| 10,000,000 | 3 | widths about 10000333px | 4 | sampled widths zero |

All failure samples include the first, middle and final item. Later items are positioned around -17,895,706px in these runs. The 32-item/1000px control passes. Setting grow=0 preserves the specified basis and zero outer advance at all three tested failure scales. The 35,791/35,792 pair was repeated exactly in reverse order. Three captures retain fourteen observations, computed margins/flex values, geometry and Firefox 158.0 UA. The probe removes its nodes after every run. Its owned browser tab was closed and the preexisting tab preserved. No preference/profile-isolation claim is made.

The browser tool initially refused an absolute saveTo destination outside its output area. Returned JSON was then saved through the workspace file tool. No browser save-path restriction was changed.

## Cause and scope

The native-arithmetic review identified mTotalItemMBP as an nscoord accumulator even though mTotalOuterHypotheticalMainSize uses AuCoord64. AddLastItemToMainSizeTotals adds every item's margin/border/padding to that narrow accumulator. ResolveFlexibleLengths chooses growth from the wide outer total but later computes the content-box space using the accumulated MBP value. At 60 app units per CSS pixel, 35,792 * -60,000 = -2,147,520,000, outside signed 32-bit range; each individual value and outer-size cancellation are in range. The observed failure threshold matches this prediction.

Source evidence is retained in source-mbp.txt. The existing overflow comment discusses huge individual item sums and huge gaps; this candidate instead accumulates individually valid values. The browser observations support the consequence and threshold, not a precise assertion about optimized C++ undefined behavior or the machine instructions. No memory-corruption or security impact is established. This is a layout defect requiring a large accumulated magnitude; initial triage suggestion is P3, subject to a real-world testcase.

Discovery attribution: static review of the native assumptions missing from the signed rational proof produced the arithmetic counterexample; browser execution confirmed it. No Lean theorem or SMT solver discovered this native defect. The signed policy proof remains correct within its stated rational scope.

## Specification

[Flexbox resolving flexible lengths](https://drafts.csswg.org/css-flexbox-1/#resolve-flexible-lengths), snapshot 38344222a11dfb6fd993f03323ad21badb79c1c13ea56af1b1395e8d3f88cbe2:

1. The outer hypothetical sum is zero, below the container's 1000px main size, selecting growth.
2. Nonzero equal grow factors and equal base/hypothetical sizes leave these items flexible.
3. The initial and remaining free space is 1000px because each base plus its negative margin cancels.
4. Equal grow factors allocate 1000/N to each base. These positive results encounter no min/max constraint in the probe.

Verdict: REACHED for the stated sizing result. Collapsed-item gap interpretation is not involved.

## Repair and validation plan

candidate.patch contains only a proposed mTotalItemMBP widening to AuCoord64 and the new WPT. Its base is the retained source before the separate signed-wrap repair; the two native hunks do not overlap. SumOfGaps arithmetic is a separate obligation and is not changed by this candidate.

The WPT has 56 cases across row/column, reversed directions, wrap/nowrap, boundary counts and non-growing controls. It uses at most 358 nodes per case; the 35,792-node test remains a standalone research probe. The installed Firefox 158 ran this exact WPT through testharness.js/testharnessreport.js over a temporary localhost server: harness OK, 16 failures and 40 passing controls. All failures are the predicted positive-grow boundary cases and report zero main size. RELEASE-WPT.json retains all rows. This is a browser-tab baseline, not a mach wpt run. The server exited cleanly and the owned tab was closed. WPT-specific lint passed. The proposed native fix has no build or fixed-browser evidence yet. After the signed-wrap build and its tests finish, capture the new WPT baseline, apply this candidate's native hunk, rebuild and rerun the WPT plus focused regressions. Keep its eventual native/WPT commit independent of the preceding research/proof work.
