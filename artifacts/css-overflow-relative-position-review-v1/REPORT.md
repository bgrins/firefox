# Overflow-continuation relative positioning: independent native review

## Recommendation

**GO for the bounded two-part native repair**, subject to the normal final formatting/lint and exact landing-patch binding. No source-level blocker found. This is not acceptance of the proposed full formal companion, a proof of every continuation lifecycle, or an isolated-upstream runtime result.

Reviewed patch SHA256: `a476af8083aa4240e5a70e2240135d2309a5a330cb7c1f4ed60a1ad31f1ad4fc`. The candidate changes only predecessor coordinate selection and the logical `FinishReflowChild` flag. `SOURCE-CHECK.json` reconstructs the complete candidate from exactly those two replacements and binds the tested WPT.

## Independent normative oracle

CSS Fragmentation 4, [Transforms, Positioning, and Pagination](https://drafts.csswg.org/css-break-4/#transforms), requires fragmentation before relative positioning, applying the effect to each fragment. Its overflow-only origin rule supplies an empty box at the fragmentainer start. CSS Positioned Layout 3, [relative positioning](https://drafts.csswg.org/css-position-3/#relpos-insets), supplies a visual displacement after ordinary layout. These together justify translating each already-calibrated descendant fragment by the requested offset while preserving its size and unrelated items. The special permission concerning block-start positions dependent on fragmentation does not justify omitting an independently specified constant relative displacement here.

Both current primary documents are retained as HTML and hashed in FILES.json. They were verified through the web tool on this review turn. This review does not reinterpret percentage resolution, auto/overconstraint policy, or page-level printing behavior as part of this patch.

## Coordinate and source review

1. `prevInFlow->IStart(wm, containerSize)` reads used placement. For a relative predecessor that already includes a visual inline shift, adding a fresh offset to it repeats that shift. Merely enabling the Finish flag is wrong.
2. `GetLogicalNormalPosition` uses the predecessor's saved physical normal point, converting with `containerSize - predecessor.Size()`. Reading only its inline coordinate is deliberate: overflow-continuation block origin stays zero. The patch preserves the existing choice of container-size input; it does not fix incorrect caller-supplied final container dimensions.
3. `ReflowChild` receives the normal logical point and unchanged flags. It performs the ordinary reflow and continuation deletion/tracker work. A virtual child callback and the returned dimensions remain real external providers, not algebraic equal-size assumptions.
4. Logical `FinishReflowChild` sets the current returned size before relative-position conversion. Thus converting the current point uses the current size, not the predecessor size. It stores the current physical normal position, adds current physical computed offsets, converts back, and installs the final rect. Unequal sizes and reversed axes are handled by this existing provider sequence.
5. `frame->IsRelativelyPositioned()` delegates to the same frame-aware display predicate used by RI offset construction: relative style and exclusion from the SVG-text subtree. A style-only predicate would broaden applicability. Sticky frames are deliberately unchanged; their offset timing belongs to StickyScrollContainer.
6. RI computes relative offsets in the containing block writing mode, stores their physical representation, and converts to the child mode for Finish. The patch reuses those computed values, including auto, end-side and percentage handling. It neither copies predecessor offsets nor reparses styles.
7. `NoMoveFrame` would make this a different contract, because Finish can store a normal position but skip installing the corresponding rect. None of the six actual indexed callers supplies it. Do not generalize the result to arbitrary flags.

### Six callers

| Caller | Flags and container-size provider | Review boundary |
|---|---|---|
| Fieldset | Default; available size fallback | Shared inner-child available-size limitation remains; child predicate controls application. |
| Block | Default; explicit `state.ContainerSize()` | Generic helper delta applies before ordinary block work; fixed block runtime cases exercised. |
| Canvas | Default; available size fallback | Pagination and root/canvas-specific placement not exhaustively tested. |
| Flex | Default; tentative border-box size | Existing final-size adjustment is separate. Current paired build contains that separate repair on both sides. |
| Grid | Default; available size fallback | RecomputePosition declines grid-item optimization and requests reflow; grid-specific percentage CB acquisition not proved. |
| Table wrapper | Default; available size fallback | Internal table eligibility/offset providers remain existing behavior; no new unconditional style-only offset application. |

Searchfox call roster matches the six retained caller files. The source role and flag arguments were independently read, not inferred from the WPT.

## Normal-position lifecycle

`ApplyRelativePositioning` stores the unshifted physical point on every reflowed relative continuation. Subsequent optimized `RecomputePosition` iterates continuations, recomputes current offsets, and sets position to saved normal plus those offsets. This explains the reproduced nonzero-initial update failure: without a saved normal point, the old fallback can treat the already shifted used position as normal. The candidate establishes the missing property on this path even when the initial relative offset is zero.

Restyle skips never-reflowed/dirty/SVG frames and falls back to reflow for unsupported cases such as grid-item containing blocks. The style-change branch removes the normal-position property when leaving relative/sticky positioning. `PROPERTY-LIFECYCLE.json` records exact agreement of that branch between current local source and independently retrieved upstream source; the complete files differ and are not asserted equivalent.

Predecessor readiness remains a source lifecycle condition: a previously positioned predecessor must possess its correct normal-position property, or be genuinely unshifted when the getter falls back. The 144-case independent coordinate model explicitly distinguishes a missing-property/shifted-predecessor counterexample. This is not a new browser bug report or evidence that the proposed repair creates such a state. Full proof must derive readiness from prior regular/overflow reflow and restyle events. Skipped dirty decisions, reparented frames, continuation deletion, and callback interference are not universally proved here.

## Evidence and challenges

- Authenticated all 193 runtime capsule payloads against externally supplied FILES digest `964dc83d0b53e1e35f915579daff0c99062e0a2595c6c339b645ca2ecc85b6f2` before executing its verifier in isolated, nonoptimized Python.
- Independently recounted 140 new subtests: 30 FAIL→PASS, 110 PASS→PASS. All 336 additional subtests unchanged PASS. Existing file outcomes remain 24 PASS, 10 expected FAIL and one separate OK harness. Neither this report nor the verifier treats those ten existing failures as passing tests.
- Both retained build receipts are successful, source restoration is recorded, and source/test/binary stability is checked by the runtime verifier. This is a shared combined build, not isolated upstream execution.
- The WPT has nonvacuous zero-offset geometry calibration, fixed-size overflow and auto-size normal controls, initial versus zero-first updates, doubled offset, restore-to-zero, dimension and other-item checks. All 70 configurations use LTR. Vertical-rl flex is intentionally omitted to avoid coupling to the separate final-size repair; vertical-rl block is included.
- `coordinate-challenges.py` independently checks 144 exact-integer examples across six axis/direction combinations, unequal predecessor/current sizes and distinct previous/current offsets. It checks stored normal and final used position, not only a final cancellation equation. Mutants using the used predecessor (72 distinctions), wrong current-conversion size (90), and omitting Finish positioning (96) are distinguished. These are finite mathematical checks, **not extracted C++ execution, machine-overflow proofs, or compiled native mutation tests**.
- Ordinary arithmetic-domain limits and the existing unconstrained-RTL container assertion remain. This patch does not widen coordinate arithmetic or establish safety for arbitrary int32 inputs.

## Remaining gates and scope

No mandatory native semantic correction identified. The separate doubled-direction RTL pair is now authenticated and accepted as additional finite evidence: 304 payloads, FILES digest `42e6e88f304296756edd1a23c7c5b9b46b800d888eb1264d7132e4f7e2b013fd`; 60 FAIL→PASS and 220 unchanged PASS across 280 matrix rows. All 61 existing non-flex file outcomes remain unchanged (24 PASS, 36 expected FAIL, one OK harness containing three PASS subtests). Both builds passed and restoration is recorded. `RTL-RECHECK.json` retains the fresh verifier result. I read the exact fixture delta: RTL measures inline origin from the right edge in horizontal mode and bottom edge in vertical modes, while preserving block-direction conversion and zero-offset calibration. This is a separate diagnostic suite, not a change to the original 140-case landing WPT. `TEST-GAPS.md` records focused percentage/end-side and caller coverage suggestions. The full seven-part proposal formal scope remains open: constructor/normal readiness, actual conversions with all executed machine bounds, callback/status/tracker/overflow and ordered lifecycle composition must still be discharged. The preliminary algebraic lemmas do not replace those obligations.

No production source, test, browser, build, or Git state was changed by this review.
