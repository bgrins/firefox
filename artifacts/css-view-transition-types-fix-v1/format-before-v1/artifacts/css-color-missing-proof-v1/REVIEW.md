# Review record

The color audit and browser probe found the original bug. Lean did not discover
it independently. This model explains the counterexample and establishes the
bounded repair: transfer the same missing-channel identities across RGB/XYZ
spaces before choosing interpolation operands.

The declarative side compares component categories with quantified relations,
including residual sets. The native side uses bit-mask union and a separate
four-way outcome table. The `rgb_transfer` theorem exhaustively establishes the
finite category law for all 15 space IDs subject to the nine-member RGB/XYZ
predicate, all eight missing masks, and all three channels. The subsequent
refinement accepts arbitrary existing converted masks. The generic copy theorems
quantify arbitrary endpoint values, without claiming numeric color conversion.

Four semantic mutations are compiled independently: old early return, overwrite
converted flags, carry only red, and copy from the missing side. Each must fail
in the exact expected semantic theorem bodies. Diagnostics outside those bodies,
missing/extra diagnostics, arbitrary tool failures, successful exit codes,
stderr, and altered axiom inventories are rejected. Twelve positive theorem
axiom reports are checked exactly; none uses `sorryAx` or unchecked declarations.

Sixteen source controls cover the branch, native component bits, RGB/XYZ family,
conversion/carry ordering, alpha forwarding, interpolation outcome choices and
the exact one-line delta. Full source hashes additionally bind reviewed bytes.
This is a manual source bridge, not a Rust extractor or end-to-end refinement.

The first discovery run included unused-variable and unused-simp-argument linter
errors caused by mutations. Those runs are retained but excluded from acceptance.
The final gate disables those two linters equally for positive and negative
compilations so only meaningful theorem failures satisfy the negative gate.

`check-v3` is the final live-native gate. `snapshot-check-v1` independently runs
the companion's source-only mode; its report explicitly denies live native
verification. `freeze.py` authenticates both gates and records their outputs.
Earlier development/discovery/gate directories remain historical evidence and
are excluded from acceptance. Browser/WPT results are owned by the native-fix
record and are not fabricated or implied by this proof artifact.

Residual-set carry, direct relative-color keywords, conversion math, NaN and
powerless-component behavior remain separate obligations. In particular,
`residual_counterexample` is a specification example, not a theorem that the
unmodified residual-set implementation is correct.
