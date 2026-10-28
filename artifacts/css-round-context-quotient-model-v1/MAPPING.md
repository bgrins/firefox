# Source and mathematical correspondence

| Model item | Captured source or evidence | Boundary |
|---|---|---|
| positive/negative reconstruction | generic CalcNode::resolve_internal finite Round branch reconstructs toward-zero and neighboring bounds from a remainder | Premises are exact decomposition and strict signed-remainder bounds. No proof that native f32 remainder/f64 reconstruction satisfies those premises universally. |
| adjacent multiples and selected endpoint | lower/upper differ by one positive step; branch selects one endpoint | Common integer scale has exact arithmetic. Float casting can round the final bound. |
| choose nearest/up/down/toZero | four existing RoundingStrategy match arms | natAbs models mathematical magnitude, not signed zero or NaN comparisons. |
| roundExact with remainder0 | early remainder.is_zero return | Proves preservation conditional on zero remainder, not IEEE modulo classification. |
| quotient witness | old div=value/step, floor/ceil then multiply | Exact cross-products locate1/step between dyadic neighbors3-2^-22 and3, strictly above their midpoint. Neighbor identification is checked separately using encoded values; no complete binary32 decoder/rounding proof in Lean. |
| final product witness | old floor(rounded quotient)*step | 3*step is1+2^-25, closer to1 than1+2^-23. This reproduces the old helper's result with exact rational distance comparisons. |
| source-first/browser attribution | sealed v2 source report/helper; saved34-snapshot baseline | Four original discrepancies predate this model; prospective exposure snapshots currently pass. |

For the positive witness, scale33554432 gives A=33554432, B=11184811, lower=22369622, upper=33554433. The residual11184810 is strictly between0 and B. For the negative witness, lower=-33554433 and upper=-22369622; to-zero/up use the latter. Exact-quarter and tie controls prevent interpreting every input as a quotient defect.

The full specification permits implementation-defined numeric precision. This companion isolates why premature quotient rounding can lose the interval decision; it does not prove that every exact-rational/native disagreement violates a universal precision requirement. Existing accepted special-case bodies and consumer prerequisites are not re-proved here. In particular the source's f64 reconstruction must not be identified with the exact integer construction for every finite f32 pair (including huge quotient cases such as1 versus3 times the minimum subnormal).
