# Separate signed ligature repair review

Status: native patch, font tables and recorded paired runtime evidence reviewed independently of the root author. This is not independent acceptance of this worker's formal companion. Current-primary-spec freshness remains open because retrieval failed authentication; no current-spec acceptance is claimed.

## Source and arithmetic

The candidate `gfxTextRun.cpp` has SHA256 `cccb5d91b51904481aad022405f2a837f029cb1b099af18607faff6064849c0e`. Replay reconstructs the complete file from the original by exactly the approved signed quotient and three product substitutions. `ComputeLigatureData` executes completely in the extracted native bridge. A supplemental slice of its arithmetic exercises uint32 count endpoints without claiming to allocate buffers of that size.

`gfxHarfBuzzShaper::ShapeText` passes shaped glyph positions to `SetGlyphsFromRun`. The latter preserves signed advances in detailed records when they cannot use the simple-glyph encoding. `ComputeLigatureData` accumulates that signed width, counts clusters and apportions selected clusters. In the original expression, the unsigned cluster count converts the signed negative width before division. A small negative width therefore produces a large positive partial advance. The candidate first widens the numerator to signed64; uint32 denominator/counts are representable there. Truncation and the final remainder remain explicit. The int32 total-width domain bounds quotient-products even when counts span uint32.

All nine complete shaping/measurement/partial-drawing definitions are retained by replay in `negative-source-callers/INVENTORY.json`. They expose direct advance measurement, partial measurement, break/measure and draw consumers. These surrounding functions are source-only here, not claimed as universally verified or compiled by the ordinary emphasis bridge. Signed accumulation overflow and downstream clipping/rasterization remain explicit boundaries.

## Independent font decoding

The actual WPT font has SHA256 `551d1cb3037b0b22cff1473fa2c21a613b30fae3b9c2ecd068a6d5e2eb57a8a4`. The review decodes SFNT checksums, cmap, hmtx, script/language/feature lookup chains, GSUB ligature coverage and signed GPOS ValueRecord bytes directly, without fontTools or the producer's assertions. A/B/C map to glyphs35/36/37. All three nominal advances are1000 units with1000 units/em. `liga` maps AB to C; `kern` supplies C xAdvance−2500. The resulting advance is−1500 units (−30px at20px). This establishes the font input, not a universal HarfBuzz or sanitizer theorem.

## Recorded browser evidence

An independent per-name oracle predicts exactly four original failures: AB with both features enabled, split as adjacent Text nodes or differently colored spans, in both directions. The other44 cases are controls. The candidate passes all48. Positive calibration asserts exact20/40px widths; negative cases assert only that a negative advance does not turn into a large positive width. The test intentionally does not prescribe exact negative CSS box width or painted clipping.

The26 regression raw result keys agree before/after. Retained execution receipts show25 new-suite pins and80 regression-suite pins stable within each run; only the source file and two browser binaries differ across the pair. Historical binary hashes are evidence from those receipts, not freshly inspected historical executables. This worker did not run a browser or build.

The WPT metadata identifies CSS Text's boundary-shaping section. The fresh CSS Text3/OpenType GPOS retrieval attempts and failures are retained under `spec/`. Network authentication failure prevented current primary text verification. The arithmetic finding, actual font bytes and recorded observations are established separately; normative freshness is an explicit open review gate.

## Reproduction and acceptance boundary

The parent authenticated source-only replay invokes `negative_review.py` and writes `NEGATIVE-INDEPENDENT-REVIEW.json`: exact retained-file checks, decoded font fields,48 predictions, paired pins and complete source-only inventory. The same replay separately compiles signed/legacy and classifier variants, arithmetic mutants and matching kernel witnesses. Root must arrange independent review of the full formal companion and decide the separate repair's acceptance after the remaining normative gate. No production/WPT edits or frozen-v1 changes are included here.
