# Contract mapping

| Model | Reviewed source/concept | Unproved bridge |
| --- | --- | --- |
| registered/current/inEffect | `KeyframeEffect::UpdateTargetRegistration` retains relevant effects through current OR in-effect | Owner/target/replacement validity and full registration lifecycle |
| registeredPolicy and compositorGuardMask | `EffectCompositor::UpdateCascadeResults` unions properties of registered Animation-level effects | Source-shaped abstraction, not extraction/refinement |
| selectOrigin | `ComposeSortedEffects` uses complementary origin masks; Animation-level composition can include transitions | Fixed two-class ordering and fresh masks, not generic full-stack ordering |
| absent sample | `KeyframeEffect::ComposeStyle` returns on null progress; normative effect-value step 1 aborts on unresolved iteration progress | Timing-to-progress-to-sample correspondence |
| inEffectPolicy | Proposed separate composition-origin membership | Normative interpretation remains unresolved |
| composite | Fold of supplied samples with a supplied total function | Interpolation, floats and full CSS composition |
| cascade | Transition above author-important above Animation above ordinary | Full cascade semantics |
| forwardNoFill | Positive-direction, resolved-time, no-fill snapshot | Full Web Animations timing model |

The generic theorem requires **both** policy exclusion and sample absence. The specialization obtains exclusion from the proposed policy; the coherence corollary obtains absence from an explicit premise. `emptyInEffect` prevents treating the missing converse as a theorem.

The source-shaped witness changes routing, not its interpolated value: identical symbolic transition composition moves to Animation origin and loses to important. This resembles the observed 0.5→0.8→0.5 behavior; Lean never imports those numbers or asserts their normative correctness. The model was built after that observation.

The native source and Firefox release binary are not asserted identical. Cached-mask updates, sample-time selection, compositor eligibility and endpoint-inclusive behavior remain outside the proof. The original conservative property union must remain separate from any proposed composition mask. Even the paused/nonpending case still needs a reviewed source/browser bridge; current input coherence is not a proof of arbitrary pending-time equivalence.
