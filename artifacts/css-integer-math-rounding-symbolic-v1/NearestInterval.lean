import Std

namespace IntegerRounding

theorem nearest_interval_floor (n d r : Int) (positive : 0 < d)
    (lower : 2 * d * r - d ≤ 2 * n)
    (upper : 2 * n ≤ 2 * d * r + d) :
    (2 * n + d) / (2 * d) =
      if 2 * n = 2 * d * r + d then r + 1 else r := by
  have denom : 0 < 2 * d := by omega
  have commute : r * (2 * d) = 2 * d * r := Int.mul_comm _ _
  by_cases tie : 2 * n = 2 * d * r + d
  · simp only [ite_eq_left tie]
    apply (Int.ediv_eq_iff_of_pos denom).mpr
    simp only [Int.add_mul, Int.one_mul, commute]
    omega
  · simp only [ite_eq_right tie]
    apply (Int.ediv_eq_iff_of_pos denom).mpr
    rw [commute]
    omega

#print axioms nearest_interval_floor

example : (2 * (-1) + 2) / (2 * 2) = (0 : Int) := by decide
example : (2 * 1 + 2) / (2 * 2) = (1 : Int) := by decide

end IntegerRounding
