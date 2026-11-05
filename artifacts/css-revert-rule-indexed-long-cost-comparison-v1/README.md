# Indexed C: longer-batch A–B–B–A comparison

All four profiles completed 107,520 measured updates with exact opacity checks and complete validated raw reports. The indexed candidate removes the previous scan-shaped cost but retains measurable Rule-specific overhead. At 256 rules, medians were 24.648–26.016 microseconds/update versus 10.742–10.762 for baseline. Literal and Layer controls remained close. This is about 2.3–2.4 times baseline in this synthetic one-element workload, not an estimate of end-user impact or overall Firefox performance.

Seven samples of 1,024 updates per row; all modes use identical fixed batches and preferences. Observed medians in microseconds/update:

| Count / mode | A1 | B1 | B2 | A2 |
| --- | ---: | ---: | ---: | ---: |
| 0 / revert-rule | 4.941 | 4.863 | 4.805 | 4.980 |
| 32 / revert-rule | 5.879 | 8.320 | 8.184 | 5.820 |
| 64 / revert-rule | 6.406 | 11.094 | 10.488 | 6.523 |
| 128 / revert-rule | 8.340 | 15.625 | 15.293 | 8.027 |
| 256 / literal | 10.449 | 10.469 | 10.137 | 10.391 |
| 256 / revert-layer | 11.230 | 11.309 | 11.133 | 11.426 |
| 256 / revert-rule | 10.742 | 26.016 | 24.648 | 10.762 |

These baseline medians were substantially more stable than in the earlier short-batch experiment. Longer batches reduce clock quantization effects but do not remove machine-load, allocation, GC or thermal confounders. The two profiles per source role do not support a universal statistical bound. No timing threshold was used. The reached opacity value remains the observable correctness check; native index/lookup counts were not instrumented.

Baseline source is committed A+B+D plus ArcSlice. Candidate uses the frozen indexed C cascade and cold-C stylist source already validated by all 190 correctness assertions and exact historical controls. This experiment changes no native algorithm. Baseline application build revision remains 2d867; harness and candidate build revision are 85e24df1f6960471e64bd64037889b607a1e5a88, with intervening commits checked to modify artifacts only.

Candidate owner f99787/session3643/52a723 exited 0. Independent restore audit 727408/session6129/966427 exited 0. A1 eee800/session56508/91e332 and A2 22f57a/session99751/8e9317 exited 0. Original sources/application/Git state were preserved, owned processes were absent and the backup was removed. The saved-data replay 107443 exited 0 and authenticated full reports, raw events, metadata, source pins and recorded cleanup for all four runs. It supplements the separate live restoration audit.

Next assess the separate single-trigger workload: indexing all source entries on the first Rule can charge unrelated declarations, a tradeoff hidden by a chain where every block triggers rollback. The shared-allocation versus semantic-rule-occurrence audit remains separate. Do not promote this candidate solely because it is faster than the original scans. No new bug entry is counted by this measurement.
