# Standalone hidden-flex invalidation review

## Recommendation and status

Recommend the **single addition of `MarkPrincipalChildrenDirty()` immediately before the existing hidden `ReflowChildren` return** as the minimal candidate. Do not combine it with the miss-only direct `AddStateBits` patch. Source applicability is verified; final native acceptance remains pending uninstrumented WPT/regression evidence and the focused boundaries below. The earlier direct-item Lean proof does not prove this candidate.

The defect is preexisting: the separately sealed installed-Firefox158 probe has 12 wrong stages across eight configurations using sibling-induced computed-size changes, including clean queried descendants. That evidence is independent of the added padding/containing-block key fields. The shared-tree traced experiment reports 400 correct stages for the subtree candidate, versus four remaining descendant failures for the direct-bit candidate. This review relies on the separately authenticated reviews of those records; it does not rerun browsers or equate traced success with final uninstrumented acceptance.

## Exact standalone source delta

`SOURCE-ROLES.json` records read-only Git extraction of committed branch `209dc941c40a5e0b34724bdac38b607b1f67dda6` and upstream `976279105b2e78b8666a959eb3f25c9176cefaf8`. Both have the same hidden-return seam. `APPLICABILITY.json` records zero-fuzz forward/reverse patch application in artifact-only disposable trees with exact resulting bytes.

| Role | Original SHA-256 | Candidate SHA-256 |
|---|---|---|
| Committed branch | a4ebad4b40076d3aea3ef9d48f9d84357d93ad3784c29b93bb6e9dbb9603ae98 | 83c646378ba60da82d6501bb94089532992a9ecf1bdc20258c7ea28ee48ff3f5 |
| Pinned upstream | 3a7fe90d495e15b1b92a0cb59cb3a993996891b9faddebbe99ed4c8baa4e88b6 | e11261c04c2b4c8eda15a016cda1f4f64cfa20b88cae0cf893fbe797cb497cac |

There is **no source dependency on fix98 or fix101**. The upstream candidate leaves the original four-field measuring key unchanged. The complete relevant helper bodies are identical in branch/upstream nsIFrame.cpp; declarations and state-bit documentation are retained. `ROOT-VARIANT-TRANSFER.json` independently authenticates the proposed four runtime variants: the branch candidate is byte-identical to this review's result, and both key-stripped variants' complete `Key` declaration/constructor/operator match upstream. That is not an entire-upstream runtime equivalence claim.

Use the already reviewed 48-case `hidden-flex-item-measuring-reflow.html` from `css-hidden-geometry-release-key-review-v1` (SHA eb312bfbbc11a7be47fd9b77693ccab938b464d68a64c1ef5f5f1559339fa842) for a two-file native+WPT landing package. It uses original-field shrink cases, not only fixed-size cases exposed by the new key. The supplied patches here contain only the native one-line delta; final two-file packaging/format/lint belongs to root's later gate.

## Why this seam

The source performs measuring/layout construction before `ReflowChildren`. The hidden return skips both final reflow and movement, and later skips placeholder reflow in that method. Therefore a cache hit cannot prove final geometry or placement current. Dirtying actual principal roots covers those skipped ordinary children and their descendant lists independently of measuring-cache outcome. It preserves the existing forcing API instead of changing equality or removing a required key input.

`MarkPrincipalChildrenDirty` visits the actual principal list. `MarkSubtreeDirty` sets the visited root dirty and traverses all child lists with an explicit stack. It neither follows arbitrary continuation links nor a placeholder's external out-of-flow target. It does not delete caches, change keys, invalidate intrinsic sizes, invoke reflow or schedule a new reflow itself. Ordinary later dirty-sensitive measuring/final-reuse checks will require work.

The native dirty-bit contract requires reflow of descendants; it **does not guarantee every descendant carries a dirty bit**. `MarkSubtreeDirty` returns immediately for an already-dirty root and prunes already-dirty descendants or table-column groups. Thus unconditional clean-leaf query eligibility is not derived. The one-line call improves the demonstrated clean-root route; actual producer/history invariants and representative already-dirty histories remain obligations. Adding the direct-bit miss patch first would itself create the problematic dirty-root barrier and is not recommended.

This operation is before any local final-child pointers/caches are captured in `ReflowChildren`; its helper only walks frame lists and sets bits. No new synchronous callback or property deletion is introduced by the call. It may traverse newly visited descendants and make later measuring/final-reflow cache checks miss. Repeated skipped parent work can re-mark previously cleaned subtrees; no performance-neutrality claim follows. Repeated direct queries without intervening changes should retain stable geometry and avoid unnecessary repeated forced layout, as the existing forcing path intends.

## Native and normative boundaries

The exact branch/upstream guard is preserved; no indexed-source `!GetNextContinuation()` condition is imported. Current fragment principal children are marked, not other container fragments' detached/overflow lists. Normalization/drain and later overflow/absolute-frame processing remain unchanged. A positioned frame actually in a visited descendant list may be marked, but container-owned absolute lists and external placeholder targets are not covered merely by the principal traversal. These are reasons for controls, not established new defects.

CSS Containment permits skipped rendering but geometry APIs still require their ordinary results. Its hidden-content example explicitly forces previously skipped layout for a descendant bounding rect; CSSOM View obtains the bounding rectangle from the element's generated boxes. These support the unchanged exact-size/reference oracle, not a specific dirty-bit algorithm. Verified current primary sources: [Containment restrictions](https://drafts.csswg.org/css-contain-2/#cv-notes), [example](https://drafts.csswg.org/css-contain-2/#cv-examples), and [CSSOM bounding rect](https://drafts.csswg.org/cssom-view/#dom-element-getboundingclientrect), accessed 2026-10-20. The Containment editor's draft identifies 15 October 2026. No painting/visibility semantics are changed by the proposed bit marking alone.

## Concrete acceptance gates

1. Run the identical 48-case WPT with all 240 phase observations collected before assertions: direct/nested, prepend/append, hidden/visible, shrink/no-shrink/zero-sibling, bounding/offset. Keep outer-parent flush and separately constructed visible references. Preserve 0×0 direct and stale100×32 descendant baseline failures; no expected-value relaxation.
2. Run all four proposed phases on exact committed native sources: full-key baseline/candidate and original-key baseline/candidate. Candidate improvement must hold in both key regimes. Caption/padding tests that depend on removed key inputs are expected to fail in both original-key phases and must be reported, not silently omitted or forced green. This isolates cache-key independence but is not an isolated-upstream build.
3. Add a **position** observer: for prepend/reorder with unchanged target size, compare target-minus-container coordinates against a separate visible reference. Size-only controls cannot discriminate skipped movement. Include first/repeated query, removal and show restoration.
4. Exercise nested hidden wrappers, a dirty-parent/clean-leaf history through public DOM/style operations, an anonymous flex wrapper, and positioned descendants/placeholder cases. Compare against visible references and preserve no-change controls. A public fixture does not by itself prove a particular native dirty-bit state; source tracing is needed if interpreting its cause.
5. Include a multicol/continuation getClientRects control and show/hide restoration. Do not flatten the fragment union into one arbitrary expected box.
6. Existing regression roster should include content-visibility-040.html (hidden flex/abspos painting), content-visibility-068.html, -070.html, -072.html, -088.html (geometry/forcing), and content-visibility-layout-containment-001.html, plus the retained caption/padding repair tests. Searchfox discovery logs are retained; running all content-visibility tests is also a reasonable root gate. This review does not infer pass status from absent metadata.

The full arbitrary frame/callback/cache-lifetime and allocation F1–F16/F11/F12 obligations remain open. The successor proof should explicitly retain dirty barriers, table groups, continuation ownership and out-of-flow exclusions rather than assuming their desired closure.
