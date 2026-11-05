# Single rollback with unrelated matched blocks

The indexed candidate pays measurable whole-source construction cost even with one Rule trigger. At 256 unrelated payload blocks, its two medians are 16.504–16.523 microseconds/update versus 8.867–8.965 baseline, about 1.84–1.86 times baseline in this bounded workload. Literal and Layer controls remain close. This is a candidate design tradeoff, not a newly discovered release bug or a general Firefox performance estimate.

Each profile completed 107,520 measured updates and all exact value/report checks. Seven samples of 1,024 updates per row; observed medians in microseconds/update:

| Payload blocks / mode | A1 | B1 | B2 | A2 |
| --- | ---: | ---: | ---: | ---: |
| 0 / revert-rule | 5.645 | 5.508 | 5.859 | 5.977 |
| 32 / revert-rule | 6.094 | 7.363 | 7.207 | 6.250 |
| 64 / revert-rule | 6.484 | 8.770 | 8.809 | 6.250 |
| 128 / revert-rule | 7.207 | 11.621 | 11.660 | 6.973 |
| 256 / literal | 9.043 | 8.711 | 8.770 | 9.141 |
| 256 / revert-layer | 9.043 | 9.180 | 8.945 | 9.141 |
| 256 / revert-rule | 8.867 | 16.523 | 16.504 | 8.965 |

There is always one strongest opacity declaration in each mode. In Rule mode, zero payload still means one Rule trigger; it is not the chain benchmark's shared no-Rule floor. All N payload blocks match the probe and contain distinct custom-only declarations. The old scan's owner search should find the strongest trigger near the rule-tree leaf, whereas the indexed candidate eagerly visits every source block. Timing and changed opacity do not directly count native visits or allocation bytes.

A1 a5e88d/session75361/b8bf28 and A2 975289/session43275/0f4dff exited 0. Candidate owner 5f97d3/session6918/ce48a6 exited 0. Independent restoration audit 9b821f/session4870/1d89ab exited 0, verifying original sources/application/Git state, all owned process groups absent, backup removed and transition lock absent. Saved-data comparison 5af625 exited 0 and replayed all four raw streams, reports, source-role bindings and recorded cleanup.

All source/build bindings and explicit preferences match the longer-chain experiment: A+B+D plus ArcSlice baseline application built at 2d867, artifact-only harness/candidate revision 85e24df1f6960471e64bd64037889b607a1e5a88, and exact frozen indexed source bytes. The candidate has already passed all 190 correctness assertions and identical historical controls. No numerical timing threshold or statistical significance claim is applied here.

Next candidate work: lazily extend the ownership index only through requested originals and reject irrelevant property/priority prefixes before owner lookup. Preserve full normalized-priority equality, original-entry identity and the no-Rule allocation behavior. Consider many-longhand/all shorthand allocation costs as well as this one-property fixture. A new candidate still needs native compilation, the full correctness/control suite, both workloads and source-identity coverage. This experiment does not adopt a fix or increment the bug catalogue.
