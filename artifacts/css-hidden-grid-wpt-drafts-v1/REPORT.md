# Own-hidden grid WPT diagnostic draft

Status: **eight unrun WPT cases; no native bug or candidate acceptance claim**. Separate from the running104-case campaign. Intended future companion to the four auto-scroll drafts.

The source fixture is preserved verbatim in `source/`. Its three payloads authenticate against original FILES `3b995f1ce5f845a61a5e78e7068303d87a79acd1e6e62a8581585b1de95f5ac5`. `SOURCE-AUTH.json` and `SOURCE-TRANSFER.json` describe the transfer.

## Cases and unchanged operations

`hidden-grid-own-content-queries.html` registers visible/hidden × direct-item/leaf-first × bounding/offset:8cases,40stage observations. Proposed installed path: `css/css-contain/content-visibility/hidden-grid-own-content-queries.html`. Only standard testharness resources are needed. `EXPECTED-ROSTER.json` contains the exact ordered subtest names.

The grid itself is the only potentially hidden element. Its parent remains an ordinary visible200px block. A single minmax(0,1fr) grid column and explicit32px row contain the32px item and50%-wide16px leaf. The parent changes to120px without changing descendant styles. Expected item sizes are200×32 then120×32; leaf sizes100×16 then60×16.

CSS bytes, fixture creation, selected target, measurements and operation order match the original. The five observations remain visible-calibration, initial-query, after-parent-width, repeat-query, shown-restoration. Only the parent is queried before the changed selected-target read. Leaf-first fixtures never query the item first. Bounding cases record width/height only; offset cases record offsetWidth/offsetHeight. This deliberately preserves the original size-only coverage.

Shown restoration restores content-visibility:visible at120px; it does not restore the parent to200px. No extra width reversal or geometry read has been added. The wrapper only adds harness registration/assertions, immediate cleanup registration, and global raw records (`window.gridQueryResults`). Cleanup removes the host even on failure.

## Calibration and failure classification

Each case finishes all five measurements before assertions. Initial visible geometry, changed visible parent120×32, and final shown geometry are asserted first and have `calibration` labels. The four entirely visible controls also label all intermediate expectations as calibration. A runtime controller must stop on those failures rather than classify them as hidden-query defects. Hidden intermediate reads are ordinary selected-query assertions and retain their exact observed/wanted data.

No source dirty-bit, measurement-cache or subtree-mark cause is inferred from a size mismatch. There are no flex, table, font, transform, fragmentation or out-of-flow dependencies. The original source lead remains a proposed grid own-content skip path; this artifact supplies tests, not a repair.

## Static validation

Node syntax checking and stub-only test registration pass. `static-check.js` checks exact ordered8-name registration, descriptors, exact CSS bytes and the complete fixture/read sequence after removing the one harness-cleanup insertion and indentation. It does not invoke test callbacks or a DOM. `STATIC-CHECK.json` records the result; `VALIDATION-HISTORY.json` retains one corrected syntax typo in the validation script, not in the WPT.

No browser, native build, production file edit or Git operation was performed. All actual visible calibrations and hidden outcomes remain pending the parent-owned diagnostic run.
