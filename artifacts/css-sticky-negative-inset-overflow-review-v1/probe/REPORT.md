# Large negative sticky insets: arithmetic overflow lead

Runtime-confirmed new lead; no accepted repair or native commit yet.

Both installed Firefox 158 and the current shared development build reproduce exactly the same 60 observations: 24 mismatches and 36 passing controls. Every fixture calibration passes. Two very large negative opposing insets cause a sticky target to move 200 pixels from its ordinary position. The tree is small: 100px scrollport, 1,000px containing block, 200px spacer and 10px target. Both physical axes and scroll offsets 0/100/400 are covered. Smaller negative pairs and one-large/one-small negative pairs are controls. Binary, XUL, source and fixture hashes are stable within each run; temporary private profiles are removed.

The CSS positioned-layout rule expands the sticky view rectangle for negative insets. In these fixtures the ordinary position remains within that rectangle and the containing block, so no sticky offset is required. Each row compares with a separately measured static-layout fixture and validates dimensions, scroll distance and the static position. Spec: https://drafts.csswg.org/css-position-3/#stickypos-insets (read 20 October 2026).

## Discovery attribution

Reviewing the H1/H2 formal caller model revealed that its numeric-domain predicate checked only the requested coordinate, although native helpers evaluate both coordinates. Independent kernel counterexamples and extracted-C++ UBSan witnesses establish that verification gap in css-sticky-insets-proof-root-v2. One witness keeps all port/inset inputs in the ordinary nscoord range. That prompted this separate browser probe. This is a verifier/review-guided discovery followed by runtime confirmation, not a theorem that proves Firefox has an observable defect.

## Source hypothesis and repair requirements

ComputeStickyLimits computes the view extent using signed32 subtraction and the sum of opposing offsets. Two sufficiently negative insets can overflow the view extent. Widening only that calculation may still leave a second issue: the origin-plus-size mStick rectangle cannot represent a very wide valid interval, even when both endpoint coordinates fit. SetBottomEdge/SetRightEdge subtract the near edge when storing the size.

A candidate must preserve endpoint geometry through normalization, limit construction and each caller. Investigate wider intermediate arithmetic and direct edge storage; do not silently clamp away valid movement or assume a passing normalizer fixes the rectangle representation. H1/H2, positional finite-sentinel and explicit-auto-alias repairs must remain independently packaged. Existing source snapshots and proof contracts remain immutable.

No security/exploitability claim, native fix, WPT acceptance or standalone applicability claim is made here. Next: a standalone WPT baseline, source/representation review, independently packaged repair, paired runtime regression and a formal arithmetic companion.
