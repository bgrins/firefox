# Independent review of the collapse-through candidate

## Verdict

This corrected report supersedes REPORT.md before independent review acceptance. See PROOF-PLAN-REVIEW-v1.md for the corresponding finite-tree model constraint.

**Candidate v1 fixes the measured ordinary-block discrepancy. Final native acceptance remains pending focused provider controls.** No production change is requested from source review at this point. This is one shared collapse-classification bug family, covering the padding, preferred-size and minimum-size paths. It does not establish separate landable bugs for every property.

The independent checker completed with exit 0. It reconstructs both patch outputs against the original base and current HEAD, authenticates retained source inputs, reconstructs all expected test identities and derives the before/after outcome changes from raw WPT logs. No browser, build, production/WPT edit, index mutation or commit was performed in this review. The author of this review did not write the candidate, WPT or original runtime probe. Root owns the candidate and runs; sigma_design_review independently reviewed the original runtime evidence.

No formal companion is accepted by this report. A scalar guard theorem would remain conditional on the ReflowInput providers discussed below.

## Independently reproduced evidence

| Check | Result |
| --- | --- |
| New subtest identities | 90 in each run, exactly the independently generated inventory |
| Baseline | 36 FAIL, 54 PASS |
| Candidate | 90 PASS |
| Existing reftests | Five PASS in both runs |
| Total identities including harness result | 96 |
| Outcome changes | 36 FAIL to PASS; 60 unchanged |
| Before/after pins per run | All 26 stable |
| Retained nonbinary inputs authenticated | 24 per run, 48 total |
| Changed identities between runs | Candidate native file, Firefox executable, XUL |
| Patch reconstruction | Original base and current HEAD produce exactly the retained candidate native/WPT bytes |

The failing inventory is derived from three properties, two box-sizing values, three positive interior bases and two initial orders: 3 × 2 × 3 × 2 = 36. Each raw failure says parent top was 80 instead of 10, at state 0 for expression-first and state 1 for literal-first. Thus declaration acceptance, child extent, parent left and parent width assertions preceding the failed assertion completed. A failed subtest stops at that assertion; baseline logs do not establish its later states. Candidate PASS establishes completion of all three states in each subtest, through the standard test harness. It does not provide a separate retained array of raw rectangles for passing assertions.

The two zero-extent bases and all controls pass in both versions. The minimum-height family is newly covered by this WPT and exhibits the same independently derived outcome pattern. The existing references check selected margin-collapse and min-height behavior, not all layout or fragmentation paths.

`check.py` does not import the producer's expected outcomes. It uses the rational witness at the five integer bases, generates names separately, checks raw failure messages, verifies unique event identities and compares its result to the producer summary only after deriving the result. Its small patch applicator checks all original context/deletion lines and hunk counts, then compares the reconstructed bytes with retained source snapshots. Read-only `git show` supplies originals at base `32226ddf3a29d58a52291babebdff2a5a7ce46c6` and HEAD. Historical binaries are identified by retained run receipts; they were not independently rebuilt.

## Normative chain

The live primary CSS22 margin rules and CSS Sizing 3 box-sizing section were checked during this review. The original accepted round11 report retains the fuller specification and runtime chain.

For these ordinary in-flow blocks, positive separating padding or a definite positive height prevents own-edge collapse. A positive minimum controls the zero preferred height. Without the separator, adjoining positive margins combine by maximum. The parent's initial set is its zero start plus the first child's 10; the following 80 cannot cross a positive first-child extent. Border-box dimensions account for padding and borders with a zero content-size floor. See [CSS22 collapsing margins](https://www.w3.org/TR/CSS22/box.html#collapsing-margins) and [CSS Sizing 3 box sizing](https://drafts.csswg.org/css-sizing-3/#box-sizing).

The CSS22 wording distinguishes computed height from CSSOM resolved height. This report does not turn a resolved zero into a universal computed-zero theorem. In particular, a positive expression capped by max-height:0 must be examined as a compatibility observation; equality with a literal positive height capped by zero is not an assumed normative oracle.

## Native design review

### Output and traversal behavior

The added code executes after both existing empty-output paths: all traversed child lines empty followed by IsSelfEmpty, and the fallback IsEmpty path. Existing nonempty results remain false; a null output pointer leaves behavior unchanged. The explicit hidden-by-parent predicate preserves the preexisting true result for skipped content.

The guard does not prevent the frame's own start margin from adjoining its parent's. It prevents the caller from adding that frame's end margin and proceeding to following siblings. This placement matches the observed contamination mechanism. The current frame's children can still contribute their start margin when allowed, even if the current frame itself has positive block size.

Both logical border/padding sides are checked individually, avoiding an introduced sum overflow. The positive-size check excludes NS_UNCONSTRAINEDSIZE. Auto/unknown alone therefore does not produce a separator. Existing style eligibility is retained rather than globally replaced by a syntactic or universal-zero predicate.

Clearance and nonempty-line exits set a false result only while the output has not already been initialized. After the first normal-line pass sets it, a later overflow/next-in-flow nonempty exit can stop traversal without overwriting a prior true result. The new guard can then refine that retained true result using the original frame's resolved inputs; it does not alter this preexisting initialization rule. The method's dirty-line return value and clearance retry bookkeeping are unchanged. Top-level callers omit the emptiness output; their margin traversal still changes through recursive calls where a concrete child separator is found.

### Size providers

For ordinary blocks, ReflowInput::InitConstraints obtains its content-box size from nsIFrame::ComputeSize. That provider resolves the preferred size, applies maximum then minimum constraints, and handles border-box subtraction before storing the result. ReflowInput::ComputeMinMaxValues similarly applies box sizing, maps unresolved percentage minimums to the initial value, and floors maximum constraints at the minimum. Thus the new reads are not direct evaluations of unbounded preferred CSS sizes.

A positive minimum beats a smaller maximum; the additional ComputedMinBSize check is particularly necessary when the preferred size is auto/unknown. Auto/intrinsic cases without an independently positive resolved minimum retain the old eligibility. Existing aspect-ratio exclusions in IsSelfEmpty remain intact. Flex/grid items, replaced frames and BFC boundaries already have different nonempty/margin-root behavior; this patch does not redefine those global predicates.

The existing height/min-height border-box WPT variants use zero borders and zero padding. They are useful spelling coverage, but do not establish a nontrivial content-box conversion. The required extra controls below close that specific gap.

### Wrappers and fallback

DescendIntoBlockLevelFrame can inspect the block inside a column-set wrapper while the final decision still refers to the original frame/ReflowInput. The recursive path constructs the extra wrapper input for descendants. The guard consistently uses the original frame's own dimensions rather than accidentally combining an inner frame's writing mode with outer dimensions.

However, nsColumnSetFrame::IsEmpty can return true when its columns have no principal children. Its fallback is not universally false, so wrapper safety cannot be dismissed on that premise. The focused fragmented-empty control must retain actual fragment counts. Generic nsIFrame::IsEmpty returns true only for hidden-by-parent content, covered by the explicit exemption. Inline/text lines use their line emptiness before this recursive block output; the patch does not fix global inline endpoint classification.

### Fragmentation

ComputedBSize represents the element's computed content-box size, not necessarily its remaining fragment size. nsSplittableFrame::GetEffectiveComputedBSize explicitly subtracts consumed size later, and decoration sides can be suppressed at fragment boundaries. Therefore it would be incorrect to justify the guard as always reading the final positive fragment extent.

There are mitigating source facts: normal and float top-level start-margin processing is restricted to first continuations, the recursive traversal intentionally visits normal/overflow/next-in-flow lines, and the existing IsSelfEmpty style tests already reject literal positive sizes independently of consumed space. The new check makes the non-monotonic positive case act like that existing size classification. These facts support the design but do not prove every continuation arrangement. A focused empty-fragment comparison remains a gate rather than being replaced by a full-layout theorem claim.

### Global predicates

IsSelfEmpty still has callers in ReflowInput, inline/line-layout paths, editing and selection-related behavior. The endpoint predicates remain potentially unsound at other consumers. Those are separate investigation surfaces, not fixes silently included in this candidate. Restricting this patch to the collapsed-margin consumer avoids changing their semantics without evidence.

## Required focused controls

These are finite provider and compatibility gates, not a request for comprehensive layout testing. Root and a separate probe author are preparing them.

1. **Minimum wins maximum:** original fixture, basis100, min-height expression or10px, max-height:0. Child extent10 and parent top10 are normative.
2. **Maximum caps preferred height:** original fixture with expression height and max-height:0. Child extent0 is normative; retain observed baseline/candidate parent geometry as compatibility evidence. Do not assert that capped literal10 must have identical collapse eligibility.
3. **Indefinite basis:** parent height:auto; expression height versus auto, and expression min-height versus0. The percentage-containing expression behaves as initial; child extent0 and parent top80 are expected in the ordinary empty fixture. B's later positive used height does not make P a definite percentage basis.
4. **Actual box-sizing adjustment:** height/min-height expression or10px with bottom padding20. Border-box child extent20 (zero content size), content-box extent30, parent top10. This verifies an actual subtraction/floor and padding barrier.
5. **Empty fragmented separator:** multicol container height50,width200,count2,gap0,fill:auto; P height200; empty A with max(0px,min(100%,400px - 100%)) versus200px. Retain all client rectangles and require multiple actual fragments. Compare expression/literal geometry with separate literal baseline/candidate preservation. A nonempty120px child is only an additional unchanged control: it already fails IsEmpty and cannot exercise the new guard.
6. **Hidden ancestor transition:** P height100 with content-visibility:hidden, then visible, then hidden. Hidden P is contained and has parent offset0; visible positive A permits only its start10 to reach P. Avoid synchronous reads of hidden descendants that may force layout. This is semantic compatibility evidence, not instrumented proof that the exact exemption branch executed.

No final acceptance should cite this report until the controls have been independently reviewed. A subsequent report can accept the same candidate or request a targeted revision based on those results. Preserve this initial assessment and the original WPT evidence.
