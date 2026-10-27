# Proposed float repair

`proposed-fix.patch` contains one eight-line Gecko addition and two WPTs. It is a proposal, not an accepted fix. It targets saved HEAD `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e` and contains no block-line, column, or Grid repair. Research artifacts belong in a preceding commit; the eventual fix commit should contain only the three paths listed in `BINDINGS.json`.

The Gecko addition marks non-pushed entries in the current block's Float child list before hidden-content line processing. `gecko.patch` is byte-identical to the original reviewed float proposal. The static check verifies forward and reverse application against saved HEAD and float-only bodies, and verifies that composition with the separate block repair produces the exact tested combined body. This establishes source composition, not runtime independence.

| Proposed WPT | Cases | Original-fixture result with all three accepted repairs present |
| --- | ---: | --- |
| `hidden-float-owner-queries.html` | 8 | 4 PASS / 4 FAIL → 8 PASS |
| `visible-float-push-calibration.html` | 4 | 4 PASS → 4 PASS |

The main WPT retains direct and inline-nested floats, root and leaf queries, and visible and hidden states. It preserves the warm/hide/change/show/restore sequence, outer-only flush, repeat query, and fresh visible calibration. Cleanup removes only the nested-block fixture and unused result recording. The four push calibrations retain their assertions and case names; unused global result recording and its extra geometry/style reads are removed. `wpt-cleanup.patch` and `push-cleanup.patch` show the reductions; `PARTITION.json` binds every retained or excluded row to the completed comparison.

The four nested-block cases remain in diagnostic evidence. They already pass in the baseline containing all three accepted repairs; that run does not isolate which repair caused them to pass. The completed 95-case comparison improved from 91 PASS / 4 FAIL to 95 PASS, with restoration successful. Neither cleaned file has been run or linted yet.

## Next checkpoint

1. Use the existing local comparison and restoration machinery for a no-block experiment. Normalize the 24 sources to their saved HEAD roles, omitting all three accepted overlays in both phases. Compare saved HEAD's block body with the float-only body using these exact two proposed WPT files. Require the four hidden improvements and eight unchanged passing controls. Record unexpected outcomes without changing expectations. This directly tests the proposed patch without the block repair or either other accepted overlay. Do not require unrelated block-dependent WPTs to pass when their repair is deliberately absent.
2. Reuse the local cost machinery for direct and inline-nested float owners at bounded sizes, such as 1, 32, and 128 entries. Measure first recovery separately from repeated clean queries and visible controls; check geometry alongside timing. The baseline's stale answer does less useful work, so a slower correct recovery alone is not evidence of regression. Pin source and binary roles and report variance. The float pass executes per `ReflowDirtyLines` invocation, which may recur during reflow; first-mark traversal and worklist allocation remain unmeasured costs.

The helper is iterative, but that does not establish a performance bound for native callers. The Lean model covers selected current-owner roots under stated ownership and dirty-path assumptions; it does not verify arbitrary C++ execution. These visible push controls do not prove native pushed-list membership. Pushed/overflow owners, continuations, and dirty-root/clean-leaf histories remain explicit limits.

No source, test tree, index, build, or browser was changed for this proposal. Only static artifact checks were performed.
