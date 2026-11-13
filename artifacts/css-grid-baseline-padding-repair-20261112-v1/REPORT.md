# Repeated baseline padding on non-root reflows

The local three-file native repair corrects all 28 failures in the 120-case WPT
and preserves 92 passes. All 120 cases pass on the rebuilt browser. The three
existing grid reftest outcomes are unchanged: one PASS and two metadata-expected
FAILs, with both failing screenshot pairs byte-identical by their report hashes.
The candidate remains applied and built, uncommitted pending signing.

PresShell's non-root DoReflow initializes ReflowInput from current used padding.
That cache already includes grid content-baseline padding. InitOffsets previously
added the contribution again, progressively shifting contents and reducing their
reported content size during repeated descendant edits. The opt-in
PaddingIncludesBaseline flag identifies that supplied snapshot. InitOffsets
recognizes it only when the explicit padding override wins acquisition and
suppresses only the numeric addition. Property lookup, padding-cache policy and
block-size state bookkeeping remain intact. PresShell removes the flag after
Init; ordinary parent/child inputs retain their existing behavior.

The standalone candidate.patch contains only LayoutConstants.h, PresShell.cpp,
ReflowInput.cpp and grid-baseline-content-reflow-root.html. It applies and reverses
exactly against HEAD without the other uncommitted fixes. The WPT covers first
and last baseline, five containment modes, three writing modes, both directions,
two peer font sizes and four repeated edits. No new failure metadata is added.

## Validation

- baseline-v3: 28 FAIL / 92 PASS, harness OK; owned groups absent.
- build: mach build binaries -j2 exits 0 at 621284; XUL identity changes and all
  installed candidate hashes match. Mach emitted export-tier monitor exceptions
  and unrelated compiler warnings; the native build nevertheless completed and
  the resulting binary was used for the following runtime checks.
- fixed: 120 PASS, harness OK, terminal 749be7; all control outcomes retained.
- targeted mach WPT/clang-format lint: 0 problems, terminal 9d702f.
- standalone patch application/reversal against HEAD: 529e35.
- retained verification: fe1391; verify.py checks source identities, command
  outcomes, matching case names, binary linkage and unchanged control outcomes.
- native/test source review:../css-grid-baseline-padding-final-patch-review-20261112-v2.

The first baseline attempt used test after promise_setup and failed at the
harness level; its original source and error remain retained without bug or
regression credit. The corrected extended baseline-v2 additionally exposed a
separate parent peer-font discrepancy. That entire test/report is retained;
the focused bugfix test restores the original child-edit assertions using the
correct asynchronous harness. It does not hide or claim to repair the parent
issue. A separate installed-Firefox158 probe confirms that issue independently.

The feedback model in ../css-baseline-padding-feedback-model-20261112-v1 proves
ten reviewed scalar history obligations and a concrete old-transition violation.
It is supporting mathematical evidence, not a universal native refinement proof.
This defect was found through source/cache analysis while developing the formal
work and reproduced in the browser; Lean did not autonomously discover it.

Suggested relative priority is P3: progressive visible mislayout at ordinary
sizes, requiring baseline content alignment plus layout/size containment. No
security impact is established. Theme/SVG-specific runtime paths, complete
native refinement and the separate wide padding/geometry work remain outside
this repair's validated scope. Tooling and model artifacts belong in preceding
commits; the native/WPT patch remains independently reviewable and landable.
