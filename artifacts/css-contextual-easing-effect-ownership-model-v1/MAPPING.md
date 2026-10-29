# Mapping and prior coverage

Fresh primary reads on 2026-10-29 confirm the successful-only precedence rule in [CSS Animations2](https://drafts.csswg.org/css-animations-2/#animations), including its last-matching-rule removal exception. [Web Animations setKeyframes](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-setkeyframes) leaves effect keyframes unchanged when argument processing throws. These are manual anchored reads, not automated exhaustive call-chain verification. The historical specification/source trace remains pinned in `css-contextual-easing-js-override-plan-v1`.

| Model boundary | Native/case correspondence and limit |
|---|---|
| Successful setKeyframes event | CSSAnimationKeyframeEffect::SetKeyframes processes arguments before setting mIgnoreKeyframesGeneration and CSSAnimationProperties::Keyframes. The event assumes processing already succeeded. |
| Rejected event | The ErrorResult failure return precedes those mutations. The model excludes reentrant author code during argument conversion. |
| Script-owned refresh shielding | UpdateOldAnimationPropertiesWithNew checks PropertiesOverridenByJS before replacing keyframes and the default timing function. Other timing properties have independent override bits and are not shielded by this theorem. |
| Current selection/root evaluation | Complete expressions and declaration/root identities remain explicit inputs. Actual selected-rule scope transport and context construction are external obligations. |
| Independent transition capture | Reuses the restricted start/capture interpretation from Dependency.lean. It does not prove a new transition-only invariant or native transition scheduling. |

Existing `KeyframeEffect-setKeyframes.tentative.html` covers successful calls followed by rule changes, successful calls followed by timing-function changes, and rejected calls followed by rule changes. The four contextual cases in `css-contextual-easing-js-override-plan-v1` cross sibling/font inputs with successful/rejected calls. They compare literal Steps5 override against CSS Steps3→4→3 or2→3→2 and retain animation/effect identity. This model abstracts those parameter choices; its [5] is a parameter token, not the rendered opacity0.6. The model's changing selected root and declaration is a separate theoretical witness, not an assertion that those four browser cases exercise scope changes.

The pre-existing dependency model already proves structural locality, covered-mask cache soundness, same-support/different-expression counterexamples, and restricted transition capture retention. This companion reuses that evaluator by authenticated import and adds ownership trace composition. It does not claim previously untested native behavior or unique normative coverage.

The independently prepared `css-contextual-easing-after-moves-next-step-20261029-v1.md` identifies this ownership boundary as useful and keeps the existing nineteen-case experiment unchanged. It records the four script-override cases as unexecuted; this model supplies no browser result for them. That note is pinned as ancillary provenance after run-4; no Lean source, negative control, or kernel command changed.
