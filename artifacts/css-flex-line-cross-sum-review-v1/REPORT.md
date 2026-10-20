# Independent review: wrapped flex line cross-size accumulation

## Decision

**ACCEPT the two-file native/WPT repair and its stated sum-only mathematical scope.** The frozen candidate correctly widens and saturates the initial gap product and each subsequent line addition. The WPT checks a valid bounded consequence after calibrating the large inputs. No required native or WPT correction was found.

The original eleven proofs are primitive arithmetic results. This review adds ten independent results, including the missing conditional optional-min/max and automatic-minimum observer composition. Neither set proves all flex layout arithmetic, all provider construction, or a verified C++ translation. The explicit upstream and downstream exclusions remain intact; acceptance does not silently expand the candidate contract.

## Frozen identities and source scope

- Candidate: `css-flex-line-cross-sum-fix-v1`, FILES `a65108f346c5576e95a1c4fccf61cc0f37d80531827c1eb06a0eb028022853e1`, 98 listed files.
- Discovery: `css-flex-line-cross-sum-probe-v1`, FILES `af68a3e61020406fe203398ad50d60be8be19ab8eddb8a1995a093c74d8a1342`, 39 listed files.
- Exact native/WPT patch: `34a5ec601d2bc24d428160f6cbd5422b584a82cfeea3662fb96e9764135d3798`.

Both inventories were independently checked for exact files/directories, hashes, nonregular entries, path validity and freeze binding. The tested candidate CPP and WPT match the packaging identities. The initial working source copy is byte-identical to the frozen final candidate; it is not an alternate tested-source role. `SOURCE-REVIEW.json` records inspected source spans in the before, combined candidate and both standalone snapshots, plus the exact provider headers.

The candidate differs from its paired before source by exactly the two recorded replacements. The standalone patch was independently applied and reversed in disposable filesystem trees against both retained Git bases, without changing a Git index. Resulting native and WPT bytes match the packaged standalone snapshots. The observed browser run used the combined shared build; no standalone upstream browser build is claimed.

## Native arithmetic and provider premises

`GenerateFlexLines` always constructs one initial line, including for an empty container. The changed `Length() - 1` expression therefore does not underflow on this caller path. The line array is not removed or replaced before accumulation. `nsTArray::Length()` returns `size_t`, but the backing length is `uint32_t`; using the full uint32 range is a conservative bound even though capacity imposes additional restrictions.

`ResolveGapToLength` returns zero for `normal`; otherwise it calls `ResolveToLength<true>`, whose result is floored at zero. This establishes the nonnegative returned gap, assuming the underlying length-percentage resolution executes with defined behavior. The source sum consumes returned `nscoord` values, so their signed32 upper bound is sufficient here. Percentage basis resolution and its internal arithmetic are not verified by this repair.

After `ComputeCrossSizeAndBaseline`, a defined line-size result is nonnegative: the maximum includes `largestOuterCrossSize`, initialized to zero. In the combined source, the earlier baseline-sum repair also caps that result. In the standalone source, the original baseline calculations are unchanged; their possible overflow is an explicit independent issue. This repair requires defined preceding provider execution, not the presence of another patch. Plain line/gap reproductions do not use baseline alignment.

For the admitted nonnegative signed32 values:

- The initial product is evaluated after **both operands** are converted to signed64. Its largest admitted value is `2147483647 * 4294967294 = 9223372028264841218`, below signed64 maximum.
- Each later addition is at most `nscoord_MAX + INT32_MAX = 3221225470`, because the stored accumulator is capped after every step.
- The cap produces a value in `[0, 1073741823]`, so narrowing to `nscoord` is exact.
- An arbitrary mathematical total need not itself fit signed64: only the initial product and each individually capped step are evaluated in that type. The arbitrary-list Lean theorem matches this design.

Nonnegativity is necessary for early saturation to equal saturation of the final total. The independent negative-suffix witness demonstrates the failure without that premise. A zero-line array is similarly outside the source domain; an empty browser container has one zero-sized line and therefore no inter-line gap.

## Consumer behavior and the absent-maximum distinction

The complete frozen `ComputeCrossSize` and `ApplyMinMaxBSize` bodies were inspected and independently compiled with scalar provider facades. The sum has the following observers:

| Branch | Dependence on the sum |
| --- | --- |
| Column-oriented | Returns tentative cross size; ignores the sum. |
| Definite block size without automatic minimum | Returns computed block size; ignores the sum. |
| Intrinsic size containment | Applies min/max to the containment size; ignores the sum. |
| Auto row block size | Applies the optional maximum, then optional minimum, to the sum. |
| Automatic minimum | Further takes the maximum with computed block size. |

The call uses the default `aConsumed = 0`, so the helper's addition/subtraction of consumed size is identity. A bound encoded as `NS_UNCONSTRAINEDSIZE` is skipped, not applied as an ordinary finite maximum or minimum. Minimum wins if the bounds conflict.

`IndependentLineSum.optional_bounds_commute_with_saturation` proves that capping commutes through the optional bounds when every present endpoint is nonnegative and at most `nscoord_MAX`. `complete_optional_observer` additionally covers the automatic minimum under the same bound for computed size. These are explicit conditional observer theorems; they do not prove construction of every ReflowInput field. The unaffected branch selection is reviewed against the full source and calibrated separately.

Exact old/new identity holds for nonnegative totals within `nscoord_MAX`. It **does not hold for all old signed32-defined inputs**. With no maximum, two 720,000,000-au lines formerly yielded 1,440,000,000, and now yield 1,073,741,823. The new value is deliberate supported-range saturation. The frozen producer report states this correctly; the bounded-maximum theorem is not used to conceal the distinction.

## Independent replay

`native-v2/RESULT.json` records 669 arithmetic inputs in each of O0 and O2, both with undefined-behavior sanitization enabled. There are 620 fold cases and 49 isolated gap-product cases, covering zero/one/large components, cap boundaries, signed32 boundaries and the full conservative uint32 count bound. Huge counts test only the extracted gap expression; they do not allocate huge native arrays or claim browser reachability. The extracted statements are byte-derived from the frozen candidate, with documented scalar facades for the array length and line getter.

The old expressions additionally match 155 cases whose complete arithmetic fits signed32, in both configurations. Three large lines trigger the old signed-addition UBSan failure in both configurations. Three arithmetic mutants compile and execute successfully but disagree with the reference: counting one extra gap, discarding gaps and omitting per-step saturation. Zero count, negative gap/line and excessive count inputs are rejected by the calibration harness. These are harness-domain guards, not new runtime guards in Firefox.

`observer-v1/RESULT.json` records 2,304 combinations of all consumer branches, optional/contradictory bounds, zero/finite/sentinel computed sizes, containment and raw totals around the cap. Both O0 and O2 match an exact mathematical sum observer followed by supported-range capping, under the stated bounded provider domain. Three successfully compiled consumer mutants are distinguished: missing automatic minimum, treating absent maximum as zero, and reversing min/max priority. This is finite source calibration, not a source-translation theorem.

`proofs-v1/RESULT.json` records fresh kernel checking and strict axiom auditing of the eleven producer results and ten independent results. The audit permits only `propext`, `Classical.choice`, and `Quot.sound`. Two false claims are kernel-rejected; a custom-axiom theorem compiles and is rejected by the audit. The Lean executable hash is pinned; its installed libraries, compiler/SDK, Python and host remain trusted. This review does not claim a newly closed full SDK/toolchain inventory.

The first independent native harness attempt failed compilation because its generated newline literal was malformed. The failed generated source/log remain in `native-working-v1`; this was repaired in the harness and the terminal evidence is `native-v2`. It is not counted as a semantic mutation or a candidate defect. The producer's separate failed typed-coordinate attempt and successful signed64 build are also retained in its immutable evidence.

## Browser test and regression assessment

The test uses one nonflexing item per line, non-stretch alignment, logical block/inline dimensions, both row directions, both wrap directions and three writing modes. The conditional prerequisite checks only whether the requested large item sizes and gaps are supported. Once admitted, inline-size, fixed-size/restoration controls and the final small cross-size oracle are unconditional. Baseline failures occur at that final oracle, after the prerequisite and controls.

The content-based flex cross size follows the line sizes and normal formatting-context size constraints; gaps supply fixed spacing between lines. These rules support the test's expected `min(100px, line sizes + intervening gaps)`. Large numeric inputs require calibration because CSS does not require arbitrary numeric range support. Sources: [Flexbox cross-axis sizing](https://drafts.csswg.org/css-flexbox-1/#algo-cross-container), [Box Alignment gaps](https://drafts.csswg.org/css-align-3/#gap-flex), [CSS Values numeric types](https://drafts.csswg.org/css-values-4/#numeric-types). The primary-source snapshots are retained in the discovery artifact.

`evidence-v1/RESULT.json` independently recounts and validates:

- Discovery: 40 identical release/development observations, 11 supported-input zero-size failures, fixed-size controls and restoration stable. The phase called `candidate` in discovery is pre-repair.
- Paired WPT: 96 FAIL → PASS, 48 unchanged PASS status/message pairs, all 144 numeric prerequisites admitted. Source/input inventories are stable within each run; only the flex CPP and two browser binary pins differ between runs.
- Regression: 914 passing subtests, 20 passing reftests and six OK harnesses. `content-height-with-scrollbars.html` has a metadata-known intermittent FAIL, explicitly retained and not counted as passing. No baseline comparison for that failure is claimed.
- Exact tested-source/WPT identity and independent apply/reverse checks on both retained bases.

This review authenticated the producer's build/lint/browser receipts; it did not rerun a main build or browser. The regression result provides no evidence that the intermittent failure was caused or fixed by this patch.

## Separate remaining arithmetic lead

`CrossAxisPositionTracker` still stores `mPackingSpaceRemaining` as `nscoord` and subtracts each line size before subtracting gaps. With a 6000-au bounded container and three 720,000,000-au lines, the third subtraction mathematically gives `-2159994000`, below signed32 minimum. The independent kernel witness records this limit, and the frozen source confirms the separate executed loop. Further position and baseline operations also remain outside this repair.

This is an existing downstream limitation, not an introduced regression or a claim of a new demonstrated security impact. The repaired bounded container size and passing WPT must not be described as proving safety of that full layout path. A dedicated packing/position arithmetic investigation is a sensible next task, with its own source model, browser oracle and patch if warranted. No change to that code is required to make the present two-expression repair independently reviewable.

## Reproduction and cleanup

Use fresh output paths:

```
python3 -I -S artifacts/css-flex-line-cross-sum-review-v1/check_evidence.py --artifacts artifacts --output /tmp/flex-line-evidence-new
python3 -I -S artifacts/css-flex-line-cross-sum-review-v1/calibrate.py --before artifacts/css-flex-line-cross-sum-fix-v1/before.cpp --candidate artifacts/css-flex-line-cross-sum-fix-v1/candidate.cpp --output /tmp/flex-line-native-new
python3 -I -S artifacts/css-flex-line-cross-sum-review-v1/check_observer.py --candidate artifacts/css-flex-line-cross-sum-fix-v1/candidate.cpp --reflow artifacts/css-flex-line-cross-sum-probe-v1/providers/layout__generic__ReflowInput.h --output /tmp/flex-line-observer-new
python3 -I -S artifacts/css-flex-line-cross-sum-review-v1/check_proofs.py --output /tmp/flex-line-proofs-new
```

`verify.py --manifest-sha HASH` checks this review's sealed closure against an externally supplied manifest. Owned compiler binaries, Lean products and patch application trees were removed after preserving sources, logs and receipts. Shared source, WPT, index, browser and build state were not modified.
