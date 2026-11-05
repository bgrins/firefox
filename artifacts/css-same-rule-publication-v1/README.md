# Same-rule rollback published locally

Fix 0f18d294fbac contains only two Rust files and three WPT changes. Research immediately precedes it in c1209aa91006. It requires the cumulative rollback repair e63fc6b1892b (#163); it is not independently cherry-pickable onto the pre-project ancestor.

In LTR styling, a rule combining margin-left:5px with margin-inline-start:revert-rule could incorrectly retain the 5px declaration instead of falling back to the lower rule. The fix retains the original declaration source across substitution and excludes matching physical-property declarations from that source. See the CSS Cascade [rule rollback section](https://drafts.csswg.org/css-cascade-5/#revert-rule-keyword) and the committed regression tests.

The updated [catalogue](../css-all-work-readout-20261105-v13/README.md) lists this as tier B entry164: wrong styles, without demonstrated crash or security impact. There are163 browser repair entries;120 is excluded,160 remains held, and the generic ArcSlice repair is separate. The synthetic dense-case cost and source prerequisite remain explicit in the assessment; local packaging does not establish upstream or release readiness.

The [committed build](../css-same-rule-committed-build-v1/README.md) is ready at objdir-full.noindex/dist/Nightly.app. Its selected source and binary hashes were rechecked after the actual terminal; build and wake groups are absent and the build lock is removed. All experiment owners are closed. No push, Try run or external submission occurred.

RESULT.json inventories17 pre-existing untracked WPT research probes by hash. They are preserved outside this repair and are not being labeled obsolete. Completed same-rule work is committed; unrelated ongoing probes are not implicitly ready to land.
