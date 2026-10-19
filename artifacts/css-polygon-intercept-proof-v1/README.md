# Polygon intercept proof companion

## Scope

The repaired `nsFloatManager::PolygonShapeInfo::XInterceptAtY` delegates its
intermediate multiplication/division to `NSCoordMulDiv`. This companion establishes
integer arithmetic properties under the reviewed bounded-difference contract. It
preserves **x1 + truncTowardZero((y-y1)*(x2-x1)/(y2-y1))**. It does not truncate the
whole interpolated real value, replace the arithmetic with floating point, or
claim complete CSS Shapes correctness.

The primary polygon definition supplies straight edges. Its prose does not specify
Gecko's app-unit truncation implementation. `css-shapes-1.html` is a retained current
primary snapshot; `SPEC-v1.json` records its URL, retrieval time and hash. The formal
integer model is an explicit refinement of that geometric boundary, not an automatic
translation of the whole CSS specification.

## Domain and source correspondence

Let M = 1073741823 and D = 2M = 2147483646. All five endpoint/query coordinates are
representable signed32 integers; y1 < y2; y lies inclusively between them;
0 < y2-y1 <= D; and -D <= x2-x1 <= D. Absolute final coordinates need not stay
within [-M,M]. Common representable translations can move them outside that range.

The source-domain review in `artifacts/css-polygon-intercept-design-v1/REPORT.md`
traced finite coordinate resolution through `ShapeUtils::ComputePolygonVertices`,
`LengthPercentage::Resolve`, logical-coordinate conversion, polygon construction
and subsequent common translation. Finite resolved coordinates are clamped to
[-M,M]; common offsets cancel from differences, and reflections/axis permutations
preserve their bounds. `DOMAIN-SOURCES-v1.json` pins those inspected sources.

**These source-to-model facts remain bridge premises:** resolution has finite
inputs and defined behavior; adding reference offsets, logical reflections and
later translations does not already overflow; the selected edge has the stated
ordering and inclusive intersection; the exact helper receives those values.
The companion proves the algebra of common offsets/reflections, not an executable
parser-to-frame pipeline. It does not excuse undefined behavior upstream or prove
all shape-margin/rasterization paths safe.

## Universal Lean results

`Interpolation.lean` audits 15 theorems over arbitrary mathematical integers:

- For positive and negative slopes separately, the truncated delta lies between
  zero and dx. The interpolated value lies between the endpoints and is exact at
  both endpoints.
- Inclusive y and bounded differences make all three argument subtractions
  representable signed32 values. The product is within ±D², where
  D² = 4611686009837453316, strictly inside signed64 bounds.
- Positive denominator prevents division by zero and the signed-minimum/-1 case.
  The quotient lies within ±D, so returning it as nscoord is exact. Containment
  makes the final addition representable signed32.
- A checked wide integer evaluation returns exactly the mathematical interpolation.
  Whenever the original signed32 product is representable within this domain, the
  old checked evaluation returns exactly the same result.
- Common integer translation commutes with interpolation. Common translation or
  reflection of raw coordinates in [-M,M] gives differences within ±D. Applying
  the component result after an axis permutation is a bridge step; no complete
  writing-mode implementation is proved.
- Concrete counterexamples preserve the rounding anchor and exhibit the old
  product overflow. At x1=5, x2=4, y1=0, y2=2, y=1, the required result is 5;
  truncating the entire rational interpolation instead gives 4.

The Option-valued checked evaluation models representability checks mathematically;
Gecko does not execute these checks at runtime. This is not a formal C++ operational
semantics or compiler correctness proof. The Lean auditor permits only standard
propext, Quot.sound and Classical.choice; it rejects admitted proofs, added axioms,
unexpected diagnostics and missing audits. The pinned Lean installation and its
standard library are trusted; the latter is not independently bootstrapped here.

## Exact native bridge

`BINDING-v1.json` pins the full original and candidate `nsFloatManager.cpp` plus
`nsCoord.h`. Replay reverses only the intended return expression and checks the
reconstructed full original hash, rejecting other edits. The original hash was
compared with the separately archived pre-fix design source during preparation.
This avoids copying the entire float manager into the companion.

`bridge.py` extracts the complete original/candidate function definitions, the exact
`NSCoordMulDiv` helper, and the actual nscoord alias. `.inc` files are authenticated
views of those exact extracts. The candidate's qualified function definition is
compiled unchanged. The original is placed in an outer namespace so both can run
in the same executable. Minimal class declarations, a two-field nsPoint and an
assertion macro are explicit adapters. They supply the fields and assertion
semantics used by this function; no Gecko frame construction is simulated.

Clang compiles at O1 with warnings as errors and
`-fsanitize=undefined,implicit-integer-truncation -fno-sanitize-recover=all`.
The independent Python oracle uses arbitrary-precision signed-magnitude division.
Finite fixtures include exhaustive small coordinates, zero/positive/negative slopes,
endpoints, D-scale differences, translated absolute coordinates outside [-M,M],
rounding remainders and deterministic random samples. Original execution is limited
to cases with a representable signed32 product. This finite native bridge supports
source correspondence; the arbitrary-value results are the separate Lean theorems.

Semantic mutations cover slope sign, anchor, numerator offset, denominator,
whole-value truncation and widening after multiplication. UBSan must reject both
the original overflowing product and an out-of-domain full-int32 subtraction in
the repaired function. The latter is a required scope control, not a repaired bug.
Source guards cover tooling/spec/native identities and preservation outside the
single return expression. Compiler warnings, syntax errors and runtime stderr are
also rejected.

## Runtime evidence boundary

Root reported the new WPT baseline as 16 FAIL / 16 PASS, with two existing
shape-outside reftests passing. Browser-finding acceptance is separate from this
arithmetic companion. This package does not run a browser or rebuild Firefox and
does not claim paired browser success before root's own runtime gate finishes.

## Replay and commit layout

From the repository root with the native repair applied:

```sh
python3 artifacts/css-polygon-intercept-proof-v1/check.py --out artifacts/css-polygon-intercept-proof-v1/root-replay-v1
```

Use a fresh output directory. `RECEIPT-v1.json` is deterministic across output paths
on the pinned toolchain. `tooling-paths-v1.txt` lists companion sources for a
preceding commit; generated binaries, datasets, mutation files, logs and receipts
are excluded. `prepare.py` is only for initial preparation: do not rerun it to
silently accept drift in a frozen package.

Excluded: arbitrary full-int32 differences, NaN handling, upstream overflow,
full polygon construction/winding, rasterization, float-band selection, clipping,
layout, release impact, and unrelated geometry policies. The retained source-domain
assumptions are part of the contract, not machine-checked conclusions about every
CSS input.
