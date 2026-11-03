# Direct animation and SVG/SMIL coverage

The root-self candidate's `element.is_root()` is sufficient for the two reviewed non-pseudo entry points. The supplied style is obtained for that same element without a pseudo request. This is a source conclusion, not new browser coverage or a separate bug.

## Actual caller chain

`Servo_AnimationValue_Compute` has one indexed C++ wrapper, `ServoStyleSet::ComputeAnimationValue`, whose sole indexed caller is `AnimationValue::FromString`. That function obtains `nsComputedDOMStyle::GetComputedStyle(aElement)`, then passes the same element, parsed declaration and resulting style to the wrapper. The omitted `PseudoStyleRequest` argument defaults to `{}`. Its indexed caller is `nsDOMWindowUtils::ComputeAnimationDistance`, which supplies the caller's Element and two value strings; it has no pseudo argument. Thus a document root means its primary style, not the host's `::before` style. An internal pseudo backing element would itself not be the document root. No arbitrary host-plus-pseudo ComputedValues caller was found in this indexed chain.

This conclusion is limited to the current callers: the Rust FFI signature alone does not enforce that an arbitrary future caller supplies a matching primary style. The source/extraction tests do not exercise the privileged WindowUtils API. A Firefox-specific privileged test could compare root font-size distance between `1rem` and `3rem` with twice an independently calibrated initial font size; this is not a portable WPT entry point.

SMIL takes a different route: `SMILCompositor::CreateSMILAttr` constructs `SMILCSSProperty` with `mKey.mElement`; `ValueFromString` passes that element to `SMILCSSValueType::ValueFromString`. The latter obtains `GetComputedStyleNoFlush(aTargetElement)` without a pseudo request. `ValueFromStringHelper` parses the CSS declaration and forwards that same target/style through `ServoStyleSet::GetAnimationValues` to `Servo_GetAnimationValues`. `font-size` is explicitly admitted by `IsPropertyAnimatable`. Again, the actual target, rather than its animation child or an outer SVG viewport, determines document-root identity. The no-flush style lookup does not establish freshness by itself; the proposed test establishes a clean underlying style before starting an animation.

The exact e86 saved FromString, SMIL value converter, wrapper and Rust sources were independently authenticated against the existing source map. New upstream caller searches corroborate that chain but are discovery evidence, not an e86 blob-identity claim. `ContextForSubstitution` remains a separate Inspector path with its explicit `!is_pseudo` guard; this investigation adds no runtime coverage there.

## Minimal feasible SMIL WPT

Use an HTML testharness parent and a same-origin **SVG document** in an iframe, not an inline SVG subtree. Check that its `documentElement` is the target SVG. A nested `<svg>` control must remain non-root even though it establishes an SVG viewport.

Use a fresh SVG document for each target/unit case. Measure and flush its literal underlying root font-size/line-height first (for example 23px/37px). Obtain expected initial font and normal line metrics in a separate reference document using ordinary root `font-size: 2rem` or `2rlh`; never animate, cancel, or reset a comparator in the target document. Record the reference's computed pixel result rather than assuming 16px or a fixed normal multiplier.

Append `<animate attributeName="font-size" from="1rem" to="3rem" begin="indefinite" dur="2s" fill="freeze">` directly to the target root, and separately use `rlh`. Pause the outer SVG timeline, establish time zero, begin the animation, then seek to one second. Read the target's computed font-size first and after frame settling; require both to match the independent ordinary-root reference. Include a literal 20px-to-40px animation at midpoint, plus descendant/nested-SVG font-size rem/rlh cases under an unanimated 23px/37px root (expected 46px/74px). Record the timeline time and paused state so an inactive animation cannot masquerade as correct conversion. Preserve every observed value if calibration or SMIL sampling fails.

Do not include root line-height animation in the first test: its SMIL property admission is a separate prerequisite. Root-host pseudos are already covered by the keyframe fixture and are not SMIL targets. No fixture, manifest, browser run, or new acceptance claim is produced here.

## Normative trace

1. SVG Animations, target selection: without `href`, the animation's parent is its target. Property selection searches CSS properties before XML attributes. Thus the child animate element above targets the SVG document root's CSS font-size.
2. CSS Values 4, font-relative lengths: root-relative units identify root metrics; for a font-affecting property on that same root, absence of an element parent selects initial font/line-height metrics. The special lh/rlh rule likewise applies to font-affecting properties.
3. SVG Animations, SVGSVGElement timing methods: the outermost SVG's pause/seek methods control its SVG animation timeline. Existing upstream WPT uses pauseAnimations/setCurrentTime followed by a computed-style assertion, supporting the proposed harness mechanism, not proving this new case passes.

**REACHED** for the proposed root font-size rem/rlh expectation and caller identity. Browser execution and exact synchronous SMIL sampling behavior remain untested here. This is additional coverage for the existing root-self repair, not a new observed defect.

Sources: [CSS Values 4 font-relative lengths](https://drafts.csswg.org/css-values-4/#font-relative-lengths), [SVG animation target](https://svgwg.org/specs/animations/#HrefAttribute), [SVG animation timing interface](https://svgwg.org/specs/animations/#InterfaceSVGSVGElement). Tool-sourced excerpts and provenance are recorded separately.
