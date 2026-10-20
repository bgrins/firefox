# Independent review: large negative sticky-inset arithmetic

## Recommendation

**ACCEPT the native three-file repair and WPT. Full formal-companion acceptance remains PENDING.** The change fixes the demonstrated normalization/extent representation defect and preserves the old results wherever the old operations are defined. No introduced native regression was found in this review. A concrete preexisting GetScrollRanges clamp overflow is retained as a separate follow-up and as a required explicit boundary for the full caller proof.

Only this new review artifact was modified. No production/WPT/Git changes, browser execution or Firefox build were performed by the reviewer. The review used frozen original/combined/standalone snapshots, authenticated the supplied exact patch, independently checked raw retained evidence, fetched primary specification and implementation sources, and ran small extracted C++ calibrations. The temporary standalone live-source switch was not treated as candidate drift.

## Candidate identity and independent packaging

The exact patch SHA256 is `68c14d1d2b0fdb2fad21efc9e670a6ddcdf40740c1e84230225f7bae57251484`. It contains only StickyScrollContainer.cpp, StickyScrollContainer.h and position-sticky-large-negative-insets.html. audit_evidence.py independently parses its hunks, checks exact context, applies and reverses them against read-only Git snapshots of both `92a6fddf18e5828b17d7491a34663a0d5a9c12ad` and `976279105b2e78b8666a959eb3f25c9176cefaf8`, and checks the exact resulting native files and WPT.

| Role | Sticky CPP SHA256 |
|---|---|
| Combined baseline | `2a0794213ffad4d35d96b915b0fc858e2bfb18ddf74b20e4884a2d6b6f0f3b4b` |
| Final combined candidate | `0e3b5f3e85e41a9e65164c489acfba58d12634e9a6658df71dcd3bf141ab4096` |
| Both immutable upstream/HEAD bases | `877d9e663bd76a750537c19fe02d2f357be6407bab87484366f0766799ccc817` |
| Standalone candidate | `52c7c219259af222e620c9913a0d2993c8fcf7cdea31b3d76b7b734e8fbf1a78` |

The header changes from `2df4e7ce…` to `e4c44b8a…` in both adaptations. The initial unbuildable candidate `8fac022a…` is development evidence; the tested candidate is the final `0e3b5f3e…` file. Browser RUN, BUILD-v2 and regression identities match that final combined source exactly. The additional standalone RUN uses the distinct `52c7c219…` source. Restoration receipts name the original combined final source and successful rebuild. All identities are retained in the review; replay does not consult current mutable native files.

The standalone patch retains upstream's computedOffsets operands, both-non-auto activation and LTR/RTL end selection. The combined candidate retains effectiveOffsets, auto-to-zero normalization, either-non-auto activation and writing-mode end selection. Widening is applied to the appropriate existing operands in each source. It does not import the separate H1/H2, positional sentinel or explicit-inset alias changes. Source applicability is not an isolated upstream build claim. The extra standalone browser run uses HEAD-plus-this-patch for these two Sticky files while unrelated worktree changes remain.

## Native arithmetic and narrowing

The first conversion to int64_t occurs before subtraction. Thus both successive view-extent subtractions and the subsequent box-minus-view delta are evaluated in signed64; replacing TopBottom/LeftRight also removes their signed32 addition. The compound end-inset subtraction uses signed64 before assigning back to nscoord.

For nonnegative port and border-box extent at most M = 1073741823, and effective insets in [-M, M], the widened view lies in [-2M, 3M]. The executed positive delta is at most 3M. After normalization, the chosen end inset equals `min(original end, port - other inset - box)`, which lies in [-2M, M]. This fits the full signed32 storage range, so the assignment back to nscoord is exact even when the result leaves the narrower conventional coordinate range. The intermediate expression bounds fit signed64 by a large margin. Each axis changes only its selected end side; original side activation is preserved.

Those size/provider bounds must not be inferred merely from the typedef `nscoord = int32_t`. The in-flow union uses saturating union for nonempty combinations, but also has direct-return paths; complete range justification is a remaining formal provider obligation. With arbitrary signed32 geometry, widened intermediates are still safe but a result need not fit signed32. For example port=0, box=2147483647, other inset=M can produce -3221225470. This is a counterexample to a type-only narrowing argument, not evidence that a real Firefox frame with those inputs is reachable. The preliminary proof correctly states its additional geometric premises.

Where the old sum/view/delta/subtraction operations are all defined, widening preserves their exact integer values, comparison and selected-side result. No rounding, allocation, provider call, auto decision or writing-mode policy is added by this arithmetic patch.

## Direct-edge storage and consumers

nsRect stores an origin and signed32 extent. Setting the far edge subtracts the near edge, which may overflow even when both endpoints fit. nsRectAbsolute stores all four signed32 endpoints directly. Its setters are assignments and X/Y/XMost/YMost return those endpoints. The exact fetched geometry headers match the local headers byte-for-byte; hashes are in GEOMETRY-SOURCE-IDENTITIES.

The initial unbounded rectangle converts safely: its endpoint additions are representable and retain the same sentinel values. Every mStick mutation is an edge setter; mContain remains the original nsRect pipeline. All three ComputeStickyLimits consumers were examined: DoComputePosition, GetScrollRanges, and GetStickyScrollRangesForAxis. Position callers use accessors instead of direct x/y fields. The per-axis range caller already uses accessors. GetScrollRanges now references the directly stored endpoints rather than converting an origin/size rectangle; the reference remains within the structured binding's lifetime. There is no width/height use of mStick itself in these callers.

When the old setters and endpoint queries are defined, both representations retain the same near/far endpoints. FromRect's old overflow rejection is not lost on that domain: after a defined edge setter, recomputing the opposite stored edge yields a representable original endpoint. The unchanged containment conversion, source arithmetic used to construct endpoint arguments, normal-position subtraction, and later range arithmetic still need their own domains; changing storage does not prove them safe.

The downstream display-list range conversion reads endpoints and converts them to floating point. ClipManager consumes edge differences and bounded offsets. Their arithmetic is unchanged; its safety is not inferred from this storage repair. Relevant exact primary source snapshots are retained under upstream/.

## Independent extracted calibration and remaining range lead

calibrate_ranges.py extracts the whole frozen GetScrollRanges function from before/after, uses the actual BaseRectAbsolute template, and supplies stable frame/limit inputs and a small nsRect facade. The facade's setters and overflow behavior were checked against upstream definitions. This is concrete source calibration with admitted providers and system compiler/runtime, not a mechanized C++ semantics proof or a browser run.

Two cases run at -O0 and -O2 with UBSan for both source variants, and the complete eight-run calibration was repeated in a separate output directory:

- **Wide interval:** near=-1073741823, far=1073747223. Both endpoints fit signed32, but their extent is 2147489046. Old SetBottomEdge trips UBSan; the new direct-edge GetScrollRanges path completes successfully at both optimization levels.
- **Existing clamp limitation:** near=-1073741823, far=1073740223; old extent=2147482046 fits signed32. A zero-width inner interval in the orthogonal axis triggers MoveInsideAndClamp. That routine computes outer.Height() as `1073801223 - (-1073740223)`, overflowing signed32. Both old and new source fail at the same operation at both optimization levels.

FOLLOWUP-RANGE-LEAD provides the complete second input. Its old normalization and stick construction can be entirely defined: port height 6000, box height 600, top=-M, bottom=7000-M, zero offsets/padding, normal y=12000 and containment height 59400. The other axis has port/box width 6000 and zero opposing insets, creating the empty inner interval. This demonstrates that representable endpoints alone do not establish caller arithmetic safety, even before this patch. It is not an introduced regression and is not a browser reachability claim. Browser investigation is a separate follow-up; the full companion must retain this witness and the branch-sensitive clamp domain explicitly.

## WPT and retained runtime evidence

The [sticky positioning rule](https://drafts.csswg.org/css-position-3/#stickypos-insets) uses insets to form the view rectangle and shifts a box only when an applicable border edge lies outside it, subject to containment. Negative opposing insets expand that rectangle. In this small fixture the normal box remains inside it, so the independent static position is the correct oracle. [Numeric-range rules](https://drafts.csswg.org/css-values-4/#numeric-types) allow implementation clamping; this test does not require exact representation of the enormous authored values. It relies on those negative values remaining large enough in magnitude to contain this small box. Primary pages are retained in spec/.

The WPT uses a 100px port, 1000px containing block, 200px spacer and 10px target, both axes, ten negative inset pairs and scroll offsets 0/100/400. It calibrates all dimensions, actual scroll, computed sticky positioning, both non-auto sides, and a separately measured static target. Expected normal positions are 200, 100 and -200. All 24 baseline failures occur at the final position assertion and have exact observed positions 0, -100 and -400; fixture calibration succeeded first. Smaller pairs and asymmetric one-large/one-small pairs are controls. The active opposing sides and small positive geometry avoid dependence on the pending auto/sentinel/alias repairs.

audit_evidence.py independently verifies exact 60-case identities and raw events against receipts: 24 FAIL become PASS, 36 controls retain their passing status/message, both harnesses are OK, within-run pins are stable, and only the two Sticky source files and browser/XUL change across the pair. The regression record has 1,408 passing subtests and three passing reftests. Both earlier Firefox 158 and shared-development probes independently reproduce the same 24 mismatches among 60 calibrated rows. The later standalone Sticky-source build/run passes all 60 cases with stable exact source pins; it does not establish an otherwise pristine worktree.

Combined BUILD-v2 succeeds with zero compiler warnings; native/WPT v2 lint logs contain zero problems. The subsequent standalone/restored builds succeed while reporting nine suppressed warnings in gfx/gl and widget/cocoa. Their retained progress-monitor KeyError does not change the successful terminal build results. Failed initial build and non-running initial lint invocations remain development evidence and are not credited as passing gates.

## Required full formal companion

The preliminary 12 Lean results are useful algebra, not the completed contract. Native acceptance does not waive any of these remaining requirements:

1. Exact source-derived normalization and every widened intermediate bound; explicit provider joins for port/box/inset ranges and signed32 result conversion. Cover genuine combined and standalone operand/activation variants, and both end-side choices.
2. Direct-edge initialization/setters/queries, intervals too wide for signed32 extents, preservation where the old representation's operations are defined, and all executed endpoint-construction intermediates under named provider conditions.
3. Complete position and first-continuation composition, absolute GetScrollRanges construction, Intersect, emptiness branch and MoveInsideAndClamp. Include branch-sensitive width/height/add/subtract preconditions and the retained counterexample; do not replace this join with endpoint-only lemmas.
4. Per-axis threshold/range observers, including both-axis helper evaluation. Keep remaining unchanged containment, position/translation and timeline arithmetic assumptions explicit. No all-coordinate safety or all-CSS claim.
5. Exact genuine before/after combined and standalone extraction/calibration, kernel audit, semantic mutations and closed source/toolchain integrity evidence. Passing browser counts do not discharge these obligations.

## Reproduce and cleanup

Authenticate FILES/FREEZE using the separately supplied handoff pins. `python3 -I -S check.py --manifest-sha <pinned hash> --authenticate-only` checks the closed artifact roster. With `--out <absent external directory>` it also repeats the retained native-evidence audit and all eight extracted before/after range runs, preserving the known UBSan failures as expected findings. Successful replay means the evidence reproduces; formal acceptance remains pending.

The complete review checker also passed from a separate sealed source copy. An initial relocation subset omitted the probe receipts and failed before range output; its traceback and inventory are preserved. Adding the unchanged probe directory corrected the bundle, and the exact checker/evidence logic then passed. This development failure is not counted as a successful replay.

Only owned calibration executables and disposable replay copies are removed, with hashes and commands retained. System tools, native/build/browser artifacts, prior sealed reviews and other agents' work remain unchanged.
