import Std

namespace CentralRange

def halfAway (total : Int) := total.tdiv 2 + total.tmod 2

theorem complement_identity (extent selected opposite : Int) :
    extent - (halfAway (extent + selected + opposite) - selected) =
      (extent + selected + opposite).tdiv 2 - opposite := by
  have := Int.tmod_add_mul_tdiv (extent + selected + opposite) 2
  unfold halfAway
  omega

theorem quotient_range (total : Int)
    (lo : -2147483648 ≤ total) (hi : total ≤ 2147483647) :
    -1073741824 ≤ total.tdiv 2 ∧ total.tdiv 2 ≤ 1073741823 := by
  have equation := Int.tmod_add_mul_tdiv total 2
  have upper := Int.tmod_lt_of_pos total (b := 2) (by decide)
  have lower := Int.tmod_lt_of_pos (-total) (b := 2) (by decide)
  rw [Int.neg_tmod] at lower
  by_cases nonnegative : 0 ≤ total
  · have := Int.tmod_nonneg 2 nonnegative
    omega
  · have sign := Int.tmod_nonneg 2 (a := -total) (by omega)
    rw [Int.neg_tmod] at sign
    omega

theorem literal_margin_range (extent selected opposite : Int)
    (lo : -2147483648 ≤ extent + selected + opposite)
    (hi : extent + selected + opposite ≤ 2147483647)
    (marginLo : -1073741823 ≤ opposite)
    (marginHi : opposite ≤ 1073741823) :
    -2147483647 ≤ extent - (halfAway (extent + selected + opposite) - selected) ∧
      extent - (halfAway (extent + selected + opposite) - selected) ≤ 2147483646 := by
  rw [complement_identity]
  have := quotient_range (extent + selected + opposite) lo hi
  omega

theorem int32_witness :
    2147483647 + (-2147483647 : Int) = 0 ∧
    halfAway 2147483647 = 1073741824 ∧
    halfAway 2147483647 - 2147483647 = -1073741823 ∧
    2147483647 - (halfAway 2147483647 - 2147483647) = 3221225470 ∧
    (2147483647 : Int) < 3221225470 := by
  decide +kernel

end CentralRange

#print axioms CentralRange.complement_identity
#print axioms CentralRange.quotient_range
#print axioms CentralRange.literal_margin_range
#print axioms CentralRange.int32_witness
