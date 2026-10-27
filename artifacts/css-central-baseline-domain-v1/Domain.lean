import Std

namespace CentralDomain

def halfAway (total : Int) := total.tdiv 2 + total.tmod 2

theorem half_relation (total : Int) :
    2 * halfAway total = total + total.tmod 2 := by
  have := Int.tmod_add_mul_tdiv total 2
  unfold halfAway
  omega

theorem remainder_range (total : Int) :
    -1 ≤ total.tmod 2 ∧ total.tmod 2 ≤ 1 := by
  have upper := Int.tmod_lt_of_pos total (b := 2) (by decide)
  have lower := Int.tmod_lt_of_pos (-total) (b := 2) (by decide)
  rw [Int.neg_tmod] at lower
  omega

theorem nonnegative_extent_lower_margin (extent selected opposite : Int)
    (extentNonnegative : 0 ≤ extent)
    (totalHi : extent + selected + opposite ≤ 2147483647)
    (oppositeLo : -1073741823 ≤ opposite)
    (oldRawHi : halfAway (extent + selected + opposite) - selected ≤ 2147483647) :
    -2147483647 ≤ extent - (halfAway (extent + selected + opposite) - selected) ∧
      extent - (halfAway (extent + selected + opposite) - selected) ≤ 2147483646 := by
  have relation := half_relation (extent + selected + opposite)
  have rem := remainder_range (extent + selected + opposite)
  by_cases nonnegative : 0 ≤ extent + selected + opposite
  · have := Int.tmod_nonneg 2 nonnegative
    omega
  · omega

theorem negative_insets (extent selected opposite : Int)
    (extentLo : 0 ≤ extent) (extentHi : extent ≤ 2147483647)
    (selectedLo : -2147483647 ≤ selected) (selectedHi : selected ≤ 0)
    (oppositeLo : -2147483647 ≤ opposite) (oppositeHi : opposite ≤ 0) :
    -2147483648 ≤ extent - (halfAway (extent + selected + opposite) - selected) ∧
      extent - (halfAway (extent + selected + opposite) - selected) ≤ 2147483647 := by
  have := half_relation (extent + selected + opposite)
  have := remainder_range (extent + selected + opposite)
  omega

theorem noninverted_last_defined (extent raw : Int)
    (rawLo : -2147483648 ≤ raw) (rawHi : raw ≤ 2147483647)
    (oldQueryLo : -2147483648 ≤ extent - raw)
    (oldQueryHi : extent - raw ≤ 2147483647) :
    -2147483648 ≤ extent - raw ∧ extent - raw ≤ 2147483647 ∧
      -2147483648 ≤ extent - (extent - raw) ∧
      extent - (extent - raw) ≤ 2147483647 ∧
      extent - (extent - raw) = raw := by
  omega

end CentralDomain

#print axioms CentralDomain.half_relation
#print axioms CentralDomain.remainder_range
#print axioms CentralDomain.nonnegative_extent_lower_margin
#print axioms CentralDomain.negative_insets
#print axioms CentralDomain.noninverted_last_defined
