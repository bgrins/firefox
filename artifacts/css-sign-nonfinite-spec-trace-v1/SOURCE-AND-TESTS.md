# Native obligations and existing tests

The source-shaped method experiment remains `css-sign-zero-font-repair-review-v1/CHAIN.json`. It establishes exact extracted-method outputs under the explicitly modeled font multiplication, not that a browser traversed every branch. The special-value correction must preserve the ordinary zero-font dependency repair and avoid moving normalization earlier than the enclosing result.

## Actual producer operations

Pinned HEAD90 `NoCalcLength` bodies are in the existing sign source audit. `Leaf::to_computed_value` calls that conversion for each Length before `CalcNumeric::resolve` invokes generic runtime Sign. `CalcNode::to_computed_value` currently maps all leaves without distinguishing which operator owns them.

| Unit family | Actual arithmetic/provider before censoring | Consequence for a repair |
| --- | --- | --- |
| Absolute | `to_px_if_absolute`, effective zoom, then `finite()` | Ordinary depth-first Sign already canonicalizes an absolute child. A new computed path must not accidentally change its current finite values. |
| Font relative | `reference_font_size_and_length` selects the actual metric/basis and records dependencies; `(reference_size * length).finite()` | Preserve the original coefficient in the multiplication. A raw-result path can use the same actual provider, cache flags and multiplication, withholding only final censoring. |
| Viewport | Actual variant/axis/writing mode provider, effective zoom of AU extent, `trunc(zoomed_AU * original_coefficient /100) / AU_PER_PX`, then f32 and `normalize` | Preserve coefficient placement and AU truncation. Resolving coefficient1 first is not equivalent. NaN is censored here; infinity can remain infinite. |
| Container | Actual size-query provider and flags; `(container_px_f64 * original_coefficient /100) as f32`, then `finite()` | Different arithmetic order/precision from viewport; cannot substitute a rounded coefficient1 result. |
| Internal ServoCharacterWidth | Coefficient cast to i32; `average_advance*(cols−1)+max_advance`, then `finite()` | Affine and integer-admitted, not a CSS linear unit. Keep separate; no author-visible Sign exposure is established by this audit. |

For example, with an unzoomed viewport width1px=60AU, coefficient1 gives `trunc(.6)/60=0`, whereas coefficient2 gives `trunc(1.2)/60=1/60px`. Scaling the first result yields0, already wrong for finite coefficients. An infinite coefficient on the positive60AU basis gives infinity through the actual expression, while multiplying its rounded coefficient1 result by infinity gives NaN. At zero AU extent, the actual product is NaN. These are arithmetic consequences of the pinned expression, not measured viewport inputs. Likewise container size1px with coefficient1 produces a rounded f32 .01; that is not an exact scale factor for arbitrary subsequent coefficients.

A Sign-specific route cannot merely fold a direct nonfinite leaf or modify the post-conversion `sign_from`: nested sums/products/min/max may contain multiple leaves, and current global mapping has already lost their NaNs before Sign executes. If narrowed to a Sign subtree, the traversal must preserve raw nonfinite values throughout that subtree and maintain all provider/cache dependencies. A shared raw-per-unit conversion with normalization explicitly selected at the caller is another design direction. Neither is selected or implemented here. Finite behavior, compound operands, absolute controls, percentage guards, zero-sign propagation and the internal unit exclusion all remain review obligations.

## Existing WPT coverage

Searchfox discovery was restricted to `testing/web-platform/tests/css/css-values`; copies of the three newly identified files were read from immutable HEAD90, not the active native tree.

- `signs-abs-computed.html` (existing pinned233 cases) has nonzero em/rem/vw sign tests, zero coefficients, mixed cancellations and bare number abs(NaN/infinity). Its NaN section does not place a relative nonfinite leaf inside Sign. The existing four-case zero-font diagnostic remains unchanged.
- `calc-infinity-nan-computed.html` includes `width:calc(NaN * 1rem) → 0px`. This is a top-level result; premature child censoring gives the same observable value, so it does not distinguish the reported issue. Its min/max NaN tests use absolute px operands.
- `calc-infinity-nan-serialize-length.html` retains relative NaN in min/clamp serialization. It does not exercise computed nested Sign.
- `signs-abs-serialize.html` tests sign(infinity) and sign(±1 * NaN) as number expressions. It does not require font resolution.

This is bounded coverage evidence, not a claim that no related WPT exists anywhere. New special-value controls should be an explicit successor: independently calibrated positive and zero font bases, NaN/±infinity, and an outer nonzero term so early NaN→0 is visible. They must not silently replace the original4+233 campaign or treat changed failures as preserved. Runtime and native acceptance remain open; source-first discovery attribution is unchanged.
