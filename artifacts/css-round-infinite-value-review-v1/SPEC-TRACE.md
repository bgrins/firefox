# Primary-source trace

Fresh CSS Values 4 Editor's Draft (dated 24 August 2026) was read on 28 October 2026 through the web tool. `webspec-index` is unavailable; the previously attempted bootstrap did not supply it. A direct Python fetch failed DNS before writing any capture. This is a bounded primary-text trace, not a generated exhaustive caller graph.

1. [Round argument ranges](https://drafts.csswg.org/css-values-4/#round-infinities) make a zero step and two infinite operands NaN. The finite-step rule for an infinite value is read subject to that zero exception.
2. [NaN rules](https://drafts.csswg.org/css-values-4/#calc-ieee) give NaN priority, propagate it through nested operations, and censor it to zero only at the top-level calculation.
3. [Simplification](https://drafts.csswg.org/css-values-4/#simplify-a-calculation-tree) requires sufficient numeric information before operator evaluation; an unresolved leaf does not itself establish that information.
4. [Font-relative lengths](https://drafts.csswg.org/css-values-4/#font-relative-lengths) supply the zero basis of the 1em diagnostic. The fixed-pixel control separates this from a general zero-font effect.

**REACHED:** the ordinary opacity diagnostics have a specified zero result for NaN/zero steps and preserve the infinity sign for a finite nonzero step. **INCONCLUSIVE here:** the appropriate contextual-easing API representation and admission policy. This trace does not convert observed parser rejection into acceptable behavior.
