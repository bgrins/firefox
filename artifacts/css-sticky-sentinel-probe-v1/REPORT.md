# Finite sticky limits move an all-auto box

Status: reproduced in installed Firefox 158 and the shared Firefox 160 development build; no repair or accepted fix commit yet.

The sticky proof work exposed that the rectangle used for an unrestricted sticky axis has finite edges. Its far edge is 536,870,912 app units, about 8,947,848.53 CSS pixels. Source inspection suggested that an all-auto sticky box could reach this clamp through normal layout. A browser probe confirms it: a box following a 9,000,000px spacer is moved to about 8,947,849px, although both insets are auto. A 11,666,666px spacer produces the same clamp. This is an extreme-size rendering defect; no crash, memory corruption or performance impact is claimed.

[CSS Positioned Layout §3.4](https://drafts.csswg.org/css-position-3/#stickypos-insets) explicitly keeps the original position on an axis whose two insets are auto. Both static and relative controls retain that position in the probe.

Each final run has 42 observations: seven spacer sizes, static/relative/sticky, and scroll offsets zero/100. Six sticky rows above the sentinel differ; 36 rows agree, including all 28 static/relative controls. Measured containing-block height, spacer height, target height, requested scroll position, computed position and sticky auto insets are checked. Three near-boundary sizes distinguish the numeric threshold. Source and executable hashes remain stable within each run; temporary profiles are removed.

V1 used an overly strict less-than-one-pixel comparison and flagged two ordinary rows with one-pixel CSSOM rounding. It is retained. V2 allows two pixels, while the observed large cases differ by tens of thousands or millions. This tolerance addresses measurement precision, not the erroneous sticky movement.

The four-variant H1/H2 formal work retains this as a separate boundary finding. Its current theorem premises must not be weakened or replaced to count this as an H1/H2 repair. A new standalone Gecko/WPT repair requires native design and review, both-axis/one-active-axis controls, arithmetic and downstream range/timeline analysis, paired WPT and its own formal companion. Current runtime does not isolate the development changes; the independent installed release reproduces the same discrepancy.

Evidence: `COMPARISON-v2.json`, `candidate-v2/RESULT.json`, `release-v2/RESULT.json`. Discovery source: `../css-sticky-insets-proof-v1/SENTINEL-LEAD.md`; the formal producer remains in progress.
