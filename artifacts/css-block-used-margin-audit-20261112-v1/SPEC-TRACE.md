# Overconstrained block used margins

Question: must getComputedStyle expose the adjusted inline-end margin of a
normal-flow block whose definite inline size overflows its containing block?

Scenario: a connected, rendered, non-replaced block in standards mode; no
positioning, floating, transforms, borders, padding, margin trimming, or HTML
alignment. The containing block is 100px wide and the child is 200px wide,
with both horizontal margins auto and direction ltr.

1. [CSSOM getComputedStyle step 5](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle)
   obtains resolved longhand values for the connected rendered element. The
   exact tool-emitted step and its guard are retained in cssom-trace.md. The
   depth-nine query found one one-hop route to CSSOM#resolved-value.
2. [CSSOM resolved values](https://drafts.csswg.org/cssom/#resolved-values)
   lists physical and logical margins among the properties whose resolved
   value is their used value when applicable and displayed. This scenario
   satisfies that guard. The overconstrained exception in the following
   category applies to insets, not margins. See cssom-resolved-values.md.
3. [CSS2 block width](https://drafts.csswg.org/css2/#blockwidth) requires the
   margin/border/padding/width sum to equal the containing width. The exact
   rule introduces that equation with:

   > The following constraints must hold among the used values of the other properties:

   Overflow makes auto margins zero for the subsequent rules. The next
   overconstraint rule adjusts the direction-dependent end margin. Thus the
   used left margin is zero and the right margin is -100px. For rtl the sides
   exchange. See css2-blockwidth.md for the complete deciding prose.

**Verdict: REACHED** — the current CSSOM/CSS2 rules require the adjusted used
margin for this scenario. The browser observation is zero instead of -100px.
The CSS2 portion is a manually inspected declarative rule, not an additional
algorithm edge discovered by the graph tool. No competing route was found or
rejected. CSSOM#dom-window-getcomputedstyle, CSSOM#resolved-value, and
CSS2#blockwidth were independently validated with webspec-index exists.

## Source and historical interpretation

ReflowInput::CalculateBlockSideMargins already computes the negative margin
in its reflow state. Its negative-space return bypasses the later update of
nsIFrame::UsedMarginProperty. nsComputedDOMStyle::GetMarginFor reads that
property for layout-dependent margins; simple lengths have a distinct path.
The proposed repair refreshes an existing property before that early return.
It does not change the margin allocation or create properties for plain lengths.

This is historical rediscovery: bug 381328 comment 0 described the same
negative-end-margin symptom and comment 1 identified early cache storage.
That bug was closed as a duplicate of bug 1298008, whose positive auto-margin
repair did not update this early return. Neither a new security issue nor
proof-generated discovery is claimed.

Current Chromium source distinguishes fixed margins from layout-derived ones
in MarginRight::CSSValueFromComputedStyleInternal. Its ResolveInlineAutoMargins
computes a negative inline-end value for overflowing auto-end cases. These
source observations support the auto-end comparison but are not a Chromium
runtime result, nor evidence of agreement for every percentage/fixed case.

- https://bugzilla.mozilla.org/show_bug.cgi?id=381328
- https://bugzilla.mozilla.org/show_bug.cgi?id=1298008
- https://raw.githubusercontent.com/chromium/chromium/main/third_party/blink/renderer/core/css/properties/longhands/longhands_custom.cc
- https://raw.githubusercontent.com/chromium/chromium/main/third_party/blink/renderer/core/layout/length_utils.cc

The broader discrepancy between literal-length reporting and CSS2 used values
is not resolved here. The focused candidate preserves that existing behavior.
Cross-engine runtime compatibility and additional consumers of cached margins
remain review considerations.
