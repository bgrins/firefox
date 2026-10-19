# Tab-cache caller admission audit

## Result

The retained uncovered-cache model witness is still not established as reachable through ordinary browser operations. This audit found a sharper, unexecuted source-level candidate: MathML token reflow can trim leading preserved whitespace while the display provider retains it. Tab entries use a provider-relative origin, so an unchanged cache can then address a different character. The artifact probe tests this specific origin disagreement. It is not a browser result or an accepted defect.

No native, WPT, browser, build or Git changes were made. The existing full ownership and language scopes, including refuted partition claims, remain unchanged and open. This capsule adds source evidence, not universal C++ or scheduler refinement.

## Identities and checks

`IMPORT.json` identifies four source files copied from the sealed `measurement-query-v1` supplement. `CURRENT-SOURCES.json` separately identifies current-source caller snapshots; they are not substituted for historical inputs. The authenticated extractor compares 18 complete previous text-provider definitions with their current counterparts: all match. `SOURCE-BINDINGS.json` retains 27 additional complete definitions; all 12 that also exist in the historical text-frame snapshot match. Files can differ outside these definitions.

`check.py` authenticates the closed file inventory before importing the extractor, repeats all bindings and comparisons, checks the preserved input hashes, and validates the source-relative coordinate witness. It does not compile or execute Gecko. `JS-SYNTAX.json` records successful Node syntax checking only.

## Caller and provider trace

| Contract | Source evidence | Disposition |
| --- | --- | --- |
| Reflow prepares the provider before measurement | `nsTextFrame::ReflowText` ensures the text run, computes the trimmed source offset, positions `iter`, and constructs the reflow `PropertyProvider` with the block inline distance. | Source-established order; actual frame/skip-map readiness remains an admission. |
| Fitted text has fetched spacing | `gfxTextRun::BreakAndMeasureText` fetches initial/refill spacing before measuring that buffer and selecting a break; final metrics query the fitted interval using the same provider. | Supports a fitted-prefix coverage theorem. No claim that the complete native-loop/caller theorem was proved here. |
| Published continuation lengths restrict display | `ReflowText` derives `charsFit`, bounds the result, and calls `SetLength`; `nsInlineFrame::ReflowInlineFrame` creates a next-in-flow when the child is incomplete. `nsLineLayout::ReflowFrame` publishes bounds and calls `DidReflow`. | The audited inline path supports coverage; whole block, bidi, first-letter, overflow and interrupted-layout paths remain unclosed. |
| Normal preserved text has a shared origin | For ordinary HTML, significant whitespace disables leading trim in both `ReflowText` and `GetTrimmedOffsets`. Collapsing modes transform tabs to spaces; suppressed-newline preservation uses `COMPRESS_NONE_TRANSFORM_TO_SPACE`. | Conditional source invariant for admitted normal text, not all MathML or frame types. |
| Trailing trim does not expose a new tab | `TrimTrailingWhiteSpace` excludes significant tabs from its trimmable suffix. | Negative evidence against this ordinary extension route. |
| A fresh cache replaces an earlier epoch | Reflow provider starts without a borrowed cache. `CalcTabWidths` creates/replaces `TabWidthProperty` when needed; absent tabs remove stale property. `EnsureTextRun` removes a content-offset-mismatched cache only in its rebuild branch. | Cache validity is not a complete `(run, source epoch, provider start, style)` key. Caller freshness is required. |
| Text/style/font changes schedule reflow | `CharacterDataChanged` clears runs and requests reflow; `nsStyleText::CalcDifference` gives reflow for relevant whitespace/tab/spacing changes; `InvalidateFrameDueToGlyphsChanged` requests reflow. | Source triggers established. Complete scheduling/admission remains open. Clearing a run alone does not delete `TabWidthProperty`. |
| Public geometry flushes first | `AbstractRange::GetBoundingClientRect` / `GetClientRects` default to `aFlushLayout=true`; `CollectClientRectsAndText` flushes layout and rechecks connectedness. `Document::CaretPositionFromPoint` flushes layout first. | Ordinary API entry supports freshness. Internal `CollectClientRects` can request no flush and requires caller readiness. |
| Borrowed property remains alive | `FrameProperties::SetInternal` destroys replaced values and `RemoveAll` destroys properties. The provider borrows a raw `mTabWidths`; audited deletion in `EnsureTextRun` precedes construction. | No concrete dangling pointer found. Whole reentrancy/frame destruction exclusion is not proved. |

The older uncovered-cache witness remains meaningful as a violated precondition: tabs at positions 0 and 2, a cache prepared through 2, then a display query through 3 can produce `[8,8]` instead of full-reflow `[8,7]`. The native code asserts last-tab coverage before such borrowing. This audit does not remove that assertion premise or infer it from independently valid query states.

## MathML source-origin candidate

The exact source chain is:

1. `nsMathMLTokenFrame::SetInitialChildList`, `AppendFrames` and `InsertFrames` call `MarkTextFramesAsTokenMathML`, which marks text descendants with `TEXT_IS_IN_TOKEN_MATHML`.
2. `ReflowText` enters its leading-trim branch on that flag even when `WhiteSpaceIsSignificant()` is true. `GetTrimmableWhitespaceCount` uses the character-only whitespace predicates, which include tabs, rather than the style-sensitive predicate. `iter` and the reflow provider then start after that prefix.
3. `GetCSSWhitespaceToCompressionMode` can retain tabs under significant preformatted whitespace. `NewlineIsSignificant`, `ShouldSuppressLineBreak` and the style-adjuster source do not themselves impose MathML nowrap. The retained MathML UA stylesheet has no token-wide whitespace override. Actual anonymous-frame admission remains for the probe to establish.
4. `CalcTabWidths` stores each offset relative to `mStart.GetSkippedOffset()`. `mValidForContentOffset` records the frame content offset, not this trimmed start.
5. Display initialization calls `GetTrimmedOffsets`, whose significant-whitespace branch returns the original frame interval before trimming. It therefore can select a different origin without changing the frame content offset.
6. `GetSpacingInternal` applies the retained offsets relative to that display origin. It does not check that the cached offset still identifies a tab.

For `\tA\tB`, reflow's interior tab index 2 is stored as relative index 1; with display origin 0 that points at `A`. For `\t\tA\tB`, the interior tab index 3 is again stored as 1, which now points at the second leading tab. `ORIGIN-WITNESS.json` checks only this coordinate arithmetic and contrasting same-origin controls. It is not a native rendering oracle.

With the supplied 20px Ahem font and tab-size 8, the conditional prediction is a 140px interior-tab contribution. In the one-prefix case that contribution can enlarge the range for `A`; in the two-prefix case it can move `A`. Root should retain actual raw widths and reject this numeric prediction if font, shaping, token layout or source admission differs.

### Normative limit

MathML Core's current Editor's Draft treats `white-space` as nowrap on MathML elements. A preserved-tab result therefore cannot directly be called a violation of a Core rule requiring CSS preformatted tab stops. The candidate is first an internal consistency problem in Firefox's supported behavior. Core issue 149 separately tracks token-edge whitespace trimming; it does not settle the tab-cache origin contract. [MathML Core CSS styling](https://w3c.github.io/mathml-core/#css-styling), [token whitespace issue 149](https://github.com/w3c/mathml-core/issues/149).

## Probe handoff

Serve `mathml-cache-origin.html` and `Ahem.ttf` together. It waits for font readiness, constructs 12 MathML/HTML fixtures, and records three unchanged-DOM reads with per-character and full-range rectangles, computed whitespace/tab/font styles and two glyph calibrations. Read `window.probeResult` or call `await window.runProbe()`. This worker did not execute it.

Controls distinguish origin effects from ordinary font/whitespace behavior: no leading whitespace, one/two leading tabs, one leading space, tab-size 4, normal whitespace and HTML preserved text. Require Ahem calibration, stable input/source/binary pins and unchanged-DOM agreement. A root-owned browser gate should classify coordinates independently and retain all rows rather than define expected values from the suspect output.

If confirmed, first decide whether to normalize MathML whitespace to the supported specification or keep the current extension and unify provider origins. A cache-start field alone would detect the mismatch but would not define how display should measure the trimmed characters. A minimal repair must preserve the underlying source span and complete display/measurement/justification preparation contract.

## Existing coverage and bounded history

`EXISTING-TESTS.json` and `existing-tests/` retain the exact files inspected; none was run.

- MathML `ignored-properties-001.html` tests `white-space: normal`, not leading preserved tabs. Its local metadata allows up to 51 assertions; that is not evidence of this candidate's result.
- CSS Text `tab-size.html` calibrates leading and internal HTML tab stops. `tab-size-inline-001.html` covers inline tab-size changes. `tab-size-spacing-001.html` combines ordinary letter/word spacing. These do not exercise the MathML forced-trim/display-origin pair.
- The narrow local text reftest lookup found `word-spacing-01.html`; it does not establish broad dynamic cache coverage. Earlier bug 631035 discusses cache storage and dynamic tab-size testing, but no current local dynamic test was identified by this bounded search. [bug 631035](https://bugzilla.mozilla.org/show_bug.cgi?id=631035).
- Bug 729851 reports missing precomputed tab widths through privileged no-flush `drawWindow`; it remains listed as NEW in the retrieved record. This is historical evidence for the missing-readiness class, not current ordinary-web reachability. [bug 729851](https://bugzilla.mozilla.org/show_bug.cgi?id=729851).
- Bug 807891's old overflow path reached the same provider through `RecomputeOverflow`; its obsolete whitespace mode was removed and it was closed WORKSFORME. This audit does not revive that old read-overrun claim. [bug 807891](https://bugzilla.mozilla.org/show_bug.cgi?id=807891).
- Bug 970710 repaired inconsistent trimming flags between `InitializeForMeasure` and justification preparation. The retained code contains that consistency fix. The new candidate compares reflow's MathML trim with significant-whitespace display initialization instead. [bug 970710](https://bugzilla.mozilla.org/show_bug.cgi?id=970710).

Searchfox was used for discovery; an initial MathML query identified the ignored-properties test. Later recorded invocations failed DNS, and the installed CLI lacks a permalink option. Narrow local reads of identified/current files were used to complete the audit. This is bounded duplicate research, not a novelty guarantee.

## Exact remaining gates

1. Execute the artifact probe under root ownership; establish actual preserved-tab/token-frame/source-origin admission or reject the candidate.
2. For ordinary text, prove final fitted/published interval is covered by the maximum spacing buffer frontier, including continuation creation before every display/internal geometry caller. The prior theorem `fit <= requested length` alone does not establish this.
3. Join frame source/skip-map/style/font epochs and the provider's trimmed start to persistent property identity; retain actual reflow ordering and raw-pointer lifetime.
4. Extend beyond the audited inline route to block/first-letter/bidi/interrupted/privileged no-flush paths before claiming global last-tab coverage.

The most useful immediate next step is gate 1. If the source prediction is disproved, capture the preventing caller condition and use it in the origin-admission theorem.
