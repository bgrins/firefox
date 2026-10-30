# Progress-probe specification review

Checked the current editor drafts on 2026-10-30 using direct normative pages because webspec-index is unavailable in this environment. This is a source review and exact arithmetic check, not a browser result or Lean proof.

[CSS Values 4, font-relative lengths](https://drafts.csswg.org/css-values-4/#font-relative-lengths) defines em from computed font size and lh from computed line-height. The parent-basis exception applies when those units appear in the specified font-affecting properties or line-height itself. Here the contextual units appear in animation-duration. The middle animates explicit line-height lengths while depending on inherited font size; the child animates opacity while depending on inherited line-height. Inference: this test has no self-dependent duration edge.

[CSS Inline 3, line-height](https://drafts.csswg.org/css-inline-3/#line-height-property) makes line-height inherited and computes explicit lengths as lengths. The test uses pixel endpoints, avoiding normal metrics and unitless inheritance. It checks computed line-height, not actual line-box height. The root remains fixed, so root-rem invalidation is not part of this probe.

[CSS Animations 2, animations](https://drafts.csswg.org/css-animations-2/#animations) requires animation-property changes to update the associated animation, subject to successful script overrides. The property-only probe intentionally overrides duration, retaining 2000ms applied timing while relative width endpoints change. The chain probes retain CSS duration ownership. [Pending style changes](https://drafts.csswg.org/css-animations-2/#requirements-on-pending-style-changes) requires relevant animation API results to account for pending computed-value changes; therefore membership/timing queries can affect observation. They remain separate from the earlier child-style-only samples.

Exact rational arithmetic, independently evaluated with Python fractions (31a92b/0):

| Parent font px | Middle duration ms | Middle line-height px | Child duration ms | Child opacity |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 1000 | 28 | 1750 | 3/7 |
| 32 | 2000 | 22 | 1375 | 6/11 |

The equations are middleDuration=1000*parentFont/16, middleLineHeight=16+16*750/middleDuration, childDuration=1000*middleLineHeight/16, childOpacity=750/childDuration. They assume the fixture's paused 750ms time, linear interpolation and active interval. This calculation checks the expected values; it does not prove native propagation or a convergence deadline.

Initial calibration assertions run before record transport. A failure there leaves the WPT assertion evidence but no complete post-trigger record. It must be reported as a browser failure with measurement not reached, not silently excluded or treated automatically as an infrastructure defect. Three passive frame samples do not establish first-flush correctness or native queue liveness.
