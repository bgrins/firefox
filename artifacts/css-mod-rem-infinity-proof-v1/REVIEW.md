# Review of the dispatch model

## Independent specification

`css` is a constructor match. NaN operands, infinite dividends, and zero divisors
produce NaN. Finite dividends and finite nonzero divisors use the supplied CSS
arithmetic. With an infinite divisor, rem returns the finite dividend; mod
returns it only if the signs agree. The comparison includes signed zeros.

`native` instead follows the intended native guard order: reject opposite-sign
infinite-divisor mod, preserve a finite dividend with an infinite divisor, then
run the old formula. The two functions do not call each other. The proof does
case analysis on the operands and signs, then applies the explicit backend
premises. `oldNative` omits only the identity branch.

## Manual mapping to the Rust helper

| Lean | Rust |
| --- | --- |
| `op = .mod` | `matches!(self, Self::Mod)` |
| `isInfinite b` | `divisor.is_infinite()` |
| `sign a ≠ sign b` | inequality between `is_sign_negative()` results |
| `isFinite a` | `dividend.is_finite()` |
| identity return | `return dividend` |
| `formula op a b` | unchanged subtraction/product/quotient, floor or trunc, then existing negative-zero correction |

NaN sign is abstracted away. A signed NaN may take the first Rust guard or fall
through to arithmetic; either route yields abstract NaN. This observational
equivalence is a manual bridge obligation, not an equality between the source
control-flow graphs for every bit pattern.

## Explicit fallback assumption

`FormulaContract` is deliberately visible in the main theorem. Its category
table has the following manual justification for the existing arithmetic:

| Operands | Existing formula behavior |
| --- | --- |
| Any NaN input | Arithmetic propagates NaN; `r == 0.0` does not repair it |
| Zero divisor, finite nonzero dividend | Quotient is infinity; zero times infinity is NaN |
| Zero divisor, zero dividend | Quotient is NaN |
| Infinite dividend, finite nonzero divisor | Infinite quotient/product; subtraction of equal-signed infinities is NaN |
| Both infinite | Quotient is NaN |
| Finite dividend, infinite divisor | Quotient is signed zero; floor/trunc keep zero; infinity times zero is NaN |
| Finite dividend, finite nonzero divisor | Supplied finite arithmetic backend, including final zero-sign correction |

Infinite-dividend/zero-divisor combinations also reach NaN through zero times
infinity. The abstraction does not verify the platform implementation of these
operations, IEEE rounding modes, signaling NaNs, fast-math behavior, or the
finite formula's numerical quality. In particular, the old-dispatch witness
is conditional on this category table. It is not a proved extraction of the
arithmetic expression from Rust.

For the new branch, identity is exact at the abstract value level and requires
no finite arithmetic premise. `rem_infinite_identity`,
`mod_same_sign_identity`, and `mod_opposite_sign_nan` quantify over any fallback
function, demonstrating that those results do not depend on the fallback.

## Proof and mutation inventory

There are twelve audited theorems. Every positive theorem permits only Lean's
`propext` axiom; no `sorry`, added axiom, unsafe declaration, or native decision
procedure occurs. All proofs compile with warnings treated as errors.

Four separately compiled mutations must fail inside the intended theorem
bodies with an exact inventory of `unsolved goals` diagnostics:

- Removing the identity branch breaks refinement and both identity lemmas.
- Dropping the finite-dividend guard breaks refinement on infinite dividends.
- Applying mod's sign exception to rem breaks refinement and rem identity.
- Replacing returned signed zero with positive zero breaks refinement and the
  general identity lemmas.

The diagnostic checker rejects compilation success, unrelated failures,
foreign paths, out-of-body diagnostics, missing/extra diagnostics, stderr,
parser/name failures, and unauthorized positive theorem axioms. A theorem
downstream of an intentionally failed lemma can still compile using Lean's
error placeholder during a negative run; the checker relies on the explicit
primary failure inventory, never on the negative run's axiom output as proof.

## Pending integration

Root must review the native patch and WPT independently, run the checker again
against the patched exact helper, and preserve the tooling companion before
the standalone native/WPT commit. A successful preparatory replay against the
old helper verifies the conditional model and authenticates the old snapshot;
it does not certify a native repair. No changes to shared CSS model modules
are part of this preparation.
