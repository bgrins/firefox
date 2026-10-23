# Independent column diagnostic runtime review

**Verdict: ACCEPT the bounded runtime evidence and principal/OOF improvements, with the measured first-query cost disclosed. HOLD any comprehensive hidden-layout claim or column-candidate acceptance.** The complete runtime and root analysis are authenticated; final restoration passed.

## Correctness evidence

Independently reconstructed exact test/subtest identities from raw JSON, rejecting duplicates, comparing complete status/message tuples with phase RUN receipts and the prior compact-v3 runs. All 58 prior identities retain exactly the same outcomes and messages in each corresponding phase. The eight new ordinary-block identities are separate.

| Phase | PASS | FAIL | Harness ends |
|---|---:|---:|---:|
| Baseline | 30 | 36 | 7 OK |
| Principal + OOF repairs | 55 | 11 | 7 OK |

There are 25 FAIL→PASS, 30 PASS→PASS, 11 FAIL→FAIL and zero PASS→FAIL. The 50 compact landing cases all pass with both repairs; the four earlier column/group residuals remain. The new ordinary-block fixture has seven failures and one pass in both phases: all outer-width targets fail; direct table-width col/group/td fail; direct table-width/table passes. No failure is normalized away. WPT process exit 1 is expected for these real failures.

These phases test the principal and OOF fixes, **not the proposed column-provider gate**. Their bounded repair evidence is supported; comprehensive hidden-layout correctness and column-fix acceptance are not.

## Controlled local cost

Independently reconstructed the exact 220 serial progress messages, including both warmup rounds, and 84 measured rows. For each row checked configuration rotation, sampled indices, full visible-peer and initial target rectangles, checksum, all query bucket identities/order, timing vector lengths and finite nonnegative values. Each phase contains 13,440 measured rectangle reads. Before/after pins, six execution inputs, WPT-to-timing source/binary joins, startup environment and cleanup receipts agree. The startup controls include safe-mode-key disable, removal of inherited safe-mode restart and early update-processing disable. These are local-build runs, not installed-release launches.

Baseline has 3,213 rectangle mismatches, all in hidden OOF groups. Both repairs have zero. Zero mismatches in the principal timing topology do not substitute for its distinct failing WPT histories. Root analysis RESULT and all COST query sample arrays, medians, read/mismatch counts were independently reproduced.

The 256-child first-query bucket sums over 16 mutations show concrete extra work:

| Group | Baseline seven sums (ms) | Both seven sums (ms) |
|---|---|---|
| Principal hidden | 0,0,1,1,1,1,1 | 8,9,9,8,8,8,9 |
| OOF hidden | 0,0,1,0,1,1,1 | 9,6,7,6,9,9,7 |

Medians are 1→8 ms and 1→7 ms per 16-query bucket (about 0.5 and 0.44 ms per first query in this topology). The repeated, other-leaf, second-pass and no-mutation bucket medians are zero at this timer resolution. They do not prove zero work or absence of overhead. Visible controls do not expose a clear large cost here; equal/zero quantized timings cannot bound predicate lookup cost. Construction, visible establishment, mutation/outer flush and query timing are retained separately in INDEPENDENT.json. Total fixture elapsed 903→955 ms includes acknowledged progress and round yields and is not a native operation benchmark.

The measured extra first-query work is consistent with doing previously skipped layout; OOF correctness also changes, so ratios to the incorrect baseline are not equivalent-work performance comparisons. One process per variant, fixed baseline-before-both order, seven correlated rounds and acknowledged network progress do not support general statistical or no-regression claims. This bounded result does not independently demand a performance hold, but the scaling cost should be disclosed and reviewed before landing.

## Native trace

Independently parsed 414 tagged records from the raw instrumented WPT stream. The exact 16 test outcomes match the uninstrumented both phase. There are 196 column and 98 group publications. For each queried kind (column and group): 44 clean-target/clean-table calls, 12 clean-target/dirty-table calls and four dirty-target/dirty-table calls. Thus the proposed additional entry condition genuinely occurs in this run; it is not solely an abstract countermodel.

The records preserve process and pointer values, not DOM identities, frame generations or stable lifetime. They do not establish which stage/case a pointer belongs to or that a particular publication follows the failing query causally. There are no table-kind target query records: the table element may have a wrapper primary, but absence alone does not establish that mapping. These logs do not prove the proposed gate repairs every failing case, nor exclude clean-table/stale-position histories. The ordinary-block td/table failures remain outside the proposed column-specific addition.

## Scope and remaining gate

Accept the recorded phase observations and bounded principal/OOF improvement evidence within the stated fixture domain. Preserve all eleven residuals and the column/provider source review's HOLD for native acceptance. A column-candidate run needs its own source binding and outcomes. No native/browser/compiler/build/Git operations were performed by this review.

## Final authentication and restoration

Authenticated runtime FILES `95f4290b6c8d5cc27afac52c94fb20e501282c7cea239caf455d71f52fe2f3e8` (258 payloads) and root analysis FILES `c5fef6c3896e0e76ace2eaf4efd2650ee395a133dfc71ce413fcd269849f29fa`, with closed rosters. Historical BEFORE equals FINAL, including HEAD, index hashes and all 28 native source pins. Independently read the restored 28 sources and confirmed their bytes; all ten temporary test paths are absent. Baseline, both, trace and restoration builds returned zero, experiment returned zero, recovery-errors list is empty. Build-monitor export KeyError and post-build telemetry-helper warnings remain recorded as nonfatal build limitations, not erased logs.

`analyze.py` reproduces the raw results from retained inputs. `authenticate.py` also checks current source bytes/temporary absence and therefore intentionally requires the recorded restored source state; future unrelated native changes need historical receipt review instead of treating current-byte mismatch as a failed historical run. No current Git command is required. All reviewer handles are terminal; no generated compiler products exist.
