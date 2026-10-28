# Erased dependencies and retained registration values

Do not activate the prototype's all-clear audit as a registration certificate. The specification defines independence in terms of obtaining the computed value without CSS-controlled information; it does not define it as absence of every contextual token or as absence of calls to Stylo's Context API. Conversely, a parser's simplified tree is not automatically a sound witness of that property. The concrete bad-fold witness in this checkout is already held fix 120, not a new discovery.

## Current specification boundary

The [JS registration algorithm](https://drafts.css-houdini.org/css-properties-values-api/#the-registerproperty-function) first parses the initial value using the chosen syntax, then tests the parsed value's [computational independence](https://drafts.css-houdini.org/css-properties-values-api/#computationally-independent). Independence allows the property's own value and global information that CSS cannot change. This is a capability/semantic condition, not a requirement to reproduce a particular engine's internal sequence of reads. It is still about the specified computed-value rules, not arbitrary equality observed in one browser environment.

[CSS math simplification](https://drafts.csswg.org/css-values-4/#simplify-a-calculation-tree) combines identical units and preserves their unit, limits conversions to cases with enough information, and explicitly retains zero-valued terms when their unit can affect behavior. [Computed math values](https://drafts.csswg.org/css-values-4/#calc-computed-value) use the information available at computed-value time. These rules rule out blanket removal of every zero term; they do not supply a complete registration-specific theorem for all cancellation expressions.

| Case | Current source and test evidence | Admission conclusion |
|---|---|---|
| `calc(0 * 1em)` | Scalar multiplication updates the coefficient of the Length leaf, retaining em. | No erased-history witness here. Exact registration acceptance is not established by the located WPTs. |
| `calc(1em - 1em)` | Same-unit addition produces a zero em leaf; it does not become an absolute px literal. | Same limitation. Do not substitute real-number algebra for specified unit-preserving math. |
| `calc(0 * 1cqw)` / `calc(1cqw - 1cqw)` | The same retained-unit machinery applies to container units. | No blanket independence oracle inferred. Container selection/fallback still needs separate treatment. |
| `calc(1em / 1em)` / `calc(1cqw / 1cqw)` | Product reduction requires canonical numeric leaves; relative Length has no context-free canonical value. | Do not treat this as identically 1: zero font/container bases can introduce 0/0. The nearby ordinary-arithmetic WPT uses nonzero calibrated bases, not registration independence. |
| `calc(sign(1em) * 1px)` | The generic Sign simplifier can replace the relative leaf's sign using its coefficient. This erases a real dependency. | Already held fix120. It is an actual reason the post-simplification inspector cannot certify the current checkout. |
| `light-dark(red, red)` | Color5 selects a branch's computed color; both independently compute to the same color. | Equality of independently computed branch results supports independence by direct semantic reasoning. No exact JS equal-color registration WPT was found in the bounded search; add one before production validation. |
| `light-dark(Canvas, Canvas)` | Equal source branches can both depend on color scheme. | Text/AST equality alone does not establish independence. |
| `light-dark(none, none)` as image | Existing `register-property-syntax-parsing.html` explicitly accepts it. Color5 defines none's transparent-image computation. | Preserve this existing positive. Direct unequal image branches remain the previously documented computed-stage policy question. |
| `currentcolor` | Color4 says it computes to itself; element color enters later used-value resolution. Existing registered-property color reftest uses it as an initial. | Preserve symbolic currentcolor. Used-color variation is not a counterexample to computed-value independence. |

Zero bases, signed zero, infinities and NaN are not hypothetical omissions from CSS math. The captured `typed_arithmetic.html` tests signed-zero relative inputs and division by zero; `calc-type-checking` specifies special-value handling. `0*x`, `x-x` and `x/x` therefore need their actual CSS evaluation domain and stage, not a proof over nonzero finite real x. No numeric evaluation or new browser run was performed here.

## Existing WPT boundary

The captured registration syntax test rejects ordinary em/ex/rem lengths and nested calc/list uses; it accepts physical viewport arithmetic, absolute-unit arithmetic, symbolic percentage mixtures and image light-dark(none, none). `initial-value-unit-arithmetic.html` validates absolute px multiplication/division. `typed_arithmetic.html` is an ordinary computed/used-value test with calibrated fonts, not a test that relative ratios are legal registration initials. `registered-property-computation-color-006.html` supplies the symbolic currentcolor initial control.

Bounded Searchfox searches did not locate exact registration tests for zero-times-relative, same-relative subtraction, or equal color light-dark. This is not an exhaustive WPT absence claim. Search output and retrieval chunks are listed in CHECK.json. No browser pass or interoperability is inferred from source text.

## Held sign witness, without another bug count

The actual local generic `sign_from` uses `unitless_value`; `simplify_and_sort_direct_children` calls it for a Sign leaf. Specified relative Length exposes its coefficient there. The later computation path resolves the length first. The [sign rule](https://drafts.csswg.org/css-values-4/#sign-funcs) operates on the resolved argument, and [em](https://drafts.csswg.org/css-values-4/#em) uses computed font size. For a non-font-affecting consumer, font 10px → 0px → 10px requires sign(1em) = 1 → 0 → 1, rather than a permanently folded 1.

Existing held record120 is `contextual-sign-folding`, candidate_installed=false, with an 11-case landing WPT and prior scoped paired evidence. It requires fix119, and its installation is separately held for integer consumers such as steps/subgrid expressions. HELD-120.json captures that current ledger entry. The earlier acceptance report's scoped acceptance must not be presented as current installation or a completed general repair. Reuse that workstream rather than counting a new defect or applying its narrow patch without the held prerequisites.

If a new release observation is desired, reuse the existing calibrated probe: positive `opacity:sign(1em)` expects 1/0/1; negative `opacity:calc(.5 + .5 * sign(-1em))` expects 0/.5/0; absolute sign(1px) remains1; mixed sign(1em - 1px) stays deferred and changes sign at zero font. Record an ordinary width:1em calibration and first/repeated snapshots at every font state. These finite exact cases avoid clamping away the discrepancy and do not prove the IEEE/domain-wide question. The already preserved held evidence makes a fresh discovery campaign unnecessary.

## Recommendation

Retain the inspector as diagnostics until the original selected value's dependency evidence survives all relevant simplifications, or the simplification passes have the needed source-correspondence guarantees. The held Sign counterexample is sufficient to reject unconditional trust in the current simplified AST. Replacing that with “reject every syntactic relative unit” is not a complete semantics implementation either, especially for equal branches and potentially independent cancellation. Preserve successful syntax selection and transactional failed-alternative rollback throughout.

For unresolved zero/cancellation registration acceptance, keep observations separate from conformance assertions and seek an explicit CSSWG/WPT decision if implementation choices require one. The fresh primary text supports semantic computed-value capability, but the bounded evidence does not adjudicate every such expression. The exact selected-AST/cache integration is in RETENTION.md; it can be implemented independently once the certificate contract is complete.

No source, index, epoch, staged artifact, canonical model or browser was changed. No new native fix, release regression or proof credit is claimed.
