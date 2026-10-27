# Registered numbers, font operands and cycle handling

**Question:** Do current specifications require a font-size cycle edge for a registered `<number>` containing `calc(1em / 1px)`?

**Answer:** Its noncyclic computed value requires the element's font context. The precise self-dependent cycle invalidation is not fully specified by the reviewed rules. Keep numeric math support; fix unused/invalid branches independently of that unresolved cycle oracle.

**Scenario:** A non-root element, parent font-size 19px, registered `--n` with syntax `<number>`, inherits false and initial-value 3. No animations, alternative registrations, CSS-wide keywords or competing declarations. Except for explicitly noncyclic controls, its font-size is `calc(var(--n) * 1px)`.

## Trace

1. Registration accepts the declaration's token syntax initially, then validates the registered grammar at computed-value time. Rejection yields the registered property's invalid-at-computed-value-time behavior. A valid numeric function uses that function's computed-value rules. Registered var substitution uses the computed result, rather than the original em-containing tokens. [API computation](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values), [registered substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution).

2. Property replacement substitutes functions, checks guaranteed-invalid results, then parses the resulting value. Its grammar-failure branch says:
   > If this returns failure, prop is invalid at computed-value time; return.
   Non-inheriting registered `--n` then defaults to 3. [Property replacement](https://drafts.csswg.org/css-values-5/#property-replacement), [invalid substitution](https://drafts.csswg.org/css-values-5/#invalid-substitution).

3. A ready `--ready:5` supplies 5; var fallback substitution is conditional on an invalid primary. Consequently `var(--ready,1em)` selects no em operand. A missing primary selects 1em, which fails the number grammar; a ready red primary also fails that grammar without retrying its fallback. [var replacement, steps 2–5](https://drafts.csswg.org/css-variables-1/#replace-a-var-function).

4. `calc(1em / 1px)` differs: division inverts the denominator's length type, giving a dimensionless number after multiplication. Math with that result type is allowed where a number is required. The grammar admits the expression; it does not admit bare 1em. [Math type checking](https://drafts.csswg.org/css-values-4/#calc-type-checking).

5. Calculation simplification converts dimensions when context is available; computed math uses computed-value information. For a known target font-size 20px, the ratio becomes 20, and becomes 30 after setting font-size to 30px. This is a real semantic dependency, although the spec does not prescribe an internal graph representation. [Simplification](https://drafts.csswg.org/css-values-4/#calc-simplification), [computed math](https://drafts.csswg.org/css-values-4/#calc-computed-value), [font units](https://drafts.csswg.org/css-values-4/#font-relative-lengths).

6. API §2.7.1 explicitly adds relative-unit cycle edges only for registrations with a length or length-percentage syntax component. A component is a registration name plus optional multiplier: `<number>` does not acquire a length component merely because a parsed math operand has length type. The API's font-size-invalidating example is a length registration. [Unit-cycle extension](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles), [syntax component](https://drafts.css-houdini.org/css-properties-values-api-1/#syntax-component).

7. Values 5's generic guard covers substitution for the algorithm's duration. Property replacement invokes it and afterwards parses the result. The reviewed math rules do not explicitly call property replacement when converting em, or specify a repeated font-size guard for that conversion. Therefore the guard model cannot supply the missing native/normative bridge by itself. [Generic substitution](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function), [guarding](https://drafts.csswg.org/css-values-5/#guarded).

**Verdict: INCONCLUSIVE** for the exact self-font numeric-cycle result. Steps 4–5 require correct noncyclic numeric computation; steps 6–7 leave its cycle/defaulting integration unresolved. The direct-invalid and unused-fallback controls have determinate results independent of that gap.

## Alternatives and limits

| Proposed interpretation | Assessment |
|---|---|
| Every lexical em creates an invalidating edge | Wrong for discarded fallback text and number-grammar failures. |
| Numbers never require font context | Wrong for admitted, noncyclic dimension-cancelling math. |
| `<number>` implicitly contains a length syntax component | Confuses registered syntax components with expression operand types. |
| Always compute the ratio using the parent's font | No general authorization: font-unit special handling for font-affecting properties does not explain noncyclic registered-number results. The API's own length-cycle example prevents treating every indirectly consumed custom property as automatically exempt. |
| Generic substitution guards already prove numeric-cycle invalidation | No explicit em-conversion-to-property-guard call is established. |
| A mathematically cyclic equation determines fallback | `F = F` has many solutions; CSS needs an explicit cycle policy. Algebra alone cannot select initial or inherited values. |

An implementation may need a demand/order dependency to obtain the correct font for valid numeric math. Treating that as an invalidating SCC edge is a plausible extension, not an explicit mandate established here. A future spec clarification should define context dependencies for admitted typed values and their relation to substitution guards, including which participants default and how simplification affects dependency discovery. Do not label an inherited-font numeric-cycle observation as a newly established conformance bug from this trace alone.

## Defensible next tests

ORACLES.json contains eight assertion cases and one observation-only cycle case. Retain the prior 14-case comparison, including its failed local calibration. All proposed cases are unexecuted. The numeric-math controls use definite noncyclic font contexts and mutations; they prevent fixing the simple false-cycle cases by dropping valid math support. Do not use CSS.supports on a custom-property declaration as proof that its registered value computes successfully.

Versions reviewed: Properties and Values API ED 6 August 2026; Values 4 ED 24 August 2026; Values 5 ED 27 October 2026; Variables ED 9 October 2026. Current primary web renderings were checked on 27 October 2026 and agree with the cited decisive clauses in the existing pinned captures. REFERENCES.json identifies those complete captures; ANCHORS.json verifies every cited fragment in them. Fresh local HTML download failed DNS before any payload was written. No byte-identity claim is made between a fresh web rendering and a retained snapshot.

webspec-index is unavailable (command lookup exit 1), so this is a manual positive trace and an explicit integration gap, not an exhaustive NOT REACHED result. No tool installation or build was started. No browser, native source, index, HEAD, epoch, ledger or canonical Lean changes, no new proof or coverage credit, and no issue filing occurred.
