# Shared Integer range-policy proposal

Status: artifact-only candidate, no acceptance or Gecko/browser execution. The source-first lead is the retained `steps(calc(-10), start)` computed-value failure; source inspection found the shared policy omission. Formal results corroborate a conditional arithmetic obligation, not discovery or native refinement.

`Integer::resolve` now applies the stored CalcNumeric clamping mode after Number::get and before existing integer rounding. HEAD90 and installed118 variants each change exactly one expression. The installed variant retains both accepted118 f64 promotions. Inline integers, unresolved/context-dependent trees returning None, unrestricted All mode, parser admission and function-specific checks are unchanged.

The two standalone patches contain only number.rs and the new 24-case timing WPT. Scratch Git apply/check/reverse passes against their exact respective saved preimages. This is textual applicability, not a clean-base runtime result. No metadata changes are included. Existing computed/valid/invalid timing tests should be controls. Only the existing negative-calculated-step expectedFAIL block is a potential metadata cleanup after a successful paired result; the other three retained timing failures are separate.

## Tests and diagnostics

The landing fixture covers animation and transition timing properties, eight calculated negative/zero/one/fractional/ordinary inputs each, three invalid literal controls each, and replacement/reset. Each calculated case uses a fresh element and verifies declaration admission before its computed-value assertion. Inert registration finds exactly24 unique names; Node syntax passes, but callbacks were not run. No huge counts, context-dependent units, jump-none minimum2 claim or broad function-range repair is introduced.

`subgrid-calc-zero-diagnostic.html` is separate and excluded from both landing patches. Two-column 200px spans limit expansion to three lines. Its literal repeat(1) twin must first calibrate the resolved line-name serialization `subgrid [fixed] [auto] [tail]`; only then does it compare calc(0). This prospective literal/geometry oracle has not been browser-verified. A failed calibration is inconclusive, not a defect witness. No negative repeat is executed. The source predicts cached count1 versus2 despite computed repeat count1, potentially allowing auto-fill to consume the final tail. See the prior audited source chain; specified style serialization alone would not prove placement.

## Extracted arithmetic check

`replay.py` authenticates saved sources, extracts native normalize/get/clamp methods and both integer rounding expressions, and constructs a scalar facade for an already resolved Number leaf. The parser, CalcNode/context traversal, enum storage and real Servo types are not compiled. The equality premise is the same already-resolved Number leaf on both routes; arbitrary context-dependent CalcNodes are outside this helper. The facade wires the source-confirmed callback order explicitly:

1. Number::get normalizes NaN to0 and limits infinities to finite f32 extrema.
2. Both candidate context-free and context-bearing paths apply the stored mode to that value.
3. The context-bearing path repeats normalize/finite limiting, then applies its original rounding expression.

Sixty exact binary32 bit patterns cover NaN payloads/signs, infinities, signed zeros, subnormals, fractional and integer boundaries, and large odd values. All four enum modes (All, NonNegative, AtLeastOne, ZeroToOne) and two source epochs yield480 rows per optimization. The first three are the audited Integer parser modes; ZeroToOne is additional enum-level coverage, not a newly claimed Integer caller. Opt0 and opt2 output bytes agree. Candidate/context outputs agree in all480 rows; old/context differ in92 HEAD90 rows and93 installed118 rows. An independent Python Fraction decoder computes normalization, policy, ties-to-positive-infinity rounding and signed32 saturation: installed118 candidate has zero disagreements; HEAD90 retains seven arithmetic disagreements. These are deliberately not hidden by the range repair. This is finite evidence, not a universal IEEE/parser/compiler proof. AtLeastOne of a raw NaN yields1 because normalization precedes the clamp; clamping raw NaN is not the modeled native order.

The helper is built using existing rustc with overflow checks at opt0/2; no sanitizer claim is made. Owned executable and Lean object products are removed by TemporaryDirectory. Source/log/receipt outputs remain for review.

## Conditional formal statement

`RangePolicy.lean` reuses the existing `CssIntegerRounding.round_max` and `round_integer` proofs. Its one new general result characterizes precisely when omitting an integer lower clamp is invisible: `round(max minimum value) = round value` iff `minimum <= round value`. Concrete checked examples distinguish negative witnesses from a below-minimum fractional input whose rounded output already meets the range. The false universal omission claim is rejected. No new credit is assigned to the reused commutation theorem. This is rational arithmetic with an integer threshold; finite normalization, saturation, IEEE operations and source/controller correspondence remain external. No canonical registration or count changes.

## Reproduction

From the repository root, choose absent output paths:

```
python3 artifacts/css-integer-resolve-range-repair-v1/replay.py --output /tmp/integer-range-review
python3 artifacts/css-integer-resolve-range-repair-v1/check-package.py --output /tmp/integer-range-package-review.json
```

The retained successful helper/check outputs are in results/ and PACKAGE-CHECK.json. Earlier development attempts encountered a Lean root-directory invocation error and an insufficient contradiction tactic; both were corrected before the successful replay, without changing the mathematical statement or Rust results. No native source, parent index, browser, canonical library or Gecko build was modified. REFERENCES selects the prior audit/review and118 proposal; this package does not claim recursive closure of their full dependencies.
