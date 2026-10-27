# Hidden iframe: fallback versus stale viewport

The retained run has three PASS cases and one calibrated first-value failure: hidden 10vw is 30, not the predicted stale 20 or resized 40. Its classifier correctly rejected this unanticipated result and preserved the tree. The original raw first failure does not expose the copied repeat/post-query array; later assertions were not reached. No values from that inaccessible array are inferred here.

The highest-value source explanation is iframe reinitialization at the 300×150 fallback, rather than retention of the old 200×100 viewport. Searchfox discovery followed by bounded reads of the exact installed bodies establishes these conditional links (all five inspected files match HEAD90; hashes and excerpts retained):

1. `style_adjuster` adds STYLE containment for content-visibility:hidden. `nsStyleDisplay::CalcDifference` returns ReconstructFrame when STYLE containment changes.
2. `nsSubDocumentFrame::ShowViewer` calls `nsFrameLoader::Show`. The latter initializes the child base window with `GetInitialSubdocumentSize()`.
3. That method can reuse a detached presentation shell's visible size; otherwise it returns `kFallbackIntrinsicSize`, exactly 300×150 CSS pixels. `GetSubdocumentSize()` also selects this initial method while FIRST_REFLOW is set.
4. `ShowViewer` calls corrective `UpdatePositionAndSize` only when FIRST_REFLOW is absent. Actual reflow and its callback normally publish the iframe size. The earlier pinned viewport-provider audit connects presentation-context viewport size to SVGLength's vw/vh factors.

This makes hiding alone a plausible source of a fallback reset before the pending host resize. It does not prove that reconstruction, fallback selection, first-reflow skipping, or a particular callback occurred in runtime17097. Detached-shell reuse is an explicit alternative. A source trace is still required for invocation-level attribution. The numerical 30 result alone does not establish both viewport dimensions or native app-unit values.

## One follow-up

The unexecuted eight-case probe uses independent fresh iframe histories: vw/vh each with visible-resize, hidden-only and hidden-resize, plus two absolute px hidden controls. Initial size is 240×120; resized size is 460×260. Thus observed 30/15 would distinguish the fallback from initial 24/12 and resized 46/26. Every history also independently calibrates a populated visible twin and a default-sized iframe's width, height and SVG length. The default iframe is only an empirical fallback-size reference, not proof that the hidden iframe selected the same native branch.

There is no extra subject read between hiding and the first measured SVG value. The original hide-style/host-only flush is retained; hide-only and hide+resize use separate subjects. First and repeat are copied before any subsequent geometry query. Host/frame/client dimensions, post-query value, reveal and reset are then copied. Strict visible/default/initial/reveal/reset calibrations precede the final current-viewport hypothesis assertion. That assertion embeds the entire copied JSON snapshot in its failure message, requiring no new reads. Later snapshot values are observations, not independently validated normative assertions or independent first queries. A calibration failure remains inconclusive.

Only JavaScript syntax was checked (exit0); no browser, build, native, test installation or index action occurred. The original sealed fixture/runtime remain unchanged. The synchronous hidden-child viewport requirement remains the prior SPEC.md's INCONCLUSIVE question; this probe classifies provider history and does not accept a new defect, compatibility claim or security impact.
