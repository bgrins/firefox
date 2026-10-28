# Selection before independence

Scenario: CSS.registerProperty, fresh valid name, supported non-universal syntax and explicit initial value. Manual official-primary trace read 2026-10-28; webspec-index is unavailable. SPEC-CAPTURE.json pins the HTML and verified anchors. No exhaustive indexed-route claim is made.

1. [Registration step 4](https://drafts.css-houdini.org/css-properties-values-api/#the-registerproperty-function) parses first and then checks the parsed result:
   > If parsed initial value is not computationally independent, throw a SyntaxError and exit this algorithm.
2. [Alternative matching](https://drafts.css-houdini.org/css-properties-values-api/#combinator) uses declared order. The later independence failure does not resume parsing. Step 6 inserts only after validation.
3. [Multipliers](https://drafts.css-houdini.org/css-properties-values-api/#multipliers) form lists; [computed-value rules](https://drafts.css-houdini.org/css-properties-values-api/#calculation-of-computed-values) determine selected-type computation. A sufficient certificate must account for all relevant components.

Verdict: REACHED for selection-before-independence and exit-before-insertion under these assumptions. Reclassifying a successful dependent parse as a grammar mismatch is the rejected route. Failed partial parses can be retried, but their temporary flags are not the selected value. Actual grammar results and CSS-to-model dependency interpretation remain premises; equal-branch semantics are not adjudicated.
