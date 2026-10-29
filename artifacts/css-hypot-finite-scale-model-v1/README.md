This companion explains the exact arithmetic boundary behind the observed
finite-scale hypot failures. It follows source inspection and browser
reproduction; the Lean proof did not discover the defect. The canonical CSS
library remains unchanged.

Binary32Magnitude represents nonnegative binary32 magnitudes as natural
numbers on a grid whose unit is 2^-149. Its two pinned dependencies are copied
and freshly compiled in a temporary directory for each replay. The witnesses
are exact finite inputs 2^-80 and 2^64, with exact finite denominators twice
their value. Both normalized input ratios are exactly one half.

The general below_half_unique theorem proves that whenever an exact positive
quantity lies below half of the least nonzero grid value, every nearest
binary32 magnitude is zero. The tiny squared witness satisfies that bound;
tiny_square_rounds_zero also constructs the nearest result, so the contract
is inhabited. Squaring 2^-80 produces 2^-160, although the unsquared input is
representable. The proof quantifies over every binary32 candidate, rather
than checking a sampled set.

The finite_bound theorem bounds every finite binary32 magnitude using the
existing encoding theorem. large_square_out_of_range then proves that the
exact square of 2^64 exceeds every finite binary32 value. The original input
and its doubled denominator remain representable. This is a range result;
it does not model the IEEE overflow threshold or prove a particular machine
instruction returns infinity. The browser observations separately record
that behavior.

Nearest rounding is an explicit arithmetic contract, not a verified Rust or
LLVM implementation. There is no model of square root, parsing, CSS typing,
normalization, opacity clamping, libm hypot, or the proposed pairwise repair.
The nonnegative squared-norm identity and exact ratios support the expected
mathematical witness; they do not settle the CSS specification's allowance
for implementation-defined precision and range. No native refinement or
general correctly rounded hypot theorem is claimed.

Run-1 compiled both dependencies but rejected the initial proof because
the chosen by_contra tactic is unavailable in this Std environment. Its
ad-hoc wrapper returned zero despite the recorded Lean exit one; those logs
are failure history, not proof evidence. The source now uses a case split.
Run-2 successfully audited twelve declarations and rejected three false
controls; the replay wrapper was subsequently strengthened to require
isolated execution and explicitly allow only the standard axioms propext,
Quot.sound and Classical.choice. The final replay record is run-3.

Replay with:

```
/Users/bgrins/venvs/firefox/bin/python -I -S -B artifacts/css-hypot-finite-scale-model-v1/replay.py run-4
```

The output directory must be absent. Each compiler result is retained before
checking success. False controls must fail specifically because their
propositions are false. No sorry or native decision shortcut is allowed;
temporary compiled objects are removed on exit. Twelve audited declarations
include routine supporting lemmas and are not a measure of CSS coverage.
