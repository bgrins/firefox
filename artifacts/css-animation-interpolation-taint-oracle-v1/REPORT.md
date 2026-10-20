# Numeric interpolation and attribute taint: oracle review

## Verdict

The current normative texts justify a focused observable test: a registered numeric interpolation with either endpoint attribute-tainted must retain that provenance at interior progress .25 and .75. The URL-containing `--bundle` is a valid observer when paired with direct-URL and static calibration controls. This is an independently derived interpretation, not yet a browser-confirmed defect in this artifact.

The exact zero-weight endpoint policy is less explicit. Keep the clean endpoint opposite a tainted zero-weight endpoint diagnostic. Do not require a global all-progress union theorem, transition restart, metadata-sensitive numeric equality, or changed URL base data on this evidence alone.

`NORMATIVE.md` was written before inspecting the native interpolation implementation. Its table gives the directional oracle and explains the remaining ambiguity. Pinned primary sources and URLs are in `spec/INDEX.json`.

## Normative chain

1. Registered `<number>` animates by computed value: [Properties and Values API](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior).
2. Numeric interpolation combines both endpoints with positive weights at the selected interior samples: [Values 4 numbers](https://drafts.csswg.org/css-values-4/#numbers).
3. Provenance propagates into substitutions, including registered equivalent token sequences; tainted URL use is invalid at computed-value time: [Values 5 attribute security](https://drafts.csswg.org/css-values-5/#attr-security).
4. An image and numeric slice form a border-image value: [Backgrounds 3 shorthand](https://drafts.csswg.org/css-backgrounds-3/#border-image). The whole custom substitution taints its URL; a direct URL adjacent to only a tainted numeric substitution remains a control.

The key inference is that a nonzero numeric contribution from an attribute-derived endpoint remains involved in creation of the later substituted value. The sources do not provide a separate, fully explicit animation-metadata algebra. Addition similarly combines both operands, but its native provider/order path is not adjudicated here.

## Runnable diagnostic

`probe.html` registers 40 unique subtests, checked by Node registration without invoking callbacks (`FIXTURE-CHECK.json`):

- Eight static controls: initial, inherited attr value, and two literal numbers, with each observer.
- Thirty-two samples: four endpoint-taint combinations × four progress values × two observers.
- Two of the 40 are explicitly labelled boundary diagnostics and accept either taint polarity while checking numeric progress and valid image serialization. The other 38 have a fixed URL expectation.

There are no support guards or skips. Every animated sample checks that its effect exists, its progress is exact, and its computed numeric value equals the weighted sum. Each uses a new target. Endpoints are `initial` (clean 12) and explicit `inherit` (parent attr-derived 8); this avoids unresolved attr()/var() keyframe conversion and equal-payload endpoint/base invalidation. No image download is required. Root owns the browser execution and source/binary pinning; this directory contains no browser execution receipt.

For a necessary landing WPT after reproduction, the two interior clean-to-tainted samples plus direct/clean/static calibrations are sufficient to expose first-operand-only metadata. Reverse and boundary cases can remain diagnostic coverage or be retained if independently justified. These tests do not establish standalone runtime independence of all earlier metadata fixes; the chosen providers reduce that risk, and actual calibration must decide it.

## Native hypothesis, after normative derivation

Searchfox discovery is retained in `source/searchfox.txt`. `source/value.rs` is the full frontier snapshot, SHA `b9913783537d2aba504115bd0e4cd755e5aa968365ca7342621a840cf05f754c`; byte comparison found it equal to the local source at inspection. The selected source bodies inspected were `CustomAnimatedValue::animate`, `Value<Component>::animate`, its component/list enum and providers, `CustomAnimatedValue::from_declaration`/`from_computed`/`to_declaration`, and registered uncompute/serialization helpers.

`CustomAnimatedValue::animate` preserves the name and delegates through the optional value. `Value::animate` combines the payload using the requested procedure, then copies URL data and attribute taint only from `self`. Therefore a successful clean-first/tainted-second numeric combination predicts lost provenance. Tainted-first cases predict retention. Exact endpoint dispatch may bypass or specialize interpolation, so the source hypothesis does not substitute for boundary measurements. This audit does not extract or execute the full segment/effect stack, generated derives, optional arithmetic provider, map publication, or substitution consumer.

The narrow prospective correction is preserving both contributing operands' attribute provenance on successful arithmetic combination. No native patch is supplied: progress-boundary and addition policy require separate review if the repair touches all procedures. Failed/discrete combinations and URL-data selection must remain distinct contracts.

## Prior art and negative scope

The current Values 5 source links the retained WPT `attr-security-transition-interpolated.html`. [WPT PR 61421](https://github.com/web-platform-tests/wpt/pull/61421), merged July 20, 2026, imported a Chromium correction for interpolable custom-property attr-taint (Chromium issue 517746687 / change 8102417). `prior/` retains the primary test and PR metadata. There is no novelty claim.

That test uses `steps(1,start)` and `if(style())` with a URL. Its three assertions do not independently calibrate a clean supported observer or confirm transition existence. It is useful prior art, but a pass alone does not establish the broader provenance contract. Our observer avoids `if()` and checks actual sampling.

Not covered: transition creation/retention equality, raw attribute keyframe computation, base-cache invalidation, add/accumulate native ordering, extrapolation, lists, multiple effects, animation taint, numeric IEEE corner cases, URL-data equivalence, or a universal Lean/native refinement. No implementation or WPT tree was changed. A speculative static prediction is not recorded as a bug.
