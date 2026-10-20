# Source-only next direction

Investigate returning exact app-unit translation information from the **existing transform traversal**, rather than performing a speculative full ancestor walk before that traversal.

The retained `GetTransformMatrix-source.txt` is the exact method extracted from the same nsIFrame.cpp identity pinned by all six runs. Its ordinary-frame branch already walks until the requested ancestor or a potentially transformed frame, accumulates an app-unit offset, and finally converts that offset to float pixels for a translation matrix. Its own comment explicitly avoids walking the same parent chain twice. The new helper duplicates this work when a transform occurs near the root. The benchmark's branch-dependent direction agrees with that source structure.

A possible successor is an opt-in result carrying a checked exact app-unit translation and an eligibility bit alongside the ordinary matrix result. The root-relative CSSOM consumer could use that exact translation only when the whole relevant route reached its target through the admitted same-context, ordinary, layout-viewport path. On encountering a transform or another excluded boundary, it would continue the already-required matrix processing without restarting from the original frame. Keep other matrix consumers on their current API behavior unless explicitly reviewed.

This is an architecture proposal, not a patch. A concrete implementation must preserve these obligations:

- Checked integer accumulation and final rectangle bounds, including dimensions and endpoints. Existing unchecked nsPoint additions are not a new arithmetic proof.
- Same-context ancestry, target-relative stopping, SVG/text/outer-frame exclusions, cross-document APD changes, requested viewport, zoom/APZ, scrolling/sticky flags, perspective, and existing clipping order.
- Exact normal-route geometry without inferring eligibility from a matrix that merely happens to be identity or translation. Real CSS transforms and cancelling transforms remain meaningful source paths.
- Fallback matrix construction and segment rounding/composition unchanged for excluded routes. Carrying a partial offset into a differently grouped matrix is not automatically equivalent.
- An opt-in mechanism whose extra per-frame checks and API surface do not move the cost onto all GetTransformMatrix callers. The design requires its own source review, correctness tests and bounded timing check.

A cheap cached 'has transformed ancestor' predicate would need lifecycle/invalidation proof and still would not establish the other exclusions; no such predicate is assumed here. Calling GetOffsetTo after a separate eligibility scan likewise retains a duplicate walk and lacks this helper's checked bounds. Simply capping scan depth could reduce wasted work but leaves exact-geometry correctness dependent on DOM depth, so it is not the preferred repair direction.

No source change, new benchmark campaign, or acceptance is authorized or performed by this note.
