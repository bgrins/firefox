# Complete clamp candidate model

This extends the preserved preparation capsule with the complete candidate control flow. `Clamp.lean`, `SOURCE-v1.json`, and `PREPARATION-v1.json` remain unchanged.

## Proven scope

`Candidate.lean` models all leaf gates, strict compatible-unit folding, the refined relative-infinity result gate, NaN rejection before comparison fallback, all four winner branches, and retention of unknown/nonleaf operands. `candidate_preservation` proves preservation for arbitrary finite nested trees and arbitrary environments/operator interpretations, conditional on the explicit native bridge certificates described below. This structural theorem includes both the compatible-unit and mixed-unit paths.

`Scaling.lean` proves strict clamp commutes with same-unit scaling for arbitrary exceptional coefficients and finite nonnegative rational bases, subject to the exact refined guard: if an input is infinite, the folded coefficient must be nonfinite. Positive bases preserve the full scalar order; at zero, infinities resolve to NaN and a permitted nonfinite result also resolves to NaN. The preparation's finite coefficient theorem covers zero-basis signed-zero behavior. Negative percentage bases remain excluded.

`Instances.lean` constructs complete bridge instances for canonical values, common relative units, and comparison fallback. The relative instance yields an unconditional arbitrary-tree preservation theorem for the modeled nonnegative rational contexts. Controls cover every winner, all NaN positions, unknown upper trees, unavailable raw values, unresolved percentage hints, safe infinite/NaN relative results, rejected finite results with infinite relative inputs, and negative zero after zero-basis scaling. The bridge assumptions are therefore inhabited and exercised; the native bridge remains manual.

## Exact native bridge premises

`Bridge.compatible` classifies each successful, accepted two-operation `try_op` chain into one of two independently proved cases:

- Canonical: each input and result has the claimed environment-independent value, and the result is the strict raw min/max coefficient calculation.
- Same relative unit: all inputs and result use one common finite nonnegative basis; result raw coefficients equal strict raw min/max; and the accepted source guard implies `safeRelative`.

The local `Leaf::try_op` discriminant check and `NoCalcLength::try_op` same-unit check support this classification. Absolute length operations normalize to px. Other supported numeric categories use their canonical units. Relative length operations are allowed only for matching units. A complete successful chain therefore cannot silently mix different relative units.

`Bridge.nonNan` requires every fallback-admitted leaf with `is_nan() == Ok(false)` to resolve to a non-NaN value in the permitted environment. This uses finite nonnegative unit bases, known raw coefficients, exclusion of unresolved percentages, and rejection of relative infinities.

`Bridge.comparison` requires successful native comparison certificates to respect resolved order: Less implies `≤`, Greater implies `≥`, Equal implies equality. Strict inequalities would be too strong when distinct finite coefficients both resolve to the same signed zero at zero basis. The source's cross-sign branch, canonical comparison, and same-relative-unit comparison support these weaker obligations.

These are explicit source-reviewed premises, not Lean extraction of Rust or a verified native evaluator. The models retain raw NaN until the calculation boundary. They do not assume all native CSS leaf conversions preserve exceptional values: the separately observed `.finite()` length-conversion defect is outside this clamp rewrite and is not repaired or certified here. The structural theorem preserves a supplied leaf/operator interpretation; it does not establish general CSS evaluation conformance.

## Replay and source reconstruction

```
python3 artifacts/css-clamp-nan-proof-v1/check_v2.py artifacts/css-clamp-nan-proof-v1/replay-NEW
```

Add `--live` to require the exact native candidate and helper hashes in the current tree. Default snapshot mode supports the preceding proof companion commit before the native patch is applied.

The replay reconstructs the original generic source from commit `11482ee213bf63c749b6d205c2c7591d783bdaa8`, applies the separately recorded exact mod/rem delta to recover the pre-clamp source, then applies the clamp delta to recover the final candidate. It also applies only the clamp delta directly to the original revision and verifies the standalone result hash. Helper sources are reconstructed from the same immutable commit and authenticated. No source archive, browser binary, or generated Lean object is needed in the source companion.

The final candidate generic-source SHA-256 is `63a9b384909ddd08ef254dce9ca438ce8357346171caa759064e814447653637`. It corresponds to `candidate-calc-final.rs` in the fix evidence.

The checker replays the original preparation, builds each new module in fresh directories, checks exact axiom inventories, compiles eight additional incorrect variants, and requires reviewed theorem-local errors. Together with preparation: 47 unique audited declarations, 15 compiled mutations, 24 poisoned-record guards, and 13 source feature controls. Source feature controls are text-binding controls, not Rust compilations.

## Limits

Exact rational finite values model ordering/scaling, not IEEE rounding, overflow, underflow, or every native conversion. The native type/unit classification, finite basis constraints, and comparison bridges remain explicit manually reviewed obligations. Arbitrary opaque operators are interpreted consistently across the rewrite, not independently proved correct. Parsing, dimensional type inference, root censoring, CSS `none` endpoints, browser execution, and general Stylo conformance are not proved. Browser evidence is maintained by root separately.
