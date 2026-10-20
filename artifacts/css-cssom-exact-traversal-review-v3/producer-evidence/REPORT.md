# Exact rectangle traversal: specialized implementation

Status: **ARTIFACT_PROPOSAL_PENDING_INDEPENDENT_REVIEW_AND_FULL_BUILD/PERFORMANCE**.

This successor preserves the v2 arithmetic/geometry contract while specializing invariant traversal choices. It has not been applied to the shared tree, built as Gecko, run in a browser or benchmarked. The parent's v2 browser/build success and timing hold motivate this work; they do not establish v3 behavior or speed. Main source, Git/index and shared build/browser state were not touched.

## Source candidate

`proposal.patch` is the four-file standalone change against the retained pre-v2 originals. `v2-to-v3.patch` is the smaller implementation delta: only nsIFrame.cpp changes from v2. The carrier definition, both public signatures, GetTransformToAncestor metadata handling, exact rectangle wrapper, self-identity case, BoxToRect opt-in and cached fallback are byte-identical to v2. Original, v2 and candidate full snapshots are pinned in CANDIDATE-PINS.json. Both patches apply and reverse byte-exactly in private temporary directories.

The ordinary portion of GetTransformMatrix has one traversal definition in a local generic lambda. A single dispatch selects:

1. Null metadata: original signed32/nsPoint arithmetic and flags behavior.
2. Requested metadata, empty flags, layout source and target: checked signed64 arithmetic, direct GetPosition and IsTransformed stopping.
3. Other requested metadata: checked signed64 arithmetic and the original complete flags/viewport stopping logic.

The source transformed/zoom early branch is unchanged. Common-layout specialization is selected only when its three predicates hold; it is not the eligibility predicate for an exact result. Context, SVG, parent, reached-target and APD checks remain. Target equality is still checked before transform stopping, preserving exclusion of the target's own transform.

Four raw signed64 accumulators replace CheckedInt objects in the wide modes. Each addition uses public mozilla::SafeAdd, backed by the same checked-add builtin as CheckedInt. All overflow failures and mixed-APD narrowing failures return through the existing null-metadata restart. Each pair uses temporary outputs and commits them only after both checks succeed. No signed addition is executed unchecked, no accumulator is clamped and no tree-depth bound is imposed.

The two SVG state checks are combined into one mask. Source PresContext is saved once; every previously checked ancestor is still compared against it. Parent-shell assertions were not promoted into a reason to delete those comparisons. Default callers' loop instantiation has no per-iteration metadata-mode branch or checked64 operations. Whether this produces faster machine code remains unmeasured.

## Preservation argument and boundaries

At every reached wide loop head, v2's CheckedInt accumulators are valid: initialization converts signed32 exactly, every addition is checked before the next step, and APD flush failure returns immediately. Replacing persistent validity state with SafeAdd therefore preserves every successful arithmetic value and failure decision. On x failure, v3 may skip a second pure local addition that v2 evaluated; no frame/provider call is skipped. On y failure, v2 may have updated a private x accumulator while v3 has not committed it; both immediately abandon this local state through the same restart. Neither difference can publish metadata or affect fallback inputs.

The old-defined matrix argument is unchanged: null mode keeps the original operations; wide modes preserve the same docOffset grouping, APD flush order, signed32 scaling inputs, ancestor choices, final integer-to-float cast/divide and matrix composition. At differing APD, the actual nsPoint::ScaleToOtherAppUnits API remains the provider. No alternative rounding formula was introduced into native source.

The full v2 checked-exact domain is retained, including cases outside v1's signed32 rectangle-prefix filter. The existing example rect.x=1,000,000,000 with positions+1,500,000,000,-2,000,000,000 still returns exact500,000,000. Both wider carrier requirements remain: docOffset2,800,000,000 with final800,000,000, and translation2,500,000,000 with rect.x=-2,000,000,000 and final500,000,000. No additional prefix filter was added to pass timing.

The prior numeric nine-result Lean component justifies signed64 capacity on v1-admitted prefix differences; v3 does not introduce or claim a new kernel proof of native traversal. Its source-preservation argument extends over successful signed64 v2 states, not just that narrower sufficient domain. Stable frame/context lifetimes, getter purity, real graphics/SVG/viewport providers and full caller/header integration remain the same admissions as v2.

The existing numeric restart can execute legacy undefined arithmetic outside the old-defined and admitted exact domains. The cross-document/APD witness deliberately retains this UBSan outcome in original, v2 and v3. This patch is not a universal arithmetic-safety repair or a new recovery policy. No invalid or discarded exact state can recover on a later segment.

## Extraction and checks

The closed capsule extracts complete original/v2/v3 GetTransformMatrix and GetTransformToAncestor methods and the actual exact wrapper. It uses the retained Mozilla CheckedInt/CheckedArithmetic headers. The frame/context/viewport/legacy rectangle providers are facades; the matrix models limited affine behavior with an operation trace, not actual full 3D Gecko GFX. ScaleToOtherAppUnits is a facade for calibration, not execution of its production implementation. These limitations prevent a full provider/caller proof claim.

Canonical and manifest-only relocated replays each compile20 variant/optimization combinations at O0/O2 with UBSan. Expected outcomes include:

- Original, v2 and v3 agree on168 old-defined matrix values, operation traces, ancestor results and method-entry counts per optimization. Modes include null and requested metadata, empty and three nonempty flag values, layout/visual routes, transformations, SVG, context transitions and APD29/61.
- Frozen v2 and v3 complete normal stdout agree, including2,048 v1-admitted generated chains, expanded-domain example, exact self case, wide cancellation, clipping/cache and stale-metadata controls.
- Original UBSan failures on the two wide-domain witnesses become successful exact results in both v2 and v3. Cross-document restart remains an explicit expected UBSan negative in all three roles.
- Eight injected boundary states per optimization in both v2 and v3 test positive/negative signed64 doc/offset overflow on x/y. Each clears metadata, restarts once and returns the ordinary null-path result. The injection replaces a private accumulator only in this test mode; it does not claim those states are reachable from the small frame fixture. Normal and generated-domain runs leave the injection disabled.
- Seven semantic mutants are rejected at both optimizations: wrong exact translation, removed SVG exclusion, removed empty-flags eligibility, dropped cached fallback, dropped self identity, wrong specialization dispatch, and suppressed doc-x overflow detection. The last mutant deliberately passes normal cases and is killed by positive/negative injected x-overflow controls.
- Seven guards reject wrong external pin, extra cache, changed source, output inside capsule, optimized Python, nonisolated Python, and a resealed wrong compiler-driver pin before compiling or creating output. The last control reaches the driver-pin check after authenticating its altered test manifest.

Independent review caught an initial facade representation omission: HasAnyStateBits included the svgText boolean in its mask while IsInSVGTextSubtree returned only that boolean. A states-only SVG_TEXT value could then violate the actual native accessor identity. The final facade uses the exact native IsInSVGTextSubtree body calling HasAnyStateBits, and an explicit states-bit-only control requires cached fallback. First development source/replay evidence and this correction are preserved; the native candidate did not change because of this correction.

Instrumentation adds a method-entry counter, stderr restart marker, and the conditional accumulator seed described above. Method-body hashes are recorded before instrumentation. Mutation changes are checked before instrumentation, so instrumentation cannot make a no-op mutation appear effective. The installed compiler driver hash/version was checked; external backend/SDK/standard-library state remains admitted.

## Handoff

Run the outer verifier with its externally supplied FILES hash. For a fresh native extraction replay:

```
python3 -I -S -B capsule/replay.py --files-sha256 993dde69e30ebadf821bafb8587baba61f010bfc537600fad61a0839652db5eb /tmp/NEW-UNUSED-OUTPUT
```

The capsule is closed and authenticated before output creation or compilation. Existing four-case standalone WPT identity is retained in WPT-REFERENCE.json. No test oracle was relaxed. Changed method ranges were formatted in the artifact; this is not a main-tree lint/full build.

Next gates are independent source/replay review, parent-owned reversible full compilation and established browser checks, then the focused timing campaign. Three generated traversal variants could increase code size or fail to improve inlining. Public SafeAdd already underlies CheckedInt, so this change must not be advertised as a new cheaper arithmetic primitive. No v3 performance or native acceptance claim is made.
