# Indexed same-rule rollback validation

The indexed candidate compiled and passed all 190 assertions in the exact existing C correctness roster. The existing controls preserved five passing assertions, two known failures, their complete recorded signatures and the crashtest. This validates the frozen candidate cascade hash b454e10310175f3c41bbe8cadde6fb8d0b12ee3e1bb900f91422cd44cad453f3 with the existing cold-C stylist body; it does not add another bug entry or adopt the patch.

Native owner 806505/session92083/80b116 closed with exit 0. Independent restoration audit a402b8/session56673/5e8f63 closed with exit 0. The two original source files, three ArcSlice inputs, unchanged cascade-priority input, Git state, 9,378 application entries and three extra files were preserved. All six owned process groups are absent; the approximately 1 GB backup and source-transition lock were removed. The installed application is the committed A+B+D plus ArcSlice baseline, not the indexed candidate.

Both timing repetitions completed with all 1,680 measured value checks and full report validation. Observed medians in microseconds/update:

| Rule count | Indexed run 1 | Indexed run 2 |
| --- | ---: | ---: |
| 0 | 13.75 | 6.25 |
| 32 | 8.75 | 10.00 |
| 64 | 12.50 | 12.50 |
| 128 | 18.75 | 16.25 |
| 256 | 28.75 | 27.50 |

The prior scan candidate measured 280–291 microseconds/update at 256 rules, versus 11–21 for its two baselines. The indexed results remove the large scan-shaped growth in this bounded workload. These were sequential experiments on a shared machine, with short batches and observed baseline drift; do not claim a precise speedup, performance equivalence, universal complexity or release impact. The previous A–B–B–A report records the qualification and full controls. No timing acceptance threshold was applied.

The source changed only in the two reviewed overlay files during the experiment. Two intervening commits since the completed baseline build modified artifacts only; the owner verifies that ancestry and retains all exact baseline source/application hashes. Candidate source/build and harness revision is 8b26f6a764bfa926ffea5d71c17e26c5d42f9363, while the restored baseline application remains bound to 2d867102694afce0fdd85030e0dd68c7ef7ccacb.

The new Lean proof establishes owner-index completeness and full-key list/set gate equivalence under unique live entry ownership and coverage of every queried original. It does not verify native hash-table internals or identify shared allocation with semantic rule occurrence. Before promotion, run a separately versioned longer-batch baseline/indexed comparison, assess one Rule among many unrelated source entries, and finish the semantic occurrence audit. Keep the two-Rust-file fix with its C/substitution WPTs and D48-to-D64 expansion separate from this research.
