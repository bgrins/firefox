# Hidden OOF boundary diagnostics

## Handoff

`hidden-oof-provider-boundaries.html` has **16** independently named tests: 8 provider cases, 4 containing-block transitions, 2 external-to-inner-flex ownership cases, and 2 OOF fragmentation cases. `EXPECTED-ROSTER.json` is the exact ordered roster. Registration-only Node execution confirms 16 unique names without invoking callbacks. No browser, build, native, Git or index mutation occurred. Earlier sealed proposal and tests remain unchanged.

These are additional diagnostics for the root-owned four-variant experiment, not assertions of new reproduced bugs. All target observations follow an outer flush and precede visible-reference queries. Reference assertions run before target assertions. No unsupported case is silently skipped; calibration failures must be reported separately from target mismatches.

## External containing-block feasibility: correction to earlier source discussion

For ordinary descendants, a hidden flex box establishes absolute and fixed positioning containing blocks through its containment effects. It therefore cannot keep an ordinary absolute/fixed descendant's containing block outside that hidden box. The earlier sealed OOF proposal's external-owner discussion described the native API's possible ownership distinction; it did not establish this ordinary web topology as reachable. Do not promote that discussion into a demonstrated counterexample to marking the hidden owner's absolute list.

Layout and paint containment both establish these containing blocks. Size containment also makes the contained box monolithic. The tests below either change the containing block when hidden is toggled or keep an external-to-inner-flex owner **inside** the hidden boundary. They never require a normal OOF descendant to escape the hidden ancestor. [CSS Containment layout](https://drafts.csswg.org/css-contain-2/#containment-layout), [paint](https://drafts.csswg.org/css-contain-2/#containment-paint), [size](https://drafts.csswg.org/css-contain-2/#containment-size), [hidden contents](https://drafts.csswg.org/css-contain-2/#content-visibility).

This is an additive clarification; the earlier sealed reports were not edited. Top-layer, nonordinary SVG and unusual box-generation exceptions are not covered by the ordinary feasibility conclusion.

## 8 provider tests

Canvas, outer SVG, flex and grid each have static-position and explicit-offset cases. The OOF border box is initially12×20, then20×30, in a positioned200×80 flex subject at(10,10). Static center expects(104,10) initially and(100,10) after resize. Explicit(7,9) offsets expect(17,19) throughout. Each test warms, hides, prepends a20px in-flow child, resizes the OOF and shows the subject. A visible peer performs the same mutations.

Canvas and outer SVG avoid external resources; this is CSS box geometry, not an image/network test. Flex/grid providers contain a small child but the observed object is the OOF root. These differ from the prior ordinary-block fixture. Searchfox provider excerpts show canvas/SVG proceed into sizing rather than using the ordinary block early return, while grid has a hidden-in-flow-parent return. They challenge the proposal's marking of providers that may still do work, as well as a different skipped provider.

Source-discovery limitations: `provider-3.txt` is a misresolved Searchfox definition excerpt in ComputeAvailableSizeForItems, not a full flex Reflow binding. `flex-hidden-entry.txt` is the subsequent targeted discovery. The saved excerpts are current indexed source, not a proof that the root's pinned binary dispatches to those exact bytes. Actual frame types, early-return execution and dirty flags need native tracing if used for causal claims.

## 4 containing-block transitions

A transformed host at(10,10) establishes a containing block for both absolute and fixed descendants. Its unpositioned flex child is offset40px/30px. Before hiding, explicit(7,9) gives(17,19). Hidden containment moves the containing block to that flex child, giving(57,49). Showing restores(17,19).

The independent reference applies explicit `contain:size layout style paint` only during the hidden phase, preserving the expected containing block without suppressing its contents. Both container dimensions are fixed, so content-independent sizing is controlled. Direct OOF and leaf-first observers are separate tests. The leaf is50%×40% of the12×20 parent, giving6×8. For absolute cases, offsetParent is captured **after** the target reads and checked against the actual host/subject identity. Fixed cases use the distinct calibrated coordinates rather than treating offsetParent as an ownership API.

This tests real external→local→external ownership changes. It must not be read as external ownership while hidden. The transformed host introduces no nonzero or fractional transform.

## 2 external-to-inner-flex cases

The outer positioned flex subject owns an absolute frame whose placeholder is inside a nested unpositioned flex. The root or its leaf is queried first. offsetParent must remain the outer subject before/while hidden. Explicit offsets are relative to the outer subject, not the inner flex's moved content box. Adding an inner in-flow sibling does not change them.

This is an actual ownership distinction, but the owner is within the hidden boundary. The OOF's immediate in-flow parent is the inner flex, which does not itself have hidden content visibility. Thus the proposed immediate-parent mark predicate need not fire. These are useful preservation controls, not evidence that the original direct-hidden-parent failure has an external-owner variant.

## 2 continuation cases

A fixed220×40 outer flex/block contains a complete two-column context (100px columns,20px gap). A positioned ordinary block inside the columns has80px of normal content and an absolute60×80 child with two40px blocks. The absolute child and its containing block must each produce more than one visible rectangle. Proposed exact OOF calibration is `(10,10,60,40),(130,10,60,40)`. Reducing second chunks to20px and the OOF height to60px changes the second rectangle to `(130,10,60,20)`.

The whole fragmentation context is inside the hidden boundary. The hidden outer itself is not required to fragment. No break-before/after is imposed on the absolute box. Absolute positioning participates in the containing block's fragmentation flow; CSS break properties do not provide a shortcut to forcing a break on the absolute box itself. [CSS Fragmentation](https://drafts.csswg.org/css-break-3/#transforms).

The target's immediate in-flow parent is the internal positioned block, not the hidden outer. Accordingly these cases preserve an actual fragmented OOF path under hidden ancestry, without claiming a direct-hidden-parent continuation executes the new marking branch. Frame identity across hiding is not asserted: observable fragments may be rebuilt. If visible fragmentation or the exact lists fail, retain that calibration failure and investigate it; do not drop extra zero-sized fragments or replace the list with its bounding rectangle.

## Oracle and remaining scope

The root-observer alignment expectations follow the special static-position rules for absolute flex children; an in-flow sibling does not become part of their sole-item static-position calculation. [Flexbox positioned children](https://drafts.csswg.org/css-flexbox-1/#abspos-items). Client rectangles observe current box fragments, including zero-sized ones, in their specified order. [CSSOM View](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects).

Full virtual callback behavior, already-dirty subtree pruning, external frame-list lifetime, all continuation/reparent histories, anchors, top-layer ownership and numerical overflow remain outside this finite diagnostic. Expected PASS values are proposed assertions, not claimed results. All visible controls and existing unchanged tests must be retained in the runtime comparison; a source-level conditional law does not make an unavailable calibration pass.
