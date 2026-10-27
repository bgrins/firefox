# Local nonnegative resolution policy

For an already parse-time-resolvable calculated weight, let R(x) be the existing Integer::resolve rounding followed by Rust's saturating i32 cast. The local helper returns max(R(x),0). The proposed generic range correction instead uses R(max(x,0)) for NonNegative. The pinned historical AllowedNumericType::clamp branch is val.max(0.).

| Resolved operand | Existing resolution then local max(0) | Nonnegative clamp before existing resolution |
| --- | --- | --- |
| finite x >= 0 | existing R(x), already nonnegative | identical R(x) |
| finite x < 0 | rounding cannot exceed zero; result becomes 0 | R(0)=0 |
| +infinity | cast saturates to i32::MAX; unchanged | identical |
| -infinity | cast saturates to i32::MIN; then 0 | R(0)=0 |
| NaN | cast gives 0; remains 0 | f32::max with numeric zero gives zero; R(0)=0 |
| either signed zero | integer result 0 | integer result 0 |
| unresolved expression | None propagated and parser rejects | unchanged unresolved policy |

For finite negative x, the existing f32 addition of one half cannot round above one half, so its floor is at most zero; negative saturation likewise cannot produce a positive integer. This argument also holds with accepted118's promotion before addition. For nonnegative x, the extra clamp leaves the operand/value alone. Therefore the local nonnegative result agrees with the generic range-corrected result in either rounding epoch. Applying both clamps is idempotent. This is a source/language-semantics argument, not a new symbolic IEEE or native compiler proof.

The language premises are documented by the [Rust numeric-cast reference](https://doc.rust-lang.org/reference/expressions/operator-expr.html#numeric-cast) and [f32::max](https://doc.rust-lang.org/std/primitive.f32.html#method.max), checked 2026-10-24. These statements concern a value that reaches Integer::resolve; they do not assert CSS parser reachability for every special-value spelling. The original rounding and earlier expression simplification remain unchanged.

For example, old f32 addition may map the positive integral operand 8388609 to 8388610, whereas accepted118's promoted addition retains 8388609. Local max(0) changes neither positive result. The independent additive repair must not be advertised as fixing that separate rounding defect or as importing fix118. Ordinary fractional controls (1.4,1.2; 1.6,1.4; 0.49,-0.6) exercise descending/equal results without depending on those exceptional rounding boundaries.

Literal negative weights still fail Integer::parse_non_negative at admission. Calculated negative weights retain their specified expression while the helper supplies their nonnegative semantic value. The helper is used at both parser ordering and native export; there is no parser/export mismatch and no representation rewrite.
