# Third raw-attribute oracle: implicit function closure at EOF

The first raw O/C comparison repaired the 13 expected failures but failed its acceptance gate on the historical EOF expectation in attr-cycle. The candidate returned a CSS string containing the exact characters `attr(data-foo`; the existing test expected abc. `OBSERVATIONS.json` retains the exact raw row and complete per-test counts; it does not recast that failed comparison as passing.

`SPEC-TRACE.md` adjudicates the result from freshly fetched primary CSS Syntax and Values algorithms. An independent trace reaches the same outcome. EOF completes the nested function object, while the raw read returns unchanged DOM attribute text. This warrants an explicit third historical oracle correction; it is not a new native implementation change or separately counted bug.

`PROPOSED-CONTROLS.json` supplies seven reduced controls for the next immutable proposal: raw EOF, explicit raw-string EOF, real typed recursion with one or two EOF-closed functions, valid trailing tokens under universal syntax, invalid trailing tokens under string syntax, and an unmatched closing token. These are predictions, not browser observations. The previous 29 new tests and both opposite-order assertions must remain intact.

No live WPT expectation, native source, runtime evidence, capsule, index, HEAD or epoch was changed. No browser/build was launched by this audit. A newly frozen fixture requires a fresh original/candidate comparison before acceptance. This trace extends beyond the normalized Lean model: that model does not prove CSS tokenization, EOF recovery or parser/native correspondence.
