# Independent normative contract (before native inspection)

Status: proposed interpretation of the retained current Editor’s Drafts; no browser result. Source hashes are in `spec/INDEX.json`.

## Required interior behavior

[CSS Properties and Values API, animation behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior) selects by-computed-value interpolation for a registered `<number>`. [CSS Values 4, numbers](https://drafts.csswg.org/css-values-4/#numbers) defines the weighted numeric sum. At progress .25 or .75, both endpoints contribute with strictly positive weights. [CSS Values 5, attribute security](https://drafts.csswg.org/css-values-5/#attr-security) requires taint to propagate to a substitution whose creation involved an attribute-tainted value, including equivalent token sequences from registered properties. Consequently, a later substitution of this numeric result must be tainted if either contributing endpoint was tainted. Numeric serialization alone cannot discharge this obligation.

This is an inference composing three normative rules, not an explicit animation-specific taint algorithm. It concerns attribute taint, not animation taint.

## Endpoints and choices left open

[CSS Values 4, combining values](https://drafts.csswg.org/css-values-4/#combining-values) gives the endpoint identities at progress 0 and 1. A tainted selected endpoint must stay tainted. The text does not explicitly resolve whether a zero-weight, unselected tainted operand still counts as involved in creating the result. Thus this review does not demand that taint disappear at the clean boundary, and does not treat conservative union there as a defect. Both endpoint-identity and conservative-union interpretations agree on every mandatory tainted assertion below.

| Start → end | 0 | .25 | .75 | 1 |
| --- | --- | --- | --- | --- |
| clean → clean | clean | clean | clean | clean |
| clean → tainted | diagnostic: clean or conservative taint | tainted | tainted | tainted |
| tainted → clean | tainted | tainted | tainted | diagnostic: clean or conservative taint |
| tainted → tainted | tainted | tainted | tainted | tainted |

For addition, both numeric operands contribute to their sum: a later substitution must retain either operand’s taint. For an initial probe, isolate replacement interpolation first; addition introduces an underlying-value provider and effect-composition ordering. Discrete selection differs from arithmetic combination and is outside the interior union claim. This contract does not prescribe transition creation/restart equality or equal-payload endpoint retention.

## URL observer

Set `--bundle: url(DATA) var(--n)` and `border-image: var(--bundle)`. The border-image shorthand admits an image plus numeric slice. Taint from the numeric substitution taints the whole custom-property substitution, including the URL, so the shorthand becomes invalid at computed-value time and `border-image-source` becomes its noninherited initial value `none`. A clean numeric result retains the data URL. Data URL identity and numeric slices must be calibrated independently; network success is unnecessary.

A control with `border-image: url(DATA) var(--n)` has the URL outside the tainted substitution: the tainted numeric slice alone is not a URL. It should keep the URL. This distinction follows Values 5’s direct-use versus whole-custom-substitution examples. The observer intentionally measures the URL longhand, not custom-property serialization, which cannot expose taint.

## Fixture requirements and prerequisites

Use registered inherits:false `<number>` with initial 12 and a parent whose value is `attr(data-n type(<number>))` = 8. Explicit child `inherit` supplies the tainted endpoint and `initial` the clean endpoint. This avoids raw attr()/var() keyframe endpoint parsing and does not require the prior raw-keyframe conversion repair. Static inheritance/initial calibration and actual numeric animation samples must pass before interpreting the URL observer. Both directional runs, literal clean controls, constant inherited tainted controls, direct-URL controls, and both boundary diagnostics are needed. Build a new target per sample to avoid metadata-only invalidation/equality repairs influencing the result.

The first fixture will not cover add/accumulate, extrapolation, multiple effects, registered lists, URL-valued properties, or parsing/scheduling equivalence. These remain explicit coverage boundaries.
