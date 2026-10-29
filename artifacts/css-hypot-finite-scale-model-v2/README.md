This successor retains the twelve declarations from the finite-scale witness
model and adds six general arithmetic bounds for the proposed widened pair
operation. It is implementation support, not a proof of CSS conformance or
of the compiled Rust code. The earlier model and its failed initial replay
remain unchanged.

For any two finite binary32 inputs, pair_wide_upper proves their exact sum
of squares is below 2^257. When either magnitude is nonzero, pair_wide_lower
proves that sum is above 2^-1022, the smallest normal binary64 value. Both
statements use the exact integer grid from Binary32Magnitude: pairSquares
must be divided by unit squared to recover the real magnitude. They quantify
over all finite bit patterns, including subnormals and sign aliases.

The significand and exponent capacity lemmas use the existing binary32
encoding's coefficient below 2^24 and exponent at most 253. Squaring its
coefficient needs fewer than 53 bits, and its squared exponent fits well
inside the binary64 dyadic range. These are capacity bounds. They do not
construct an IEEE binary64 encoding or prove Rust casts, multiplication,
addition or square root implement those encodings and rounding contracts.
Addition can round, even when the individual widened squares are exact.

Together the bounds explain why direct binary64 square/sum/sqrt avoids the
observed intermediate range failures for a pair of binary32 inputs. The
proposed implementation still rounds each pair's magnitude back to binary32
before the next argument. Correct rounding of an arbitrary n-ary norm,
summation error, native refinement, special-value behavior and performance
are outside this model. Special values are covered separately by the actual
Rust arithmetic checks and planned WPT controls.

Run-1 passed all eighteen declarations and the three inherited false controls.
Run-2 additionally checks two false propositions: that the large pair's sum
of squares fits binary32's range, and that every squared significand fits
24 bits. The final replay compiles both pinned library dependencies afresh,
prints eighteen axiom audits, rejects all five false propositions, and
removes temporary compiled objects. Only the standard propext, Quot.sound
and Classical.choice axioms are allowed. No sorry or native decision
shortcut is used.

Replay into a new output directory:

```
/Users/bgrins/venvs/firefox/bin/python -I -S -B artifacts/css-hypot-finite-scale-model-v2/replay.py run-3
```

The canonical CSS library and its coverage totals are unchanged. These
bounds followed source review and browser reproduction; they did not
discover the failure. The declaration count includes helper lemmas.
