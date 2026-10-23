# Independent source review: hidden table-column readiness

## Verdict

**GO for a bounded candidate diagnostic; HOLD native acceptance.** No source-local blocker found in the proposed eligibility extension. This review does not establish that the immediate table is dirty at every stale query, or that the scheduled flush publishes fresh geometry. Current root experiment is still running; no outcome is adopted as a completed acceptance gate here.

Authenticated all 26 producer payloads against externally supplied FILES `7f0df39d04c097b4116d66b50e1b10c2b39523d35e189a117f022ca997d3c170`. Candidate and patch match supplied pins. Independently checked that the complete file prefix before the method and suffix from `topmostFrameWithContentHidden` onward are unchanged. A 384-row finite branch check compares the concrete checked-parent sequence to the dirty-target-or-dirty-provider predicate. This is a finite control calibration, not native translation or a Lean theorem. No compiler, browser, build or Git action ran.

## Native change

- Null and already-dirty targets preserve their original path. A dirty target does not acquire a new parent-validity requirement.
- A clean column is admitted only through an immediate column group and its immediate table; a clean group only through its immediate table. Both require actual `IsSubtreeDirty`, including dirty descendants. Ordinary clean frames, missing/unrecognized parent chains and clean table providers remain rejected. No arbitrary ancestor search, wrapper substitution or global dirtying is added.
- The original queried frame remains the start of the `GetInFlowParent` traversal. This preserves any hidden table or intermediate ancestor that a walk starting at the provider could omit. The provider pointer is read before scheduling and is never retained across a flush.
- The unchanged suffix inserts hidden ancestor content and schedules the topmost hidden ancestor. Its preexisting set/scheduling invariant is still required: a nonempty forcing set must correspond to the discovered hidden ancestor. The geometry caller explicitly asserts an empty initial set. The scroll caller retains its existing lifecycle assumptions; this draft does not prove them.

## Ownership, spans and fragmentation

Retained typed accessors assert exactly the immediate group/table relationship used by the candidate. The group accessor also asserts its parent table is first-in-flow. The patch checks kinds but does not add a first-in-flow runtime check; it relies on the same constructor/lifetime invariant as the typed accessor. This is reasonable bounded source correspondence, not a construction proof.

`ConstructTableCol` initializes each span continuation with the same supplied parent and connects nonfluid continuation links. The gate therefore chooses the same table for those span frames under the constructor invariant. This does not prove CSSOM union geometry for a span or fragmented table.

`SetColumnDimensions` obtains first-in-flow column widths, iterates owned groups and columns, and writes their actual rects. It supports the chosen geometry provider; it does not alone show that every dirty table execution reaches these writes. Dirty group reflow with dummy sizes is not substituted as the geometry publisher. Continuation sharing, repeated fragment publication, collapsed columns and observer unions need dedicated calibration before broader claims. No reason was found to replace the checked immediate parent with a different continuation in this narrow patch.

## Callers and unchanged boundaries

`nsIContent::GetPrimaryFrame(Layout)` first performs the ordinary flush, then invokes the forcing helper and reacquires the original primary frame. The patch fits this existing reconstruction/lifetime protocol; it does not return the table as the requested frame.

`ScrollContentIntoView` is also affected for newly eligible columns/groups beneath content-visibility:auto. It marks auto ancestors temporarily visible, calls this helper, updates relevancy, then flushes; interrupted/suppressed reflow remains best effort. Source-local predicate extension cannot prove scroll-position equivalence or notification timing. Add a targeted auto-hidden scroll calibration if this repair advances. Do not advertise geometry-query-only behavior.

## Lean draft assessment

Read all of `ProviderReadiness.lean` and its obligations. It is correctly labeled uncompiled. The provider function matches the checked immediate-parent roles; the old dirty alternative is retained. The draft's finite-fuel ancestry function is an abstract selection list, not the native content set, topmost choice, FrameNeedsReflow execution, termination or publication semantics. Its identity theorem establishes reuse of the original target in that abstraction only. Capacity, actual construction, frame lifetime, scheduling, flush completion and dirty clearing are not derived.

The clean-provider/dirty-ancestor countermodel is essential: it demonstrates why eligibility alone cannot close the freshness obligation. Keep it. The hidden-provider example explains the original-walk requirement but is not evidence that every modeled hidden table state is native-reachable. No theorem count or checked-proof acceptance is granted by this review.

## Required runtime decision

For each failing query, join the target pointer/type/dirty bits, checked group/table identity and table dirty bits, forcing selection, and subsequent SetColumnDimensions publication. Distinguish four outcomes: newly admitted and repaired; newly admitted but not repaired; provider clean and gate closed; unrelated non-column failure. A passing repeated query only bounds extra work if actual dirtiness clearing and absence of intervening invalidation are observed.

While this review was in progress, root reported the ordinary-block baseline failing 7/8 cases (outer-width: all four target classes; table-width: col/group/td). These are **parent-reported partial runtime evidence**, not independently authenticated results here. They make a universal column-only diagnosis untenable: this patch deliberately cannot admit a clean td or table through the new provider branch. Retain those failures and adjudicate any residual separately; do not redefine them out of the goal or infer a broader fix from column success.

Recommended follow-ups after the current run: span and group-span targets, repeated/visible controls, an actually fragmented visible reference before asserting fragment counts, and the auto-scroll caller. No need to expand the patch before the pending provider trace establishes which cases it can address.
