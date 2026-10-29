# CSS pow exceptional-value guard and deferred evaluation

This model follows the source audit and observed WPT failures. It did not
discover them. CSS Values 4 requires NaN when either operand is NaN, and for
either sign of unit base raised to either infinite exponent. The explicit
specification cases are implemented here independently as pattern matching;
the proposed Boolean guard is proved equivalent for every abstract operand
and every fallback function.

`Value` describes exceptional-value classes. `finite token` represents other
finite inputs, including zero, with an opaque identity; it is not an integer
numeric interpretation. `unit` retains both signs. Translating actual IEEE
bits into these classes, Rust predicates, `powf`, dimensional eligibility,
top-level CSS censoring and floating-point rounding are not proved. In
particular, preserving the fallback does not prove it handles all remaining
CSS exponent cases correctly.

The expression model has literal, environment-variable and power nodes.
`folding_preserves_resolution` quantifies over every such expression,
environment and fallback. Its mutation corollary covers any pair of
environments. This proves the abstract constant-folding rule uses the same
exceptional-value contract as deferred resolution. It does not model Stylo's
dependency tracking or invalidation scheduling.

Counterexamples show that direct delegation need not propagate NaN, and
that a unit-base power cannot always be collapsed to one before resolving
its exponent. `returnsOne` is a deliberately limited witness fallback, not
a model of platform powf for arbitrary inputs. Three deliberately false
claims must fail in the replay.

The pinned Lean compiler freshly compiles the model and audits all eleven
theorems without sorry or native decision shortcuts. Run 1 rejected a
reserved constructor name in a proof pattern; escaping the name fixes the
proof syntax. Run 2 passes, rejects all three false controls, and removes
its temporary compiled objects. The earlier failure log is retained.

Run with `python3 -I -S -B artifacts/css-pow-special-value-model-v1/replay.py run-3`.
Canonical library contents and coverage counts remain unchanged.

Specification mapping, checked October 29, 2026:

* `spec`, `unit_infinite`: CSS Values 4, [exponential argument ranges](https://drafts.csswg.org/css-values-4/#exponent-argument-ranges).
* `nan_left`, `nan_right`: the same section's infectious-NaN rule.
* `folding_preserves_resolution`: an implementation obligation derived from
  applying those rules at both simplification and deferred evaluation.

The folding theorem is an abstract implementation model, not a transcription
or proof of the entire CSS simplification algorithm.
