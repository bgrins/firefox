# Release original-key probe: raw evidence review and WPT proposal

**Confirmed release observation, independently recounted.** Installed Firefox 158 produced 48 complete configurations / 240 stages. Twelve stages disagree with the calibrated visible reference; the other 228 match. This review executed only the independent raw-data checker, not a browser or build.

| Class | Failing stages | Returned | Expected | Dimensions of the cases |
| --- | ---: | --- | --- | --- |
| Direct flex item | 8 | 0×0 | 50×32 on insertion; 100×32 on removal | Hidden shrink, append/prepend, bounding/offset |
| Clean nested descendant | 4 | 100×32 | 50×32 on insertion | Hidden shrink, append/prepend, bounding/offset |

Every failure persists across all three consecutive queries. All visible references match the independent exact integer oracle, all visible/no-shrink/zero-width-sibling controls pass, and all warm/visibility/show stages pass. Nested removal returns the expected100×32, but this coincides with its old retained size; **it is not evidence that hidden removal performed a correct new reflow**. Direct removal remains0×0. Showing restores both classes.

## Independent checks

`recount.py` does not import the producer validator. It reconstructs the48 configuration keys, five ordered phases, all result shapes and the100/50×32 oracle. It compares its complete difference list to the retained SUMMARY rather than trusting that summary's counts. It also authenticates the nine source payloads, matches all recorded pre/post source and release binary pins, checks the observed Firefox158 UA, and confirms recorded cleanup/error fields. The result contains one complete POST and launcher exit0; the owned browser PID is86844 and the runner records its profile removed. No browser exit after deliberate shutdown is substituted for the valid payload gate.

All outer flushes report one subject client rect and64px scroll height.232 report100px scroll width; the eight **visible no-shrink insertion** controls correctly overflow to200px. The first independent checker incorrectly asserted100px for every outer scroll width. That audit assertion failed, was corrected with the source-derived no-shrink exception, and then passed. `INITIAL-RECOUNT-FAILURE.json` preserves this reviewer mistake. No raw result, target expectation or tolerance changed.

`source/` is the authenticated original probe capsule; `runtime/` retains exact raw result, summary and browser log. `RECOUNT.json` is the independently generated result. Source and binary pins are stable within the recorded run. The historical binary hashes establish which executable ran; they do not prove a source translation or exact cache trace.

## Oracle and source scope

Two100px flex bases, shrink factor1 each and explicit min-width0 share100px of negative free space: final50px each. Zero-width insertion and no-shrink controls retain100px. The nested target has width100% of the flex item's content box. This small-size setup avoids precision/overflow ambiguity. [Flexbox flexible-length resolution](https://drafts.csswg.org/css-flexbox-1/#resolve-flexible-lengths).

Skipping content does not license an incorrect geometry-query result: the containment specification describes processing skipped rendering work when a descendant layout query requires it, with an explicit bounding-rectangle example. This also motivates retaining repeated reads rather than treating the first as a permissible stale snapshot. [CSS Containment restrictions and examples](https://drafts.csswg.org/css-contain-2/#content-visibility).

The source hypothesis uses the **original computed-size key field**: sibling shrink can change100→50 without our added padding/containing-block key members. The retained complete original indexed key class contains computed size, computed min/max block size and available block size. Fixed100×64 subject dimensions and zero item padding/border avoid intentionally varying our added fields. Native executed key values, clean bits, skip guards and frame identities have not been instrumented here. The release observation establishes that a corresponding public failure predates the local key additions; it does not by itself prove that every local fixed-width failure has the same native cause.

This evidence supports investigating a standalone preexisting defect instead of declaring the entire issue introduced by fix101. Do not count or land a new native bug solely from this report; final source attribution, repair scope, paired candidate results and standalone packaging remain root gates. Removing the containing-block key would conceal one trigger while retaining the independently required caption-resize repair as a regression.

## Proposed WPT

`hidden-flex-item-measuring-reflow.html` is a standalone48-case testharness proposal for `css/css-contain/content-visibility/`. It retains both direct and nested targets, append/prepend, all three flex modes, visible/hidden controls and both query APIs. It copies the exact fixture CSS and helper behavior from the executed release probe. Each test first collects the complete five-phase sequence, with outer flush then first/second/third reads then a separately built visible reference. Only after collection does it assert reference calibration and each target read. An insertion failure therefore does not prevent exercising removal/show.

The only intentional harness changes are feature assertion, testharness reporting/cleanup, and assertions replacing localhost POST. All expected sizes remain exact. No source-cache internals appear in the browser assertion. Based on the retained raw sequence, the predicted WPT baseline is8 failing configurations (four direct and four nested) and40 passing configurations. **The WPT itself is unexecuted**; harness/cleanup transfer still requires root validation. This proposal supplements rather than replaces the earlier fixed-width scenario that exposed the local stronger-key trigger.
