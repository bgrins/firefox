# Combined composer and transient recascade probe

The copied temporary driver calls the reviewed request-local composer and passes its two maps into the reviewed transient pseudo recascade. It changes no composer, recascade or public CSSOM implementation. The four-file patch adds one XPIDL method, its native diagnostic, one manifest entry and one fixture, over transient-recascade source v3. Native compilation and browser execution remain unrun. No new Firefox bug or completed missing-pseudo repair is claimed.

## Independent contract

[Web Animations applying the composited result](https://drafts.csswg.org/web-animations-1/#applying-the-composited-result) chooses the insertion origin from the highest-order effect in the property's stack. [CSS Transitions 2 composite order](https://drafts.csswg.org/css-transitions-2/#animation-composite-order) places transitions before CSS animations and ordinary WAAPI animations; [its cascade-level rule](https://drafts.csswg.org/css-transitions-2/#animation-cascade-level) distinguishes transitions still associated with an owning element. Therefore active overlap can correctly yield one Animation-origin result, overridden by important author declarations. A transition-only stack instead beats those declarations.

For the before-phase/no-fill probe, [the effect-value algorithm](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-effect) aborts when progress is unresolved. Inferring that this non-sampling effect must not select the stack's origin is plausible, but the stack-order algorithm does not explicitly state that filter. The combining-effects introduction is non-normative and is not treated as a binding premise. These three assertions are explicitly classified as interpretation probes; a differential may require CSSWG clarification. Their failure alone is not sufficient for bug filing or a production patch.

## Native trace and hypothesis

The exact implementation inputs are pinned at ec467 in SOURCES.json. Searchfox discovery is retained; initial restricted-network failures are separate from the successful discovery files. CSSTransition::CascadeLevel uses IsTiedToMarkup. KeyframeEffect::UpdateTargetRegistration retains relevant effects, including IsCurrent without IsInEffect; AnimationEffect::IsCurrent includes a positive-rate before phase. The fixture verifies native transition level and current effect registration instead of assuming that instanceof CSSTransition settles those facts after retargeting.

The proposed composer builds animationProperties from every prepared animation-level property, then skips null-progress effects only during sampling. Thus a registered before-phase/no-fill animation can select the Animation output map for a transition contribution despite supplying no sample. The renderer's UpdateCascadeResults also unions all registered property sets, and ComposeSortedEffects applies the union as complementary skip masks. That renderer resemblance is context, not an independent oracle and not evidence that an unmodified browser has the same observed failure. The existing source comment about bug 1606176 concerns stale cascade information; this capsule makes no claim of novelty or equivalence to that bug.

The pinned applying-the-composited-result WPT checks a finished non-filling animation but has no transition/important overlap in that file. This is a scoped coverage observation, not a full WPT or bug inventory.

| Case | Stack/map prediction | Returned value |
| --- | --- | --- |
| Fixed px replacement | Animation 50px | 50px |
| Implicit start, base 10px and final 100px | Animation 55px | 55px |
| Replace 50px then add 20px | Animation 70px | 70px |
| Transition-only, important base 30px | Transition 50px; no Animation value | 50px |
| Active replacement overlap, important base 30px | Animation 20px; no Transition value | 30px |
| Active additive overlap, normal base 10px | Animation 70px; no Transition value | 70px |
| Current before-phase/no-fill overlap, important base 30px | Probe: Transition 50px; no Animation value | Probe: 50px |

Current composer source predicts Animation 50px, no Transition value and final 30px for the final row. This is a source prediction, not an executed result. The fixture records both maps and final style so a failed value can be separated from registration, origin-routing and cascade behavior.

## Scope, fixtures and checks

Only fixed physical margin-left endpoints and linear timing are used. No animated custom properties, font or writing-mode providers, relative/logical endpoints, progress timelines or named ranges occur. Under these deliberately stable conditions the raw pseudo style can supply both the unanimated base and endpoint-conversion context. This is a fixture premise, not a general base-to-provider equivalence. Authored bases are checked before effects are installed; selected returned raw bases are checked again. The combined driver uses FLUSH_NONE after fixture setup, completes lazy style resolution before composition, and passes explicit primary/pseudo styles to recascade. Freshness of that context remains a caller premise.

The native diagnostic copies the existing query driver's captured state and output-ownership checks, adds in-effect counts, recascade output, pseudo identity and origin-style pointer observation. QUERY-DRIVER-DELTA.patch isolates those additions. The state check covers the recorded fields and effect-set membership only; it does not prove whole-renderer purity or arbitrary-reentrancy safety. It makes no history-dependent/visited observation.

ASSERTIONS.json contains 122 exact labels in five tasks: 33 setup checks, 86 other checks and three explicitly marked interpretation probes. Native-level/in-effect checks distinguish failed setup from semantic outcomes. The source checker authenticates seven Git inputs and three prerequisite files, verifies patch replay/reversal, parses XPIDL/TOML, checks inert JS syntax, scoped ESLint with import-globals disabled, Prettier idempotence and the AST-derived inventory. These checks pass. C++ additions were formatted with clang-format 22.1.8 and the real source filename. Full XPIDL/binding compilation and installed lint remain runtime gates.

Root can adapt the accepted reversible transaction after source review. Keep existing query208 and recascade100 as independent regressions and retain the ordinary WPT130 vector. The new fixture should be reported as an investigation: all 119 non-probe assertions and setup must pass before interpreting the three probe results. Preserve failed probe values and exact callbacks; do not silently convert them into acceptance expectations or count a new bug. Public CSSOM provider coherence, generation/cache/admission, privacy and the final debug transform/change-hint gate remain open.
