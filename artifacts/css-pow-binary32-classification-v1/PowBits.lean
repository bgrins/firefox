import PowSpecial

namespace CssPowBits
open CssPowSpecial

abbrev Word := Fin 4294967296

def magnitude (w : Word) : Nat := w.val % 2147483648
def exponent (w : Word) : Nat := magnitude w / 8388608
def fraction (w : Word) : Nat := magnitude w % 8388608
def negative (w : Word) : Bool := decide (w.val ≥ 2147483648)

def classify (w : Word) : Value :=
  if exponent w = 255 then
    if fraction w = 0 then .infinity (negative w) else .nan
  else if exponent w = 127 ∧ fraction w = 0 then .unit (negative w)
  else .finite w.val

theorem magnitude_bound (w : Word) : magnitude w < 2147483648 := by
  exact Nat.mod_lt _ (by decide)

theorem nan_range (w : Word) :
    (exponent w = 255 ∧ fraction w ≠ 0) ↔ magnitude w > 2139095040 := by
  have bound := magnitude_bound w
  unfold exponent fraction
  omega

theorem infinity_encoding (w : Word) :
    (exponent w = 255 ∧ fraction w = 0) ↔ magnitude w = 2139095040 := by
  unfold exponent fraction
  omega

theorem unit_encoding (w : Word) :
    (exponent w = 127 ∧ fraction w = 0) ↔ magnitude w = 1065353216 := by
  unfold exponent fraction
  omega

theorem classify_nan_fields (w : Word) :
    isNaN (classify w) = decide (exponent w = 255 ∧ fraction w ≠ 0) := by
  by_cases he : exponent w = 255 <;> by_cases hf : fraction w = 0 <;>
    by_cases hu : exponent w = 127 <;> simp [classify, isNaN, he, hf, hu]

theorem classify_infinity_fields (w : Word) :
    isInfinite (classify w) = decide (exponent w = 255 ∧ fraction w = 0) := by
  by_cases he : exponent w = 255 <;> by_cases hf : fraction w = 0 <;>
    by_cases hu : exponent w = 127 <;> simp [classify, isInfinite, he, hf, hu]

theorem classify_unit_fields (w : Word) :
    isUnit (classify w) = decide (exponent w = 127 ∧ fraction w = 0) := by
  by_cases he : exponent w = 255 <;> by_cases hf : fraction w = 0 <;>
    by_cases hu : exponent w = 127 <;> simp_all [classify, isUnit]

theorem classify_nan (w : Word) :
    isNaN (classify w) = decide (magnitude w > 2139095040) := by
  simp only [classify_nan_fields, nan_range]

theorem classify_infinity (w : Word) :
    isInfinite (classify w) = decide (magnitude w = 2139095040) := by
  simp only [classify_infinity_fields, infinity_encoding]

theorem classify_unit (w : Word) :
    isUnit (classify w) = decide (magnitude w = 1065353216) := by
  simp only [classify_unit_fields, unit_encoding]

def bitGuard (fallback : Value → Value → Value) (a b : Word) : Value :=
  if decide (magnitude a > 2139095040) || decide (magnitude b > 2139095040) ||
      (decide (magnitude a = 1065353216) && decide (magnitude b = 2139095040))
  then .nan else fallback (classify a) (classify b)

theorem all_encodings_refine_spec (fallback : Value → Value → Value) (a b : Word) :
    bitGuard fallback a b = spec fallback (classify a) (classify b) := by
  unfold bitGuard
  rw [← classify_nan a, ← classify_nan b, ← classify_unit a, ← classify_infinity b]
  exact guard_refines_spec fallback (classify a) (classify b)

theorem negative_zero_is_not_unit : isUnit (classify ⟨2147483648, by decide⟩) = false := by
  decide

theorem signaling_nan_propagates :
    bitGuard returnsOne ⟨2139095041, by decide⟩ ⟨0, by decide⟩ = .nan := by
  decide

theorem negative_unit_positive_infinity :
    bitGuard returnsOne ⟨3212836864, by decide⟩ ⟨2139095040, by decide⟩ = .nan := by
  decide

end CssPowBits
