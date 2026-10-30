# Branch work

149 accepted native fixes remain committed locally; held ID 120 and two test-only repairs are excluded. [Every fix and commit](../css-pow-special-value-acceptance-publisher-v2/readout/README.md).

| Area | Accepted fixes |
|---|---:|
| Selectors, Bloom filters and scoping | 12 |
| Cascade, layers and shorthands | 6 |
| Parsing, tokens and CSS math | 31 |
| Attributes and custom properties | 19 |
| Animations, timelines and transitions | 18 |
| Text and fonts | 16 |
| Layout, sizing and positioning | 23 |
| Container queries | 3 |
| Colors, images, SVG and shapes | 8 |
| CSSOM geometry and hidden layout | 13 |
| **Total** | **149** |

| Current work | Verified status |
|---|---|
| Bloom milestones 1–6 | Complete within bounded recorded scope |
| Snapshot prototype V2 | Nine callbacks pass; source/app restored; no native acceptance |
| Duration/lifecycle local baseline | Five PASS, one pre-existing taint FAIL, two OK endings |
| Duration/lifecycle release comparison | Firefox four PASS/two FAIL; Chrome four PASS/two FAIL; different failure causes retained |
| Non-animation taint sinks | Local original and release Firefox: two PASS/four FAIL; Chrome: four PASS/two FAIL. Non-default fallback variant confirms the writing-mode gap |
| Lean input-selection model | Six audited theorems, five false controls rejected; no native refinement |
| Taint implementation design | Producer, propagation, sink rejection and metadata invalidation identified; four-file proposal in preparation, uncompiled and unexecuted |
| Min/max and logarithm fixes | Validated payloads awaiting separate signed publication |
| Research checkpoint V82 | Signing failed; state unchanged |
| Untracked audit | All 563 files accounted for |

[Plan](PLAN.md) · [Duration baseline details](../css-contextual-duration-taint-preservation-readout-v1/README.md). The generic sink branch baseline completed with two PASS, four FAIL and two OK endings. No native taint fix has been compiled or accepted.
