**Question:** Does the currently published CSS text establish that a registered `100cqw` value must use the selected container's content width divided by that container's effective zoom?

**Scenario:** A registered `<length>` on a child contains `100cqw`; its nearest eligible size container has `width:200px`, no padding or borders, no transforms, and effective zoom 1 or 2. The child's own zoom varies independently. There is no cycle, viewport fallback, or ambiguity in physical-axis selection.

This is a manual trace of official documents fetched on 2026-10-27. `webspec-index` is absent; anchors were verified against captured HTML. No exhaustive graph enumeration is claimed.

1. [Properties and Values computed-value calculation](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) parses the registered length and converts the dimension to its canonical unit. Registration does not preserve the original `cqw` token for later substitution.
2. [Container-relative lengths](https://drafts.csswg.org/css-conditional-5/#container-lengths) select the nearest eligible ancestor independently for each axis. Their evaluation uses “the same rules as container size queries”.
3. [The width container feature](https://drafts.csswg.org/css-conditional-5/#width) reads the query container's content box. The captured published text does not specify a zoom coordinate conversion at this point. The container-unit section contains no additional zoom conversion rule.
4. [CSS Viewport's zoom rules](https://drafts.csswg.org/css-viewport/#zoom-property) apply effective zoom during used-value calculation. [Unscaled length](https://drafts.csswg.org/css-viewport/#unscaled) is defined relative to a particular element, using that element's effective zoom. This supplies a conversion once the relevant coordinate space is identified, but does not itself identify which form the size-query feature reads.
5. [Registered substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) serializes the computed registered value into the consuming property. [The CSSOM rule](https://drafts.csswg.org/css-viewport/#zoom-om) requires non-percentage length results to be unscaled, while bounding rectangles include zoom. This constrains serialization and consumption; it cannot by itself select the earlier container-coordinate convention.

The [CSSWG resolution in issue 10268](https://github.com/w3c/csswg-drafts/issues/10268#issuecomment-2192195262) chose the Chrome/Firefox behavior for container queries. The subsequent [editor comment](https://github.com/w3c/csswg-drafts/issues/10268#issuecomment-2269576031) proposes explicitly making principal-box bounds unscaled. The issue remains open with Needs Edits in the captured API response. Its body also mentions container-relative units, but the linked testcase covers query conditions. These are strong evidence for using the source container's unscaled size, not proof that the missing edit has appeared in the published rule.

**Verdict: INCONCLUSIVE** — the published chain reaches the content-box read but does not explicitly complete its zoom-coordinate conversion. The proposed per-source normalization is consistent with the recorded CSSWG resolution and measured fixed-size cases; it remains an implementation inference pending the missing specification edit or a stronger interpretation reviewed by the relevant editors.

| Alternative argument | Why it is insufficient |
| --- | --- |
| Match ordinary Firefox `cqw` exactly | Ordinary container units have the existing zoom issue tracked as bug 1894104. Parity is not an independent oracle. |
| Divide every axis by the target's zoom | The selected axes may come from different containers; the target is not established as the coordinate owner by this trace. |
| Use CSSOM serialization to decide the container input | CSSOM constrains the output representation after the length has been computed. |
| Treat a CSSWG resolution as already-published prose | The recorded follow-up still requests the unscaled-bounds edit. |

The complete candidate observation remains useful evidence: all 124 target observations were collected, ordinary controls were preserved, physical-axis values matched the experimental per-source predictions, and the separate logical-axis scheduling issue remained. This trace does not change the accepted-fix count or claim native/formal refinement.
