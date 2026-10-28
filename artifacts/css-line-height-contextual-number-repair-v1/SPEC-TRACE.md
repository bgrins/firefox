# Unitless line-height context trace

Verdict: REACHED for named-random unitless line-height producing a positive preferred height at a positive font size. This does not depend on random-index ordering.

[Inline3 line-height](https://drafts.csswg.org/css-inline-3/#line-height-property) admits nonnegative numbers, preserves the computed number, and obtains the preferred height by multiplying it by the used font size. Its percentage and length branches have different computation/inheritance behavior, so the native special mapper must remain.

[Values5 random evaluation](https://drafts.csswg.org/css-values-5/#randomness) maps a random base to the specified finite range. Bounds1 and3 therefore produce a positive number; fixed.25 gives1.5. [Cache sharing](https://drafts.csswg.org/css-values-5/#random-caching) makes an unscoped named key share its base in the same document. Scaling all bounds/steps by the same positive font size yields the length control. Small numeric/serialization differences are tolerated; zero versus a positive control is decisive.

[Tree-counting functions](https://drafts.csswg.org/css-values-5/#tree-counting) produce numeric inclusive-sibling counts or one-based indices. In the fixture the target is second of two siblings, then third of three after prepending, then second again. Multiplication by10px gives20/30/20. These additional cases are source-grounded, not yet browser-confirmed.

All four help fragments were verified against the captured current documents. Inline3 is captured here; Values5 is referenced by exact hash. Searchfox discovery locates the same mapper upstream. The installed CLI lacks --permalink, so this packet cites function names and exact captures rather than inventing a revision URL.
