# Logical-unit writing-mode trace

Question: must a noninherited registered length use the target element's own computed writing mode when mapping logical container and viewport units?

Scenario: zoom is never set; a 320×180 iframe has horizontal root writing mode. A horizontal size container is 320×180; its vertical inline-size child is 200×120. The consuming element has an explicit horizontal or vertical writing mode, changed on the same node. There are no font, zoom, style-query or custom-property cycles. Registration is <length>, noninherited, initial 17px. Direct and unregistered var(--ready) inputs contain the same unit.

This is a manual clause trace. webspec-index is unavailable in this environment, so no machine route enumeration or negative reachability claim is made. Current official documents were read with the web tool; already captured same-day official HTML is hash-pinned separately. The earlier Values4 informative summary says root element, but its normative unit definitions and change history supersede that misleading summary.

1. [Properties and Values API computed values](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) requires admitted length dimensions to convert to canonical units. [Substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) then substitutes that computed value. Thus both custom CSSOM and the consuming width must reflect the same resolved length.
2. [Values4 viewport units](https://drafts.csswg.org/css-values-4/#viewport-relative-lengths) defines vi/vb by the box's inline/block axes. The exceptional initial-writing-mode rule applies when no styled element exists, not to this ordinary styled target. Its change history explicitly records moving vi/vb to the element's computed writing mode. Therefore vi maps to width for horizontal targets and height for vertical targets; vb swaps these.
3. [Conditional5 container lengths](https://drafts.csswg.org/css-conditional-5/#container-lengths) evaluates units per element on the relevant axis, selecting the nearest eligible ancestor for that physical axis. The vertical inline-size inner container supplies height120; it cannot supply width. The outer size container supplies width320. [Writing Modes abstract dimensions](https://drafts.csswg.org/css-writing-modes-4/#logical-dimensions) supplies the logical-to-physical distinction.
4. [Current upstream container-units-selection WPT](https://github.com/web-platform-tests/wpt/blob/master/css/css-conditional/container-queries/container-units-selection.html) independently encodes this exact interpretation: changing the child's writing mode swaps cqi/cqb; changing the ancestor's writing mode changes which physical axis it contains. This is corroborating executable prior art, not a substitute for the normative clauses. The container-unit summary alone is less explicit about whose logical axes apply; this draft combines the per-element rule with the established WPT interpretation.

Verdict: REACHED for own-writing-mode viewport resolution and registered canonical computation. The proposed cqi/cqb oracle follows the per-element axis interpretation already used by upstream WPT; no new container-axis semantics are proposed. Both ordinary logical and independently selected physical units are mandatory controls, so a broader container-axis disagreement remains visible.

| Target writing mode | 100cqi | 100cqb | 100vi | 100vb |
|---|---:|---:|---:|---:|
| horizontal-tb | 320px | 120px | 320px | 180px |
| vertical-rl | 120px | 320px | 180px | 320px |

This trace does not adjudicate CSS zoom, container size coordinate scaling, or scheduling-dependent cycles. No accepted bug or formal-model coverage is added.
