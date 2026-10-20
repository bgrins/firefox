# Percentage-padding measurement-cache discrepancy

Both restored project Firefox and installed release produce the same 18 rows: four discrepancies and 14 controls. Every initial layout, reconstructed-layout baseline and requested width/padding calibration passes. The fixture is unchanged across runs. Source and binary hashes are stable within both runs; isolated profiles were removed. The first sandbox attempt failed to bind localhost before starting a browser.

## Observable result

A 600px outer row contains a 100px/200px fixed sibling and a flexible inner row. The inner target has fixed 100px content width and 10% top padding. Its peer has the same one-line font and zero padding. Both share first or last baseline alignment.

Changing only the sibling changes the inner width from 500px to 400px and padding from 50px to 40px. Target height updates to 60px, but the peer remains at its old 50px offset and the baselines differ by −10px. Growing reverses the discrepancy. A fresh copy at the same final state has aligned baselines and the expected geometry. Constructing that copy does not repair the warm tree. Restoring the original sibling size produces the opposite stale offset; this is an additional observed failure, not a passing restoration calibration. Literal 50px padding, zero padding and no-change controls pass.

## Normative trace: REACHED for the fixture

The retained current [Flexbox §4.2](https://drafts.csswg.org/css-flexbox-1/#item-margins) resolves percentage padding against containing-block inline size. The measured 500/400px widths therefore require 50/40px padding. [Flexbox §8.3](https://drafts.csswg.org/css-flexbox-1/#align-items-property) requires participating items to share aligned baselines. [Alignment §6.4](https://drafts.csswg.org/css-align-3/#baseline-align-self) and §9 supply the first/last alignment relation. These ordinary horizontal one-line text boxes have natural baselines; the zero-size inline-block markers use baseline vertical alignment. No synthesized baseline, scrolling, relative positioning, fragmentation or collapsed item is involved. Fresh reconstruction is a second history-independence control, not the sole oracle.

## Source chain and remaining causal boundary

`CachedBAxisMeasurement::Key` contains computed content size, min/max block sizes and available block size, but no padding. `MeasureBSizeForFlexItem` returns the measurement when the subtree is clean and this key matches, without a measuring reflow or `SetAscent`. `SizeComputationInput::InitOffsets` already updates the used-padding property and sets `HasPaddingChange`; `InitResizeFlags` observes that bit, but the measurement-cache validity test does not. `NeedsFinalReflow` later compares final-cache padding, and can therefore reflow the child after cross-size/baseline positions have been selected. The four relevant complete flex bodies are byte-identical between retained proof source and the tested live source; `SOURCE-BODIES.json` records that transfer. Both complete sources are retained.

The runtime result confirms stale observable layout. It does not instrument the exact cache-hit/dirty-bit branch, so that causal path remains a source-supported hypothesis. A repair should invalidate or qualify the measuring result before baseline/cross-size selection; merely refreshing final-cache records cannot establish that earlier observers were current. No native repair is proposed in this artifact, and no dependency on pending allocation/baseline repairs is claimed: release reproduces identically.

## Full-scope consequence

The lifecycle proof's geometry/cache consistency alone cannot establish freshness of the earlier measuring baseline and cross-size observer. This counterexample is retained as an additional F11 provider obligation; all 16 original obligations remain active. No frozen predecessor theorem or source is changed.
