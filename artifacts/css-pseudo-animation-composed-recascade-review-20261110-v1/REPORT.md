# Independent combined diagnostic source review

Ready for a bounded build and investigation, with no source blocker found. This is review of a temporary diagnostic over the existing request-local composer and transient recascade, not acceptance of a public CSSOM repair. No browser, native build, live source change or Git mutation was performed by this review.

## Authenticated scope

Independent replay authenticated all 34 SOURCE-ONLY inputs, reconstructed and reversed the four-file patch, and reproduced the exact QUERY-DRIVER-DELTA. The existing query method remains byte-identical. The captured State structure, effect-set membership check and final state comparisons remain byte-identical. The patch changes only the window-utils diagnostic, XPIDL, manifest and its fixture; production composition and recascade helpers are unchanged. AUDIT.json records these checks and scratch cleanup. The source checker also passed in a copied capsule with only its repository locator adjusted in memory; frozen files were unchanged.

The source capsule pins nsTransitionManager files, but CascadeLevel and IsTiedToMarkup are defined in CSSTransition.h. ADDITIONAL-PINS.json and the three captured native files close that narrow evidence gap without modifying the author's frozen capsule. CascadeLevel checks owning-element association, not merely the C++/JS transition class. The driver checks actual native level and IsInEffect counts after retargeting. It does not snapshot the exact owning-element identity; that stronger claim is not needed or made here.

## Composition and ownership

The driver retains strong document, element, shell, animation, effect and timeline references; rechecks document/shell identity after an optional flush; performs lazy resolution before the request-local composition; and passes the two fresh owned maps directly to transient recascade. It checks exact effect/animation membership immediately around the helper work. Raw style pointer retention, pseudo identity and absence of generated pseudo creation are observations of this diagnostic, not a proof of all renderer state neutrality.

The preexisting timing/target/range/pending/rate/level snapshot comparisons are retained through the added recascade. Captured target and pseudo are owning/coherent, but shared style/provider epochs and arbitrary reentrant mutation remain external premises. No claim is made about unrecorded property arrays, caches or all animation state. Added IsInEffect observations use the const timing path; fixed paused samples limit moving-clock ambiguity. This does not establish unrestricted accessor purity.

The fixture uses fixed physical margin-left values with linear timing and stable providers. Using raw pseudo style as both base and endpoint context is justified only for these cases. It does not close the remaining relative-value, animated-provider, named-range, public-cache, visited/privacy or debug change-hint gates.

## Independent oracles and three unresolved probes

There are exactly five tasks and 122 unique assertions: 119 non-probe checks, including 33 setup checks, plus three explicitly marked interpretation probes. Fixed replacement, implicit endpoint and additive arithmetic have independently checkable 50px, 55px and 70px results. Transition-only composition beats important author style; active WAAPI overlap selects the Animation origin, so important style wins. These distinctions follow the highest-effect class rule and transition owning-element rule, rather than the candidate's output. [Web Animations composition](https://drafts.csswg.org/web-animations-1/#applying-the-composited-result), [CSS Transitions cascade level](https://drafts.csswg.org/css-transitions-2/#animation-cascade-level).

The before-phase, positive-rate, fill:none effect is current but does not contribute a resolved sample. The effect-value abort does not by itself explicitly remove that effect from origin selection. The introductory prose is nonnormative. Consequently the three final assertions remain interpretation probes, not established conformance expectations. [Web Animations effect value](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-effect).

Source inspection confirms the request-local composer collects animation property membership before skipping null-progress samples. Its predicted result for that case is therefore Animation 50px, Transition absent, final 30px. This is a source prediction, not a measured failure or new confirmed bug. Similar renderer membership behavior cannot independently settle the normative question.

## Required execution reporting

A subsequent runner must require all 119 non-probe checks, all setup prerequisites, all five tasks and all 122 callbacks. It must separately retain each probe's status and exact message. A missing callback, premature exception, unrelated FAIL, crash or malformed lifecycle invalidates interpretation. Probe failures may affect the harness ending or process exit; any allowance must be restricted to those three classified failures, not arbitrary nonzero exits or harness errors.

Keep the existing query208, recascade100 and ordinary WPT130 gates separate. Report completed investigation and probe disagreement separately from helper acceptance; do not silently adopt the predicted outcomes as normative expectations. Native compilation and all runtime gates remain outstanding for this four-file diagnostic.
