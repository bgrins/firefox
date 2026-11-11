import Model

namespace TransitionOrigin

theorem hasClass_spec (policy : Policy P V) (property : P) (origin : Origin) (effects : List (Effect P V)) :
    hasClass policy property origin effects = true ↔ HasClass policy property origin effects := by
  simp [hasClass, HasClass, eligible, Bool.and_eq_true, and_assoc]

theorem selectOrigin_spec (policy : Policy P V) (property : P) (effects : List (Effect P V)) (origin) :
    selectOrigin policy property effects = origin ↔ Selected policy property effects origin := by
  cases ha : hasClass policy property .animation effects <;>
    cases ht : hasClass policy property .transition effects <;>
    cases origin with
    | none => simp [selectOrigin, Selected, ← hasClass_spec, ha, ht]
    | some origin => cases origin <;> simp [selectOrigin, Selected, ← hasClass_spec, ha, ht]

theorem hasClass_insert_excluded (policy : Policy P V) (property : P) (origin : Origin)
    (before after : List (Effect P V)) (effect : Effect P V)
    (excluded : eligible policy property effect = false) :
    hasClass policy property origin (before ++ effect :: after) = hasClass policy property origin (before ++ after) := by
  simp [hasClass, List.any_append, excluded]

theorem selectOrigin_insert_excluded (policy : Policy P V) (property : P)
    (before after : List (Effect P V)) (effect : Effect P V)
    (excluded : eligible policy property effect = false) :
    selectOrigin policy property (before ++ effect :: after) = selectOrigin policy property (before ++ after) := by
  simp only [selectOrigin, hasClass_insert_excluded policy property _ before after effect excluded]

theorem off_excluded (property : P) (effect : Effect P V) (off : effect.inEffect = false) :
    eligible inEffectPolicy property effect = false := by
  simp [eligible, inEffectPolicy, off]

theorem sampleFor_absent (property : P) (effect : Effect P V) (absent : effect.sample property = none) :
    sampleFor property effect = none := by simp [sampleFor, absent]

theorem composite_insert_absent (combine : V → V → V) (property : P) (underlying : V)
    (before after : List (Effect P V)) (effect : Effect P V) (absent : effect.sample property = none) :
    composite combine property underlying (before ++ effect :: after) =
      composite combine property underlying (before ++ after) := by
  simp [composite, List.foldl_append, step, sampleFor_absent property effect absent]

theorem insertion_noninterference (policy : Policy P V) (combine : V → V → V) (property : P) (underlying : V)
    (before after : List (Effect P V)) (effect : Effect P V)
    (excluded : eligible policy property effect = false) (absent : effect.sample property = none) :
    insertion policy combine property underlying (before ++ effect :: after) =
      insertion policy combine property underlying (before ++ after) := by
  simp only [insertion, selectOrigin_insert_excluded policy property before after effect excluded,
    composite_insert_absent combine property underlying before after effect absent]

theorem inEffect_noninterference (combine : V → V → V) (property : P) (underlying ordinary : V)
    (important : Option V) (before after : List (Effect P V)) (effect : Effect P V)
    (off : effect.inEffect = false) (absent : effect.sample property = none) :
    render inEffectPolicy combine property underlying ordinary important (before ++ effect :: after) =
      render inEffectPolicy combine property underlying ordinary important (before ++ after) := by
  simp only [render, insertion_noninterference inEffectPolicy combine property underlying before after effect
    (off_excluded property effect off) absent]

theorem coherent_off_noninterference (combine : V → V → V) (property : P) (underlying ordinary : V)
    (important : Option V) (before after : List (Effect P V)) (effect : Effect P V)
    (coherent : Coherent effect) (off : effect.inEffect = false) :
    render inEffectPolicy combine property underlying ordinary important (before ++ effect :: after) =
      render inEffectPolicy combine property underlying ordinary important (before ++ after) :=
  inEffect_noninterference combine property underlying ordinary important before after effect off (coherent.2 off property)

theorem transition_over_important (ordinary value important : V) :
    cascade ordinary (some important) (some (.transition, value)) = value := rfl

theorem important_over_animation (ordinary value important : V) :
    cascade ordinary (some important) (some (.animation, value)) = important := rfl

theorem no_samples_no_insertion (policy : Policy P V) (combine : V → V → V) (property : P) (underlying : V) :
    insertion policy combine property underlying [] = none := rfl

theorem composite_all_absent (combine : V → V → V) (property : P) (underlying : V)
    (effects : List (Effect P V)) (absent : ∀ effect ∈ effects, effect.sample property = none) :
    composite combine property underlying effects = none := by
  induction effects with
  | nil => rfl
  | cons effect rest ih =>
    have same := composite_insert_absent combine property underlying [] rest effect
      (absent effect (by simp))
    simp only [List.nil_append] at same
    rw [same]
    exact ih (by intro member h; exact absent member (by simp [h]))

theorem insertion_all_absent (policy : Policy P V) (combine : V → V → V) (property : P) (underlying : V)
    (effects : List (Effect P V)) (absent : ∀ effect ∈ effects, effect.sample property = none) :
    insertion policy combine property underlying effects = none := by
  simp [insertion, composite_all_absent combine property underlying effects absent]

theorem compositorGuardMask_spec (property : P) (effects : List (Effect P V)) :
    compositorGuardMask property effects = true ↔
      ∃ effect ∈ effects, effect.registered = true ∧ effect.targets property = true ∧ effect.origin = .animation := by
  simp [compositorGuardMask, hasClass_spec, HasClass, registeredPolicy]

end TransitionOrigin
