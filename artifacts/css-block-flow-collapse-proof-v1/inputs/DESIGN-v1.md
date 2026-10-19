# Collapse-through resolved-size guard: design under review

The accepted browser witness and root/independent replay live in
artifacts/css-breadth-probes-round11-v1/block-flow/. No production edit is made
by this design document.

## Defect and candidate

IsSelfEmpty uses two endpoint evaluations for both padding and preferred/minimum
block sizes. The non-monotone expression max(0px,min(10%,100px - 10%)) is zero
at both sampled endpoints and positive at ordinary intermediate bases. During
ComputeCollapsedBStartMargin, an empty child then admits its end margin and the
following sibling's start margin into its parent's start aggregate. PlaceBlock's
later actual-size check does not undo that aggregate.

The recursive traversal already has a ReflowInput containing resolved padding,
preferred size and min/max constraints. A candidate additional nonempty guard
would reject collapse-through if resolved block padding is positive or a finite
resolved preferred/minimum block size is positive. It must cover both the
IsSelfEmpty and fallback IsEmpty output paths. Retain existing predicates as
eligibility conditions for zero or unknown values; do not replace their global
meaning in editor, caret, inline or line-layout callers.

## Design obligations before native integration

- Distinguish NS_UNCONSTRAINEDSIZE from ordinary positive dimensions.
- ReflowInput computes content-box sizes and applies box-sizing in its size
  providers; confirm how min/max clamping and definite preferred sizes interact.
- Do not mistake positive raw preferred size for a positive fragment size after
  consumption. The current traversal crosses normal/overflow/next-in-flow lines.
- Preserve IsSelfEmpty's explicit hidden-by-content-visibility-of-parent result.
- Confirm wrapper and non-block fallback semantics; the recursive descent can
  enter column-set wrappers while retaining the outer ReflowInput.
- Keep auto/intrinsic/indefinite and zero-basis behavior. IsDefinitelyZero is a
  syntactic classifier and would reject the accepted actual-zero controls.
- No universal equality between CSSOM resolved zero and CSS computed zero is
  claimed. Positive witnesses are clear; zero cases are compatibility controls.

## Initial WPT baseline

The proposed test has 90 subtests: padding-bottom, height and min-height across
content-box/border-box, five bases and both initial orders, plus positive literal,
plain percentage, zero, flow-root and no-contaminating-margin controls. Each
checks first-child extent and parent geometry during A/B/A changes. Minimum-size
coverage extends the earlier accepted browser probe and requires baseline review.
Existing min-height and collapse reftests accompany it. Tests are synchronous
geometry tests; no font, remote resources or animation settling is required.

## Formal target

Prove the endpoint counterexample over a length-percentage comparison model,
then a guard contract: positive resolved separation cannot be classified empty,
and prior zero/unknown eligibility is preserved. A margin-set traversal model
should admit a later sibling only after sound collapse-through classification.
Native source linkage and provider assumptions remain separate from the scalar
model; no full reflow or fragmentation theorem is implied.

Primary rules: CSS22 box.html#collapsing-margins and CSS Sizing 3 #box-sizing,
read against current primary pages on 2026-10-18 and the retained round11 audit.

## Candidate and measured baseline

Baseline session 42831 exits 1: 36 new failures, 54 passes, five existing reftest
passes. Every failure is parent top 80 instead of 10, after extent calibration
passes. All 26 run pins and metadata absences remain stable. Minimum-height
coverage reproduces the same discrepancy as the earlier preferred-height and
padding paths.

A candidate now adds a final rejection guard in ComputeCollapsedBStartMargin
after both existing empty-output paths. It checks both resolved block border/
padding sides separately, finite positive ComputedBSize and finite positive
ComputedMinBSize. It preserves the explicit hidden-by-parent content-visibility
case. There is no sum of padding sides that could introduce arithmetic overflow.
The traversal's own start-margin aggregation is unchanged: this result controls
whether the caller admits the child's end margin and continues to siblings.

Formatting session 84318 exits 0; 12 unrelated changes were restored byte for
byte, with Python AST equality verified before restoration. Initial sandbox
format attempt failed on the external mach environment lock before formatting.
Candidate source SHA256:
0e299c0a3fc978f73721b62454246e1229c70d9591ba3efb9712e65a170139b0.
Build, paired WPT and independent design/formal reviews remain gates.
