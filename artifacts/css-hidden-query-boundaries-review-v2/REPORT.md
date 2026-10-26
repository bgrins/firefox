# Hidden-query boundary runtime: independent result review

**ACCEPT bounded runtime/restoration evidence; native landing remains pending.** This review independently reconstructs raw results and cost observations. I authored the controller, so this is not an independent controller review; that was performed separately. No native/build/browser/Git work was performed here.

## Complete seven-phase matrix

| Phase | PASS | FAIL | Prior66 | Compact18 | Span12 | Auto4 |
|---|---:|---:|---|---|---|---|
| Baseline |64|36|55P/11F|5P/13F|0P/12F|4P|
| Column |76|24|61P/5F|5P/13F|6P/6F|4P|
| Block |78|22|58P/8F|16P/2F|0P/12F|4P|
| Both |98|2|66P|16P/2F|12P|4P|
| Without104/105 baseline |37|63|30P/36F|3P/15F|0P/12F|4P|
| Without104/105 column |45|55|32P/34F|3P/15F|6P/6F|4P|
| Without104/105 block |51|49|33P/33F|14P/4F|0P/12F|4P|

Every phase has exactly100 ordered subtests and10 OK harness ends; no calibration failures. All four current-HEAD prior66 outcomes/status messages exactly match their historical counterparts. Standalone baseline matches its older66 oracle. Each phase authenticates the28native roles, resources/metadata, raw/RUN identity and retained source copies; all seven builds exit0.

Main patterns are64 alwaysPASS,12 column-dependent,14 block-dependent,8 requiring both and2 alwaysFAIL. All six meaningful additive comparisons have zero regressions. Replacing column-only with block-only is not an additive comparison and is not called regression-free. The remaining main failures are float root/leaf stale widths50 instead25. They remain failures and unresolved scope, not optional controls or conformance passes. Original failed fragmentation calibrations remain unreached coverage in v1; this run does not establish table fragmentation behavior.

Standalone phases remove exactly104/105 while retaining101 and the other authenticated HEAD roles. Tracked50 retain29P/21 historical failures in all three standalone phases; these are separated from the new candidate50. Standalone column repairs8 candidate cases and standalone block14, without regressions. This establishes the selected repairs' tested independence from104/105; it is not a fresh upstream build lacking all other changes.

## Landing-test relationship

Column's three table-width identities (col, colgroup, table) and four unchanged auto-scroll controls pass with and without104/105. All14 selected block identities pass in both block-only configurations, including later inline children/leaves and table-first rescue. The td case was correctly excluded from column's draft because its fix requires block readiness; it remains in the full corpus. Float/OOF cases remain in the larger diagnostic corpus.

These are case-identity results from the full campaign. The subsequently cleaned final landing bytes, new filenames and packaged patches have not been executed by this campaign. Their planned final run and separate native/formal gates remain required; no native fix acceptance follows automatically from this report.

## Cost evidence

Independently reconstructed each run's90rows,220progress receipts and2,952,000 timed reads, including full recovery rectangles, clean-state calibration, hot checksums, workload identities and all timing samples. Source/binary/fixture pins and original-process-group cleanup/profile removal join. Baseline720 stale recovery rectangles become zero with both repairs; clean/hot geometry is correct in both. This makes the recovery comparison unequal useful work, not a regression measurement of identical behavior.

For128 siblings, median first-query sums across16 mutation rounds are block0→4ms,td0→6ms,col1→7ms. Repeat medians0 are quantized, not evidence of no work. Clean hot-loop medians are mostly2–3ms per16,384 calls; median changes are within±1ms with mixed directions, including visible128 cycling block2→3,td3→3,col2→3ms. Individual distributions remain in COST.json. One process per phase, fixed order, five samples/group and millisecond timing limit inference about small lookup overhead. The evidence does not warrant a broad no-regression claim or a cost HOLD solely for doing newly correct recovery. See COST-NOTE.md for details.

## Final authentication

Runtime FILES `6999853af6434ecd130590b4159eec577059bc989186293e27a5dd76317c926a` authenticates all489 payloads and a closed directory roster. INPUTS `7f8b3a0e3d5892d65a1a6472f283a7c942f4f172b10ca4b7630f0bfb51ee4fbd` binds98payloads and15 external cost pins. Historical BEFORE=FINAL=prepared snapshot, HEAD90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e, terminal status, restored=true, restore build0 and no failure/recovery errors are authenticated. Parent reported its immediate live28guard/index/temp-absence verification; review intentionally does not require live test absence during subsequent diagnostics.

Reproduce with `python3 -I -S -B recount.py PHASE` for each named phase, `python3 -I -S -B cost_recount.py`, and `python3 -I -S -B authenticate_final.py`. These read artifacts only and regenerate reviewer receipts. No compiled products or profiles were created by this review.
