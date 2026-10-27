# Captured MathML hidden-query diagnosis

The trace now establishes the skipped-reflow/default-publication/query-rejection sequence on the instrumented working build. Minimal next candidate: call MarkSubtreeDirty() immediately inside nsMathMLContainerFrame::Reflow's existing hidden-parent early-return branch. The candidate has not been run or accepted. Restoration was pending root verification when this diagnosis was requested; this artifact makes no terminal/restoration claim.

I authored the fixture and instrumentation. I independently reparsed both raw WPT logs and the marked stdout records, rather than relying only on the controller summary. Both phases reproduce the exact eight keyed outcomes and failure messages: six PASS, two FAIL, file-level OK. All 2,210 native records, 256 phase records and eight complete result records join back to raw events. Native input pins remain equal within each retained RUN. This is not an independent fixture-design review or an isolated upstream reproduction.

## Observed sequence

Event indices below are zero-based positions in marked/raw.json. The process is 54122. Join by case/ID as well as pointer: arena addresses are reused across cases. Owner and child mrow have class 9/type 0; mspace has class 10/type 0. Selected queries report primary=1. Native dimensions are app units (60 per CSS pixel in these measurements).

| Observation | c1, mrow-first | c3, mspace-first |
|---|---|---|
| Before/after child input | 641–642 | 1354–1355 |
| Actual hidden return | 644 | 1357 |
| Caller output after child reflow | 645 | 1358 |
| Cached empty output | 646–647 | 1359–1360 |
| Owner width adjustment | 648–649 | 1361–1362 |
| Empty rectangle published | 651–652 | 1364–1365 |
| DidReflow hidden return | 654 | 1367 |
| First query entry/rejection | 701–702 | 1414–1415 |
| Repeat query entry/rejection | 704–705 | 1417–1418 |

During mutate:outer, before and after ReflowInput, the child mrow has dirty=0, dirtyChildren=0, subtree=0 and its mspace child has kidDirty=0/kidSubtree=0. Input construction does not dirty either in this run. The mrow's hiddenParent=1 and parentForcing=0; math-hidden-return executes with size0,0, ascent1073741823 and bm0,0,0. That ascent is the initialized ASK_FOR_BASELINE sentinel. After the caller's ReflowChild helper, ascent is zero; size and bounding metrics stay zero. The empty output is cached twice, then used by placement.

The owner logs requested width3600 and prior content width0, followed by shiftX3600. Its child is positioned at3600,0. Publication changes the mrow's old local rectangle3600,0,2400,960 to3600,0,0,0. DidReflow takes its hidden return with both the mrow and leaf still clean. The owner subsequently clears its own dirty-children state.

The first and repeat c1 queries select that clean, empty mrow and take query-clean-reject. The c3 queries select the clean mspace and take the same rejection. Its local rectangle remains0,0,2400,960. The leaf's immediate-parent hidden predicate is false because its direct parent is the mrow, but the hidden owner remains further up the ancestor chain. Clean-target admission rejects the query before that ancestor walk. There are no admission/forced-reflow events in either failing first/repeat phase.

Root and leaf readiness do not diverge here: both are clean. Their geometry diverges because the skipped root's empty output is published while its unvisited leaf retains its local size. Both therefore need dirty marking; a root-only bit would leave leaf-first admission unsatisfied.

## Copied rectangles and controls

| Hidden mutation | First | Repeat | Visible peer |
|---|---|---|---|
| c1 mrow-first | [70,25,0,0] | [70,25,0,0] | [30,10,40,16] |
| c3 mspace-first | [70,25,40,16] | [70,25,40,16] | [30,10,40,16] |

The x70/empty-mrow result follows the captured shift and publication; the retained leaf size explains the size difference. The exact setter producing the final ancestor y-offset is not traced during mutate. A comparable hide:first ancestor event shows owner y900, but that is a different phase and is not proof of the mutate placement path. Do not claim the trace fully attributes y25.

Hide:first succeeds in these same cases: c1 events587–589 and c3 events1300–1302 show a dirty selected target, admission and the hidden owner entering forced layout. Subsequent repeat queries can safely reject the now-clean target because the forced result is correct. In root-block hidden controls c5/c7, mutate:first similarly has dirty selected targets (events1951–1953 and2471–2473), admission and forced owner layout; all their first/repeat rectangles match the peer. Four visible controls also pass. These controls distinguish missing readiness from a blanket rule that clean-query rejection itself is incorrect.

## Minimal repair experiment

Add only MarkSubtreeDirty() before the existing return when IsHiddenByContentVisibilityOfInFlowParentForLayout() is true. The observed mrow is clean at that point, so this call's already-dirty-root shortcut does not prevent descendant traversal in these failures. The existing DidReflow hidden branch should preserve the added bits. A later dirty mrow or mspace query should be admitted, mark its hidden ancestor for forced layout, and replace the temporary empty metrics with real layout. This is a source-based prediction to test, not an executed repair result.

Require an uninstrumented original-versus-candidate comparison using the unchanged eight cases: original six-pass/two-fail messages, candidate eight PASS, both query orders and first/repeat arrays correct. Root should select the existing hidden-layout regressions before acceptance. If marking repairs only mrow-first, or query admission occurs but layout remains wrong, stop and investigate the leaf/placement path. The already-dirty-root-with-clean-descendant case remains outside this trace; do not broaden the fix on that hypothetical basis before evidence. No generic PresShell admission relaxation or MathML metric-preservation change is needed for the first experiment.

EVENTS.json retains the decisive native records and successful admission controls. MEASUREMENTS.json retains all eight marked-run results. RECOUNT.json pins the raw inputs and exact recount. No browser/build/compiler was run and no production source or index was written by this analysis.
