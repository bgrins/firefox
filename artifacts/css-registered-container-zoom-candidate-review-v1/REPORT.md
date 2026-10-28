The experimental candidate realizes the proposed physical-axis canonical coordinate predictions in this capture. This is observational confirmation of the chosen implementation contract, not proof of normative parity. The separate horizontal cqi/cqb axis discrepancy remains.

Both saved raw payloads independently replay through the sealed validator and reproduce their summaries. The comparison also recomputes exactly:30 of42 initial cases and all3 mutation sequences changed. All124 target observations remain present with no registration errors. Pre/post preservation, application metadata and owned profile/group/server cleanup receipts check successfully. Root observed candidate session25578 launch8f90fe terminalcfb47d exit0; this reviewer did not directly observe that OS exit and launched no browser. Candidate RESULT SHA:f318977f4fbb8326611915f53086cfb44026ecc6ede545da4dec804e9d52920c.

All42 initial ordinary target records,4 ordinary small-viewport fallback controls and10 mutation ordinary records are byte-identical to the original capture. Ancestor measurements and environment snapshots also match. The current execution HEAD is6eb538; historical candidate56 application metadata retains1c787. Bytes, identities, symlink and BuildID agree after only that authenticated revision-label difference. Both observation runs use fresh default profiles, not WPT preferences.

Core 100cqw results (both direct and ready-primary/unused-fallback registered paths):

| Parent zoom | Target zoom | Candidate custom / width | Candidate rect width |
|---|---|---|---:|
| 1 | 1 | 200px / 200px | 200 |
| 1 | 2 | 200px / 200px | 400 |
| 1 | 0.5 | 200px / 200px | 100 |
| 2 | 1 | 200px / 200px | 400 |
| 2 | 2 | 200px / 200px | 800 |
| 2 | 0.5 | 200px / 200px | 200 |

The demanding parent2/target2 row changes custom100→200px, consuming width400→200px and rect1600→800. Ordinary cqw stays width100/rect400. Agreement with ordinary cqw is deliberately not the criterion: ordinary handling already has bug1894104.

Per-axis observations support distinct source normalization. The outer container's raw measured width640 at effective zoom2 yields registered cqw320px; the inner container's height120 at effective zoom1 yields cqh120px. Both custom CSSOM and width now agree with those values, for both target writing modes. Rect widths are640 and240 because the consuming target's effective zoom is2. The height is no longer wrongly exposed as60px. This distinguishes the source-container scale from a uniform target-scale division.

Logical-axis scheduling remains unresolved: for a horizontal target, registered cqi is120px and cqb320px while ordinary uses width320 and height60 CSSOM under zoom. The registered paths retain the inherited vertical-axis choices seen before normalization. For a vertical target, the axis choices align. The change repairs representation scale for whichever physical source was selected; it does not establish that logical selection used the final target writing mode. The separate no-zoom logical-unit investigation owns that question.

No-container fallback is also consistent with the proposed canonical contract: registered cqw stays1366px and cqh683px at target zoom1 and2, matching the ordinary svw/svh control lengths and scaled geometry. Ordinary cqw/cqh themselves remain unchanged. Literal200px and viewport1366px registrations now expose canonical custom values across all tested zooms. Percentage registrations remain100%, with every complete percentage target record unchanged; no claim about arbitrary mixed percentages follows.

Mutation results preserve the expected separation: targetzoom1→2→0.5→1 keeps custom/width200px while rect400→800→200→400; parentzoom1→2→1 keeps custom/width200px while rect400→800→400. Container width200→300→200 changes both registered custom and consuming width200→300→200, and rect800→1200→800. Both registered paths agree in every step. Ordinary controls remain exactly their baseline observations.

No new numerical oracle, accepted fix, security claim or native-equivalence proof is added. These simple integer dimensions and zooms do not discharge quantization/IEEE error, other layout modes, transforms, subframes, animation or broad regressions. READOUT.json retains all compact before/after values and complete candidate mutation snapshots; exact raw evidence is hash-pinned in REFERENCES.json.
