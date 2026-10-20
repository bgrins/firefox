# Relative flex-item baseline trace

Question: may a relative block-axis offset on an in-flow flex item move its baseline-aligned containing flex box or the peer aligned with that box?

Scenario: an unfragmented 160 by 80 pixel inline-flex box, one text donor, parallel horizontal writing modes, no scrolling, and first or last baseline alignment in an outer inline or flex context. The text item is relatively positioned by minus ten, zero, or ten pixels; a static peer is otherwise identical.

1. [CSS Position 3, position](https://drafts.csswg.org/css-position-3/#position-property) lays out a relative box as static, then visually offsets it. Its definition prohibits changes to non-descendant box size or position except for ancestor scrollable overflow. The containing flex box and its peer are non-descendants of the shifted item.
2. [CSS Align 3, baseline export](https://drafts.csswg.org/css-align-3/#baseline-export) delegates flex-container baseline selection to Flexbox. It does not specify a relative-position exception.
3. [CSS Flexbox, flex baselines](https://drafts.csswg.org/css-flexbox/#flex-baselines) selects the natural item baseline or synthesizes from item edges, with first/last and row/column rules. Selection does not override the relative positioning rule. Its separate initial-scroll-position requirement is not exercised here.
4. The ancestor alignment therefore must use the item position from normal layout. The observed ancestor displacement of the opposite sign violates the non-descendant restriction. Removing the relative class restores both item position and ancestor alignment; restoring it reproduces the displacement.

Verdict: REACHED for the stated relative-position scenario. This is a direct normative-rule composition, not a claim that an automated call-graph query proves the result. Complete relevant section output and section hashes are retained in the spec logs; ANCHORS.json validates the cited anchors. The definition-only query omitted the surrounding prose, so position-property.log is the decisive source.

Gecko: the retained shared source has three baseline coordinate consumers using GetLogicalPosition. GetLogicalNormalPosition converts GetNormalPosition to the requested logical writing mode; GetNormalPosition uses NormalPositionProperty when present and the current position otherwise. The indexed provider definitions are retained as observations, not asserted byte-identical to the retained Git base. The source fix replaces the coordinate query without changing actual frame placement or overflow collection. The upstream standalone patch changes the two preexisting fallback consumers; a new helper added by the separate natural-donor fix will independently use normal position.

Boundaries: no claim here about arbitrary-coordinate overflow, normal-position property freshness, fragmentation, orthogonal donor synthesis, or sticky scroll updates. The later WPT expands relative positioning to vertical modes and empty donors; those receipts remain separate from this original probe.
