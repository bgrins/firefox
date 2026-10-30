# Font metric matrix on installed Firefox 158

The completed thirteen-case run produced **3 PASS, 10 FAIL, harness OK**. Root execution 29144 / 9eaccc / e8693c exited 0; inner WPT exit 1 retains the ordinary assertions. The earlier attempt stopped during an optional HTTP/3 server port collision, produced no complete test result and cleaned up. The retry disabled only that unused server. All test resources, profile settings and expected assertions were unchanged.

| Axis/input | Registered value at 20px | Literal reference | Result |
|---|---:|---:|---|
| Weight 700, ex | 16px | 10.7167px | FAIL |
| Weight 700, cap | 16px | 14.2833px | FAIL |
| Weight 700, ch | 20px | 11.0167px | FAIL |
| Italic selected face, ch | 20px | 11.0167px | FAIL |
| Condensed selected face, ch | 20px | 11.0167px | FAIL |
| Size adjustment 0.8, ch | 11.0167px | 16.5167px | FAIL |
| Vertical upright, ch | 11.0167px | 27.2333px | FAIL |
| Weight 700, ch through unregistered alias | 20px | 11.0167px | FAIL |
| Weight 700, ch through registered alias | 20px | 11.0167px | FAIL |
| Typed attribute containing 1ch, weight 400 | 8px | 20px | FAIL |

Family em/ch and weight em controls pass. Every failing callback recorded four phases: two axis selections at font sizes 20px and 30px. The saved check independently verifies all 40 phase records' selected style fields, em controls and positive/distinct ch calibrations, and finds 22 metric mismatches. Every non-attribute failure matches its normal-axis reference and fails its alternate-axis reference at both sizes. The attribute case remains 8px in all four phases. All eight font faces were loaded before target creation. PASS records prove their assertions completed; their phase values are not archived.

This establishes release-browser failures, not ten independently fixed bugs or exact internal causal routes. The selected-weight/style/stretch/adjustment/orientation cases strengthen the metric-readiness hypothesis. The attribute symptom must be checked on the published branch before novelty attribution: existing fix 58, commit 58200fa81a6f92f92a1898ba2866a2fbcbac0daa, already repairs resolved attribute unit metadata and lands attr-resolved-unit-dependencies.html, including explicit-font-size ordering. Its em case does not establish the new ch/weight matrix outcome.

Actual browser BuildID 20261007201254 and release changeset identify installed Firefox 158. Other run-info fields describe the local harness. The run used a fresh WPT stable profile, not an untouched user profile. Saved app critical-file snapshots and input hashes match; the runner reports its owned process group absent and temporary profile root removed. This outcome check is a saved-data audit, not an independent live full-app scan. No native baseline/candidate build or fix acceptance occurred.
