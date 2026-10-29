# Binary32 operand classification for CSS pow

This extends the abstract exceptional-value model with every 32-bit operand
encoding. `classify` decodes sign, eight exponent bits and 23 fraction bits.
It distinguishes NaNs, signed infinities and signed units; other finite
encodings retain an opaque token. No finite arithmetic is modeled.

`nan_range`, `infinity_encoding` and `unit_encoding` prove the equivalence
between field classification and magnitude-bit comparisons. The proof of
`all_encodings_refine_spec` applies to all pairs of words and any fallback
function. It connects those comparisons to the earlier abstract CSS guard,
including every NaN payload, both infinity signs and both unit signs.

This closes the field-classification gap within the model. Connecting the
model to Rust's actual `is_nan`, `is_infinite`, `abs`, equality, compiler and
hardware remains a refinement obligation. The proposed native patch uses
those Rust operations, not this bit-comparison implementation. This does not
prove `powf`, ordinary accuracy, parsing, invalidation or complete CSS pow
semantics. It did not discover the previously observed browser failures.

The field interpretation follows binary32 as documented for [Rust f32](https://doc.rust-lang.org/std/primitive.f32.html).
The guard contract follows [CSS Values 4 exponential argument ranges](https://drafts.csswg.org/css-values-4/#exponent-argument-ranges)
and its infectious-NaN rule. Sources were checked October 29, 2026. These are
manual specification and representation mappings, not imported axioms.

Run 2 freshly compiles both modules, audits 14 new theorems and rejects four
false claims: infinity is NaN, a signaling NaN is finite, negative unit raised
to infinity is one, and the finite predecessor of one is a unit. Only standard
Lean axioms occur; no sorry or native decision shortcut is accepted. Run 1
failed due to proof tactics splitting a match instead of its conditional,
and rewriting through dependent Decidable instances. The corrected proof
uses explicit field cases and simplification. Failure logs are retained.

Replay: `python3 -I -S -B artifacts/css-pow-binary32-classification-v1/replay.py run-3`.
Temporary compiled objects are removed after execution. The canonical CSS
library and its coverage counts are unchanged. `PowSpecial.lean` is an exact
copy of the already committed abstract model.
