# Fixed-position scroll-anchor exclusion: formal companion scope

18 October 2026. Plan only: no Lean proof, native capsule compilation, browser execution or live source/test edit performed here. Root owns the repair and browser gates in `artifacts/css-scroll-fixed-anchor-fix-v1/`.

## Status and intended claim

Root baseline session 94273 exited 1 as expected: the transformed local fixed candidate prevented the expected 100→130 adjustment (observed 100), while four new controls and three existing WPTs passed. The root baseline review reports stable pins. The candidate source adds computed fixed positioning to the existing sticky exclusion in `ExamineAnchorCandidate`. Its build/paired browser gate was pending when this scope was captured; this plan does not accept the final native repair.

The companion should establish candidate exclusion, traversal safety and preservation of unaffected selection, using the **complete** candidate classifier and recursive traversal. A Boolean lemma about `position == fixed` is insufficient. Keep the own-scroller suppression endpoint repair outside this companion.

## Exact code boundary

Extract these complete items from separately pinned original and candidate snapshots with a balanced-token extractor and exact-byte comparison:

1. `ScrollAnchorContainer::ExamineResult` and its four alternatives.
2. `ScrollAnchorContainer::ExamineAnchorCandidate`, including all exclusions, non-replaced/anonymous passthrough, nested-scroller/replaced handling, visibility and continuation precedence.
3. `ScrollAnchorContainer::FindAnchorIn`: child-list filtering, retained list order, and the second absolute-list pass.
4. `ScrollAnchorContainer::FindAnchorInList`: placeholder dereference, proper-ancestor rejection, all four decision branches, early return and fallback.
5. `ScrollAnchorContainer::SelectAnchor`, `CanMaintainAnchor`, and `SetAnchorFlags`, so the actual public selection path reaches the classifier and records the chosen node consistently.
6. `nsPlaceholderFrame::GetRealFrameFor` and `GetRealFrameForPlaceholder` bodies, with their underlying frame fields explicitly adapted.

Retain/authenticate complete provider source for `FindScrollAnchoringBoundingRect`, `FindScrollAnchoringBoundingOffset`, frame ancestry and child-list APIs, plus the PresShell caller. Those geometry/layout providers are not silently replaced by alleged proven native equivalents. The primary native execution comparison may adapt their observations; label every such boundary.

`PresShell::FlushPendingScrollAnchorSelections` calls `scroll->Anchor()->SelectAnchor()` and clears its queue. `SelectAnchor` directly searches `mScrolledFrame` if `CanMaintainAnchor` succeeds; there is no separate focused/find-in-page priority selector in this inspected boundary. Do not claim implementation or proof of the specification's complete priority-candidate algorithm. The priority behavior this capsule must preserve is **native list order, placeholder order, immediate acceptance, descendant preference for Traverse, and fallback**. A retained caller trace is required even if the PresShell queue itself remains outside the executable capsule.

The internal `Frame()` implementation uses containing-object arithmetic. Do not fabricate a C++ object layout to make it appear source-bound. Provide an explicitly documented owner lookup adapter with stable storage and a single lifetime owner. If attempting to extract that function, instantiate actual compatible layout with checked offset and alignment rather than relying on undefined pointer arithmetic. Neither choice proves real Gecko ownership.

## Independent model

Use Lean structures for a finite frame universe, physical frame-parent relation, ordered child lists with native list kinds, optional placeholder target, and candidate observations. Observations include computed position, sticky-frame predicate, overflow-anchor, text/continuation status, chrome/pseudo/replaced/inline/anonymous status, nested-scroller anchor/capability, visible rectangle relation and dirty state. Keep computed sticky position and native `IsStickyPositioned` distinct until their bridge is justified.

Model visibility as independently supplied disjoint/partial/full observations for the structural proof; use exact rational rectangles for a separate bounded adapter oracle. It must be possible to vary visibility independently of position. Never define the oracle's classification by invoking the producer classifier.

Define a specification-level ordered selection interpreter, including the native refinement for anonymous/non-replaced inline frames and native nested-scroll boundaries. Then define the native-shaped traversal independently and prove agreement. Frame traversal is **not simply a tree**: placeholder aliases and the second absolute-list pass can revisit a node. Give recursive descent a well-founded rank, with each recursive child/alias edge decreasing rank; duplicate visits from different siblings or a second pass remain legal. Reject malformed cycles in input validation; do not hide cycle rejection as an assumed result of the theorem. Real frame construction's rank/acyclicity is a bridge premise.

Trace events should distinguish list entry/pass, placeholder resolution/rejection, candidate examination/result, descend, candidate return, traversal fallback and final selection. Identify stable frame IDs, not raw addresses. Keep full traces in bounded comparisons so a right final answer cannot hide an incorrect visitation order.

## Theorem obligations

1. **Fixed/sticky candidate exclusion:** every fixed observation or sticky-frame observation yields Exclude, regardless of later visibility/descendant fields. Earlier exclusions are permitted and should preserve the same result without necessarily producing the same reason label.
2. **Selected-node safety:** under well-founded provider inputs, every non-null result of FindAnchorIn/List has passed candidate examination and is neither fixed nor sticky. Prove by well-founded recursion over the complete four-way traversal.
3. **Excluded subtree barrier:** after Exclude, that invocation never recurses into the candidate. For a descendant whose every reachable traversal route crosses that excluded candidate, selection cannot return the descendant. Explicitly quantify the all-routes premise; do not claim arbitrary DOM-subtree exclusion from a frame-tree model.
4. **Alternate-route limitation:** construct an abstract alias graph where a descendant is also directly reachable elsewhere; demonstrate that a local exclusion alone does not prove the global subtree statement. This is a model boundary test, not a claim that a valid Gecko frame graph permits the specific alias. Bind relevant actual fixed-containing-block ancestry before making the WPT-specific subtree claim.
5. **Non-fixed classifier preservation:** for every observation with computed position other than Fixed, original and candidate classifiers agree. This includes legitimate local Absolute and every Sticky observation.
6. **No-fixed traversal preservation:** if all nodes reachable by either program's provider graph are non-fixed, original and candidate return the same ID and the same semantic traversal trace. This must include the second absolute pass and duplicates. Do not assert preservation merely because the original winner was non-fixed; an earlier newly excluded branch can change traversal/fallback.
7. **Priority and fallback:** Accept returns before later siblings; Traverse prefers a descendant but returns itself if none succeeds; PassThrough never returns itself; Exclude visits neither descendants nor itself. Prove filtered-list ordering and the extra absolute pass, rather than assuming a flattened candidate order that omits fallback behavior.
8. **Public selection bridge:** CanMaintainAnchor=false produces no anchor. Otherwise SelectAnchor stores the traversal result, updates dirty/suboptimal state and performs old/new flag transitions consistently. Offset calculation is an explicit provider result. Selection safety follows through this caller; actual scroll delta and suppression-window behavior do not.

Require arbitrary finite-list/graph-rank proofs, not only bounded enumeration. Audit all theorem axioms, prohibit `sorry`/`admit`/custom unsound axioms, and distinguish definitional helper lemmas from safety/refinement theorems. It is acceptable to prove exact enum/list structure while treating physical geometry as a named parameter; it is not acceptable to relabel parameter assumptions as a full browser proof.

## Bounded native corpus and independent oracle

Begin with a generated truth-table domain covering all decision branches, but require end-to-end graph fixtures from SelectAnchor as well:

- Reproduce the fixed/local witness through both a principal-list placeholder and the containing block's later absolute-list visit; place a fully visible candidate later so exclusion has an observable selected ID.
- Keep the same graph and vary Fixed→Absolute, Static, Relative and Sticky. Legitimate local absolute must still win when otherwise acceptable.
- Fixed parent with an attractive child; sticky parent with an attractive child; nested exclusion inside PassThrough and Traverse; completely excluded branch versus a later sibling; no eligible candidate.
- Placeholder target outside the scroll-frame ancestry; valid local target; duplicate target also in absolute list; skipped Float/OverflowFloats/Absolute first pass; retained Fixed/Principal/other native list IDs according to actual enumeration.
- Accept ahead of better-looking later candidates; Traverse with/without eligible descendants; PassThrough with/without descendants; second-pass absolute candidate only reachable after the first pass fails.
- Text primary versus continuation; non-text continuation; anonymous/non-replaced inline passthrough; replaced and nested scroller atomic acceptance; zero/intersecting/fully visible rectangles; chrome/pseudo, br and overflow-anchor:none; disabled/origin/perspective gates.
- Old anchor same/different/null, dirty descendants, and provider offsets to observe SelectAnchor effects. Keep shared ancestors and duplicate visits legal without permitting recursion cycles.

An independent reviewer reconstructs expected traces from raw fixture descriptions and the semantic interpreter. Compare selected ID, examination decisions, descendant calls, ordering, fallback, final flags/state and provider-call counts where ordering matters. Geometry assertions should avoid all-passing magic values. Keep canonical initial state per run, stable owned storage and initialized output fields; no temporary-backed references or uninitialized semantic mutations.

Mutation controls must compile and run: remove fixed exclusion; exclude all out-of-flow positions; remove sticky exclusion; return PassThrough instead of Exclude for fixed; ignore placeholder ancestor rejection; examine the placeholder instead of real frame; skip absolute second pass; accept Traverse before descendants; return self for empty PassThrough; continue after Accept; bypass CanMaintainAnchor. Each requires a designated deterministic witness and all expected rows. Test inability to derive unsupported global subtree safety separately as a model limitation, not a native mutation failure.

Extractor/body hash changes, malformed graph rejection and compiler diagnostics are **diagnostic controls**, not semantic mutation evidence. A mutant assertion failure counts only as an explicitly planned assertion control, never a completed full-corpus semantic run.

## Bridges and limits

- Frame construction puts local fixed frames under a transformed containing block and gives their placeholders the expected target; fixed establishes the relevant descendant containing-block relationships. Root's exact WPT plus retained construction source supports this bridge, but the capsule does not construct a browser frame tree.
- Computed position and overflow-anchor arrive unchanged from style; native sticky predicate/provider identities are bound separately.
- Geometry providers report actual visible bounding rectangles, continuation unions and ancestry correctly. No claim about transforms, SVG, fragmented bounding boxes or the spec's open geometry issues follows.
- Providers do not mutate/reparent/destroy frames during traversal; stable owner lifetimes, child-list order, finite size, ancestry consistency and decreasing recursion rank are explicit.
- Existing native policies at logical scroll origin, perspective and nested scrollers are modeled for preservation, not declared universally conforming CSS.
- No proof of adjustment arithmetic, suppression triggers, scheduling chronology, APZ, highlighting raster output or arbitrary browser execution is included.

## Execution and acceptance gates

Freeze original/candidate native sources and exact WPT/control identities after root's candidate build. Bind to root baseline and candidate receipts using full hashes, source/binary provenance and actual terminal status. Candidate browser acceptance remains a prerequisite to treating this as a completed bug companion.

Producer should publish a source-only replay capsule: independently readable model, raw fixtures, exact extraction map, adapters, compiler/SDK/Lean pins, complete commands/terminal receipts and manifests checked before/after execution. Use the existing verified local Lean toolchain if available, but rehash the executable and record actual version. Record compiler executable resolution, flags, target and SDK settings; never credit an unavailable sanitizer. Previous ASan startup problems remain an environment limitation until a fresh diagnostic proves otherwise.

Run once in an isolated artifact directory, then obtain a fresh root replay and independent review. Require the reviewer to read the complete extractor, classifier, traversal and oracle; verify arbitrary-list/rank theorem quantification and audit every provider premise. A green replay alone is insufficient. Keep the formal companion in a tooling commit preceding the single native+WPT repair, per the user's history requirements.

This scope package authenticates planning inputs only. `verify.py` checks its frozen files; it performs no formal or native verification.
