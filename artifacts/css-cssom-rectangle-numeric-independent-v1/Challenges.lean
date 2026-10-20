import Edges

namespace RectangleIndependent
open RectangleNumeric

theorem quantum_always_positive (n : Int) : 0 < (quantum n : Int) := by
  have h : 0 < quantum n := Nat.two_pow_pos _
  omega

theorem divisibility_is_necessary (ticks au : Int)
    (exact : 60 * ticks = 65536 * au) : au % 15 = 0 := by omega

theorem grid_exact_iff_divisible (au : Int) :
    60 * grid au = 65536 * au ↔ au % 15 = 0 := by
  unfold grid
  omega

theorem lower_cell_included_upper_excluded (n : Int) :
    appRound (4294967296*n-2147483648) = n ∧
    appRound (4294967296*n+2147483648) = n+1 := by
  unfold appRound
  omega

theorem cancelling_nonfixed_components :
    narrow 16777217 ≠ 16777217 ∧ narrow 16777219 ≠ 16777219 ∧
    observe narrow 16777217 33554436 = 33554436 := by decide

theorem fixed_start_is_insufficient :
    narrow 0 = 0 ∧ observe narrow 0 16777217 ≠ 16777217 := by decide

theorem fixed_width_is_insufficient :
    narrow 0 = 0 ∧ observe narrow 16777217 16777217 ≠ 16777217 := by decide

theorem rounding_cell_conditions_are_not_necessary_for_sum :
    appRound 4294967296 ≠ 0 ∧ appRound (-4294967296) ≠ 0 ∧
    appRound 4294967296 + appRound (-4294967296) = 0 := by decide

theorem negative_width_requires_right_accessor_boundary :
    observe narrow 10 5 = 5 ∧ max (narrow 10) (observe narrow 10 5) = 10 := by decide

theorem arbitrary_int_quantizer_has_no_float_overflow :
    narrow (2^160) = 2^160 := by decide

theorem negative_binade_ties :
    narrow (-16777217) = -16777216 ∧ narrow (-16777219) = -16777220 := by decide

end RectangleIndependent

#print axioms RectangleIndependent.quantum_always_positive
#print axioms RectangleIndependent.divisibility_is_necessary
#print axioms RectangleIndependent.grid_exact_iff_divisible
#print axioms RectangleIndependent.lower_cell_included_upper_excluded
#print axioms RectangleIndependent.cancelling_nonfixed_components
#print axioms RectangleIndependent.fixed_start_is_insufficient
#print axioms RectangleIndependent.fixed_width_is_insufficient
#print axioms RectangleIndependent.rounding_cell_conditions_are_not_necessary_for_sum
#print axioms RectangleIndependent.negative_width_requires_right_accessor_boundary
#print axioms RectangleIndependent.arbitrary_int_quantizer_has_no_float_overflow
#print axioms RectangleIndependent.negative_binade_ties
