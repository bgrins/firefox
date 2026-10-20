# Scroll-container natural-baseline conversion

## Finding

The natural-baseline provider returns a distance from the requested baseline group's edge. ScrollContainerFrame added the block-start border to that distance for both groups. For the last group this confuses the two coordinate origins. Flex and grid scroll containers with a 9px asymmetric block border visibly misalign text in installed release Firefox. This arose while testing the native-provider assumption of the new natural-donor proof; that helper exposes the same defect for additional nested block scrollers.

The repair converts the scrolled-frame last baseline to a block-start position, adds the block-start border, clamps to the outer border box, then converts back to a block-end distance. Merely substituting the block-end border is insufficient when scrolled and outer block sizes differ. Intermediate arithmetic is widened; optional absence, layout containment and the earlier legacy line-layout branch retain their existing order.

The [baseline export rules](https://drafts.csswg.org/css-align-3/#baseline-export) preserve the content's baseline subject to the scroll-container border clamp. The native API's group-relative convention is a separate implementation contract. Its complete caller/provider proof remains under review.

## Paired evidence

- The standalone 384-case WPT covers three writing modes, both directions, flex/grid scrolled content, first/last groups, four border configurations and four overflow modes.
- Before: 72 failures and 312 passes. After: 384 passes. All 312 controls have unchanged status/message; every baseline failure reaches the final alignment assertion after geometry/removal/restoration calibration.
- Pinned inputs change only ScrollContainerFrame.cpp and the browser binaries. The original source equals HEAD. The exact tested candidate built successfully and passed scoped native and WPT lint.
- Thirty-eight focused regression files pass: 24 reftests, 675 subtests and 14 harnesses, including existing flex/grid baseline-overflow tests and both pending baseline repairs.
- The unchanged original 64-row diagnostic also passes completely after repair, eliminating six newly exposed nested-block failures.
- The two-file native/WPT patch applies and reverses independently on HEAD and retained upstream. The real HEAD, index and worktree are preserved by packaging.

## Limits and next gates

The shared browser contains other pending project changes; no isolated upstream runtime is claimed. The paired one-source experiment establishes this repair's local effect. The 24 inline-block mismatches in the exploratory v2 diagnostic involve a separate legacy policy and are excluded from this finding.

Independent source review and the complete source-bound provider companion remain pending. The initial 14-result root mathematical draft covers coordinate orientation, clamping and sufficient machine bounds; it is not an accepted proof of the complete method or provider lifecycle. Fragmentation and natural-baseline truth remain separate obligations.

The natural-donor native queue remains blocked pending this provider repair and an explicit review of its prerequisite/standalone relationship. Its earlier acceptance is superseded; no existing capsule was rewritten. This repair is not yet included in the accepted-pending count. No commit or push was made.
