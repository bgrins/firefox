# MathML tab-cache origin: independent adjudication and repair design

## Finding

The root-owned browser receipt confirms the previously predicted source-origin mismatch on the pinned local project build. The corruption is observable in ordinary, layout-flushing Range geometry. It is not evidence that MathML must preserve CSS tabs, and it does not establish release-browser behavior.

`review.py` independently authenticates the 23 retained source/input snapshots against the receipt, checks all 25 before/after pins, verifies the served HTML/font digests, and compares raw observations. Both runs are identical; each contains three identical geometry samples per fixture. MathML and HTML Ahem glyph calibrations are 20px. The four unique failing glyph-width observations are:

| Fixture | Character | Observed width | Calibrated width |
| --- | --- | ---: | ---: |
| MathML leading tab, tab-size 8 | A | 160px | 20px |
| MathML leading space, tab-size 8 | A | 160px | 20px |
| MathML leading space, tab-size 8 | B | 0px | 20px |
| MathML leading tab, tab-size 4 | A | 80px | 20px |

The two-leading-tab fixture instead assigns 140px to the second leading tab and moves A to x=140px relative to the element, while A's own width remains 20px. This separate position symptom is retained but is not an assertion in the portable glyph-width test.

All raw rows remain in `evidence/receipt.json`; the independent digest and normalized observations are in `REVIEW.json`. HTML tab widths are not treated as equivalent to MathML tab widths: the label occupies inline space and changes the tab-stop origin. No candidate browser run or build was performed by this worker.

## Actual observable call chain

The Range path uses `AbstractRange::GetPartialTextRect` and `ExtractRectFromOffset`, not `GetCharacterRectsInRange`. After layout flush, it starts with the text frame rectangle and clips its ends using `nsTextFrame::GetPointFromOffset`. That method creates a display `PropertyProvider`, calls `InitializeForDisplay(false)`, normalizes the offset through `UpdateIteratorFromOffset`, then measures the prefix through `GetPointFromIterator` and `gfxTextRun::GetAdvanceWidth`.

`ReflowText` unconditionally applies token-leading trim when `TEXT_IS_IN_TOKEN_MATHML` is set. `GetTrimmedOffsets` instead returns the untrimmed interval immediately for significant whitespace. `CalcTabWidths` stores offsets relative to the reflow provider's trimmed start. Display applies the same offsets relative to its untrimmed start. This assigns tab spacing to the wrong source index. `ExtractRectFromOffset` clamps to the frame rectangle, explaining how a shifted later boundary can become a zero-width B range.

The MathML producer sets the token bit when installing/inserting/appending token text children. The full text-run construction source expressly exempts `mtext` from `TEXT_USE_MATH_SCRIPT`. The fixture has ASCII A/B, Ahem, zero letter/word spacing, no text transform, no kerning/synthesis and no justification. There is no partial grapheme, stretching operator, ancestor transform or text-combine behavior needed to explain these widths.

`REVIEW.json` binds 15 complete source definitions spanning the geometry consumer, preparation, cache and reflow paths. The actual browser receipt snapshots are used; the earlier static audit stays sealed.

## Smallest coherent proposed source repair

`proposal/leading-origin.patch` changes only `nsTextFrame::GetTrimmedOffsets`:

1. Significant whitespace can return immediately unless this is a MathML token text frame.
2. Token text participates in the leading-trim condition even if it is not marked start-of-line, matching the existing `ReflowText` condition. `NoTrimBefore` still prevents trimming.
3. Significant whitespace returns after leading trim, before the existing trailing-trim branch.

The third step matters. Merely exempting MathML from the original early return would also start trimming significant trailing tabs. `BreakAndMeasureText` tracks trailing `CharIsSpace()` in its trimmable-width state, while tabs are a distinct glyph classification. `TrimTrailingWhiteSpace` has a null-line-container measurement path explicitly premised on not processing tabs. This proposal does not introduce significant trailing-tab trimming.

For ordinary non-MathML text, all early returns, leading/trailing conditions and flags are unchanged. For MathML with non-significant whitespace, the only extra case is leading trim away from start-of-line, which agrees with the existing token reflow rule. For MathML with significant whitespace, the provider start now agrees with existing leading token trimming. This is a scoped consistency repair; it does not change CSS whitespace computation or impose nowrap on every MathML element.

The artifact checker verifies that the full candidate differs from the authenticated original only in this complete function and that the supplied patch exactly reproduces that delta. It has not compiled, applied or executed the candidate. Root owns formatting, standalone applicability, paired regression results and final source binding.

### Limits and risks

- MathML leading/trailing preservation, all-whitespace nodes, preserved newlines, NoTrimBefore/NoTrimAfter, multiple token text children and continuation boundaries need regression coverage. The proposal preserves significant trailing behavior rather than solving all historical token whitespace issues.
- `GetTrimmedOffsets` serves display, measurement, selection and justification. Its token-leading normalization deliberately reaches all those consumers; this is preferable to changing one Range callsite while painting uses the wrong origin.
- There is no new allocation, property field, cache invalidation or source run rebuild. Token prefix scanning now occurs in significant-whitespace display preparation; its cost is linear in the trimmed prefix, as in existing reflow trimming. Repeated queries can repeat this scan.
- Element widths 340px/500px versus full-text range width 180px are separate retained observations. Intrinsic sizing and MathML child box sizing can include leading preserved whitespace through other paths. Do not assert that this patch fixes those dimensions without measuring them.
- The broader persistent-cache coverage, source epoch, scheduler, font and borrowed-property lifetime contracts remain open. This local origin repair does not prove them.

## Browser regression oracle

`proposal/token-leading-whitespace-range.html` is a draft WPT-style test, not installed in the live test tree. It creates mtext fixtures with normal/pre whitespace, tab-size 4/8 and no/space/one-tab/two-tab prefixes. Each test compares single-character A/B Range widths with isolated same-style A/B calibrations and verifies that both calibrations are 20px.

This oracle does not assert whether a tab is collapsed, preserved, trimmed or expanded, does not compare HTML and MathML tab stops, and does not prescribe element widths. It should hold both when a browser follows Core's nowrap requirement and when Firefox retains its current preformatted extension. CSSOM View defines horizontal text-range bounds using text advance width; the isolated ASCII glyphs and font/style controls eliminate the relevant shaping exceptions. [CSSOM View Range geometry](https://drafts.csswg.org/cssom-view/#dom-range-getclientrects).

MathML Core still requires `white-space` to be treated as nowrap on MathML elements. That rules out using a required 140px MathML tab width as the normative oracle. The token-edge whitespace question is separately tracked in Core issue 149. [MathML Core CSS styling](https://w3c.github.io/mathml-core/#css-styling), [issue 149](https://github.com/w3c/mathml-core/issues/149).

Recommend a normal WPT geometry regression if cross-engine/manual review confirms this narrow oracle; a Mozilla-only test is the fallback if an actual normative geometry ambiguity is found. The mere use of `white-space: pre` does not require a Mozilla-only test when its assertions hold under both supported behaviors. Root should retain the raw original diagnostic beside the narrower assertions.

## Root validation plan

1. Review/apply the sole-function proposal and run the draft test against exact original/candidate bytes, with source/binary/font/HTTP pinning.
2. Require calibrated A/B widths in all rows; retain all prior raw element/tab/position observations as diagnostics. Do not require unrelated element-width changes to accept the narrow repair.
3. Run relevant MathML token/whitespace, Range geometry and tab-size tests. Include trailing-tab and all-whitespace controls specifically to guard against the rejected broader early-return change.
4. Bind the formatted final candidate and minimal native/WPT patch before any formal or native acceptance. Current proposal is a design handoff, not acceptance.

Known-issue research from the sealed caller audit remains applicable: bug 970710 fixed a different measurement/justification flag disagreement; bug 729851 concerned privileged no-flush missing caches. Neither is shown to duplicate this confirmed origin mismatch. No broader novelty claim is made.
