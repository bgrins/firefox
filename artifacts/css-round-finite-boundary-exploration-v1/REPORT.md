The sampled native candidate agrees with an independent exact directed-multiple reference in **4,151,200 strategy executions**. No projected-result counterexample was found. This is finite evidence, not a universal IEEE proof or a Gecko/browser acceptance result.

| Sample | Input pairs | Strategy executions | Candidate mismatches |
|---|---:|---:|---:|
| All 255×255 finite exponent fields, four mantissa profiles; deterministic random inputs; binade/half-ULP/subnormal boundaries; exact ties and adjacent floats | 618,754 | 2,475,016 | 0 |
| Constructed products at binary32 midpoints or one/two product-grid units beside them, adjacent inputs and both signs | 419,046 unique pairs | 1,676,184 | 0 |

Counts are executions, not distinct-input or theorem counts across the combined samples. The midpoint generator constructs 69,903 products using modular inverses of odd step significands. It targets possible double rounding rather than relying only on random inputs. Both campaigns additionally compare Rust's actual truncating remainder with the exact signed remainder; no difference was observed.

All finite binary32 inputs are represented exactly as integer multiples of `2^-149`. The oracle computes the mathematical floor quotient and adjacent multiples with Python integers, chooses the specified directed bound or upper bound on nearest ties, and projects the selected exact integer to binary32 using a separately written nearest-even encoder, including signed zero and overflow. This avoids first rounding a quotient and does not model Rust `%` with SMT `fp.rem`.

The executed Rust helper preserves the sealed proposal's complete old/candidate scalar function bodies. Only its input/output adapter changes. It runs the actual candidate `%`, binary64 reconstruction/distance operations, and final binary32 cast. The adapter omits CalcNode child resolution and type checking, as in the prior helper. `rustc 1.92.0`, optimization level 0, and overflow checks were used. All builds/runs exited 0; owned executables were removed. Large generated input/output streams are represented by deterministic generator and SHA-256 digests, not copied into this capsule.

`analyze.py` independently simulates binary64 nearest-even operations on the same integer grid and reproduces the entire first campaign's native output digest. It cross-checks 912 rational floor-bound calculations and 3,648 projected values with Fraction arithmetic and a separate binary-search encoder. No finite nonzero intermediate here approaches binary64 underflow or overflow.

The analysis disproves two overly strong proof premises: **114,743** sampled pairs have inexact reconstructed bounds, and **47,227** choose a different nearest bound than exact arithmetic. Their final binary32 results still agree. Therefore, a universal theorem must preserve the projected result, not require exact reconstruction or the same selected adjacent multiple.

Two compact, separately compiled witnesses are retained in `WITNESS.log` and `WITNESSES.json`. Let `u = 2^-149`, and `a = 1` (`0x3f800000`):

| Step bits | Exact adjacent bounds | Binary64 bounds | Exact nearest / native branch | Final result |
|---|---|---|---|---|
| `0x00000003` (`3u`) | `1−2u`, `1+u` | `1`, `1` | upper / upper | `0x3f800000` |
| `0x00000005` (`5u`) | `1−2u`, `1+3u` | `1`, `1` | lower / upper | `0x3f800000` |

In both, the actual remainder is `0x00000002`; both native distances round to binary64 positive zero. The second witness demonstrates opposite nearest selection. Both exact bounds project to the same binary32 `1`. These are counterexamples to proof obligations, **not repair failures**. The report does not claim they are globally minimal bit-pattern counterexamples.

The promising remaining proof split is conditional: small steps may put both exact adjacent bounds in the input's binary32 rounding cell; otherwise the quotient/significand bound may make relevant binary64 operations exact. Binade asymmetry, exact midpoints, overflow projection, and a very large step versus a small value need explicit treatment. Neither that split nor a universal Rust remainder refinement is proved here. NaN/infinity/zero-step behavior, provider readiness, typed evaluation, compilation refinement, and the native integration campaign remain separate obligations. No canonical model, native source, index, browser, or Gecko build was changed.

Replay the primary campaign into an absent directory:

```
python3 -B -I -S artifacts/css-round-finite-boundary-exploration-v1/replay.py --output /tmp/round-boundary-replay-UNIQUE
```

`analyze.py` and `midpoint.py` print their receipts to stdout and read the immutable first campaign helper/receipt. Run them with `python3 -B -I -S`; redirect output outside this sealed directory. The latter compiles only a temporary standalone Rust helper and removes it. To replay the two witnesses, compile `witness.rs` with the same `rustc --edition=2021 -C opt-level=0 -C overflow-checks=yes` flags into an owned temporary directory, compare stdout with `WITNESS.log`, then remove that directory.

References pin the prior source/helper proposal and exact remainder-to-bounds Lean bridge. Discovery remains source/numeric analysis; this campaign supplies additional finite evidence rather than new theorem credit.
