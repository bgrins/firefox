# SVG/SMIL boundary

**Question:** Does the current SVG/SMIL chain justify changing existing equal-auto mixed-rectangle from-by and cumulative behavior to CSS componentwise addition?

**Scenario:** SVG animation elements target the CSS clip property, including the existing marker-based from-by controls; mixed numeric/auto rectangle operands; optionally repeatCount>1 and accumulate=sum. This is separate from HTML WAAPI.

1. Current [SVG Animations, relationship to SMIL](https://w3c.github.io/svgwg/specs/animations/#RelationshipToSMILAnimation) incorporates SMIL while reserving SVG-specific constraints. The directly retrieved Editor's Draft is dated9 November2026.
2. [SMIL animation function values](https://www.w3.org/TR/smil-animation/#AnimFuncValues) restricts from-by forms to:

   > attributes that support addition

3. [SVG animatable types](https://w3c.github.io/svgwg/specs/animations/#AnimationAttributesAndProperties) distinguishes numeric values from:

   > keywords (which are not additive)

   Its table also marks otherwise-unlisted types nonadditive unless their property definition supplies an exception. This is strong reason to retain the current SVG policy pending reconciliation; it is not explicit pseudocode for a rectangle containing both numeric and keyword components.
4. [SVG additive attributes](https://w3c.github.io/svgwg/specs/animations/#AdditionAttributes) and [SMIL accumulation](https://www.w3.org/TR/smil-animation/#AccumulateAttribute) suppress cumulative application when addition is unsupported. The deciding SVG phrase is:

   > does not support addition

5. The unresolved branch is the host's mixed-rectangle admission: how the SVG keyword restriction composes with clip's modern CSS by-computed-value definition. Existing SMIL tests and the historical native patch intentionally reject this case, but tests/history are not a normative resolution of that integration question.

**Verdict: INCONCLUSIVE** — the evidence does not authorize changing existing SVG mixed-auto rectangle behavior. Preserve SMIL's established admission while repairing the separately reached CSS contract, or seek a targeted specification clarification first.

| Route not established | Why |
| --- | --- |
| CSS matching-component rules automatically override SVG host admission | The SVG host has explicit nonadditive guards; no retrieved integration statement resolves this mixed-rectangle case. |
| Unsupported accumulation implies the whole animation must stop | SVG says to ignore unsupported cumulative behavior; from-by admission is a separate step. |
| Current SMIL tests prove the normative rule | They prove an implementation constraint and historical intent only. |

webspec-index query/exists could not resolve the SVG/SMIL multipage anchors (receipts retained). Directly downloaded primary HTML contains every linked anchor, verified in HTML-ANCHORS.json. Consequently no exhaustive SVG graph-search claim or NOT REACHED verdict is made. This is a named indexing/integration boundary, not absence of normative text. SVG1.1 was consulted for history; this trace uses the current SVG Animations draft and its normative SMIL reference.
