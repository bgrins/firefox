# Independent review: flex baseline cross-size sums

## Decision

**Bounded native repair: ACCEPT. Primitive formal claims: ACCEPT. Native/WPT package: HOLD pending the WPT correction and a fresh paired browser run.**

The frozen candidate is `css-flex-cross-baseline-overflow-fix-v1`, patch `fix-candidate-v2.patch` SHA256 `c5a8e37b6f7fb142b62bcc8a963371b141e926dde290e10bee7731b47c4aec56`. Its 107-file manifest and the 37-file discovery manifest authenticated exactly, including closed directory rosters and original external pins. This review does not change either producer, production files, the index, or the browser build.

### Required correction: numeric-range calibration

The test currently demands computed heights and margins of up to 17 million pixels within two pixels of the requested values. CSS does not require every implementation to support that numeric range. CSS Values explicitly leaves numeric range and precision dependent on the implementation and context. Consequently, an implementation with a smaller supported range can fail a calibration assertion without having this flex defect. [CSS Values numeric types](https://drafts.csswg.org/css-values-4/#numeric-types).

`proposed-wpt-correction.patch` replaces only those three calibration assertions with `assert_implements_optional` on the same measured conditions. Width remains asserted; after calibration succeeds, the final 100px height assertion remains unconditional. The proposed test is not applied to production. Root must apply it in new evidence, rerun both browser states, check that all 54 cases remain admitted on Gecko and preserve the 12 FAIL / 42 PASS to 54 PASS transition. Unsupported ranges must be recorded as optional prerequisites, not passes. No fresh browser result is claimed here.

The JavaScript control-flow challenge exercises the exact proposed script with synthetic DOM results: supported/fixed gives 54 passes; supported/old geometry still gives 12 failures and 42 passes; a smaller supported range gives 12 passes and 42 `PRECONDITION_FAILED` outcomes. These checks verify assertion routing only, not CSS layout. The frozen harness implements the optional assertion by throwing `OptionalFeatureUnsupportedError`.

## Native reasoning

`FlexLine::ComputeCrossSizeAndBaseline` initializes each baseline component maximum to -1073741823 and the ordinary-item maximum to zero. Eligible items update their selected sharing group; auto margins exclude an item from baseline sizing. The patch changes neither that selection nor the stored first/last offsets.

Each final group addition now converts its first operand to signed64 before adding. Two arbitrary signed32 operands sum within [-4294967296, 4294967294], safely inside signed64. The maximum also includes the nonnegative ordinary-item maximum, so it is nonnegative. Taking its minimum with nscoord_MAX yields [0, 1073741823], making the final signed32 assignment exact. Both sums execute, including absent groups; their sentinel sums are safe. The initializer-list maximum uses signed64 for every member. No new memory access or allocation is introduced.

This is identity when the mathematical maximum is at most nscoord_MAX. It intentionally changes some formerly signed32-representable values above that cap: the 700000000/1400000000 group produces 2100000000 before, and 1073741823 after. A later maximum-size cap at most nscoord_MAX produces the same mathematical result in either case, including a surrounding minimum-size clamp. It would be inaccurate to claim identity for every old defined signed32 result.

The full extracted native body, rather than just a replacement arithmetic expression, was compiled for each genuine role. The input facade admits item sizes, baseline distances, group assignment, alignment and auto-margin counts. It does not implement frame layout, provider internals, writing-mode derivation or baseline synthesis. Normal corpus cases explicitly require every executed earlier `outer - distance` subtraction to fit signed32.

The adjacent last-baseline conversion `lineSize - offset` is also bounded when lineSize is in [0, nscoord_MAX] and the selected offset is in [-nscoord_MAX, INT32_MAX]. An independent lemma proves that conditional statement; it is not a proof of all subsequent changes to line size or all callers.

## Source identity and evidence

The tested combined CPP, final formatted CPP and both standalone CPP snapshots retain distinct original hashes. The selected body hashes match their producer records. Independently verified: the tested-to-formatted file transfer consists of exactly two whitespace-only changed blocks; applying and reversing the exact two-file patch on each Git-authenticated retained base restores its original CPP and removes the new WPT. Both standalone results equal their frozen snapshots. No isolated upstream browser build is inferred from these checks.

Raw JSON independently confirms 54 unique paired WPT cases: exactly 12 final-height failures (100 expected, zero observed) become passes, and all 42 passing status/message pairs are unchanged. Every failure passed the earlier input calibration. Only the native CPP and the two browser binary pins differ between runs. All 29 requested regression endpoints occur once: 26 reftests pass, three harnesses end OK, and their 63 subtests pass. The producer records a successful native build and clean lint; this review authenticates those records without rerunning Firefox build or lint.

The release-158 and local-160 discovery records have stable pins and identical 27 rows. Six high-input baseline/last-baseline rows are zero height; 21 controls are 100px. Their computed heights and opposing margins pass the recorded calibration. The earlier unbounded probe is diagnostic, not a second set of proven bugs.

## Spec trace and oracle

For this horizontal, nonwrapping, auto-height flex container, the cross-sizing algorithm combines baseline-edge maxima, compares the result with other item sizes and zero, then clamps the single line by the container min/max cross sizes. Opposing margins leave each item's outer cross size positive; baseline groups require a larger positive line size. The 100px maximum therefore gives the representable 100px observer used by the fixture. [Flexbox cross sizing](https://drafts.csswg.org/css-flexbox-1/#cross-sizing).

First and last baseline preferences use their respective compatible sharing groups; both are exercised by the fixture. Reversing the main-axis row order does not reverse the vertical cross axis. The test does not cover vertical writing modes, wrapped lines or provider arithmetic. [CSS Box Alignment grouping](https://drafts.csswg.org/css-align-3/#baseline-sharing-group).

The primary draft sections are retained. `webspec-index` was unavailable, so this is a manually checked primary-source trace; no graph traversal from that tool is claimed. The calibrated 100px oracle is reached. A requirement to preserve arbitrary enormous numeric values is not reached.

## Independent replay

`replay-canonical-v5` and `replay-relocated-v1` have identical summaries:

- 1,293 deterministic independent cases, covering empty/mixed groups, signed32 boundaries, auto-margin exclusion, first/last alignments and both group assignments, ordinary items, near-overflow browser inputs, and seeded multi-item combinations.
- Four repaired source roles × two optimization levels × 1,293 rows = 10,344 successful native observations. The two standalone sources intentionally have identical bytes. Before-source controls add 2 × 1,250 observations whose executed old sums are defined.
- Five successfully compiled semantic mutants are rejected at O0 and O2: dropped cap, dropped last group, dropped ordinary maximum, included auto-margin items, excluded last-baseline items. Auto-margin mutation uses only cases with all newly executed earlier subtractions representable.
- Six producer kernel audits plus five independent results pass with only the allowed foundational axioms. The four original discovery lemmas replay separately. Three false kernel claims are rejected: universal identity above the cap, safety of the earlier subtraction, and safety of three large ordinary lines. Both `sorry` and native-evaluation axiom injections are detected.
- Five integrity controls reject an extra cache, a resealed extra cache, an extra empty directory, changed proof bytes, and a resealed tested/formatted role substitution. The last reaches the source-role gate rather than merely a digest failure.

Development interruptions and failures are preserved and explained in `DEVELOPMENT-CLEANUP.json`. In particular, the auto-margin mutant initially exercised an admitted earlier subtraction overflow; the final semantic corpus handles that domain explicitly. Compiler products and the disposable relocated source clone were removed after retaining evidence.

Reproduce in a writable checkout with the pinned tools:

```sh
python3 artifacts/css-flex-cross-baseline-overflow-review-v1/verify.py
python3 artifacts/css-flex-cross-baseline-overflow-review-v1/replay.py --out /tmp/flex-cross-review-replay
python3 artifacts/css-flex-cross-baseline-overflow-review-v1/check_evidence.py
node artifacts/css-flex-cross-baseline-overflow-review-v1/check_proposed_test.js
```

The output path must be new. `check_evidence.py` deterministically rewrites the identical evidence summary. Executable hashes are checked; installed Lean Init/Std, compiler headers/runtime, OS, Python and Node remain trusted. The replay does not machine-prove the C++ compiler, extraction correspondence or full frame/provider semantics.

## Separate follow-up leads

1. Earlier `curOuterCrossSize - crossStartToBaseline` still overflows for synthetic providers INT32_MAX and -1. UBSan witnesses persist in before and all repaired roles at both optimization levels. Browser reachability is not established here. This is explicitly outside the accepted final-sum repair.
2. The unchanged `sumLineCrossSizes += line.LineCrossSize()` can exceed signed32 for three ordinary lines of nscoord_MAX each, even with no baseline overflow. The independent integer witness proves that bound violation; no browser reproduction or complete caller diagnosis is claimed. Since ordinary groups already produced those sizes before this patch, the witness does not establish an introduced regression.

Neither lead is a new accepted fix or a security finding. This review accepts the stated narrow arithmetic repair and primitive proofs while holding the combined patch for the concrete WPT correction above.
