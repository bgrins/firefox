import Model

namespace CssAnimationTaint

theorem available_some (destination binding value) :
    available destination binding = some value ↔
      Allowed destination binding ∧ binding.value = some value := by
  cases destination <;> cases binding with
  | mk contents tainted => cases tainted <;> simp [available, Allowed]

theorem available_none (destination binding) :
    available destination binding = none ↔
      ¬ Allowed destination binding ∨ binding.value = none := by
  cases destination <;> cases binding with
  | mk contents tainted => cases tainted <;> simp [available, Allowed]

theorem derives_evaluate {environment destination expression result}
    (derivation : Derives environment destination expression result) :
    evaluate environment destination expression = result := by
  induction derivation with
  | literal value => rfl
  | hit name fallback value permitted present =>
    cases fallback <;> simp [evaluate, (available_some _ _ _).mpr ⟨permitted, present⟩]
  | missing name unavailable =>
    simp [evaluate, (available_none _ _).mpr unavailable]
  | fallback name expression result unavailable nested ih =>
    simp [evaluate, (available_none _ _).mpr unavailable, ih]

theorem evaluate_derives (environment destination expression) :
    Derives environment destination expression (evaluate environment destination expression) := by
  cases expression with
  | literal value => exact .literal value
  | reference name fallback =>
    cases lookup : available destination (environment name) with
    | some value =>
      obtain ⟨permitted, present⟩ := (available_some _ _ _).mp lookup
      cases fallback <;> simpa [evaluate, lookup] using Derives.hit name _ value permitted present
    | none =>
      have unavailable := (available_none _ _).mp lookup
      cases fallback with
      | none => simpa [evaluate, lookup] using Derives.missing name unavailable
      | some expression =>
        simpa [evaluate, lookup] using
          Derives.fallback name expression (evaluate environment destination expression)
            unavailable (evaluate_derives environment destination expression)

termination_by expression

theorem evaluation_iff (environment destination expression result) :
    evaluate environment destination expression = result ↔
      Derives environment destination expression result := by
  constructor
  · intro equality
    rw [← equality]
    exact evaluate_derives _ _ _
  · exact derives_evaluate

theorem deterministic {environment destination expression left right}
    (leftDerivation : Derives environment destination expression left)
    (rightDerivation : Derives environment destination expression right) : left = right := by
  exact (derives_evaluate leftDerivation).symm.trans (derives_evaluate rightDerivation)

theorem selected_reference (environment destination name fallback value)
    (permitted : Allowed destination (environment name))
    (present : (environment name).value = some value) :
    evaluate environment destination (.reference name fallback) = ⟨some value, [name]⟩ := by
  exact derives_evaluate (.hit name fallback value permitted present)

theorem unused_fallback (environment destination name first second value)
    (permitted : Allowed destination (environment name))
    (present : (environment name).value = some value) :
    evaluate environment destination (.reference name first) =
      evaluate environment destination (.reference name second) := by
  rw [selected_reference _ _ _ _ _ permitted present,
    selected_reference _ _ _ _ _ permitted present]

theorem blocked_fallback (environment name expression)
    (tainted : (environment name).animationTainted = true) :
    evaluate environment .nonanimatable (.reference name (some expression)) =
      let result := evaluate environment .nonanimatable expression
      ⟨result.value, name :: result.reads⟩ := by
  simp [evaluate, available, tainted]

theorem blocked_missing (environment name)
    (tainted : (environment name).animationTainted = true) :
    evaluate environment .nonanimatable (.reference name none) = ⟨none, [name]⟩ := by
  simp [evaluate, available, tainted]

theorem animatable_preserves (environment name fallback value)
    (present : (environment name).value = some value) :
    evaluate environment .animatable (.reference name fallback) = ⟨some value, [name]⟩ := by
  exact selected_reference _ _ _ _ _ (Or.inr rfl) present

theorem attribute_payload_preserved (environment destination name fallback value)
    (permitted : Allowed destination (environment name))
    (present : (environment name).value = some value) :
    (evaluate environment destination (.reference name fallback)).value = some value := by
  rw [selected_reference _ _ _ _ _ permitted present]

theorem attribute_taint_does_not_block (destination tokens attributeFlag) :
    available destination ⟨some ⟨tokens, attributeFlag⟩, false⟩ = some ⟨tokens, attributeFlag⟩ := by
  simp [available]

theorem selected_fallback_failure (environment destination name fallback)
    (unavailable : ¬ Allowed destination (environment name) ∨ (environment name).value = none)
    (failure : (evaluate environment destination fallback).value = none) :
    (evaluate environment destination (.reference name (some fallback))).value = none := by
  simp [evaluate, (available_none _ _).mpr unavailable, failure]

theorem equal_tokens_different_animation_taint (value) :
    available .nonanimatable ⟨some value, false⟩ ≠
      available .nonanimatable ⟨some value, true⟩ := by
  simp [available]

theorem equal_tokens_animatable_same (value firstTaint secondTaint) :
    available .animatable ⟨some value, firstTaint⟩ =
      available .animatable ⟨some value, secondTaint⟩ := by
  simp [available]

theorem infectious_dependency {seed references name dependency}
    (edge : references name dependency) (tainted : Infectious seed references dependency) :
    Infectious seed references name := by
  exact .reference name dependency edge tainted

theorem infectious_least {seed references} {closed : Nat → Prop}
    (seeds : ∀ name, seed name → closed name)
    (dependencies : ∀ name dependency, references name dependency → closed dependency → closed name)
    {name} (tainted : Infectious seed references name) : closed name := by
  induction tainted with
  | seed name premise => exact seeds name premise
  | reference name dependency edge prior ih => exact dependencies name dependency edge ih

theorem infectious_monotone {seed otherSeed references otherReferences}
    (seeds : ∀ name, seed name → otherSeed name)
    (edges : ∀ name dependency, references name dependency → otherReferences name dependency)
    {name} (tainted : Infectious seed references name) : Infectious otherSeed otherReferences name := by
  apply infectious_least (closed := Infectious otherSeed otherReferences) _ _ tainted
  · intro value premise
    exact .seed value (seeds value premise)
  · intro value dependency edge prior
    exact .reference value dependency (edges value dependency edge) prior

theorem infectious_binding {environment : Environment} {seed references}
    (seeds : ∀ name, seed name → (environment name).animationTainted = true)
    (dependencies : ∀ name dependency, references name dependency →
      (environment dependency).animationTainted = true → (environment name).animationTainted = true)
    {name} (tainted : Infectious seed references name) :
    (environment name).animationTainted = true := by
  exact infectious_least seeds dependencies tainted

theorem infectious_source_selects_fallback {environment : Environment} {seed references}
    (seeds : ∀ name, seed name → (environment name).animationTainted = true)
    (dependencies : ∀ name dependency, references name dependency →
      (environment dependency).animationTainted = true → (environment name).animationTainted = true)
    {name} (tainted : Infectious seed references name) (expression) :
    evaluate environment .nonanimatable (.reference name (some expression)) =
      let result := evaluate environment .nonanimatable expression
      ⟨result.value, name :: result.reads⟩ := by
  exact blocked_fallback _ _ _ (infectious_binding seeds dependencies tainted)

end CssAnimationTaint
