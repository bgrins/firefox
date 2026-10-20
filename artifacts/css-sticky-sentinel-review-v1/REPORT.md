# Sticky finite-sentinel native review

## Verdict

**ACCEPTED: the distinct native/WPT positional repair is reviewable within its stated scope.** No native blocker remains after source inspection, independent boundary challenges, paired WPT reconciliation and regression evidence. The separate masked-clamp formal companion is still required and is not accepted by this review. H1/H2 work remains independent and unchanged.

Candidate StickyScrollContainer.cpp SHA: `38d14faa60bfe3180e87904f5085fdbbee5aa47746a38df77f4edb50360af40c`.

Standalone two-file patch SHA: `618df0d65352c15d9e5c75b1c86ac7ede7ee3c113932ceaf788066c95b9bccec`.

## Defect and discovery

The formal producer exposed that the finite unbounded-limit representation can constrain a valid normal coordinate. Source analysis identified a preceding-content route; root then reproduced it in installed Firefox158 and the current shared Firefox160 binary. This was formal boundary analysis followed by source and browser validation, not an independently proved browser-reachability theorem.

The corrected discovery fixture has42 observations per browser: six sticky discrepancies above the boundary and36 matching rows, including28 ordinary static/relative controls. Its containing block, spacer, target, scroll position and computed sticky inset values are checked. `recheck.py` independently validates the exact Cartesian roster and corrected <=2px oracle from retained raw observations. Historical v1's stricter comparison falsely flagged two ordinary rounding differences and is not relied on.

[CSS Positioned Layout](https://drafts.csswg.org/css-position-3/#stickypos-insets) supplies both the all-auto axis identity rule and the per-side non-auto movement condition. `DESIGN-REVIEW.md` traces the complete property/limits/position caller path and the distinction between original activation and effective view insets.

## Repair assessment

The exact delta guards all four existing ordered clamps using the corresponding original ComputedOffsetProperty value. Missing property returns the normal position. It neither derives activation from numerical limit values nor activates an automatic opposite edge when one side is explicit. Existing comments, source clamp order and both current/zero-scroll wrappers are preserved.

`CHALLENGES.json` retains six independent exact-integer examples: all-auto, one-active-near, one-active-far, explicit near/far edges numerically equal to sentinel values, and contradictory ordered bounds. These invalidate broader or weaker designs. They are not compiled native tests or new browser results.

The whole candidate differs from its retained before source only in DoComputePosition. That pre-change function is identical to the freshly retrieved upstream body, so the change is independent of H1/H2 limit construction. `gates.py` applies/reverses the exact source hunk in memory on both retained baseline and upstream and reconstructs the exact added WPT. Root's historical HEAD/upstream two-base apply/reverse receipts are retained; this reviewer did not repeat Git operations or claim an isolated build.

## Runtime and packaging gates

- Paired WPT:24 identical subtest identities,4FAIL/20PASS before and24PASS after. The only changed paired pins are the sticky native source and the two built executable artifacts. Each run's pins are stable and its harness completes OK.
- First regression group:8 files,1328 passing subtests and3 passing reftests, plus5 OK harness completions.
- Follow-up group:7 files,8 passing subtests,1 passing reftest, and2 failures matching the exact pinned existing single-axis metadata. Mach exits0 with no unexpected result. The wrapper incorrectly required every status to be PASS and records complete=false/exit1 externally; its original receipt is preserved. `gates.py` reconciles raw rows with the receipt and authenticates the metadata rather than silently converting those failures to passes. Root separately checked the same metadata against HEAD; reviewer relies directly on retained pinned bytes.
- Build terminal0; its progress monitor logged an export-key error, separately disclosed by root. Format leaves candidate bytes unchanged. Native lint reports no errors or warnings. WPT lint exits0 with zero errors and one unspecified warning; it is not described as warning-free.
- Standalone patch contains exactly the native function edit and the relevant WPT. No additional tooling/docs are in that patch. Runtime uses the shared local build; source applicability on other bases is not isolated-base runtime evidence.

## Scope and remaining obligations

The correction applies to DoComputePosition and consumers of its result: continuation translation, zero-scroll geometry, and stuck-state classification. It does not repair GetScrollRanges' numerical-sentinel discrimination, GetStickyScrollRangesForAxis's edge/sentinel assertions, arbitrary extreme coordinate differences, or the complete compositor/view-timeline pipeline. Their callers were inspected and retained to make this boundary concrete.

ComputeStickyLimits still executes geometry arithmetic before the new guards. Arbitrary-normal identity of the consumer is not a claim that all geometry intermediates are representable. The offset encoding also has a reserved numerical alias that a proof must exclude explicitly. Missing offsets and missing normal-position lifecycle states are distinct; the latter existing early return remains intact.

`FORMAL-CONTRACT.md` specifies the next companion: original-mask derivation, absent/missing identity, one-sided monotonicity, ordered both-sided behavior including contradictory bounds, containment preservation, closest feasible position under a nonempty interval premise, exact old/new agreement where inactive bounds truly do nothing, signed min/max representation, and complete DoComputePosition extraction. Provider, arithmetic, continuation, range and timeline boundaries must remain explicit. No theorem that assumes all finite sentinels already bound every normal coordinate can stand in for this repair.

No production, WPT, Git, browser or build writes were made by this reviewer. Only this artifact was created. Primary specification, Searchfox source/caller evidence, retained runtime receipts and reproducible independent checks are sealed together.
