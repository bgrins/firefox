# Current-context SVG length conversion

This scratch model fills a specific gap: changing a stored unit/factor while preserving its represented user-space value in one current context. It does not add canonical library coverage or establish a browser bug. The existing source lead remains unexecuted in the evidence bound here.

## Existing library coverage

| Existing module | Relevant coverage | Missing obligation for this setter |
| --- | --- | --- |
| CssUnitFactor | Fixed dimensional factors, unique lookup, positivity | No mutable source/destination representation |
| CssUnitScalar | Scaling a scalar into canonical units, signed-zero laws | No division by a destination factor or contextual setter |
| CssNumericEnvironment | Supplied percentage basis, availability and resolved value | Supplied basis is not proved current; no inverse conversion |
| CssEnvironmentUnits | Fixed/relative factors and source-unit denotation | One supplied environment; no mutation/round-trip law |
| CssCalcFiniteConversion | Calculation syntax to finite-expression conversion | Different meaning of conversion; not a DOM unit setter |
| ProviderObservation | Optional forcing before observation, history erasure | Does not prove both factors acquired by a mutating API |

No existing theorem found in these relevant modules establishes this setter invariant. `Conversion.lean` uses the same standard `Rat` arithmetic as the library without copying its existing parser, unit tables, signed-zero machinery or provider model. Nothing in the canonical library or its build cache was modified.

## Relation and proofs

For a supplied basis map, the denotation of `(unit, amount)` is `amount × basis(unit)`. The independent `Preserves` relation requires the requested output unit and equality of old/new denotations in the current context. It does not mention the conversion algorithm.

The algorithm preserves an identical unit without consulting its factor. Otherwise it rejects a zero destination factor, and computes `amount × sampled(source) / sampled(destination)`. Its input units are already validated and mutable.

The generic proofs establish:

- Soundness for conversion with the current basis, and completeness/uniqueness when the destination factor is nonzero.
- Agreement of just the source and destination factors suffices; agreement on unrelated units is unnecessary. Together with soundness this gives the explicit two-factor readiness obligation.
- A successful forward/backward conversion in the same context returns the exact original representation when the original unit's factor is nonzero.
- Identity conversion preserves the representation even with stale or zero sampled factors; nonidentity conversion to a zero factor fails in this mathematical model.

These are rational equalities, not a theorem that native floating-point conversion round-trips exactly. Factor agreement is sufficient, not logically necessary for every individual value: zero amounts or compensating factor ratios can hide stale inputs.

## Exact witnesses

The positive horizontal percentage basis is viewport width/100, and the px factor is one.

| Input / request | Sampled width | Current width | Converted representation | Current denotation versus required |
| --- | ---: | ---: | --- | --- |
| 50% → px | 200 | 400 | 100px | 100 versus200 |
| 100px → percentage | 200 | 400 | 50% | 200 versus100 |
| 50% → percentage | 200 | 400 | unchanged50% | 200 equals200 |

Fresh conversions give200px and25%, respectively. The destination-stale witness explicitly proves that the source px factor is already equal in both contexts; refreshing only a source-relative unit cannot establish preservation for that case. A further witness shows that correct conversion at width400 need not preserve the original representation's meaning after a later resize to200. The invariant is about the conversion's current context, not all future viewport states.

The zero-basis example probes the abstract algorithm's admission boundary. It is not a claim that native `FixAxisLength` exposes zero for this viewport path.

## Spec/native correspondence and limits

[SVG2 SVGLength](https://svgwg.org/svg2-draft/types.html#InterfaceSVGLength), read23October2026, first obtains the value represented in user units and then converts it using the target unit's context. Percentage conversion selects the associated element's directional viewport basis. This motivates the same-current-context preservation relation; the model does not prescribe a particular flush API.

The retained source audit binds scalar `SVGAnimatedLength::ConvertToSpecifiedUnits` and list `SVGLength::GetValueInSpecifiedUnit` to the multiply/divide shape. The identity shortcut corresponds to a list item or an already-set scalar base value; an unset scalar's notification/state initialization is outside this model. Native read-only/unit-validation errors, ownership/lifetimes, animation, mutation notifications, serialization, style/layout updates and change-notifier reentrancy are not modeled. The theorem assumes that the supplied factors denote the relevant current bases and remain coherent during evaluation.

Rat excludes IEEE overflow, underflow, NaN, infinity, rounding and signed zero. The concrete200/400 witness arithmetic is mathematically exact and simple, but this capsule neither executes the C++ arithmetic nor observes actual browser inputs. Native finite checks and transactional mutation remain separate obligations. Positive ordinary-width no-viewBox fixtures avoid asserting that every SVG percentage basis follows a CSS size change.

## Verification

Pinned Lean4.35.0-rc4, `LEAN_NUM_THREADS=2`, final exit0,14 axiom reports; no sorryAx, custom axiom, warning or compiler product in the final run. The initial and second logs retain failed authoring attempts; only `lean.log` is the final successful validation. No new target directory, canonical build, browser or native compilation was used.

Replay:

```
LEAN_NUM_THREADS=2 artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean artifacts/css-svg-length-conversion-model-v1/Conversion.lean
```
