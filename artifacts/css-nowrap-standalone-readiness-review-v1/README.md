This is a strong candidate for a standalone native fix plus WPT, pending one isolated native validation. No concrete correctness counterexample emerged from this bounded review. Requiring a universal CSS/formal companion would exceed what is needed to assess this change; the old FORMAL-TARGET-DRAFT is an unproved research proposal, not evidence that the local repair is unsound.

`fix.patch` changes only `dom/base/nsLineBreaker.cpp` and adds `css/css-text/white-space/nowrap-inline-break-policies.html`. The current native file equals committed HEAD a1e0ffba3651cf27853c33d22bb7b1b5368f658f and the original standalone preimage c8b2d4f7. The candidate remains a87f4210 and the 169-case test remains 3c390a8c. Patch b499d2a2 differs from historical f021b5a4 only in hunk coordinates: the historical patch described a combined worktree and relied on context-based offsets. Exact forward/reverse replay against the current bytes passes without offsets. No language or hyphenation patch is a prerequisite.

The helper applies the existing INITIAL/INSIDE suppression contract immediately before the two final AppendText SetBreaks callbacks. Offset zero has a separately controlled initial position; all other published positions are interior. Empty ranges return before pointer/length adjustment. Buffered FlushCurrentWord already applies this distinction. The change does not alter provider requests, pending text, mode transitions, allocation, cache state, capitalization, or callback ranges. In particular, it does not claim that writing a zero break erases arbitrary stale glyph state; that depends on existing text-run initialization/invalidation.

Saved evidence was independently replayed, not rerun:

| Evidence | Actual result | Limitation |
| --- | --- | --- |
| Exact 169-case WPT | 133 PASS/36 FAIL → 169 PASS; previous PASS and harness signatures unchanged | Both browser roles included other language/hyphenation changes |
| Regression pack | 720 passing subtests + 4 passing reftests + 17 OK endings unchanged | Same combined worktree; not 724 subtests |
| Existing native checks | 840 cases/2259 callbacks; 3840 language cases/24960 callbacks; 262080 bounded helper checks | Authenticated saved reports; not a universal source refinement proof or a new native execution |
| Current artifact checks | Exact patch roundtrip, 169 unique callbacks, genuine WPT manifest, underlying WPT lint zero errors | No new browser/native build |

Minimal remaining work is concrete:

1. Independently review the three native hunks, then build the current clean source and the exact standalone candidate in one reversible paired experiment. Recheck current source hashes after the active unrelated experiment finishes.
2. Run the exact 169-case fixture on both built roles with identical resources/metadata; require complete output, candidate all PASS, and unchanged existing PASS/ending signatures. Calibrated Ahem, normal/keep-all/wrap, allowed initial break, min-content and partition controls are already present. No new probe framework is needed.
3. Run the existing regression pack listed in VALIDATION.json on both roles. Preserve actual clean-baseline outcomes: some unlanded language/hyphenation tests may fail without their separate fixes. Require no regression, not a fabricated clean-baseline count of 724 PASS. The two tracked nowrap/break-all reftests are essential direct controls. Confirm formatter compatibility and lint in the actual publication workflow; this package closes WPT lint only.
4. Publish only the native file and exact WPT after those checks. The WPT already exists untracked with identical bytes and is archived in recovery0197; verify and adopt those bytes rather than blindly applying the new-file hunk over it. Keep unrelated recovered tests and their fixes out of the commit.

Prior issue notes identify bug 1507744 (missing inline breaks) and bug 1549728 (mode-change flushing), both a different failure direction, and original implementation bug 249159. This review preserves their machinery and does not establish a new Bugzilla duplicate or recheck their current issue status. CSSWG issues 3886/3897 and retained-linefeed/ruby/invalidation cases remain broader boundary questions; none supplies a demonstrated counterexample to these three hunks. They do not justify withholding the isolated experiment.

This package is review/patch preparation, not a runnable native owner or an accepted fix. Root's concurrent native13 experiment, source files, index, apps, canonical controls and old sealed artifacts were not modified. SPEC/CHECK receipts identify the evidence and its limits.
