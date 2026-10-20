# Independent committed-source hidden-flex isolation review

## Verdict

Accept the bounded isolation evidence. Authenticated all 56 payloads against the supplied FILES hash, independently reconstructed the closed 32-configuration/160-stage result, and checked historical restoration receipts. No tests, browser, build or Git operations were rerun.

All 160 raw stage records equal the earlier working-tree project result. There are 32 failing stages and 128 matching stages. Every failure is a flex append or append-again stage, across both column settings, both initial visibility settings and all four query APIs. Each failure returns 0×0 (or a single 0×0 client rect); all three repeated reads agree. Block controls and the initial/hide/show stages match 24×32. This independently checks all repeated reads, not only the driver's first-read classification.

Replacing all 20 retained dirty native files with their committed HEAD versions therefore did not remove this fixture's failure. This does not identify which accepted commit contributes, prove the same exposure on upstream, or establish a correct repair. The separate release shrink fixture and the four-variant trace have distinct roles and are not promoted into this experiment's results.

## Source/build/restoration joins

The driver checked each retained head snapshot against `git show HEAD:path` before installing it, and checked no tracked layout/dom/servo diff after building. Each of those 20 source snapshots matches the browser's before/after source hashes. The probe additionally pins DOMRect, nsLayoutUtils and nsIFrame source pairs, executable and XUL, tests, runner and INPUTS; before/after dictionaries are identical. The five extra source files were not mutated by this driver.

BEFORE and FINAL match exactly: HEAD dbfb428e2134fff1a4ef73f48438481b4eb6438f, complete index-entry hash, empty cached-diff hash and all 20 original source hashes. Both build logs report success and terminal STATE records build/probe/restoration exits 0/0/0 with no recovery errors. The logs retain build-monitor KeyError export traces and compiler warnings; these are not silently omitted or treated as compile failures. The browser return code −15 is the runner's deliberate termination after receiving the complete result, not a crash inferred from a missing callback.

This establishes source restoration followed by a successful rebuild. It does not claim a bit-identical restored XUL image; the restored binary hash is not part of FINAL. Current live files are deliberately not compared while the subsequent four-variant experiment owns them. Historical receipts are the relevant evidence.

## Scope

No new native acceptance, security claim, full hidden-layout invariant, or general cache freshness/lifetime result follows. The source hypothesis predicts that a clean hidden measurement miss can commit zero size while remaining clean; the separately running trace is needed to establish actual key values and execution. Dirty-on-miss and skipped-child subtree marking remain diagnostic variants until that experiment and focused residual controls complete.
