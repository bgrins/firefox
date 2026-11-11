# Scoped runtime gate reassessment

**An optimized real native build plus a focused, baseline-matched CSS/SMIL comparison can support bounded local acceptance of this clip patch, with debug coverage explicitly unrun.** I found no concrete changed assertion-sensitive path that makes a debug build a prerequisite for that scoped decision.

This addendum supersedes the blanket sentence “Debug/assertion coverage remains necessary” in the original independent REPORT.md. That sentence was broader than the clip-specific evidence supports. The original report and proof sources remain unchanged. This does not alter the separate missing-pseudo composition extraction's own gate.

## Source-specific assessment

- The C++ SMIL change only renames the two FFI calls. Its type/count/array-length assertions, zero finalization, wrapper updates, result assignment and loop order are unchanged. There is no new traversal, lifetime, frame, cache or effect-bookkeeping path.
- The actual evaluation-order change is that later rectangle components may run after an earlier auto. Those components are the concrete LengthOrAuto/CSSPixelLength/f32/f64 chain already inspected. Scalar weighting, min/max and casts introduce no assertion or new caller-state premise. The existing derived variant guard returns Err on discriminant mismatch.
- The derive macro does contain an existing `debug_unreachable!()` catchall. It follows the unchanged discriminant-equality check and same-variant match arms. The two-variant LengthOrAuto type has both same-variant arms; the relocation does not create a route to that catchall for valid values. Its presence is not evidence of a changed debug-only failure path.
- AnimationValue.animate has an existing property-tag mismatch panic and unsafe tag-preserving payload construction. Both precede or surround the same property-specific operation as before. No argument/property tags or representation types change. Successful Clip(Rect) construction with auto components already occurs through interpolation, while numeric arithmetic uses the same scalar representation. The patch introduces no new variant shape or invalid index.
- The SMIL final guard only reads enum/component tags and still returns null before Arc allocation for rejected rectangles. Generated binding/type and link correctness must be checked by the real native build, but an optimized build performs those checks too.

These points do not prove the entire native stack free of assertions, undefined behavior or unrelated defects. They explain why no identified **change-specific** concern demands debug as a blocking prerequisite here. A new debug-only crash or counterexample found later would still require investigation.

## Bounded acceptance conditions

Use the exact reviewed patch and a real optimized build that regenerates the renamed FFI declarations and links their C++ callers. Compare exact callback identities/results against the corresponding baseline for the focused CSS addition/accumulation/iteration cases and the existing/added SMIL from-by, from-to, repeat, sandwich and zero-finalization paths. Expected CSS improvements should occur; existing SMIL behavior and unrelated baseline outcomes should remain unchanged. Reject unexplained crashes, missing callbacks, infrastructure failures or new behavioral failures. Keep source/binary association and restoration receipts for a reversible experiment.

The universal Lean result remains supporting evidence for pure/total result equivalence and preservation of arithmetic admission, including count zero. It does not replace the real build or runtime comparison. Conversely, the absence of a debug build need not prevent accepting this narrow source change after those bounded gates pass.

Report the following as coverage limits, not completed work: no debug/assertion run, no sanitizer run, no native count-zero API test, no exhaustive numerical/IEEE or browser-release verification. The direct count-zero admission remains supported by source inspection and the Lean model; ordinary first-iteration SVG sampling does not execute that low-level branch. Optional broader debug testing may add confidence but is not a newly justified mandatory gate for this patch.

No runtime result is claimed by this reassessment. It changes the scoped acceptance criterion, not the frozen candidate bytes or observed test status.
