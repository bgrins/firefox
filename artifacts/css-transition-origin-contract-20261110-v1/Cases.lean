import Laws
import Fixtures

namespace TransitionOrigin.Cases

theorem delayed_joint_premises : delayed.registered = true ∧ delayed.current = true ∧
    delayed.inEffect = false ∧ (∀ property, delayed.sample property = none) ∧ Coherent delayed := by
  refine ⟨rfl, rfl, rfl, ?_, ?_⟩
  · intro property; rfl
  · constructor
    · intro _; exact Or.inl rfl
    · intro _ property; rfl

theorem transition_only : style registeredPolicy [transition] = .transitionSample := by decide
theorem source_shaped_change : style registeredPolicy [transition, delayed] = .important := by decide
theorem source_shaped_noninterference_fails :
    style registeredPolicy [transition, delayed] ≠ style registeredPolicy [transition] := by decide
theorem proposed_preserves : style inEffectPolicy [transition, delayed] = .transitionSample := by decide
theorem cancel_restores : style registeredPolicy [transition, cancelled] = .transitionSample := by decide
theorem active_overlap : style inEffectPolicy [transition, active] = .important := by decide

theorem unchanged_composited_value :
    composite replace .opacity .important [transition, delayed] =
      composite replace .opacity .important [transition] := by decide

theorem changed_origin_only :
    selectOrigin registeredPolicy .opacity [transition] = some .transition ∧
    selectOrigin registeredPolicy .opacity [transition, delayed] = some .animation := by decide

theorem guard_is_separate :
    compositorGuardMask .opacity [transition] = false ∧
    compositorGuardMask .opacity [transition, delayed] = true ∧
    hasClass inEffectPolicy .opacity .animation [transition, delayed] = false := by decide

theorem no_sample_does_not_imply_off :
    emptyInEffect.inEffect = true ∧ (∀ property, emptyInEffect.sample property = none) ∧
    style inEffectPolicy [transition, emptyInEffect] ≠ style inEffectPolicy [transition] := by
  refine ⟨rfl, ?_, ?_⟩
  · intro property; rfl
  · decide

theorem no_important_no_visible_change :
    render registeredPolicy replace .opacity .ordinary .ordinary none [transition, delayed] =
      render registeredPolicy replace .opacity .ordinary .ordinary none [transition] := by decide

theorem unrelated_property_no_change : style registeredPolicy [transition, unrelated] = .transitionSample := by decide
theorem empty_sample_no_insertion : insertion registeredPolicy replace .opacity .ordinary [delayed] = none := by decide

def observations : List (String × Bool) := [
  ("transition-only", decide (style registeredPolicy [transition] = .transitionSample)),
  ("registered-delayed-origin-change", decide (style registeredPolicy [transition, delayed] = .important)),
  ("proposed-delayed-unchanged", decide (style inEffectPolicy [transition, delayed] = .transitionSample)),
  ("cancel-restores", decide (style registeredPolicy [transition, cancelled] = .transitionSample)),
  ("active-overlap-control", decide (style inEffectPolicy [transition, active] = .important)),
  ("composite-unchanged", decide (composite replace .opacity .important [transition, delayed] = some .transitionSample)),
  ("registered-guard-retained", compositorGuardMask .opacity [transition, delayed]),
  ("composition-mask-excludes-delayed", !(hasClass inEffectPolicy .opacity .animation [transition, delayed])),
  ("absent-sample-alone-insufficient", decide (style inEffectPolicy [transition, emptyInEffect] = .important)),
  ("unrelated-property", decide (style registeredPolicy [transition, unrelated] = .transitionSample)),
  ("only-delayed-no-insertion", decide (insertion registeredPolicy replace .opacity .ordinary [delayed] = none)),
  ("positive-rate-before-phase-current", delayed.current),
  ("positive-rate-before-phase-off", !delayed.inEffect)
]

end TransitionOrigin.Cases
