# Sticky negative-inset arithmetic repair candidate

Status: native/WPT candidate passes; independent review and formal companion pending. No native commit or acceptance-count increment.

The exact 60-case WPT improves 24 FAIL/36 PASS to 60 PASS. Every failure in the baseline occurs at the final position assertion, after checking actual scroll, all fixture sizes, computed position/non-auto sides and the static reference. The 36 other status/message pairs are identical. Only the two native files and browser/XUL pins differ between paired runs. The new build succeeds with zero compiler warnings. Scoped native formatting and WPT lint both pass. Existing regressions pass 1,408 subtests and three reftests, including all pending sticky repairs and the explicit-auto-alias WPT.

## Changes

The view extent and normalization delta now use signed64 intermediates. StickyLimits::mStick uses nsRectAbsolute, storing near and far edges directly rather than subtracting them into a signed32 extent. The initial sentinel edges are preserved, position callers use edge accessors, and GetScrollRanges consumes the already-absolute stick rectangle. Containing-block geometry remains the existing nsRect pipeline.

A wide view is valid for very negative opposing insets. Merely widening normalization would leave potential overflow in SetBottomEdge/SetRightEdge when an interval's endpoints fit but their difference does not. This candidate handles both representations. Input-to-result bounds, original-field versus effective-field source variants and the changed range observer must be reviewed, not inferred from the passing matrix.

## Independent packaging

fix-candidate-v1.patch contains exactly StickyScrollContainer.cpp, StickyScrollContainer.h and the new WPT. It applies and reverses exactly on current HEAD and retained upstream. H1/H2, geometric-sentinel and explicit-offset repairs are excluded. package.py records the explicit source adaptation: upstream normalization reads computedOffsets, while the combined worktree reads effectiveOffsets; the same widening is applied to the operand source in each version, preserving the surrounding activation and end-side policy. This is source-only standalone evidence, not an isolated upstream build or runtime claim. PACKAGING.json records all resulting source hashes and preserves the real HEAD/index/worktree.

## Remaining gates

- Independent native/WPT/source and standalone adaptation review.
- Formal normalization identity, signed64 intermediate bounds and signed32 result-conversion bounds under explicit source-derived input ranges.
- Direct-edge limit construction/query refinement, including intervals too wide for origin-plus-size storage and compatibility where old operations are defined.
- Caller composition for positions and absolute/per-axis scroll ranges, with remaining unmodified geometry and timeline arithmetic admissions explicit.
- Native extraction calibration on genuine before/after source variants, semantic mutation and honest trust/closure controls.

Initial build-v1 failed on two direct x/y field accesses; build-v2 updates those consumers and succeeds. Both logs are retained. Initial lint invocations lacked a separator after the optional warnings argument and did not run checks; v2 invocations are the successful checks. No push, try or signing attempt was made for this candidate.
