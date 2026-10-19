# Zero-prefix candidate source binding

This adds source binding to the preserved 17-audit preparation. `PREPARATION.json`, `Fold.lean`, its checker, controls, and README are unchanged. The older README describes that earlier preparation, not this binding's final status.

## Lineage and replay

`CANDIDATE-SOURCE-v1.json` names actual Git parent `11482ee213bf63c749b6d205c2c7591d783bdaa8`. That commit contains neither the RGB missing-mask fix nor the zero-prefix fix. `source_binding.py` reconstructs five authenticated snapshots:

- The parent mix implementation and unchanged flag-definition file.
- The parent mix file with the exact reviewed one-line RGB insertion: the prezero baseline.
- That baseline with the exact zero-prefix loop delta: the candidate.
- The parent mix file with only the zero-prefix delta, demonstrating that the two source changes commute.

This is explicit patch lineage, not a claim that the prezero baseline is an existing commit. A source-only companion can run before either native patch is applied:

```
python3 artifacts/css-color-zero-prefix-proof-v1/candidate_check.py NEW_OUTPUT_DIRECTORY --snapshots-only
```

Omit `--snapshots-only` to additionally require the live mix file to equal the candidate and the flag file to equal the authenticated snapshot. Both modes compile the original Lean audits and four semantic mutations in a fresh directory, reject nine malformed diagnostic records, and run fifteen source controls. Snapshot mode does not verify the live tree. Generated snapshots and compilation outputs need not be committed.

## Reviewed bridge

`specStack` reads the normative ordered stack algorithm from CSS Color 5 `#color-mix-result`. `specPair` independently chooses progress `b / (a+b)` for positive sums and `1/2` otherwise. Nonnegative weights bridge that comparison to the native zero test. `nativeStep` maps the loop's skip condition, normalized/raw weight branch, helper call, and retained combined weight. `nativeFold` maps the loop's left-to-right iteration.

The bridge is manually reviewed, with exact source-delta checks and source-shape rejection controls. It does not parse Rust into Lean or mechanically translate specification prose. Hash authentication guarantees that review applies to these bytes; it does not turn the bridge into a theorem.

The entire candidate loop is checked in order, including conversion, helper arguments, and accumulated-weight assignment. The surrounding normalization flag, zero-total early return, initialization and final alpha scaling are checked, and exact whole-file lineage disallows any unrelated edit. The unchanged normalization flag definition is authenticated separately. Both possible native patch orders produce the same candidate bytes.

`raw_step_unchanged` and `raw_fold_unchanged` cover arbitrary signed rational weights. Source inspection additionally establishes that `normalize == false` takes the same skip condition and helper arguments for native floating-point values, including cancellation and nonfinite comparisons: the added `!normalize` is true and the normalized branch is unreachable. This latter statement is a control-flow review, not a Lean floating-point theorem, and does not claim raw animation/gradient semantics are correct.

The full generic proof assumes compatible interpolation. The instantiated single-channel proof covers missing/present channels with rational arithmetic, including alpha carry-forward. It does not establish full varying-alpha color premultiplication. The separate WPT oracle review derives that one case using premultiplied colors; all its endpoints have the same red coordinate.

The all-zero-total early return remains unchanged and outside this refinement. The rational theorem permits all-zero lists as a mathematical input; that does not establish native conformance through the early return. Underflow, overflow, nonfinite normalized weights, signed zero, omitted-weight normalization, conversion, hue, final rounding, and serialization remain outside the theorem.

## Specification provenance

`color-mix-result.html` is the complete result subsection from the already archived CSS Color 5 fetched on 2026-10-18. `CANDIDATE-SPEC-v1.json` records its full-document and subsection hashes and issue 14013's archived hash. The algorithm explicitly requires the half-progress step when the combined percentage is not positive. Its nearby nonnormative note about order independence in rectangular spaces does not hold in general when missing components make an intermediate result observable; the ordered algorithm and June 2026 correction govern these cases.
