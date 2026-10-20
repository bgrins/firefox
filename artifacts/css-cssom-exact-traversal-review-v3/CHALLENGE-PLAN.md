# Independent v3 review checks

The final review waits for the producer seal. Initial inspection found no candidate-native blocker in dispatch or SafeAdd sequencing.

Required provider correction before final replay: the draft facade exposed separate `svgText` and `states` fields, with `HasAnyStateBits` merging them but `IsInSVGTextSubtree` returning only `svgText`. Native `IsInSVGTextSubtree` reads the actual state bit. Set the facade accessor to that source expression and retain a bit-only SVG_TEXT case; otherwise the combined-mask equivalence holds only under an unstated representation restriction. This is a calibration-provider issue, not evidence of a native defect.

Review the three specializations independently:

- Null output always selects legacy arithmetic/stopping/provider order.
- Common-layout selection requires nonnull output, empty flags, both layout viewports. It does not imply SVG/context/target eligibility.
- All remaining metadata calls select generic wide traversal and retain IgnoreScrolling, visual-root and stacking/display-port behavior.

Each SafeAdd pair commits both temporary results only after both checks succeed. Failure of x short-circuits a pure local y operation; neither partial state nor overflow output is consumed before restarting with null metadata. Signed32 mixed-APD narrowing and the exact scale provider are unchanged. Raw state at every continued loop/flush point represents valid v2 CheckedInt values.

After authenticating final inputs, run the closed original/v2/v3 replay plus independent combined-flags/viewport comparisons and both-axis/negative-wide/final-clipping cases. Treat signed64 state injections as guard checks, not constructed native frame histories. Reuse immutable prior v2 source/runtime reviews as evidence; do not transfer their browser timings to v3.
