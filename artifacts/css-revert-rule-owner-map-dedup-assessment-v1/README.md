# Owner-map dedup trial assessment

The tested dedup candidate preserves the prior incremental candidate's correctness results and supports preparing a local fix commit with its explicit prerequisite. This trial found no new correctness regression or performance result that requires abandoning the dedup representation. It does retain a substantial synthetic dense-chain cost: at 256 Rule declarations the candidate is approximately 2.31–2.47 times its fresh baseline's observed medians. Local packaging is a review boundary, not upstream approval or release performance acceptance.

## Candidate and correctness boundary

Native cascade SHA-256 `cac13ba7ff2bbdfd54b906d7854a8ba703c2b013770ed4d121eb6b16af1bed6e` changes only DeclarationSourceIndex relative to the previous incremental `d32913bd213ebaf1e5bbff4ed7117ec8af0003990807f6a3f2c3f5ed7ded41f1`: the first entry's owner-map membership replaces the separate visited-block set. Empty blocks are skipped after cursor advancement. C stylist remains `fd5ded7d96e15b16caacd03bc758da255333bdbed9b99bb4bc65bc6a1900b9b3`; applicable-declaration priority and Arc prerequisites remain unchanged. The built source/binary pins are retained in VALIDATION.json.

| Lane | Dedup result | Exact comparison to prior incremental candidate |
| --- | --- | --- |
| Correctness | 190 PASS, six page ends OK | All 196 callback/page-end signatures identical |
| Regression controls | 5 PASS, 2 known FAIL, four page ends OK | All 11 signatures identical, including failure messages and expected-field presence |
| Occurrence | 6 PASS, one page end OK | All seven signatures identical; 48 end-read markers cover all four phases |
| Dense timing | Two complete repetitions | Exact correctness and report gates pass |
| Single-trigger timing | Two complete repetitions | Exact correctness and report gates pass |

The unchanged controls are the two cycle expectations in `revert-rule-cycle.tentative.html`: “Cycle between revert-rule !important and revert-layer resolves to unset instead of lower layers” and “Multi-layer chain cycle with revert-rule !important resolves to unset instead of lower layers.” They remain failures, not additional fixes. Occurrence reads cover initial rollback, small value, large value, and return to rollback, twelve reads each. This uninstrumented trial does not itself demonstrate allocation sharing or semantic equivalence between CSS rule occurrences. No new bug count follows from callbacks or from the representation optimization.

## Formal scope

The completed OwnerMapDedup refinement imports the pinned incremental model. Under `UniqueOwner` and `IndexFor`, first-entry membership for a nonempty block is equivalent to complete prior indexing. The proof transfers owner-map/cursor equality across arbitrary finite query histories, successful covered lookup, and the unchanged full-key/prefix exclusion answer. Empty blocks, repeated blocks and later-entry queries are represented explicitly. Countermodels show that partial block indexing and two blocks sharing an entry invalidate the shortcut; those are assumptions to justify, not behaviors ruled out by a passing browser test.

The retained Lean run compiled its import closure and final module, exited 0, and recorded twelve axiom audits using only the listed standard axioms. Its native mapping pins this exact candidate. Stable original addresses, live guarded immutable blocks, unique ownership, source coverage, hashmap operations and actual traversal still form the correspondence assumptions. Allocation failure/panic is not a continuing partially populated state. This verifies a mathematical refinement, not Rust memory safety, all of Stylo, CSS specification completeness, or CSS occurrence identity.

## Fresh A–B–B–A costs

Each range spans the two run medians in microseconds per update. It is an observed range, not a confidence interval. A brackets the candidate build using the accepted A+B+D/Arc baseline; B consists of two fresh-process candidate repetitions. All fixtures, modes and preferences are the frozen versions used previously.

| Workload | Baseline A1/A2 | Dedup B1/B2 |
| --- | ---: | ---: |
| Dense Rule 0 | 4.84–5.06 | 4.94–5.02 |
| Dense Rule 32 | 5.84–6.50 | 7.95–8.22 |
| Dense Rule 64 | 6.37–6.89 | 10.49–10.64 |
| Dense Rule 128 | 7.70–8.20 | 15.20–15.37 |
| Dense Rule 256 | 10.43–10.94 | 25.27–25.80 |
| Dense literal 256 | 10.14–10.63 | 10.39–11.15 |
| Dense Layer 256 | 11.09–11.13 | 11.09–11.66 |
| Single trigger, payload 256, Rule | 8.44–8.85 | 8.61–9.00 |
| Single trigger, payload 256, literal | 8.57–8.93 | 8.48–8.77 |
| Single trigger, payload 256, Layer | 8.55–9.20 | 8.57–8.98 |

Dense-chain Rule growth remains clearly distinct from literal/Layer controls at the upper counts. The single-trigger observed Rule ratio spans approximately 0.97–1.07 at 256 payload blocks, with comparable baseline/control variation; this does not establish exact zero overhead. Payload count means matched custom-only blocks, and the Rule mode still has one Rule at zero. Dense zero-count modes instead share the same no-Rule stylesheet.

The previous incremental d329 run recorded dense Rule256 medians 28.48–29.22 against its own baseline 10.41–10.92, and single-trigger Rule256 8.83–9.24 against its own baseline 8.11–8.36. The dedup dense result is descriptively lower; single-trigger ranges overlap. These experiments were in different sessions with different baseline/control levels. They support retaining the simpler representation as a local candidate, but do not yield a controlled precise speedup, significance result, or regression budget. No claim of measured allocation savings is made.

Measurements use 1,024 updates per sample, seven samples, four warmups, rotated mode order and exact opacity checks. Dense batches span 4.56–28.78ms; single-trigger batches span 4.98–12.56ms. The approximately 20-microsecond batch clock grid remains despite identical local `privacy.reduceTimerPrecision=false`. Timing includes property writes, style reads and loop/bookkeeping; stylesheet setup is separately recorded. Machine load and scheduling are uncontrolled, counts are capped at 256, and these synthetic repeated-update workloads do not estimate release-page impact. No native entry counters or allocation profiling were collected.

## Packaging judgment

No observed correctness failure blocks the proposed local five-file fix package, provided prerequisite #163 remains explicit: `e63fc6b1892bc13f4d0f6583e4efc4b58d1e54db`, “Preserve cumulative cascade rollback exclusions.” The C source/test patch depends on that repair. Arc and other branch fixes are test context, not required source hunks for this patch. The package should include only the necessary implementation and regression WPT files; the refinement, diagnostic fixtures, performance tooling and these results belong in preceding research commits. The retained synthetic dense overhead should be disclosed in the bug/commit review material instead of treating timing report validity as performance acceptance. These results do not authorize upstream landing or establish that the remaining native/spec correspondence assumptions have all been independently reviewed.

## Closure and replay

All six external executions have actual closed exit-0 receipts: long A1, single A1, native owner, independent restoration audit, long A2 and single A2. Native owner: launch `6e0ee5`, session18390, terminal `e0f394`. Audit: launch `cda193`, session27009, terminal `e5b09b`; it reports restoration verified, no observation errors and no missing process receipts. Long A2: `d54309`/session7118/`d8162f`. Single A2: `0fa23d`/session55466/`9267a1`. There is no reconstructed terminal receipt in this run. Exact records and input hashes are retained in TIMING-AND-CLOSURE.json and INPUTS.json.

Saved-data comparisons were executed only after root confirmed both A2 closures. They authenticated source-role and application bindings, raw/run-info gates, cleanup, exact callback/report rosters and report extraction. No browser/native process or live-tree mutation was performed by this assessment.

```sh
python3 -I -S -B artifacts/css-revert-rule-owner-map-dedup-native-v1/compare_long.py --a1 artifacts/css-revert-rule-owner-map-dedup-long-a1-v1 --b artifacts/css-revert-rule-owner-map-dedup-native-runtime-v1/browser/long_timing --a2 artifacts/css-revert-rule-owner-map-dedup-long-a2-v1 --output artifacts/css-revert-rule-owner-map-dedup-assessment-v1/LONG-COMPARISON.json > artifacts/css-revert-rule-owner-map-dedup-assessment-v1/long-comparison.log 2>&1
python3 -I -S -B artifacts/css-revert-rule-owner-map-dedup-native-v1/compare_single.py --a1 artifacts/css-revert-rule-owner-map-dedup-single-a1-v1 --b artifacts/css-revert-rule-owner-map-dedup-native-runtime-v1/browser/single_timing --a2 artifacts/css-revert-rule-owner-map-dedup-single-a2-v1 --output artifacts/css-revert-rule-owner-map-dedup-assessment-v1/SINGLE-COMPARISON.json > artifacts/css-revert-rule-owner-map-dedup-assessment-v1/single-comparison.log 2>&1
```

Long comparison receipt `a568ba/0`; single comparison `86c813/0`; exact correctness signature extraction `520c3d/0`; timing/closure assembly `624ff6/0`.
