import Std
set_option autoImplicit false

namespace ContentSizeCache

inductive Kind where
  | normal | inline | size
  deriving DecidableEq

structure Size where
  width : Int
  height : Int
  deriving DecidableEq

def inlineSize (vertical : Bool) (s : Size) : Int :=
  if vertical then s.height else s.width

abbrev sameKey (kind : Kind) (beforeVertical afterVertical : Bool)
    (before after : Size) : Prop :=
  match kind with
  | .normal => True
  | .inline => inlineSize beforeVertical before = inlineSize afterVertical after
  | .size => before = after

def trackedWidth (kind : Kind) (vertical : Bool) : Bool :=
  match kind with
  | .normal => false
  | .inline => !vertical
  | .size => true

def trackedHeight (kind : Kind) (vertical : Bool) : Bool :=
  match kind with
  | .normal => false
  | .inline => vertical
  | .size => true

def normalized (n : Int) : Option Int := if n < 0 then none else some n

def rawProjection (widthAvailable heightAvailable : Bool) (s : Size) :
    Option Int × Option Int :=
  (if widthAvailable then normalized s.width else none,
   if heightAvailable then normalized s.height else none)

def observable (kind : Kind) (vertical widthAvailable heightAvailable : Bool)
    (s : Size) : Option Int × Option Int :=
  rawProjection (widthAvailable && trackedWidth kind vertical)
    (heightAvailable && trackedHeight kind vertical) s

theorem key_preserves_observable (kind : Kind)
    (vertical widthAvailable heightAvailable : Bool) (before after : Size)
    (same : sameKey kind vertical vertical before after) :
    observable kind vertical widthAvailable heightAvailable before =
    observable kind vertical widthAvailable heightAvailable after := by
  cases kind with
  | normal => simp [observable, rawProjection, trackedWidth, trackedHeight]
  | size => cases same; rfl
  | inline =>
    cases vertical <;>
      simp only [sameKey, inlineSize, Bool.false_eq_true, ↓reduceIte] at same <;>
      simp [observable, trackedWidth, trackedHeight, rawProjection, same]

theorem changed_observable_requires_changed_key (kind : Kind)
    (vertical widthAvailable heightAvailable : Bool) (before after : Size)
    (different : observable kind vertical widthAvailable heightAvailable before ≠
      observable kind vertical widthAvailable heightAvailable after) :
    ¬ sameKey kind vertical vertical before after := by
  intro same
  exact different (key_preserves_observable kind vertical widthAvailable heightAvailable before after same)

theorem any_observable_consumer_preserved (kind : Kind)
    (vertical widthAvailable heightAvailable : Bool) (before after : Size)
    (consumer : (Option Int × Option Int) → Int)
    (same : sameKey kind vertical vertical before after) :
    consumer (observable kind vertical widthAvailable heightAvailable before) =
    consumer (observable kind vertical widthAvailable heightAvailable after) :=
  congrArg consumer (key_preserves_observable kind vertical widthAvailable heightAvailable before after same)

theorem raw_projection_if_eligible (kind : Kind)
    (vertical widthAvailable heightAvailable : Bool) (s : Size)
    (widthEligible : widthAvailable = true → trackedWidth kind vertical = true)
    (heightEligible : heightAvailable = true → trackedHeight kind vertical = true) :
    rawProjection widthAvailable heightAvailable s =
      observable kind vertical widthAvailable heightAvailable s := by
  cases widthAvailable <;> cases heightAvailable <;>
    simp_all [observable]

theorem key_preserves_raw_if_eligible (kind : Kind)
    (vertical widthAvailable heightAvailable : Bool) (before after : Size)
    (widthEligible : widthAvailable = true → trackedWidth kind vertical = true)
    (heightEligible : heightAvailable = true → trackedHeight kind vertical = true)
    (same : sameKey kind vertical vertical before after) :
    rawProjection widthAvailable heightAvailable before =
      rawProjection widthAvailable heightAvailable after := by
  rw [raw_projection_if_eligible kind vertical widthAvailable heightAvailable before widthEligible heightEligible,
      raw_projection_if_eligible kind vertical widthAvailable heightAvailable after widthEligible heightEligible]
  exact key_preserves_observable kind vertical widthAvailable heightAvailable before after same

theorem old_border_key_counterexample :
    sameKey .size false false ⟨100, 100⟩ ⟨100, 100⟩ ∧
    observable .size false true true ⟨100, 100⟩ ≠
      observable .size false true true ⟨60, 100⟩ := by decide

theorem old_inline_border_key_counterexample :
    sameKey .inline false false ⟨100, 100⟩ ⟨100, 100⟩ ∧
    observable .inline false true false ⟨100, 100⟩ ≠
      observable .inline false true false ⟨60, 100⟩ := by decide

theorem writing_mode_premise_needed :
    sameKey .inline false true ⟨100, 50⟩ ⟨50, 100⟩ ∧
    observable .inline false true true ⟨100, 50⟩ ≠
      observable .inline true true true ⟨50, 100⟩ := by decide

theorem availability_premise_needed :
    sameKey .size false false ⟨100, 50⟩ ⟨100, 50⟩ ∧
    observable .size false false false ⟨100, 50⟩ ≠
      observable .size false true true ⟨100, 50⟩ := by decide

theorem raw_projection_requires_eligibility_premise :
    sameKey .inline false false ⟨100, 50⟩ ⟨100, 60⟩ ∧
    rawProjection true true ⟨100, 50⟩ ≠ rawProjection true true ⟨100, 60⟩ ∧
    observable .inline false true true ⟨100, 50⟩ =
      observable .inline false true true ⟨100, 60⟩ := by decide

theorem logical_consumers_need_fixed_writing_mode :
    sameKey .size false true ⟨100, 50⟩ ⟨100, 50⟩ ∧
    inlineSize false ⟨100, 50⟩ ≠ inlineSize true ⟨100, 50⟩ := by decide

#print axioms key_preserves_observable
#print axioms changed_observable_requires_changed_key
#print axioms any_observable_consumer_preserved
#print axioms raw_projection_if_eligible
#print axioms key_preserves_raw_if_eligible
#print axioms old_border_key_counterexample
#print axioms old_inline_border_key_counterexample
#print axioms writing_mode_premise_needed
#print axioms availability_premise_needed
#print axioms raw_projection_requires_eligibility_premise
#print axioms logical_consumers_need_fixed_writing_mode
end ContentSizeCache
