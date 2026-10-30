# Original finite-depth value projection

The frozen original run (81249 / 88aff8 / exit 0; browser exit 1) reports four FAIL callbacks and one OK ending. All four literal and initial calibrations pass. This saved-record projection preserves those outcomes and does not inspect the running candidate.

Here `new` and `old` identify the generation decoded by `Oracle.bit`: metric 16/32 or leaf opacity 0/1, with parity reversed at each dependency edge. Stage 0 is the root, intermediate stages are 1 through depth, and the opacity leaf is stage depth + 1.

| Intermediate depth | Later contextual generation vector | First CSS/effect duration mismatch | First and three passive leaf samples | Required final leaf |
| --- | --- | --- | --- | --- |
| 1 | new, new, old | Leaf stage 2: 1000 / 2000 ms | 0, 0, 0, 0 | 1 |
| 2 | new, new, old, old | Font stage 2: 1000 / 2000 ms | 1, 1, 1, 1 | 0 |
| 4 | new, new, old, old, old, old | Font stage 2: 1000 / 2000 ms | 1, 1, 1, 1 | 0 |
| 8 | new, new, old, old, old, old, old, old, old, old | Font stage 2: 1000 / 2000 ms | 1, 1, 1, 1 | 0 |

At every depth the later root font is 32px and the first intermediate line-height is the new 16px, with CSS and effect durations both 2000ms. The remaining output metrics decode to the old generation. At depths 2, 4 and 8, the next font remains 16px although its CSS duration is 1000ms and its applied effect duration remains 2000ms. At depth 1 the same timing mismatch occurs directly on the leaf. Both detailed snapshots, before and after membership reads, are equal; all recorded animation/effect identity checks are true. Literal post-intervention snapshots and samples decode entirely to the new generation. Both modes' initial snapshots decode entirely to the old generation.

This is an output-value match to the prefix through stage 1 in the existing Completion/Oracle model. It does not establish the model's queue, flight, evaluation, coverage or readiness state, or count Gecko traversals. Detailed style/timing reads are sequential and occur after the passive leaf samples; they cannot establish the intermediate values at the first leaf getter. The model's evaluation operation must not be identified with a native removal or consumption marker. No new theorem or native scheduling/refinement claim is made.

`project.py` authenticates the frozen runtime, model and reference hashes, then decodes the records without changing their numerical observations. `PROJECTION.json` retains each selected metric and both duration values. Reproduce into a fresh output path with `python3 -I -B -S artifacts/css-contextual-duration-finite-depth-original-projection-v1/project.py /tmp/finite-depth-projection-new.json`. The output path must not exist. This analysis does not change any fixture, runtime or acceptance count.
