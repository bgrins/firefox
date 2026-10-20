# Fragment observer source review and standalone overflow positioning

## Verdicts

**RECOMMEND_BOUNDED_OVERFLOW_RETIMING** for the exact standalone native proposal: compute true overflow-container child geometry using the final flex fragment size, after ordinary children and output-size calculation. Final production formatting/lint and packaging are root-owned gates. This is a source-review recommendation for that bounded repair, not formal verification of every overflow-container lifecycle. This agent proposed the native change; the separate parent performed the independent browser/build experiments.

**HOLD_FULL_FRAGMENT_OBSERVER_COMPOSITION** for the broader wide packing/exact-fragment prototype. The placeholder, abspos, cumulative-consumption, finite-availability, physical API and arbitrary continuation-composition obligations remain. Passing the bounded repair does not discharge these obligations or retroactively accept the rejected packing prototype.

## Exact native target and evidence

The standalone proposal changes only nsFlexContainerFrame::Reflow: move ReflowOverflowContainerChildren from the temporary-container-size phase to after PopulateReflowOutput and ordinary child vertical-rl correction, pass aReflowOutput.PhysicalSize(), then perform the existing overflow/status joins. No arithmetic, helper API, dirty predicate, child position formula or list-manipulation implementation changes. The two-file proposed patch includes the 336-observation WPT.

Source roles are hard-pinned in verify_review.py and standalone-overflow-proposal/SOURCE.json. Base is the exact retained Git revision 92a6fddf18e5828b17d7491a34663a0d5a9c12ad; patch application and reversal recover the precise candidate and base bytes. Root browser runs used the shared combined native tree with this isolated retiming delta; they are not claimed to be isolated upstream-base builds. Source commutation alone is not a semantic independence proof.

Each root capsule listed in native-candidate-evidence/AUTHENTICATED.json was authenticated against its supplied manifest pin, complete closed roster and every payload hash. Selected raw receipts are copied into this review for reproducible recounting; the entire root browser environments are not imported.

- Paired WPT: 224 prior passes preserved, 112 vertical-rl failures corrected; candidate 336 PASS.
- Lifecycle: root retained eight calibrated stages covering growth, ordinary/overflow continuation transitions and removal/reinsertion; baseline seven failing stages, candidate eight correct. Branch internals are not inferred from geometry alone.
- First diagnostic: twelve actual OC visits, all reflow; no skipped visit.
- External sibling resize: eight calibrated cases fail before and pass after. Independent trace recount joins all 24 OC parent identities to the immediately preceding column dirty-mark identity. Eighteen column children were clean before being marked; every OC visit then reflowed. This establishes the route actually exercised, not universal skip exclusion.
- Focused regression: independently recounted 34 existing file results unchanged, 24 PASS and 10 expected FAIL. Those failures are retained and are not counted as passes. The additional new WPT again has 336 candidate passes.
- Child-mode paired raw rows: release and baseline match exactly. All 20 opposite/orthogonal actual observations are byte-identical before/after. The six same-mode zero/inline-offset cases satisfy the corrected numeric oracle. Four same-mode block-offset cases retain the preexisting successor-offset omission; the second descendant already omitted it before the patch. All block references are identical across runs; their eight nonzero same-mode cases fail the proposed reference calibration and are not treated as a normative oracle.
- Earlier abspos/overflow probes: complete pinned external observations and recounts preserve failed small-case calibrations, not just successful replacements. Tiny nested forced breaks did not calibrate the intended continuation route. Tall ordinary-size overflow probes establish the separate final-width error. Tall abspos extra-fragment counts remain unattributed.

## Why the retiming repairs the observed path

For a child whose block axis runs right-to-left, normal physical x = C − childSize − B. Reflowing with temporary C=T and later observing under final C=F produces B+(F−T). Ordinary flex-item final correction does not visit the separate OC list or its previously collected physical bounds. Ordinary 160px controls reproduce the resulting 160px/240px errors. Supplying F directly removes this term, before ConsiderChildOverflow and the final union.

OverflowCoordinates.lean proves this equation, the corrected equation, explicit signed32 operation bounds on its declared finite coordinate domain, and controls for skipped placement and a horizontal RTL conversion where container-width terms cancel. These are source-sized coordinate lemmas. Actual callbacks, arbitrary physical geometry and all writing-mode branches are not silently modeled as the same scalar equation.

## Ordering and skipped-branch review

OVERFLOW-ORDERING-AUDIT.md retains the complete inspected source argument and entry-route audit. The relevant existing invariants are normalized principal/overflow lists, distinct valid continuation chains, and the helper's previous-parent eligibility check. They are source-review premises, not newly kernel-proved frame-graph facts.

GenerateFlexLayoutResult enumerates principal children before the OC phase in both versions. Ordinary child handling can delete or create later continuations, but newly generated continuations have their predecessor under the current parent and do not become eligible existing OCs of that same parent. The late helper constructs its tracker after those mutations; no tracker survives across them. Existing eligible OC chains are disjoint from current principal normal-item chains under normalized-list invariants. PopulateReflowOutput does not manipulate continuation lists, and the status/bounds joins remain after both phases. No introduced frame-list/order counterexample was identified.

For a skipped child, passing a different container-size argument has no direct effect: that argument is consumed in the reflow branch. Parent GetSize() is not committed by PopulateReflowOutput. The unchanged skip predicate reads the same reflow flags/availability and existing eligible child overflow under the source invariants above. Direct block OCs under flex own a float manager because flex is not a float-containing block; skipped RecoverFloatsFor is consequently a no-op for that case, and non-block children also do not recover block floats.

The kernel deliberately preserves the scalar skipped-size counterexample: if an unchanged physical position is observed after an old-to-new parent-width change, logical B changes by that width difference. No actual skipped invocation was observed, and no source argument here proves that all possible skipped flex OCs have equal old/new widths. This remains a broader correctness boundary. It is not evidence that this retiming newly introduces that behavior: the skipped child's positioning is unchanged, and no changed ordering dependency affecting its tested predicate/state was found. Pagination, nested final balancing and special table reflow routes were inspected; their limited dirty/reflow implications are recorded without declaring arbitrary entry routes impossible.

## Relative positioning and child writing modes

RELATIVE-OVERFLOW-SOURCE.md records a separate existing omission. Both flex and ordinary block callers pass ReflowChildFlags::Default. The OC helper constructs (previous used IStart, 0) and forwards Default; FinishReflowChild invokes ApplyRelativePositioning only with its absent explicit flag. Thus the inline translation is inherited once, whereas relative block translation is omitted on successors. The earlier inline-accumulation concern is withdrawn for this path.

CSS Break 4 section 5.5 applies relative positioning per fragment after fragmentation and explicitly describes overflow-only fragment origins. The fresh full primary text is retained. A horizontal delta diagnostic now compares shifted versus unshifted geometry directly, with fixed-size overflow and ordinary auto-size controls. This is a separate bug lead, not a bundled repair. The proposed block reference in the earlier child-mode probe does not calibrate for nonzero same-mode offsets and is not accepted as a normative oracle.

## Broader observer work retained

DEVELOPMENT-REPORT.md preserves the complete placeholder/absolute trace and original development findings. In particular: later fragment layout results omit placeholders, so the specific late negative-temporary-size clamp does not directly reposition them through ReflowPlaceholders. That is not a proof of all later hypothetical/abspos containing-block consumers. First-fragment nonnegativity additionally needs actual nonnegative available size and source-defined padding/content providers; an admitted arbitrary nscoord does not establish these facts. The kernel retains a negative-availability counterexample.

AbsoluteContainingBlock's exact finite-available cumulative addition was extracted and reproduced at O0/O2: six safe or sentinel-skipped runs and two expected signed-overflow failures. The concrete 1,920,000,000 + 960,000,000 arithmetic inputs are individually representable. This is not a browser-local-variable trace or attribution of the extra abspos fragments. Its potential repair remains separate from the bounded flex retiming.

## Reproducibility and limits

run_checks.py authenticates tools/provider source roles, compiles 19 kernel results with allowed-axiom checks, rejects four false claims and two forbidden-axiom controls, replays eight native arithmetic cases, checks executable JS syntax, recounts selected browser receipts and applies/reverses the standalone patch. run_integrity_controls.py tests unexpected files, modified source, resealed extra caches, and resealed source-role substitution. verify_review.py enforces a closed roster and can perform a fresh manifest-only relocation and source replay. Receipt files state which runs completed; no browser/build execution occurs in this checker. Disposable compiler products are created in temporary directories and removed.

No unrestricted frame memory safety, all-coordinate arithmetic safety, all fragmentation correctness, full CSS conformance, universal clean-skip exclusion, or full native callback equivalence is claimed. The 19 kernel results are narrower than these claims. The source and native evidence supports the bounded retiming recommendation with these explicit boundaries; the full original exact-fragment verification milestone remains open.

## Dynamic-positioning boundary discovered before sealing

Root subsequently reported that all 30 horizontal delta rows pass in release and shared baseline (css-overflow-relative-delta-runtime-v1). Those cases first lay out at zero and then change offsets, unlike the initial-nonzero child-mode cases. Therefore the helper source observation cannot be generalized to dynamic positioning paths: a later position-only update can produce the expected translation. The separate lead remains unaccepted. A fresh-initial versus dynamically shifted comparison at identical final DOM/style is required next, across horizontal and vertical modes. This newly reported result is not included in the independently authenticated capsule recounts of this checkpoint.
