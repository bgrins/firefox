# Nonfinite deferred-length transport

Source-supported HOLD on the canonical-value-only sign candidate. A small per-unit math-conversion route is feasible, but must serve both numeric and length-percentage calc mapping. No patch or browser execution is included here.

## Actual conversion boundaries

| Unit family | Pinned HEAD90 arithmetic and terminal policy |
| --- | --- |
| Absolute | Convert the actual coefficient to px, apply effective zoom, then `.finite()` |
| Font/root/font metrics/line height | Obtain the context-dependent reference through `reference_font_size_and_length`, multiply the actual coefficient, then `.finite()` |
| Viewport variants/logical axes | Obtain the requested viewport and dependencies; zoom AU basis as f32, multiply actual coefficient in f64, divide by 100, floating-point truncate in AU, divide by AU_PER_PX, cast to f32, then `normalize` |
| Container units | Obtain actual container query dimensions and dependencies; multiply actual coefficient in f64 px, divide by 100, cast to f32, then `.finite()` |
| Internal ServoCharacterWidth | Cast column coefficient through i32, then compute the existing affine average/max-advance expression and `.finite()` |

`CSSPixelLength::finite` changes NaN to zero and clamps infinities. Viewport conversion only normalizes NaN; it already retains infinity. Its AU truncation is a floating `.trunc()`, not an integer/Au cast. A blanket final `.finite()` would therefore change existing viewport policy. Resolving coefficient one then multiplying is not equivalent: it changes viewport quantization order and loses the internal character-width affine rule and cast.

## Narrow API recommendation

Keep the current public property methods and their policies. Add a named math conversion entry, taking the same base-size/line-height context where needed, backed by the existing actual-coefficient per-unit calculations. A private mode can bypass only the terminal `.finite()`/`normalize` calls for math; property mode retains the original per-unit policy exactly. Preserve multiplication precision/order, viewport truncation, root/line-height selection, zoom, and all existing cache flags/dependency registrations. Do not special-case NaN/Infinity before querying dependencies: zero bases and future context changes matter.

Opt in at both existing calc mappings:

* `specified::calc::Leaf::to_computed_value`, currently calling `NoCalcLength::to_computed_value(context)` before numeric `CalcNode::resolve`.
* `specified::CalcLengthPercentage::to_computed_value_with_zoom` in computed/length_percentage.rs, currently calling `to_computed_value_with_base_size`. Retain its subsequent `should_zoom_text`/`zoom_fn` order and construction through `LengthPercentage::new_calc`.

Ordinary `ToComputedValue`, direct font-size/font helpers, and other direct property callers retain the existing wrapper. This avoids an AST walk specialized to Sign and correctly handles compound Sign operands. It is still necessary to review the entire mapped calculation's final normalization, simplification and percentage paths before implementing; this audit does not certify every calc operator or every nonfinite property result. An internal `ServoCharacterWidth` coefficient is not an authored CSS unit: keep its cast/affine semantics rather than pretending its coefficient is a general CSS scalar.

## Reachable source lead

The NaN keyword parser creates a numeric NaN. Product simplification multiplies it into the `em` coefficient. Sum simplification merges compatible units, so NaN-em plus 1px remains a Sum; it has no cross-unit NaN collapse. Sign simplification requires a leaf and therefore leaves this operand deferred on HEAD90 as well as the held candidate. Numeric calc mapping then resolves NaN-em through the font path's `.finite()` to zero px. The Sum becomes 1px and Sign becomes +1. A nonzero outer offset distinguishes this loss: `opacity:calc(0.25 + 0.25 * sign(NaN * 1em + 1px))` is source-predicted 0.5, while propagating NaN through the full outer calculation gives zero. No typed dimension-division extension is needed: the product is number×length and the sum is length+length. `PROPOSED-WITNESS.json` records controls and strict future calibration; no browser result is asserted.

Current CSS Values 4, read 24 October 2026, defines sign on its resolved argument and retains special values inside a calculation tree. NaN propagation continues through enclosing operations; censoring to zero occurs at the top-level calculation, not at a length leaf. This yields the stated outer-zero expectation. [Sign functions](https://drafts.csswg.org/css-values-4/#sign-funcs), [special-value handling](https://drafts.csswg.org/css-values-4/#calc-infinity).

Searchfox discovery confirmed the per-unit implementation and nine `to_computed_value_with_base_size` callers. Exact local authority is the retained HEAD90 sources in SOURCE-PINS.json, plus an explicit HEAD90 read of length_percentage.rs. The installed CLI rejected its documented `--permalink` option; no invented revision permalink is supplied. This audit writes only its own capsule and leaves native/index/browser/canonical state untouched. Root/peer special-controls fixture is independent and remains unchanged.
