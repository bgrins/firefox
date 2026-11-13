# Independent used-margin repair review

No blocking source or test-expectation issue found in the reviewed three-line change. This review accepts its narrow purpose: refresh an already-existing used-margin cache after the overfull block margin calculation. It is not an exact-margin representation repair or a proof of all native callers.

## Exact source and behavior

`ReflowInput::CalculateBlockSideMargins` already computes the final containing-block-logical margin, updates its reflow-input value, and on the ordinary branch refreshes an existing `UsedMarginProperty`. The negative-space branch previously returned between those actions. The candidate performs the same physical conversion and conditional cache write before that return. It allocates no property when absent, introduces no arithmetic, and preserves the preexisting early returns, direction policy, and layout sizing decisions.

`SizeComputationInput::InitOffsets` seeds the cache from `ComputeMargin`, which initially treats auto margins as zero. `nsIFrame::GetUsedMargin` prefers this cache. The missing refresh therefore exposes the earlier values to readers, even though layout used the adjusted margin. Indexed CSSOM source confirms that layout-dependent margins read the frame's used margin after a reflow flush. The initial property write and the candidate both store the full physical record; the candidate uses `cbWM`, matching the surrounding calculation and existing successful branch.

The caller in `InitConstraints` excludes inline-level frames, inner table frames, flex/grid items, outside markers, and the column-content pseudo-frame. This change is not a new margin-resolution algorithm for those contexts. No virtual getter override is changed. Orthogonal blocks remain in the possible source domain, but the new test covers parallel parent/child writing modes only.

Pure absolute-length margins retain the existing getter fast path and property-absence behavior. The audit's fixed-length overconstraint discrepancy remains outside this repair. Neither the patch nor these tests claim to fix it. The known historical descriptions in bugs [381328](https://bugzilla.mozilla.org/show_bug.cgi?id=381328) and [1298008](https://bugzilla.mozilla.org/show_bug.cgi?id=1298008) support classifying this as a rediscovered cache-coherence defect, not a novel security issue.

## Normative trace and compatibility

**Scenario:** connected, rendered, non-replaced block children, parallel writing modes, definite inline sizes, no border or padding, normal block formatting. **Verdict: REACHED** for returning the resolved margins asserted by this WPT.

1. CSSOM resolves applicable margins of these displayed boxes to their used values. This includes logical start/end properties. The rendered block guards hold in the test. [CSSOM resolved values](https://drafts.csswg.org/cssom/#resolved-values)
2. CSS2's block-width equation resolves auto margins; when the fixed sizes already overfill the containing block, auto margins first become zero. Overconstraint is then absorbed on the containing block's end side. This produces the test's twelve numeric pairs, including `0, -100` for a 200 px child in a 100 px container with two auto margins. [CSS2 block width](https://drafts.csswg.org/css2/#blockwidth)
3. Writing Modes applies those horizontal sizing rules in the inline dimension and maps direction-sensitive overconstraint to start/end. This supports the same logical pairs for vertical-rl and vertical-lr with either direction. [Vertical layout principles](https://drafts.csswg.org/css-writing-modes-3/#vertical-layout)

Fresh indexed spec excerpts and successful anchor checks are retained under `evidence`. These clauses establish the small WPT expectations; they do not require this particular cache implementation. Existing margin-box geometry observations are corroborating compatibility evidence, distinct from the CSSOM assertion trace. No claim about general transformed or wide-coordinate geometry follows.

## Test and receipt review

`verify_review.py` authenticates all candidate INPUTS hashes, checks that the native source differs by exactly the three intended lines, derives all twelve expected pairs independently from the block equation, and compares every new test name and result in both raw reports. Its source model predicts the exact baseline partition: 30 pass and 66 fail. This is a test-table cross-check, not an independent browser run or native proof.

The actual retained fixed report has 96/96 new tests, four `computed-style-005` tests, and six `cssom-getBoxQuads-001` tests passing: 106 subtests in three files. Baseline build ID is 20261112025749; fixed build ID is 20261112034848. The baseline and fixed commands enable the getBoxQuads pref. The CSSOM test itself uses no pref-gated API. The audit separately retains 24 CSSOM observations and 24 pref-enabled quad observations, including stale margins at overfull widths.

The matrix is 3 writing modes × 2 directions × 4 margin styles × 4 size sequences. On complete success it checks 192 successive style observations, each with two margin assertions. The 24 multi-step sequences cover 40→200→40→100→200 while preserving the same frame. Baseline sequence tests abort at their first failing 200 px step; only the fixed passing report establishes execution of every step. Inputs and expected values are integral, so no rounding tolerance is involved.

The root's command receipts record actual mach exits: baseline 1, build 0, fixed 0. All three wrappers encountered a process-inspection PermissionError and originally recorded unsafe/unknown cleanup. These original receipts remain failed as recorded. Root's separate ACCEPTANCE records later independent process absence and validates the logs and source/binary pins. This review read and pinned that acceptance but did not independently inspect current process groups, rebuild Firefox, or rerun WPT. It does not relabel the original wrapper failures as successful lifecycle gates.

## Residual coverage and integration

Two useful follow-up regressions are nonblocking for this store: an orthogonal child/containing-block pair to exercise `cbWM` physical conversion, and transitions between auto/percentage and absolute-only margin styles to exercise property removal/recreation. The existing sequences change size, not style category or writing mode. Mixed parent/child directions and margin-trim remain outside this matrix. The same cache is read by geometry consumers, so the six existing quad tests are useful regression coverage; they do not assert all 24 previously observed overfull quad cases after the fix.

The change is small and source-consistent enough to accept with the current 106 passing local tests, without expanding its claim to all formatting contexts. All broader exact-margin and producer/reflow targets remain unchanged and open as previously recorded. Root has installed this independent native fix. Older frozen exact-reflow/interface copies do not contain it and must not overwrite the live source; a future composed candidate must explicitly retain this delta.

## Review procedure

No native files or root artifacts were modified. Only this sibling directory was written. No compiler or browser was launched. Tool lookup failures (one obsolete CSSOM helper name, initial sandbox network/cache restrictions, and an invalid multi-anchor `exists` invocation) did not supply evidence; successful single-anchor queries and the actual CSSOM source lookup supersede them. The empty failed-output files are retained. Installed CLI update notices were not acted on.

Run `python3 -I -B artifacts/css-block-used-margin-independent-review-20261112-v1/verify_review.py` to repeat the lightweight source/report checks against the retained parent inputs. `REVIEWED-INPUTS.json` pins selected reviewed files, not the entire still-growing root package. `FILES.json` freezes this review excluding itself.
