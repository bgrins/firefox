# Nested Sign nonfinite boundary

**Question:** May relative-length conversion censor a nonfinite child inside `sign()` before its enclosing calculation completes?

**Scenario:** Valid `opacity:calc(.5 + .5 * sign(K * 1em))`, ordinary element, computed font-size0 or16px; K is NaN or either infinity. No percentage ambiguity or independent function context.

1. [Simplification](https://drafts.csswg.org/css-values-4/#calc-simplification) steps1.2,3,4 converts the child dimension using the available basis, then evaluates its parent. [Computed value](https://drafts.csswg.org/css-values-4/#calc-computed-value) supplies computed-time information.
2. [Sign](https://drafts.csswg.org/css-values-4/#sign-funcs) operates on the resolved argument. At font0, infinity multiplied by the zero em basis becomes NaN; a NaN coefficient remains NaN.
3. [Special values](https://drafts.csswg.org/css-values-4/#calc-ieee): “Any operation with at least one NaN argument produces NaN.” Sign and the enclosing multiplication/addition therefore propagate NaN.
4. [Range checking](https://drafts.csswg.org/css-values-4/#calc-range): “Nested math functions forming a calculation tree neither clamp nor round.” Only the outer calculation censors NaN to0; opacity's [computed range](https://drafts.csswg.org/css-color-4/#transparency) leaves0 unchanged.

**Verdict: REACHED** — child unit conversion is not a normalization boundary. Expected outer opacity is0 for all three K at font0; at16px it is0 for NaN,1 for +infinity,0 for -infinity.

| Rejected route | Reason |
| --- | --- |
| Treat child em conversion as a separate property value | It is a leaf within one calculation tree. |
| Censor at nested Sign | Sign remains inside the outer calculation. |
| Resolve infinity from coefficient sign alone | A zero basis changes the result to NaN. |

Primary drafts read24 October2026: CSS Values4 dated24 August2026; CSS Color4 dated20 October2026. Anchor validation is retained separately. `webspec-index` was unavailable; this is a manual trace of the primary algorithm text, not an exhaustive automated call-graph result. The verdict concerns specified behavior, not observed browser execution or acceptance of a patch.
