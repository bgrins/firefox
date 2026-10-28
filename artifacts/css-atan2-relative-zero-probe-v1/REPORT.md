# Relative atan2 zero-basis probe

Source-reachable candidate; no browser execution or accepted bug is claimed here. The five pinned ledger/readout files contain no atan2 match, and no earlier artifact directory name contains atan2. This bounded dedup is not an exhaustive search of every research file. Held fix120 concerns Sign folding and remains held.

The actual captured `CalcNode::Atan2` simplifier checks same-unit leaves and uses `unitless_value` before constructing an angle. It does not require `canonical_value`. Relative leaves can therefore disappear before their basis is known. Progress has another coefficient-based branch; this probe does not test it or count another bug.

The primary chain is [trigonometric functions](https://drafts.csswg.org/css-values-4/#trig-funcs), [argument ranges](https://drafts.csswg.org/css-values-4/#trig-infinities), [simplification](https://drafts.csswg.org/css-values-4/#calc-simplification), and [computed values](https://drafts.csswg.org/css-values-4/#calc-computed-value). The zero table defines atan2(+0,+0) as +0deg. Non-arithmetic simplification requires sufficient information; computed-value simplification uses the em basis. Thus the positive-positive witness predicts 45deg at font10 and 0deg at font0. This source/spec prediction is pending browser evidence. Negative quadrants include signed-zero pixel controls; equivalent positive/negative180deg matrices cannot distinguish serialization sign.

Load probe.js and call `probeAtan2RelativeZero()` in a fresh document. Four same-node quadrant sequences use font10→0→10, yielding12 snapshots. Literal-angle and resolved-pixel controls calibrate the matrices; positive controls remain fixed. The disposable iframe is removed in finally. Full raw values and support are returned without assertions, preferences, registrations, external resources, or automatic acceptance. Record browser provenance separately. Syntax check135dc1/0 passed; callbacks have not been run by this author.

The native branch is pinned separately from this script in the parse-mode design artifact's captured generic calc source. No native mutation or global Sign change is proposed here.
