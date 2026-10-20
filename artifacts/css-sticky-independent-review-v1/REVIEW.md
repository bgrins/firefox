# Independent review: sticky auto insets and containing-block writing mode

## Recommendation and authority

**Recommend acceptance of H1/A and H2/B as two separately reviewable native repairs with their respective WPTs.** No blocking defect was found in either patch. This is independent source, normative, oracle, and retained execution-evidence review, not a universal formal proof or a fresh browser run by this reviewer. Root owns final acceptance. H3 nested-restyle is explicitly excluded.

The reviewer did not author the native patches or their browser tests, did not execute producer Python, and changed only `artifacts/css-sticky-independent-review-v1/`. Review work used authenticated retained inputs, inspected native context and `WritingMode::PhysicalSide`, independently applied/reversed both patches, implemented a separate geometric oracle, and reprocessed raw WPT events. No browser, build, Mach, Git, native/WPT edit, commit, or submission was performed by this reviewer.

| Obligation | Verdict | Evidence and limits |
|---|---|---|
| H1 normative auto-inset rule | REACHED / satisfied | Auto is zero for constructing the sticky view, but an auto side cannot activate displacement. |
| H1 source repair | Accept | Per-side zero normalization, either-inset activation, unchanged original-auto displacement masks. |
| H2 normative logical-end rule | REACHED / satisfied | Reduced end is relative to containing-block writing mode; explicit physical mapping independently checked. |
| H2 source repair | Accept | Uses containing-block `GetWritingMode()` and maps the appropriate logical end separately for x and y. |
| WPT oracle and fixture | Accept within stated fixture | Independently enumerated 216 A cases and 1,080 B cases; normal-position/scroll calibration guards fixture assumptions. |
| H1 oracle correction | Preserved / correctly classified | Initial two negative-zero assertion failures are test defects; 18 actual geometry failures remain after correction. |
| Native runtime separation | Satisfied in fixed project worktree | Four separately built source variants; A-only and B-only independently repair only their corresponding failures. |
| Patch separation | Satisfied | Each patch changes exactly one native file plus its own WPT; independent forward/reverse checks and exact commuting edit composition. |
| Existing sticky/timeline regression evidence | Satisfied for recorded suites | Paired statuses, expectations, inputs and absent metadata checked; two preexisting expected single-axis failures remain. |
| Universal native/provider/numeric proof | Not established or claimed | Future obligations below; finite execution evidence does not discharge them. |
| H3 nested-restyle | Excluded | No acceptance, correction, or proof claim for H3. |

## Frozen input identity

- H1 `fix-candidate-v1.patch`: `001466c48760c278bc639cdb0ae2e8fe2ddb31886fd357f51d51536368b5fc85`.
- H2 `fix-candidate-v1.patch`: `e5b36f33024f4ed453bd2e02ab233a84559fb237608f480efb1861cdd765a05f`.
- Original sticky CPP: `877d9e663bd76a750537c19fe02d2f357be6407bab87484366f0766799ccc817`.
- A-only: `da6980060b11c467af91c5787702d3ebd218b00bac928848663f3d2e56212726`.
- B-only: `e3b00298f82ffb33a9c36cb63990595afbb4813247fdc12ee2810f93d94ff23c`.
- AB: `fe79e921b6309b75e8d7f7c9292521bb27182567695f74bc6245710cfc75a91f`.

Both patch hashes and all four source hashes are checked before parsing by reviewer-owned `audit.py`. Its patch reader requires unique exact old text. Forward application to original and reversal are byte exact; isolated changed blocks apply in both orders to produce AB. Full patch contexts overlap, so applying the second raw standalone patch on top of the first can require ordinary context resolution. The changes are semantically independent, not promised to apply consecutively with no context conflict. No shared timeline or unrelated project repair is included in these two patch files.

Root additionally retained clean-source application/reversal receipts against revisions `32226ddf3a29d58a52291babebdff2a5a7ce46c6` and `11482ee213bf63c749b6d205c2c7591d783bdaa8`. This reviewer did not fetch either revision or run clean-base browser builds. The four-variant browser matrix holds the rest of the current project worktree fixed, including other existing repairs. Accordingly, standalone patch applicability and controlled native runtime independence are supported; clean-base runtime/CI success is not asserted.

## Normative trace

Reviewed current retained primary pages:

- [CSS Positioned Layout 3, sticky positioning](https://drafts.csswg.org/css-position-3/#sticky-pos), retrieved 2026-10-19 01:22:44 UTC, SHA-256 `5ac9402094a5561500f4862a1af4d6fe394883426745e689591181d5a7169a70`.
- [CSS Writing Modes 4, logical-to-physical mappings](https://drafts.csswg.org/css-writing-modes-4/#logical-to-physical), retrieved 2026-10-19 01:25:21 UTC, SHA-256 `af48c806dbd7ef0a6b65ad38dac25ca825f0bd62805c6279343688d4ce8acb01`.

`evidence/spec/FETCH.json` retains retrieval headers and hashes. The reviewer authenticated both pages and verified section IDs. The spec-trace structure was used for branch reasoning; `webspec-index --help` returned command-not-found, so no reference-graph enumeration is claimed. These are direct normative layout rules, rather than a remote event algorithm requiring an inferred call route. No skill/tool availability issue prevents reading the complete retained deciding paragraphs and mapping table.

Scenario: a sticky border box in one ordinary 100px scrollport, a 600px containing block, zero margins/padding/borders in the tested axis, physical normal position 200px before scrolling, supported writing mode, and one or both explicit physical insets.

1. Sticky layout chooses the nearest matching-axis scrollport. Both insets auto gives no sticky offset on that axis.
2. Otherwise, for view-rectangle construction, the specification says auto represents “a zero inset”. This establishes H1's conversion without enabling movement on that side.
3. If that rectangle is smaller than the sticky border box, reduce the effective end inset enough to fit the border box. End is “relative to the writing mode of the containing block”. This establishes H2's owning frame and axis mapping.
4. Only a corresponding non-auto side can force an inward shift. The shift is constrained by the containing block's position box. Tests use zero margins, so they do not depend on the unresolved margin interpretation discussed in CSSWG issue 9052.
5. Writing Modes defines the physical ends below. For the horizontal physical axis, use inline-end in horizontal writing and block-end in vertical writing. For the vertical physical axis, use block-end in horizontal writing and inline-end in vertical writing.

| Containing-block mode | Direction | x end | y end |
|---|---|---|---|
| horizontal-tb | ltr | right | bottom |
| horizontal-tb | rtl | left | bottom |
| vertical-rl / sideways-rl | ltr | left | bottom |
| vertical-rl / sideways-rl | rtl | left | top |
| vertical-lr | ltr | right | bottom |
| vertical-lr | rtl | right | top |
| sideways-lr | ltr | right | top |
| sideways-lr | rtl | right | bottom |

**Verdict: REACHED** for both H1 and H2 in this scenario. Reducing a fixed physical bottom or choosing x-end solely from direction conflicts with this table. Reducing an auto effective inset does not authorize offset from an auto side; source and oracle retain that distinction. When no reduction is needed, the changed logical-end selection has no effect. When both insets are auto, neither patch activates displacement.

## Native correspondence review

`StickyScrollContainer::ComputeStickyLimits` obtains the containing block, border-box union, scroll-frame size, computed insets, frame offsets, and containment rectangle, then constructs stick limits. `DoComputePosition` combines the normal position, stick limits and containment limits; continuations receive the resulting translation. The proposed edits affect effective inset normalization only.

H1 initializes each `nsMargin` member to its computed inset or zero for `NS_AUTOOFFSET`, using the constructor's top/right/bottom/left order. It enters normalization when either side is explicit, and sums normalized effective offsets. Crucially, downstream side activation still checks the original `computedOffsets`: an effective zero from auto never becomes an active zero inset. Existing two-explicit-side behavior is preserved in the same writing modes; both-auto leaves stick limits inactive. The patch removes sentinel arithmetic from the newly covered normalization path, but is not a general integer-overflow proof.

H2 uses `cbFrame->GetWritingMode()`, not the sticky child's writing mode or the scroll container's direction. `WritingMode::PhysicalSide` incorporates block direction and inline progression, including `sideways-lr`. The height branch asks for IEnd when vertical, BEnd otherwise; width asks for BEnd when vertical, IEnd otherwise. This maps exactly to the normative table. It also delegates used-direction details such as `text-orientation: upright` to the existing writing-mode provider; those provider cases are not covered by these WPTs.

The standalone H2 source deliberately retains the original two-explicit-inset normalization gate. Its WPT always specifies both physical insets, so H2's failures and repairs do not rely on H1. A's WPT uses horizontal-tb logical progression, where the old physical-end mapping is already correct, so its failures do not rely on B. These restrictions isolate defects while the AB source composes both changes for other combinations.

The surrounding implementation includes table containing-block adjustments, fragmented frame unions, scroll-frame padding/offset conversions, fixed-viewport sizing, and downstream scroll-range/timeline consumers. They were inspected as boundaries, not proved correct here. Existing single-axis nearest-scrollport limitations remain visible as expected failures. No source edit changes the nested-restyle update order.

## Independent oracle and WPT audit

`audit.py` independently transcribes the specification's physical mapping table and constructs a feasible physical-position interval. It normalizes absent insets only for view size, subtracts the positive view deficit from the selected physical end, activates constraints only for explicit sides, intersects/project-clamps to the containing-block interval, and chooses the nearest feasible point to the normal position. Original/A/B/AB predictions use separately controlled defect toggles. This is a finite review model, not an extraction or proof of arbitrary Gecko execution.

`ORACLE-ROWS.json` retains all 1,296 named cases, desired coordinates and four source-variant predictions. Every completed raw targeted WPT row is checked for membership, uniqueness, status and, for failures, the exact expected and actual numbers in the assertion message. Passing rows only expose PASS, not measured numeric coordinates; the retained WPT source binds PASS to its coordinate assertion. Expected statuses and intermittent allowances are checked to rule out expectation laundering. All raw statuses exactly match their receipts.

### A / H1: 216 cases

3 axes × 3 sizes (60, 80, 200) × 6 inset pairs × 4 scroll positions (0, 160, 260, 400). Inset pairs cover auto-end, auto-start, both-auto, explicit pairs and negative end values. The physical normal coordinate is asserted before enabling sticky, and scroll offsets are checked. Horizontal RTL uses a reversed flex arrangement while preserving the physical reference origin; its calibration prevents an untested direction assumption from supplying the result.

The 18 original geometry failures are the 200px box with logical start auto and end -20, 0 or 20: vertical and horizontal LTR at scroll 160/260 (12 cases), and horizontal RTL at 260/400 (6 cases). Fitting sizes and both-auto controls also run. Scroll 400 reaches a containing-block bound, so tests exercise constrained movement as well as the free sticky interval.

Initial v1 recorded 196 PASS / 20 FAIL. Two failures were JavaScript `-0` versus returned `0`, both horizontal RTL, size 200, scroll 0, for start/end 0/20 and 20/auto. Geometry was equal. Root preserved the original source/raw log/receipt and then normalized expected zero without a native change. The corrected baseline is 198 PASS / 18 FAIL, candidate 216 PASS. The reviewer independently recognizes exactly those two historical messages and preserves `ORACLE-CORRECTION-v1.json`; they are not counted as native improvements.

### B / H2: 1,080 cases

5 writing modes × 2 directions × 3 child mode/direction choices × 2 physical axes × 2 sizes (70, 200) × 3 near/far inset pairs (0/0, 20/10, -20/10) × 3 scroll positions (0, 180, 400). All inset pairs are explicit, guaranteeing independence from A. Differing child writing modes exercise containing-block ownership. The fixture verifies supported mode, actual scroll and physical normal position before enabling sticky.

The 168 original failures occur in eight mode/direction/axis combinations where legacy end selection differs: vertical-rl/ltr x; vertical-rl/rtl y; vertical-lr/rtl x and y; sideways-rl/ltr x; sideways-rl/rtl y; sideways-lr/ltr y; sideways-lr/rtl x. Each contributes three child styles times seven failing oversized geometry combinations. The 70px fitting cases are controls. The WPT uses its mapping helper for fixture orientation too, but explicit physical normal-position calibration prevents this coupling from concealing a wrong fixture origin; the reviewer table and interval oracle are separately written.

Neither WPT is a raster/APZ/timing test. Synchronous bounding-rectangle reads intentionally flush style/layout, and all tested dimensions are small integer CSS pixels. No test adds expectations, timeout allowances, browser-specific behavior, or metadata suppressions. New-test and local directory metadata absence is retained in run receipts; ancestor metadata and harness inputs are pinned.

## Native execution evidence

The final four-variant runs are builds of the same project worktree with only the frozen sticky CPP variant swapped. The independent auditor checks four build exit codes, build/log/receipt hashes, unchanged before/after inputs, equal pin sets, and that only CPP plus XUL/firefox vary across runs. `INDEPENDENCE-MATRIX-v1.json` additionally pins the broader project source set. Build monitor export KeyErrors were recorded by root; builds exit 0 and subsequent browser runs complete, so this review does not reclassify that monitor noise as compilation failure.

| Native variant | A suite | B suite |
|---|---:|---:|
| Original | 198 PASS, 18 FAIL | 912 PASS, 168 FAIL |
| A only | 216 PASS | 912 PASS, 168 FAIL |
| B only | 198 PASS, 18 FAIL | 1,080 PASS |
| AB | 216 PASS | 1,080 PASS |

Each suite also completes with one OK harness result. All failures and passes match the independent oracle. This directly demonstrates that each standalone native change fixes its own WPT without the other native change. AB has 1,296 PASS and two OK harness completions.

The final root H2 packaging receipt is retained. Formatting exits 0 and leaves the candidate sticky source unchanged; root records restoring unrelated formatter changes. The lint command exits 1 with zero errors and one warning because ESLint ignores the WPT HTML. That is an incomplete lint coverage result, not a successful JavaScript lint run; the executable browser assertions provide the relevant recorded test validation here. No extra lint-success claim is made.

H1 paired existing sticky suites retain 30 PASS, two expected FAIL and eight OK; H2 paired suites add the 216-case A regression and retain 246 PASS, two expected FAIL and nine OK. The two expected failures are existing single-axis scrollport cases. Each H1 and H2 paired view-timeline run retains 17 PASS and 14 OK. The reviewer compares complete named statuses and expected/intermittent values, not just aggregate counts, and verifies paired source/metadata invariance. These finite suites support regression confidence, not universal timeline correctness.

## Formal proof requirements for any later universal claim

1. Specify raw admission: computed inset sentinel representation versus finite coordinates, frame dimensions, scroll/offset domains, valid writing modes, and arithmetic overflow premises. Do not assume all nscoord operations are mathematical integers.
2. Prove auto-to-zero view normalization while retaining independent original-auto masks; prove both-auto neutrality and explicit-side-only displacement.
3. Prove the deficit formula yields a view at least as large as the border box and changes only the effective logical end, including negative insets, equality, all writing-mode mappings, and used-direction providers.
4. Connect physical x/y selection to `WritingMode::PhysicalSide` over all admitted encodings, not merely the ten tested mode/direction pairs. Cover `text-orientation: upright` and all admitted flags.
5. Prove source-level `nsMargin`, `nsSize`, `nsRect`, subtraction/summation, sentinel bounds and containment arithmetic; bound every intermediate including negative effective insets and extreme scroll positions.
6. Prove or explicitly admit providers for containing-block identity (including table special cases), border/margin/content unions, continuations/fragments, computed inset resolution, scrollport choice/size, padding and coordinate transforms.
7. Prove `ComputeStickyLimits` through actual `DoComputePosition` branch order and continuation updates matches the normative position-box constraint. Do not stop at effective-inset algebra or replace native dispatch with a preselected abstract action.
8. Treat containing-block margin interpretation and per-axis nearest-scrollport selection explicitly. Current unresolved/spec-divergent behaviors cannot silently be assumed correct or excluded from a claimed complete sticky implementation.
9. Establish preservation for fitting views, inactive axes, mixed explicit/auto masks, all geometric containment arrangements, and interactions of A and B. The current runtime corpora isolate A and B; arbitrary mixed auto plus orthogonal-writing-mode combinations remain outside observed browser coverage.
10. Include shared `GetScrollRanges` / `GetStickyScrollRangesForAxis` / view-timeline observers and frame lifecycle only if claimed. A position-only theorem plus finite timeline tests is insufficient for universal animation/lifecycle equivalence. H3 nested-restyle needs its own specification, state/order model and evidence.

An eventual formal package must separately identify mathematical theorems, exact native extraction/source binding, finite compiled/browser agreement, and unproved external provider assumptions. This review's acceptance recommendation is for these narrow native fixes and tests, not completion of that future proof program.

## Replay and integrity

Run `python3 check_integrity.py` from this directory to authenticate every retained file against `MANIFEST.json`. Run `python3 audit.py` to repeat the reviewer-owned static, oracle and evidence checks; it uses only retained files and rewrites `AUDIT.json` and `ORACLE-ROWS.json` deterministically. Root receives external SHA-256 pins for the manifest, checker and report. Hash agreement supports evidence identity; the substantive reasoning and checks above support the recommendation.
