# Registered invalid-keyframe discriminator

Preparation only; no fixture or browser result. This plan is separate from the minimal V3 producer patch and must not imply that an invalid registered keyframe contributes an Animations-origin value.

Register --v with syntax `<custom-ident>`, inherits=false and initial horizontal-tb. Set ordinary --v:vertical-rl and writing-mode:var(--v, vertical-lr). These initial, underlying and fallback keywords are pairwise distinct. Use a fixed2s paused CSS driver and assign750ms only after readiness. Register in each isolated document; successful CSS.registerProperty plus a separate non-animated multi-ident/initial calibration proves effective registration.

All arms also include the same independent constant `opacity: 1` in both keyframe endpoints. That keeps a valid CSS animation available for readiness/time calibration even if the custom declaration is rejected. Record opacity only after the first sink samples. The opacity driver does not prove that --v contributes.

Three matched arms:

| Arm | Keyframe --v | Sink |
| --- | --- | --- |
| Invalid typed input | `one two` at both endpoints | var(--v, vertical-lr) |
| Valid control | `vertical-rl` at both endpoints | var(--v, vertical-lr) |
| Literal control | Same valid driver | literal vertical-lr |

Do not assert the invalid arm's computed custom value in advance. Capture sink first and three passive frames, then computed --v, timing, membership and effect identities. Change ordinary --v from vertical-rl to vertical-lr and repeat identical sampling before cancellation or other effect mutation. Optionally cancel after both phases for a separately labeled ordinary-value calibration; cancellation must not precede the primary records.

For the invalid arm, a source value horizontal-tb supports selecting the registered initial value; vertical-rl followed by vertical-lr supports following the ordinary underlying declaration (for example a dropped or neutral keyframe). The source trajectory, not the sink alone, distinguishes these. A sink vertical-lr could be the var fallback or the post-mutation underlying value, so never infer a rejection path from that single keyword. Animation object existence alone also cannot prove that its invalid custom declaration contributed; valid-control behavior and source response provide the needed distinction. An implementation might resolve invalid registered input before producing an animation value, outside the new producer's scope.

The valid arm retains animated vertical-rl after ordinary mutation while the literal arm remains vertical-lr. These establish the driver and sink controls. Keep effective registration, observation completeness and policy predictions separate. A fallback on invalid input is not automatically required by the active-value proposal: whether selected initial/inherited defaults acquire rejected-input or property-name taint remains a spec/policy obligation. Record the actual result before proposing propagation changes.

No change to sealed fixtures, current native owner, producer bytes, source tree, browser, Git/index or canonical controls is made. This plan has no execution gate and is not acceptance evidence.
