This immutable successor replaces the original globally quantified nearest-projection premise with a contract only at the two reconstructed and two exact bounds. The original mathematical implication remains valid, but its global finite-output premise was unsuitable as a direct model of a native cast over overflow inputs. The two unrelated geometry/error lemmas are unchanged; the projection proof uses only the four local contracts. No extra research theorem credit is claimed for this correction. Two anonymous examples establish that pointwise correctness does not require global finite-output correctness.

Three checked support results close a useful **conditional small-step projection** obligation. They do not prove the entire repaired finite binary32 Round path or a universal IEEE refinement. No canonical registrations are added.

Use integer multiples of a common positive dyadic scale, such as `2^-149`. Let `a` be the representable input, and let `p<a<n` bound the empty gaps to its neighboring representable values. The gaps may differ; at `a=1` the lower gap is half the upper gap. Define the strict rounding cell by `p+a < 2y < a+n`.

The model supplies a positive step `b`, remainder magnitude/sign conditions, an error bound `e₁` on reconstructing `t ≈ a−r`, and an error bound `e₂` on reconstructing the other bound `t±b`. It preserves the candidate's sign-dependent branch and exact reuse of `t` for one bound. Its sufficient margins are:

```
2 * (b + e₁ + e₂) < a - p
2 * (b + e₁ + e₂) < n - a
```

`cell_unique_nearest` proves the center strictly nearer than every other allowed value for any point in this asymmetric cell. `reconstruction_cells` derives that both computed bounds and both exact branch expressions lie in the cell from the remainder and error inequalities. `small_step_projection` combines these with nearest-projection contracts at exactly those four bounds: **any selection** between the computed bounds and either exact reference bound project to `a`. It requires neither exact intermediate arithmetic nor agreement between native and mathematical nearest decisions. The preceding finite exploration's opposite-choice witness is therefore compatible with this theorem.

The main theorem uses the nearest-projection minimization property only at those four supplied inputs, not an assumed conclusion that all cell points already map to `a`. It derives cell containment from arithmetic and proves uniqueness against all allowed values using the neighboring-gap certificate. The neighbor endpoints need only bound empty gaps; choosing the actual adjacent finite floats supplies that certificate. Strict margins avoid a separate tie-even argument.

The compiled witness instantiates `a=2^149`, `b=5`, `r=2`, `t=l=u=a`, `e₁=2`, `e₂=5`, and asymmetric gaps `2^125`, `2^126`. In physical values this is `a=1`, step `0x00000005`, exact branches `1−2*2^-149` and `1+3*2^-149`. Both exact branch values and both measured reconstructed bounds lie strictly inside the same cell. This transfers the arithmetic shape of the retained compiled witness; it does not itself prove the machine observation or float-neighbor encoding.

Three checked counterexamples and separately rejected false claims show why hypotheses matter: a midpoint is not uniquely nearest; the upper binade radius cannot be reused as a symmetric radius; and a small step alone cannot absorb an unbounded reconstruction error. These are mathematical obligation counterexamples, not additional observed native failures.

Composition with `RoundRemainder.remainder_bounds` still requires the supplied unbounded integer quotient/decomposition and nonzero remainder, so the exact expressions really are adjacent step multiples. The new projection lemma needs only remainder sign/magnitude because containment is independent of the quotient. The native zero-remainder early return is separate and already returns the input unchanged.

External obligations remain: exact binary32 decoding and Rust truncating-remainder refinement; finite binary64 reconstruction error bounds; actual adjacent binary32 gaps; and final nearest-even cast refinement. This integer model does not distinguish signed zeros. A nonzero center and finite-neighbor instantiation address numerical projection only; sign-bit preservation at zero and overflow endpoints require separate proofs. At uniform subnormal spacing the strict small-step inequality cannot hold for any positive grid step, so this lemma makes no claim to cover that domain. A bounded-significand/large-step branch, exponent-gap coverage, midpoint boundaries, special values, typed evaluation, and compiler/provider refinement are unfinished. The earlier proposed global split remains a conjectural route, not a proven partition.

Replay with the existing Lean 4.35.0-rc4 binary, two threads and 55-second per-process limits:

```
python3 -B -I -S artifacts/css-round-small-step-cell-v2/replay.py --output /tmp/round-small-cell-UNIQUE
```

The positive module and all three negative-control runs completed as expected. The three axiom audits use only `propext`, `Quot.sound`, and `Classical.choice`; no `sorryAx` or warning occurs in final validation. The predecessor retains initial failed syntax/proof development logs; they are not validation of this successor. No `.olean` output or new target was requested; temporary negative sources were removed. Canonical/library/native/index/browser state was not changed.
