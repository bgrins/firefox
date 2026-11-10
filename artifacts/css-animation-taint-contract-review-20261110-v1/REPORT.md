# Animation-taint contract review

Frozen 2026-11-10. Research only: no native changes, live WPT installation, build, browser execution, or commit by this review.

**Decision:** the same-element, actively animated custom-property case supports an independently reviewable partial conformance repair. The destination substitution rule is settled; complete taint acquisition is not. Do not present a sampled-value flag as a complete implementation of the current property-name wording, and do not silently clear inherited taint to implement a pending proposal. There is no novelty claim or new fixed-bug count here.

## Contract boundary

| Area | Current requirement or evidence | Classification and repair consequence |
| --- | --- | --- |
| Source | Variables 1 associates taint with custom properties used in `@keyframes`. | Normative wording; an actually applied CSS-keyframe value is the common minimum across the property-name and value interpretations. |
| Destination | A tainted source used in a nonanimatable property becomes guaranteed-invalid for that substitution. | Normative. Enforce at substitution with destination context, not by destroying the custom property's computed value. |
| Fallback | Guaranteed-invalid selects the supplied fallback; otherwise it is not evaluated. | Normative selection order. A clean fallback can recover from a rejected tainted source. |
| Propagation | References to tainted custom properties infect other custom properties. | Normative general rule. Selected same-element chains must preserve taint; unused-reference details need a separate policy decision. |
| Scope and lifetime | The definition does not give an operational registry, owner scope, or removal algorithm. | Do not infer document-global permanence, cross-shadow propagation, or cancellation cleanup from a boolean alone. |
| Inheritance | Current text supplies no inheritance-clearing exception. | Current-spec expectation favors retention; removing it is an open proposal, not adopted normative text. |
| Representation | Bit placement, map deduplication, serialization metadata, cache invalidation. | Implementation choices, provided observable semantics survive all paths. Attribute taint must remain independent. |

The normative source is [Variables 1: defining variables](https://drafts.csswg.org/css-variables-1/#defining-variables) and [replacing var()](https://drafts.csswg.org/css-variables-1/#replace-a-var-function). The broader nonanimatable restriction is already present in the [2021 CRD](https://www.w3.org/TR/2021/CRD-css-variables-1-20211111/#using-variables); the preceding renewal-gates capsule preserves the dated snapshots. Both [scroll-timeline-name](https://drafts.csswg.org/scroll-animations-1/#scroll-timeline-name) and [timeline-scope](https://drafts.csswg.org/scroll-animations-1/#timeline-scope) are expressly nonanimatable. Do not use a hand-maintained list limited to `animation-*` as the destination definition.

## Pending policy and registered properties

[CSSWG issue 13933](https://github.com/w3c/csswg-drafts/issues/13933) remains open in the freshly fetched API record, last updated May 20, 2026. It proposes removing taint on inheritance. The author explicitly distinguishes the current property-name wording from tainting a value supplied by an active animation. The [Blink implementer's response](https://github.com/w3c/csswg-drafts/issues/13933#issuecomment-4496486409) describes value taint and a clean winning `!important` declaration. That is implementation testimony, not a CSSWG resolution. It exposes meaningful acquisition-policy discriminators: unused keyframes, another element sharing the name, a losing animated declaration, and the point where animation stops contributing. These must remain visible in any repair description.

[CSSWG issue 11102](https://github.com/w3c/csswg-drafts/issues/11102) is also open. It concerns whether animated custom-property references suppress transitions and records Firefox/Chromium differences. Do not equate destination blocking with transition-trigger suppression, and do not mark every transition sample animation-tainted merely because animations and transitions share a native helper. The CSS-keyframes wording also does not by itself settle arbitrary Web Animations API effects; those need their own contract.

The current [Properties and Values API ED, section 2](https://drafts.css-houdini.org/css-properties-values-api-1/#behavior-of-custom-properties) makes registered properties follow ordinary custom-property behavior except for the specified differences. Its [animation section](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior-of-custom-properties) changes interpolation, and [substitution section](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) substitutes serialized computed values. No animation-taint exemption was found in this complete snapshot. Therefore excluding all registered properties is unsupported by this review. Required follow-up includes registered `*` and typed identifier sources, both inheritance settings, and registered/unregistered aliases. The measured fixture covers none of these. Serialization describes tokens, not permission to erase semantic provenance.

The older cached `registration-substitution.md` comes from a published TR snapshot and contains a fallback-syntax restriction absent from the current ED. It is retained as discovery history, not the authority for current registered fallback behavior. The correct current animation anchor is `animation-behavior-of-custom-properties`; failed anchor/domain queries are retained as failures.

## Fallback distinction for the proof

With taint supplied as input, the substitution proof can establish:

1. A valid clean selection does not evaluate its fallback, even when that fallback contains a reference to a tainted property.
2. A tainted selection in a nonanimatable destination is rejected before fallback selection; a clean literal fallback is usable.
3. If the selected fallback itself references another tainted property, that nested substitution must apply the destination restriction too; another nested fallback can recover.
4. The same source remains usable in an animatable destination, absent another independent invalidity.

These are evaluation claims. They do **not** establish that `--alias: var(--clean, var(--animated))` itself is untainted. The separate infectious-reference prose does not expressly say whether a reference in an unused fallback counts. A proof that obtains cleanliness solely by skipping fallback evaluation would silently add a selected-branch-only acquisition policy. Parameterize acquisition or leave this case outside the theorem. Do not import attribute-taint rules or dependency-cycle edge rules as if they settled animation-taint acquisition.

## Runtime evidence and prior coverage

The parent-owned calibration capsule supplies identical local-build and installed Nightly results: two direct timeline substitutions fail, the ordinary-variable control passes, and the inherited `animation-name` assertion fails. Harness status is OK. The source animation is paused at computed progress 0.5 with its animated value observed before the assertions. The inherited callback stops at `animation-name`; its later timeline assertions were not observed. This is one unfixed implementation lead with three demonstrated manifestations, not three separately established bugs. Installed browser: Nightly 162.0a1, build 20261109214446; scroll-driven animations explicitly enabled.

Targeted Searchfox discovery, canonical WPT directory listings, and six revision-pinned local WPT/metadata files were inspected:

| Existing coverage | What it does and does not establish |
| --- | --- |
| `variable-animation-from-to.html` | Checks custom-value animation and substitution into animatable `color`; not rejection in nonanimatable destinations. Metadata lists a conditional Windows harness outcome, not a taint bug. |
| `variable-animation-guaranteed-invalid.html` | Checks animation through the guaranteed-invalid value and resulting `width`; no taint/fallback gate assertion. |
| `at-property-animation.html` | Checks registered animation, registration changes, aliases, and inherited keyframe inputs. Its two `inherit` failure annotations point to [bug 2030129](https://bugzilla.mozilla.org/show_bug.cgi?id=2030129), an open reset-property keyframe-inheritance issue. They do not identify this destination gate. |
| `variable-animation-substitute-within-keyframe.html.ini` | Conditional Android/fission timeout metadata. [Bug 1402219](https://bugzilla.mozilla.org/show_bug.cgi?id=1402219) documents the earlier within-keyframe variable problem; [bug 1846516 comment 12](https://bugzilla.mozilla.org/show_bug.cgi?id=1846516#c12) revisits it while adding custom-property animation. |

Searches found attribute-taint tests and an unrelated visited-property WPT sync task, [bug 2087576](https://bugzilla.mozilla.org/show_bug.cgi?id=2087576), rather than a confirmed duplicate of this case. Keyword and directory searches are incomplete coverage evidence: absence of a matching title or literal does not establish novelty. No existing test was rerun by this review.

## Practical next repair

Implement and prove the destination guard with supplied provenance first. Connect the guaranteed active CSS-keyframe source and selected same-element aliases, covering typed publication paths as well as token payloads. Keep provenance changes observable even when payloads are equal. Pair the partial repair with direct positive/negative WPT assertions and explicitly list acquisition cases it does not implement. This improves a necessary subset without claiming to resolve issue 13933.

A landable patch still needs reviewer agreement on its stated incomplete boundary. If implementation changes inheritance, losing declarations, transitions, or inactive-name handling as a side effect, those are observable policy choices and need explicit tests and rationale; they cannot be hidden as storage details. Do not promise that the inherited calibration will pass from a direct-only patch. Full conformance needs an acquisition contract or CSSWG clarification beyond this bounded review. The native seam and test matrix belong to the parallel repair-design capsule.

## Reproduction and provenance

`NETWORK-SOURCES.json` and the other discovery/source receipts preserve exact requests, exit statuses, fetched timestamps, and hashes. Primary HTML/API bodies are stored locally. `LOCAL-WPT-SOURCES.json` pins test bytes to local source revision `4cda7885b649deba826da5566940cb32833c9f14`; Searchfox output is discovery, not a replacement for that revision. `INPUTS.json` pins copied runtime summaries and their parent-capsule origin. `FILES.json` freezes this capsule; `python3 check.py` validates every file and the six local Git objects without network access. A successful check authenticates evidence, not the truth or completeness of the prose-to-model interpretation.
