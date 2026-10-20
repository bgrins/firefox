# Mixed-type iteration retention: provider oracle

## Verdict

The proposed branch is reachable by a registered `<number> | <length>` value under the current native source and has a specification-backed observable. `probe.html` contains 18 **UNEXECUTED** WPT tests. It is a guard for a currently correct branch, not a newly discovered defect or a runtime claim. Node syntax and registration-only evaluation passed; no browser callbacks ran.

## Independent derivation

1. [Properties and Values API §5.3](https://drafts.css-houdini.org/css-properties-values-api-1/#combinator) permits ordered alternative syntax components. `8` and `2` parse as numbers; `20px` as a length. The registered property has noninherited initial value `1`, so the noninitial computed numbers also calibrate successful registration and typed parsing. [Animation behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior-of-custom-properties) follows computed types.
2. [WA1 effect value](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect) applies each keyframe's composition with the underlying value before final interpolation. Underlying `8` plus the additive start `2` gives numeric `10`. The end keyframe explicitly replaces with `20px`.
3. [WA2 §3.2.1](https://drafts.csswg.org/web-animations-2/) inserts iteration accumulation after keyframe composition. At current iteration1, it combines the final keyframe as first argument and each already-composed endpoint as second argument once. Its explanatory note explicitly identifies retention of the second argument for values without accumulation/addition.
4. [WA1 animation types](https://drafts.csswg.org/web-animations-1/#animating-properties) makes mismatched computed component types discrete. [Values4 combination rules](https://drafts.csswg.org/css-values-4/#combining-values) make nonadditive combination return its second operand, with accumulation defaulting to addition. Thus `20px` accumulated onto numeric `10` leaves `10`; the end length accumulated onto itself becomes `40px`. Interpolation between number10 and length40px selects10 at progress.25 and40px at.75.
5. For an underlying `attr(data-number type(<number>))`, the retained10 depends on that attribute. [Values5 attribute security](https://drafts.csswg.org/css-values-5/#attr-security) requires its provenance through registered-value substitution. In a whole custom-property bundle containing a URL and `var(--mixed)`, that substitution taints the whole bundle and invalidates its URL. In the direct border-image declaration the attribute-derived width is outside the URL, which stays usable. The late clean length branch does not use the rejected underlying number and stays clean.

Primary pages were freshly read with the web tool on 2026-10-19. Separate raw HTML retrieval failed due shell DNS restrictions, recorded in SOURCES.json; no complete downloaded normative snapshot is claimed. Section URLs above should be read with the named section if an editor changes an anchor.

## Exact source admission

`source/` retains complete local `glue.rs`, `value.rs`, animated `mod.rs`, and animation derive source, with hashes. The trace is:

- `CustomAnimatedValue::animate` checks names, then Option delegates Some/Some.
- `ValueInner::Component` delegates to `GenericValueComponent`; Number and Length are distinct variants. The derive generator returns Err before evaluating variant fields when discriminants differ.
- `Value<Component>::animate` calls its provider before output construction; successful number addition carries the current OR taint rule.
- `Servo_AnimationCompose` admits the named animatable property, obtains required underlying data, uses the final segment's explicit end, and passes timing's iteration count and computed segment position.
- `composite_endpoint` produces Some(number10) at the start; the replacing end initially has no separate composed value.
- In iteration1 `accumulate_endpoint` attempts length20px.animate(number10). Its discriminant mismatch returns Err, so `.or(Some(endpoint))` retains the already-composed number10, including taint.
- End accumulation succeeds as length40px. Final interpolation fails on the mixed variants and clones number10 below the midpoint, or length40px above it.

This is static caller/provider admission, not instrumented evidence that a browser executed the branch. Source generation, frame construction and timing implementations remain native admissions. Searchfox discovery was attempted first for iterationComposite WPTs and failed with DNS; no broad local search replaced it. Prior focused interpolation fixture informed the observer construction, not the independent arithmetic oracle.

## Probe and controls

The URL observer uses `border-image: url(...) 1 / var(--mixed)`, because border-image width accepts both numbers and lengths. Using the value as a slice would incorrectly make the length control invalid independently of taint. Each row runs with direct and whole-bundle observers.

| Row | Iteration/progress | Expected computed value | Expected taint | What it discriminates |
| --- | --- | --- | --- | --- |
| Static clean number | no animation | 8 | clean | Numeric width and clean URL |
| Static attr number | no animation | 8 | tainted | Actual typed provider and observer |
| Static length | no animation | 20px | clean | Registration alternative and width grammar |
| Main additive start, mixed last endpoint | 1/.25 | 10 | tainted | Retain full previously composed endpoint after failure |
| Same branch, literal underlying | 1/.25 | 10 | clean | Taint is not simply attached to all mixed-type failures |
| First iteration | 0/.25 | 10 | tainted | Endpoint addition independent of iteration accumulation |
| Replacing start | 1/.25 | 2 | clean | Underlying not used when replacement is selected |
| Numeric final endpoint20 | 1/.25 | 32.5 | tainted | Accumulation actually runs: from30 to40 |
| Mixed final endpoint, late selection | 1/.75 | 40px | clean | Positive length accumulation and discrete selection |

Every animated test first checks the unanimated provider and URL observer, then exact effect presence, composite modes, two admitted keyframes and values, current iteration, progress, resulting custom value, URL result and border-image width. No optional precondition or early-success guard. A blocked bundle must have initial border-image width1 as well as source none. Clean images use a fixed data URL; no network response oracle is required.

## Scope and mutation discrimination

Changing the failed-iteration Some branch to return None would yield the original start2 instead of composed10, so the main payload assertion fails even if the URL observer were accidentally broken. Retaining10 but clearing its flag would separately fail the whole-bundle image assertion while the direct control stays valid. Skipping iteration entirely fails numeric32.5 and late40px controls. Reversing the discrete selection fails the .25/.75 rows.

Fresh targets and literal keyframes avoid endpoint-update/base-notification races and typed raw-keyframe conversion dependencies. The successful numeric iteration control intentionally exercises repair80's right-operand provenance; this probe is for the current stack and is not advertised as passing an unmodified historical baseline. No fixes, standalone package or browser pass claimed. Root owns installation and runtime adjudication.
