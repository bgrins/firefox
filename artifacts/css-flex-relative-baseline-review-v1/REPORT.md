# Relative flex baseline: independent native/WPT review

## Decision

**ACCEPT the bounded two-fallback native repair and WPT/standalone packaging. Full conditional formal acceptance remains pending the separate companion.**

The official patch repairs the two preexisting consumers in `PopulateReflowOutput`. It does not depend on the natural-donor helper being present. The tested shared change additionally repairs that newly introduced helper, which belongs to the independently applicable natural-donor v2 patch. These are separate acceptance units.

## Input authentication and source roles

Authenticated the complete 96-file relative package: FILES `11ded3db7013c651482a2e3ae5120c001c816673324d5b72df1027f359abe37e`, FREEZE `5f596d6365f40612e8eac52ea217ec2ed470b71f0caee03d67ba2b60b1a8778f`. The complete related 19-file natural v2 package is also authenticated against its supplied pins. Both closed producer rosters and every payload hash are checked by `check.py`.

`inputs/previous-natural` is an explicitly labeled selected source/evidence subset authenticated against the old producer's published manifest, not a closed replay capsule. It supplies the genuine v1 donor baseline and predecessor source. The original sealed v1 review is preserved.

The build receipt, candidate WPT snapshots and regression source/binary pins agree with shared candidate SHA `e2fd1dc8d14d1fb05131d22e8929558bb2d8a0958b23506cb36a14351b906284`. There is no post-build formatting transfer. Applying `shared-native-delta.patch` to the genuine shared before-source reconstructs those bytes exactly.

The official relative patch SHA is `63cb2273307d6524aeaf9c7877efd6cd9c42ddd148b6faf24ce3394de142ba98`. On both frozen Git bases, it changes only two existing query names (plus line wrapping) and adds the WPT. It applies/reverses independently. Applying it and natural-donor v2 in either order produces the same three files and the recorded combined CPP SHA `8b2169be32feb00b52716012928e9309e1a67fdd2384c7d3f20a45eb9280949e`; reversal restores both bases exactly. None of these checks is an isolated upstream browser build.

The independent checker's first attempt compared whitespace-separated words and rejected the intentional call line wrap. The corrected token comparison preserves literal/comment contents and passes. The retained failure describes this reviewer issue; producer bytes were not changed.

## Native and provider reasoning

The baseline donor and ascent calculations stay the same. Only the position query switches to `GetLogicalNormalPosition`, so relative movement remains visible on the child while the exported baseline uses its normal layout location. First and last parent-edge arithmetic, guard conditions, donor selection and synthesis remain unchanged. This does not repair unrelated donor-selection or writing-mode policies.

The retained `nsIFrameInlines.h` is byte-identical both to the indexed provider used for inspection and to each retained Git base. Its two provider bodies are extracted directly in the native calibration. The indexed `nsIFrame.h` differs from the retained header only by unrelated fixed-position-subtree declarations; the actual natural-baseline and position contracts are unchanged. Full retained header hashes and the complete small diff are recorded in `PROVIDER-PINS.json` and `nsIFrame-provider-diff.patch`.

`GetNormalPosition` returns the saved `NormalPositionProperty` when present and current frame position otherwise. `GetLogicalNormalPosition` converts that point using container size minus frame size, which preserves reversed block-axis origin handling. The indexed `ReflowInput::ApplyRelativePositioning` inspection records normal position before adding the visual offset. In the frozen flex source, both final-reflow and move-only placement paths invoke relative-position handling. This supports the ordinary reflow path; it is not a complete lifetime proof for every property writer/remover or sticky/fragmented path.

The normative composition is recorded in [SPEC.md](SPEC.md). No new bug was found within the admitted ordinary relative-position domain.

## Independent native composition

`check_native.py` extracts the exact changed fallback assignment expressions, the complete new helper when present, and the exact retained normal-position getter bodies. It uses explicit facades for property storage, baseline providers, frame dimensions and writing-mode coordinate conversion. It does not substitute those facades for complete provider verification.

At O0 and O2 with nonrecovering UBSan, each available helper/fallback path executes 108 first/last checks across horizontal-tb, vertical-lr and vertical-rl, property present/absent, relative offsets −10/0/10 and varied coordinates:

| Source role | Natural helper mismatches | Existing fallback mismatches |
|---|---:|---:|
| Shared before | 36 | 36 |
| Shared after | 0 | 0 |
| Natural-only standalone | 0 | 36 |
| Relative-only standalone | Absent | 0 |

The natural-only standalone's old fallback mismatches are expected and retained; they demonstrate that the two independent patch scopes were not silently combined. Three compiled provider mutants are rejected in both modes: always use current position; always use property storage even when absent; omit the child-size adjustment for reversed origin. Actual current frame position remains unchanged by the read queries. Counts describe this finite corpus, not universal proof coverage.

## WPT and regression evidence

Raw event streams independently establish 288 paired cases: 192 FAIL→PASS and 96 unchanged PASS status/message pairs. Every original failure occurs at the final non-descendant-position assertion, after size, visual-offset and remove/restore controls. Candidate input pins differ from baseline only for the targeted CPP and two binaries.

The WPT uses fixed ordinary dimensions and a static peer with matching font and geometry. It measures logical block starts correctly for all three writing modes, including negated right edge for vertical-rl. It checks requested child offset, class removal/restoration and static-container equality before asserting the relative child's container does not move. The 96 zero-offset cases are unconditional controls. This covers inline/flex parents, first/last groups, all four flex directions, text/empty donors and both offset signs. It does not cover orthogonal child writing modes, fragmentation or sticky scrolling.

The final regression run has 29 files: 23 PASS reftests, 309 PASS subtests and six OK harnesses. That includes all 48 natural-donor tests. Build receipt and binary pins agree with the run; the successful producer build retains the known export-tier monitor KeyError alongside zero compiler warnings. Scoped lint is recorded as passing. This reviewer did not run a browser or main build.

## Acceptance boundaries

- The saved normal-position property must describe the appropriate normal layout state. Its complete freshness/lifetime, style transitions, ancestor adjustments and sticky updates remain unproved. Readiness of fragmented donors remains the previously reported separate lead.
- The actual property getters are source-bound; the physical/logical coordinate classes and storage system are modeled facades here. Source contracts and the browser matrix support the admitted modes, not every writing-mode combination.
- Every existing signed32 provider/consumer intermediate must be defined. This query repair is not an overflow fix or a sentinel-alias fix.
- The shared paired experiment changes three calls. Standalone applicability, native extracted behavior and commutation are verified independently, but no isolated upstream runtime is claimed.
- The separate full formal companion must close its stated conditional source/model obligations before this becomes formal acceptance. This report does not waive that gate.

## Reproduction and ownership

`python3 check.py --repo /absolute/firefox --out /absolute/new-output` verifies package identities, role separation, raw browser events and independent patch/commutation checks. `python3 check_native.py --out /absolute/new-output` runs extracted source calibration and mutants. `verify.py --manifest-sha SHA` checks the frozen outer and nested producer rosters.

Only owned review artifacts and disposable temporary native outputs were created. No shared native/WPT files, index, browser or main build were changed. A newly fetched provider file was briefly written to an incorrect discovery-directory filename, then immediately moved to the review; the discovery's closed roster and all 23 original hashes were reverified. No existing discovery payload was modified. Temporary compiler products were removed.

Final verification: `evidence-v3` includes exact retained-provider header checks. `SOURCE-TRANSFER.json` confirms all seven previously compiled original/mutant programs regenerate byte-for-byte after binding the identical indexed provider to the retained Git header. This is an exact source transfer, not an additional claimed native run.
