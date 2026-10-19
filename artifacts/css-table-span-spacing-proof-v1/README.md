# Fixed table span-spacing proof companion

## Contract

This package proves a bounded arithmetic property of the first-row cell branch in
`FixedTableLayoutStrategy::GetMinISize`. It is not a proof of table layout.
For supplied nonnegative intrinsic extent C and column spacing S, positive span K,
and representable arithmetic, each contribution is nonnegative, no greater than C,
and agrees with the existing initial span-allocation clamp in
`ComputeColumnISizes`. The repaired clamp is the unique least nonnegative integer
at least floor((C+S)/K)-S. Nonnegative contributions accumulated onto supplied
spacing cannot reduce that spacing baseline.

CSS 2.2 fixed table layout assigns first-row spanning widths among columns and
requires the table width to account for column widths and spacing. The archived
primary section motivates this contract. Its prose is not translated automatically
into Lean, and the exact integer rounding policy is an implementation refinement.

## What is proved

`SpanSpacing.lean` has 13 audited theorems:

- Clamp nonnegativity, equality with the conditional final-allocation clamp,
  the least-share specification and its uniqueness, and unchanged nonnegative raw
  contributions.
- Contribution bounds and signed32 representability of C, S, K, C+S, the quotient,
  the subtraction, and the final contribution when C+S and K are at most INT32_MAX.
  `Int.tdiv` models truncation toward zero; its equality with Euclidean integer
  division is proved for the nonnegative numerator.
- A spacing lower bound for arbitrary finite lists of nonnegative contributions,
  including contributions with differing extents/spacings/spans. A separate
  recursive safe-trace premise proves accumulator representability.
- Concrete counterexamples to the old negative contribution, exact preservation
  of division remainders, and applying the lower bound to negative adjustments.

The axiom auditor allows only Lean's standard `propext`, `Quot.sound`, and
`Classical.choice`. It rejects added proof axioms, admitted proofs, unexpected
stdout/stderr, missing audits, and failed compilation. This trusts the pinned Lean
binary and its installed standard library; the library is not independently
formally bootstrapped or hashed file by file here.

## Native binding

`BINDING-v1.json` pins the complete candidate and original native files. Replay
reads the live candidate, reverses only the exact assignment replacement, and
requires the reconstructed original to match its independently captured hash.
This rejects every other source change without copying a full table implementation
into this package. The original hash was compared against the root's archived
`FixedTableLayoutStrategy-before.cpp` during preparation.

`bridge.py` extracts the exact minimum span branch, exact existing final-allocation
span branch, exact accumulation statement, and actual `using nscoord = int32_t`
declaration. Checked-in `.inc` files are byte-checked extraction views. C++ wrappers
supply C/S/K and an accumulator, while a small frame adapter returns the supplied
spacing from `GetColSpacing`. The exact statements run under Clang with undefined
behavior sanitization and warnings treated as errors. No Gecko frame tree,
IntrinsicForContainer, style resolution, or table cell map is mocked and presented
as verified: those operations are outside the executable bridge.

The independent Python oracle uses unbounded `divmod` and a piecewise nonnegative
share. Its deterministic finite corpus covers zero spacing, span one, spans two
and three, spacing thresholds, remainders, broad random values, INT32 limits, and
accumulators ending at INT32_MAX. Values beyond Gecko's narrower `nscoord_MAX`
geometry convention are arithmetic stress inputs, not claimed reachable CSS
coordinates. Native controls run with zero initial accumulators to avoid making
mutant allocations overflow before their semantic mismatches can be compared.
A separate intentionally overflowing addition must be rejected by UBSan: the patch
does not repair overflow.

## Bridge premises and exclusions

- `IntrinsicForContainer` supplies the same nonnegative value at the compared
  minimum/allocation sites. The source includes lengths, min-content and
  max-content; intrinsic measurement and caching are not proved. Root's WPT
  exercises definite lengths, not intrinsic keywords.
- Span is positive and signed32 representable; supplied spacing is nonnegative;
  C+S is representable. The proof derives quotient/subtraction bounds. Each
  accumulation prefix must also be representable. C++ division is not executed
  with zero denominator or INT_MIN/-1.
- Native span-one branches bypass the split. Frame selection, column precedence,
  cell-map multiplicity and writing-mode/spacing projection are bridge premises.
- The sum lower bound applies only when all accumulated adjustments are
  nonnegative. The preserved percentage-cell path can subtract spacing and is
  excluded. The theorem does not claim a whole-table lower bound for arbitrary CSS.
- Equality is with the initial final-allocation span clamp for the same supplied
  inputs. Later redistribution can change column widths and is not proved.
- No exact aggregate preservation across division remainders, percentage policy,
  collapsed-border model, mixed specified columns, layout convergence, or general
  overflow safety is claimed.

## Replay

From the repository root, after the native repair is applied:

```sh
python3 artifacts/css-table-span-spacing-proof-v1/check.py --out artifacts/css-table-span-spacing-proof-v1/root-replay-v1
```

Use a fresh output directory. Replay authenticates source/spec/tooling pins, checks
Lean proofs and semantic mutations, compiles and runs the exact C++ extracts,
checks native mutations and diagnostics, checks source preservation controls, and
writes a deterministic `RECEIPT-v1.json`. Replays on this toolchain should produce
identical receipts regardless of output directory. Do not run `prepare.py` to
silently accept source drift after freezing.

`tooling-paths-v1.txt` lists the 17 source artifacts for a preceding companion
commit. Generated binaries, logs, mutation files and receipts are not source
artifacts. The repair commit remains native source plus WPT only.

## Runtime evidence supplied by root

Root reported a successful local build (82398) and paired WPT replay (29618):
new test changed from 30 FAIL / 60 PASS to 90 PASS; existing coverage remained
61 PASS / 11 expected FAIL. This companion did not execute browsers or rebuild
Firefox. Those results are integration evidence, not produced by the Lean model.
