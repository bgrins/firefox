# Literal line-height and a registered lh consumer

**Question:** With registered `--lh:1lh`, literal `font-size:20px; line-height:20px`, and `font-weight:calc(var(--lh) / 20px * 700)`, must `--lh` compute to `20px` and weight to `700` despite a separate registered `--metric:1ch`?

**Scenario:** Both registrations have `<length>` syntax and valid independent initial values; these are the winning declarations on an ordinary element. No animation, attribute, unused fallback, alternate declaration, or reference from font-size/line-height to either custom property is involved. Other font inputs are fixed; fonts are loaded for any metric comparison. The separate metric is not consumed by weight or line-height. This is a proposed discriminator, not an observed browser result.

1. [CSS2 §10.8.1, line-height](https://drafts.csswg.org/css2/#propdef-line-height) computes a length to its absolute value:
   > for <length> and <percentage> the absolute value; otherwise as specified

   Thus literal `20px` remains `20px`. Font choice can affect glyph geometry and line boxes, but does not turn this declared length into `normal` or a metric-dependent value.

2. [Values4 §6.1.1, lh](https://drafts.csswg.org/css-values-4/#lh) defines the unit by the element's computed line-height:
   > Equal to the computed value of the line-height property of the element on which it is used

   The additional conversion of `normal` through first-font metrics is inapplicable. Therefore `1lh` here is `20px` independently of weight.

3. [PVAPI §2.4 and §2.7](https://drafts.css-houdini.org/css-properties-values-api/) compute a registered length literal in canonical units before var substitution:
   > registered custom properties substitute as their computed value

   `var(--lh)` therefore supplies the computed `20px`, not a fresh `1lh` to resolve in the weight property's context. Values4's parent-metric exception for units directly in font-affecting properties does not change this already absolute substitution.

4. [Values4 §10.9](https://drafts.csswg.org/css-values-4/#calc-type-checking) gives division the left type multiplied by the inverse right type. Equal length dimensions cancel; `calc(20px / 20px * 700)` is the number `700`. [Fonts4 §2.2](https://drafts.csswg.org/css-fonts-4/#font-weight-prop) accepts numbers from 1 through 1000 and computes a number. Its computed weight is therefore `700`; actual font matching is a later question.

5. [PVAPI §2.7.1](https://drafts.css-houdini.org/css-properties-values-api/#dependency-cycles) adds a font-size dependency for registered lh and, additionally:
   > add an edge between the property and the line-height of the current element

   Both ordinary values are literal leaves in this scenario. The value-dependency chain is `weight → --lh → literal line-height`, with an additional `--lh → literal font-size` constraint. No value returns to weight. The separate `--metric:1ch` reads the selected font, including its final weight, but nothing above consumes `--metric`. Its numeric result need not be `20px`; compare it to literal `1ch` under the same final font.

**Verdict: REACHED** for the narrow `--lh:20px` / `font-weight:700` oracle. This is a manual trace of current normative clauses, not an exhaustive indexed algorithm graph. It does not depend on deciding a genuine registered metric/weight cycle. Firefox's generated LineHeight→Weight ensure order is an implementation scheduling edge; adding it to this value graph would manufacture the cycle being investigated.

| Different route | Boundary |
|---|---|
| `line-height:var(--lh)` with registered `--lh:1lh` | Returns from line-height to the registered value whose explicit relative-unit dependency is line-height. PVAPI cycle resolution applies; this trace's 20px/700 oracle no longer applies. |
| A direct recursive `var()` chain | Current [Variables §3](https://drafts.csswg.org/css-variables-1/) obtains computed custom values; [Values5 Appendix A](https://drafts.csswg.org/css-values-5/#property-replacement) guards recursive property/substitution contexts. A repeated guarded context is a true substitution cycle, not an unfinished scheduling action. |
| `line-height:normal` or weight consuming `--metric:1ch` | Can introduce real metric feedback. The exact registered metric-cycle policy remains a separate unresolved bridge recorded in the sealed prior cycle-boundary trace; no policy is chosen here. |
| Direct `font-weight:calc(1lh / 20px * 700)` | Values4's parent-metric exception applies to that direct relative unit. It is not equivalent to substituting a registered computed length. |
| Inherited/default builder metrics used while a prerequisite is pending | No clause above permits replacing a valid acyclic computed value with an intermediate implementation value. |

Primary pages were freshly retrieved on 2026-11-02: PVAPI ED 2026-08-06, Values4 ED 2026-08-24, Fonts4 ED 2026-10-26, Variables ED 2026-10-09, Values5 ED 2026-10-27, CSS2 ED 2025-12-30. `PRIMARY.json` records the reads. `webspec-index` could not query its read-only database and did not recognize the Houdini host; all requested anchor checks failed for those access reasons (`INDEX.json`). No indexed route or completed anchor validation is claimed. Browser-visible primary sections and their deciding text, rather than an absent tool route, support the verdict. No fixture, runtime, native source, or canonical state was changed.
