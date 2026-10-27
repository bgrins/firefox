import Init.Data.Rat

namespace CssSemantics.UnitConversion

structure Representation (U : Type) where
  unit : U
  amount : Rat
  deriving DecidableEq, Repr

variable {U : Type}

def denote (basis : U → Rat) (value : Representation U) : Rat :=
  value.amount * basis value.unit

def Preserves (basis : U → Rat) (input : Representation U)
    (target : U) (output : Representation U) : Prop :=
  output.unit = target ∧ denote basis output = denote basis input

def convert [DecidableEq U] (sampled : U → Rat)
    (input : Representation U) (target : U) : Option (Representation U) :=
  if input.unit = target then some input
  else if sampled target = 0 then none
  else some ⟨target, input.amount * sampled input.unit / sampled target⟩

theorem identity [DecidableEq U] (sampled : U → Rat) (input : Representation U) :
    convert sampled input input.unit = some input := by
  simp [convert]

theorem sound [DecidableEq U] (current : U → Rat)
    (input output : Representation U) (target : U)
    (success : convert current input target = some output) :
    Preserves current input target output := by
  unfold convert at success
  split at success
  · cases success
    exact ⟨‹_›, rfl⟩
  · split at success
    · contradiction
    · cases success
      exact ⟨rfl, Rat.div_mul_cancel ‹_›⟩

theorem unique (current : U → Rat) (input first second : Representation U)
    (target : U) (nonzero : current target ≠ 0)
    (left : Preserves current input target first)
    (right : Preserves current input target second) : first = second := by
  obtain ⟨fu, fa⟩ := first
  obtain ⟨su, sa⟩ := second
  obtain ⟨lf, lv⟩ := left
  obtain ⟨rf, rv⟩ := right
  dsimp at lf rf
  subst fu
  subst su
  have eq := congrArg (fun n => n / current target) (lv.trans rv.symm)
  simp only [denote, Rat.mul_div_cancel nonzero] at eq
  cases eq
  rfl

theorem complete [DecidableEq U] (current : U → Rat)
    (input output : Representation U) (target : U)
    (nonzero : current target ≠ 0) (preserved : Preserves current input target output) :
    convert current input target = some output := by
  have available : ∃ result, convert current input target = some result := by
    unfold convert
    split
    · exact ⟨input, rfl⟩
    · simp
  obtain ⟨result, success⟩ := available
  have same := unique current input result output target nonzero
    (sound current input result target success) preserved
  simpa [same] using success

theorem conversion_iff [DecidableEq U] (current : U → Rat)
    (input output : Representation U) (target : U) (nonzero : current target ≠ 0) :
    convert current input target = some output ↔ Preserves current input target output :=
  ⟨sound current input output target, complete current input output target nonzero⟩

theorem two_factor_agreement [DecidableEq U] (sampled current : U → Rat)
    (input : Representation U) (target : U)
    (sourceReady : sampled input.unit = current input.unit)
    (targetReady : sampled target = current target) :
    convert sampled input target = convert current input target := by
  simp only [convert, sourceReady, targetReady]

theorem ready_preserves [DecidableEq U] (sampled current : U → Rat)
    (input output : Representation U) (target : U)
    (sourceReady : sampled input.unit = current input.unit)
    (targetReady : sampled target = current target)
    (success : convert sampled input target = some output) :
    Preserves current input target output := by
  rw [two_factor_agreement sampled current input target sourceReady targetReady] at success
  exact sound current input output target success

theorem round_trip [DecidableEq U] (current : U → Rat)
    (input middle output : Representation U) (target : U)
    (sourceNonzero : current input.unit ≠ 0)
    (forward : convert current input target = some middle)
    (backward : convert current middle input.unit = some output) : output = input := by
  have f := sound current input middle target forward
  have b := sound current middle output input.unit backward
  exact unique current input output input input.unit sourceNonzero
    ⟨b.1, b.2.trans f.2⟩ ⟨rfl, rfl⟩

theorem different_zero_target [DecidableEq U] (sampled : U → Rat)
    (input : Representation U) (target : U)
    (different : input.unit ≠ target) (zero : sampled target = 0) :
    convert sampled input target = none := by
  simp [convert, different, zero]

end CssSemantics.UnitConversion
