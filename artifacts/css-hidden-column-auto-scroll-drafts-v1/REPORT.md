# Fixed-size auto-scroll column-provider diagnostic

Status: **four unrun WPT drafts; source and static checks only**. This is separate from the104-case campaign and does not delay it. No installed WPT/native edits, browser, build or Git actions.

## Concrete fixture and oracle

`hidden-column-auto-scroll.html` registers col/colgroup × unchanged/changed-table-width. An inner100×100 fixed-position scroller contains an8000px leading spacer, a600×80 subject and1000px tail. Scrollbars are suppressed; viewport geometry is independently checked. The table is480×40 with three equal columns. The target is the second col or second one-column group: warm rectangle[160,8000,160,40]. Changing table width to240 gives[80,8000,80,40]. Subject width/height, spacers and clipping remain unchanged.

This makes the expected scroll offset[160,8000] for no-change controls and[80,8000] after the width change. Both offsets are strictly inside the available scroll range. Explicit block:start/inline:start/behavior:instant, zero scroll margins, no snapping and disabled scroll anchoring avoid independent alignment mechanisms. A large target in the no-change case is intentional: start alignment is explicit, not nearest alignment.

Fixed dimensions neutralize the relevant size-containment difference: retaining size containment cannot change the subject's600×80 box, and the table's definite width/height do not depend on intrinsic subject size. This is a restricted geometric argument, not a claim that arbitrary auto subtrees align to their eventual visible boxes. CSS Contain explicitly keeps size containment for scrolling an auto-skipped element; focus has a different ordering. [Containment restrictions](https://drafts.csswg.org/css-contain-2/#cv-notes). CSSOM start alignment uses the target bounding border box's corresponding beginning edges. [Scroll position algorithm](https://drafts.csswg.org/cssom-view/#determine-the-scroll-into-view-position).

## Exact read/order protocol

1. Construct an ordinary visible/unskipped subject offscreen. Read and assert its explicit subject, target, three cells, scrollport dimensions and zero offsets. This warms the real target's geometry.
2. Install an event listener before applying content-visibility:auto. Await a trusted contentvisibilityautostatechange with skipped=true. A3000ms timeout is a **calibration failure**, not a passing fallback or optional skip. The event reports a state transition; it is not a native frame-dirty bit oracle. [Event definition](https://drafts.csswg.org/css-contain-2/#content-visibility-auto-state-change).
3. In the resumed synchronous turn, optionally narrow only the table, query only the outer scroller and scroll offsets, then invoke the target's scrollIntoView. No target/subject geometry reread, focus, animation-frame yield or peer layout occurs between the skip notification and this call.
4. Save the immediate scroll offsets **before** constructing a separate, unskipped peer. Calibrate that peer's subject/target/cell rectangles and its own start-aligned scroll to the literal expectations. Remove it.
5. After two rendering callbacks, save settled target offsets and final rectangles. Assert both immediate and settled scroll and final geometry. The first saved result cannot be rescued by later geometry reads.

Every support, skip-state, warm, outer and peer prerequisite assertion contains `calibration`. All data remains under `window.columnAutoScrollResults`, including events and immediate offsets before later assertions. A calibration failure must stop a root experiment's fixture gate; a candidate scroll mismatch is a separate outcome. The test does not classify a missing event as a native query bug.

## Why this may cover the new gate, and what it cannot prove

The source shared caller obtains the primary frame, makes auto ancestors temporarily visible, invokes UpdateHiddenContentInForcedLayout, updates relevancy, then chooses forced layout or its existing interruptible-layout fallback. The narrow repair only admits a clean col/group when its table provider is dirty, while retaining the original target's ancestor walk. A table-width style change plus an outer-only flush is a concrete producer candidate for that state, without a target geometry query first.

However, either caller's visibility/relevancy operations may themselves schedule sufficient layout. Baseline and candidate may both pass. A trusted skipped event and changed width establish useful public preconditions; they do **not** establish clean target/dirty provider at the native read. No new browser failure or branch-coverage claim is made. If baseline/candidate differ, correlate exact case and stage with the existing narrow query/publisher trace before attributing a native mechanism. If both pass, retain this as a shared-caller regression control, not proof that the new branch executed.

Auto relevance scheduling and event delivery remain environmental gates. The fixed8000px distance is not treated as proof of skipping; the observed event is mandatory. Its notification is asynchronous, so this is the strongest bounded public precondition used here, not a proof of every internal state between notification and call. No intervening author action changes relevance, focus or container geometry.

The existing `content-visibility-058.html`/reference remain useful independent size-containment scrolling regressions. They exercise a different intrinsic-size/absolute-child configuration and should not be rewritten to this fixed-size expectation. Their success does not establish col/group provider coverage.

## Validation

Node syntax exit0 and exact four-name registration pass (`STATIC-CHECK.json`). The static sequence check confirms no target/subject rectangle call or additional await between skip and initial scroll, and peer construction occurs after the initial scroll capture. These checks execute no test callback, DOM, process launcher or browser. Actual visible calibration, event delivery, immediate/settled offsets and candidate discrimination are all pending root runtime.
