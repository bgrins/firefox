# Central synthesis origin audit

Source-backed defect lead; browser reproduction and native acceptance remain pending. No native, index, browser, build, or installed-test changes were made. The attached six-case WPT is an unexecuted proposal.

## Specification trace: REACHED

Starting case: two empty inline-blocks in one vertical line, identical sizes and margins, differing only in explicit `baseline-source: first` versus `last`.

1. [CSS Inline 3 baseline-source](https://drafts.csswg.org/css-inline-3/#baseline-source) selects the preferred first/last set for an independent inline formatting context.
2. [CSS Align 3 baseline export](https://drafts.csswg.org/css-align-3/#baseline-export) gives an empty block container no content-derived set: there is no contributing line or child.
3. [CSS Inline 3 atomic synthesis](https://drafts.csswg.org/css-inline-3/#baseline-synthesis-box) therefore places the central baseline halfway between the margin edges.
4. [Dominant baseline](https://drafts.csswg.org/css-inline-3/#dominant-baseline) defaults to central for vertical mixed orientation. [Baseline alignment](https://drafts.csswg.org/css-inline-3/#baseline-alignment) aligns corresponding baselines. Both boxes must therefore have coincident margin-box centers, regardless of source preference.

Official drafts read 2026-10-23: Inline 3 dated 2026-10-14, Align 3 dated 2026-10-21. `webspec-index` is unavailable; official web pages supplied the trace. Installed `searchfox-cli` does not support `--permalink`; no fabricated permalink is supplied.

## Native path and lack of compensation

Authoritative source is HEAD `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`, with hashes in SOURCE-PINS.json. Searchfox was used for discovery; the pinned local bodies establish the result.

- `nsLineLayout::PlaceFrame`: inherited matching writing modes avoid its orthogonal/different-block-direction shortcut. Explicit source and a non-line-participant inline-block select `GetLogicalBaseline` with the requested group and `BaselineExportContext::Other`, bypassing the metrics-ascent shortcut.
- `nsBlockFrame::GetNaturalBaselineBOffset`: empty line iteration yields Nothing. No button/input or scroll-container specialization applies. `nsBlockFrame::SynthesizeFallbackBaseline` uses the margin-box helper.
- `SynthesizeBOffsetFromInnerBox`: default baseline becomes central. The central/mathematical/middle branch ignores the requested group, including its locally adjusted `group` variable.
- `nsIFrame::GetLogicalBaseline`: First uses the result directly; Last returns `BSize - result`. This is the normal documented origin conversion, not compensation for a group-independent helper.
- The baseline branch in `nsLineLayout::VerticalAlignFrames` positions the box at `baselineBCoord - mAscent`. The same surrounding line adjustment applies to both siblings; it does not undo a difference caused by the source preference.

For vertical-rl, BSize=100 and margins 10/30, the shared helper yields 60 for both groups. The logical query yields 60 for First and 40 for Last. The physical central baseline is unique; source preference cannot legitimately move it by 20px. With symmetric 20/20 margins the discrepancy vanishes. Vertical-lr also needs testing: its line-inverted selection changes which margin enters the helper, but does not restore group dependence.

The specimen uses only default central alignment, empty spans, visible overflow, no fonts/text/descendants, no fragmentation, and small representable integer dimensions. The six named cases cover both vertical modes, both asymmetric margin orders, and symmetric controls. Assertions validate the effective source, writing mode, orientation, margin values, empty content, box dimensions, one-line placement, repeat stability, and equal horizontal positions. Width equality plus equal margins makes equal left edges equivalent to equal margin-box centers. The first rectangle query may flush the whole line; repeated reads are stability checks, not independent first-query tests.

## Recommendation

Run this exact fixture on the restored working browser, then independently on normalized HEAD before accepting a preexisting bug. Source predicts four asymmetric failures and two symmetric passes, but those are predictions, not observed results. A later fix must produce one physical synthesized baseline and encode it relative to the requested origin; retain existing central rounding and explicitly test inverted writing modes. This audit does not select a final native patch or claim coverage of mathematical/middle overrides, odd app-unit rounding, or content/padding-box synthesis.
