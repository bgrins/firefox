# Flex measuring cache and percentage padding

Status: accepted as a bounded native/WPT repair, with independent source review and fresh root formal replay. Signed commits remain pending.

## Failure and cause

An ordinary 600px outer flex row reallocates 100px between a fixed sibling and a flexible inner row. The inner item keeps a 100px content width, while its 10% block-start padding changes between 50px and 40px. First/last baseline alignment remains one generation behind. Both release and the unchanged project build reproduce four failures among eighteen calibrated cases.

`CachedBAxisMeasurement::Key` omitted resolved border/padding. A clean item can therefore reuse a measurement after its containing-block inline size changes while its content size remains fixed. The later final-reflow padding check does not repair the earlier baseline placement. The original discovery did not instrument the cache-hit branch; causal attribution combines this source path with the focused repair's paired result.

The repair adds actual reflow-input logical border/padding to the key. Default equality compares all four sides. This preserves the old decision whenever those values are unchanged and rejects changed values before measurement reuse. It does not claim that equal keys prove arbitrary provider freshness. Storage grows by one logical margin per cached measurement; performance neutrality is not established.

## Runtime and source gates

- Identical new 18-case WPT: baseline 14 PASS / 4 FAIL, candidate 18 PASS. Four failures are first/last baseline with percentage-padding shrink/grow. All 14 old passing status/message pairs remain unchanged.
- Final formatted build: 9 files, 20 subtests, 2 OK harnesses and 7 reftests all pass. This includes existing dynamic inline-size, percentage-padding and separate-baseline-group tests.
- Both initial and final build processes exit 0, with zero compiler warnings. Existing mach monitor KeyError for export remains explicit in full logs.
- WPT lint exits0. The first attempted `mach wpt-lint` command was unsupported; the actual successful gate is `mach lint --linter wpt`.
- Formatting changes only the new initializer's line wrapping. Initial paired source and final formatted source are separately pinned and tested.
- The exact two-file Gecko/WPT patch applies and reverses on HEAD and retained upstream 976279105b2e78b8666a959eb3f25c9176cefaf8 using disposable indexes. The complete original measurement class is byte-identical on both bases and the pre-repair shared tree. No isolated upstream build/browser was run.
- The real staged roster and HEAD remain unchanged. No new build target directory was created; temporary indexes were removed.

`check_results.py` independently recounts raw WPT events, exact failure identities, unchanged controls, final results and source/test pins. `STANDALONE.json` and `UPSTREAM-STANDALONE.json` record patch application checks. The native patch contains only `nsFlexContainerFrame.cpp` and `flexbox-baseline-percentage-padding-resize.html`.

## Formal/discovery attribution

The F11 cache/provider audit generated the missing-input hypothesis. Browser tests established the observable bug. The separate Lean companion is verifying the cache-key refinement and the bounded baseline witness; it does not prove all of flex layout, dirty-event coverage, provider callbacks or cache lifecycle. Root replay checks 14 exact theorem audits, 640 cases in each original/candidate debug, optimized and UBSan run, four rejected model claims and two discriminating compiled class mutants. Independent native/WPT review found no blocker. Acceptance is recorded in ../css-flex-padding-key-root-review-v1/ACCEPTANCE.json. No security claim or full cache-freshness proof is made.
