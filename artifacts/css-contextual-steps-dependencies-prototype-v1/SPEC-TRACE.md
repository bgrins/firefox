# API context remains an activation blocker

The current Web Animations update-timing algorithm checks the easing-function grammar and assigns the result. Its parsing entry does not supply an element. The separate compute-a-property-value algorithm takes an animation target; the timing-dictionary parsing algorithm does not invoke it. The captured predecessor contains the current normative HTML and validated anchors.

[Issue 13853](https://github.com/w3c/csswg-drafts/issues/13853) resolved to reject string/Typed OM values requiring an element for range offsets. Its discussion suggests extending the idea, but the captured 25 comments do not explicitly mention easing or steps. [WPT PR 62178](https://github.com/web-platform-tests/wpt/pull/62178) is range-offset evidence, not easing coverage.

The direct follow-up is [issue 14246](https://github.com/w3c/csswg-drafts/issues/14246), explicitly proposing restrictions on easing parsed from EffectTiming/OptionalEffectTiming. It cites update-timing and contextual linear() expressions. At capture it is OPEN, with one supportive comment and no resolution. [Issue 10853](https://github.com/w3c/csswg-drafts/issues/10853) discusses general context outside ordinary styles but does not supply an adopted easing algorithm.

Verdict: INCONCLUSIVE for the complete normative API easing-context policy. The range resolution cannot be silently generalized into an implemented easing requirement. The parser guard remains; this proposal does not activate contextual WAAPI easing or choose a default context.

CSS keyframe declarations have a style context, but animated self-dependency still needs an explicit ordering policy. The six draft tests use independently specified font/root/container/viewport contexts or a script override. The separate self-font observation has no conformance oracle.
