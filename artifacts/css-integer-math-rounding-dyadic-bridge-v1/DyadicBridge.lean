import Std

open scoped Rat

namespace IntegerRounding

def Coefficient53 (n : Int) : Prop :=
  -(2^53 : Int) < n ∧ n < (2^53 : Int)

def SmallDyadic53 (q : Rat) : Prop :=
  ∃ n : Int, ∃ k : Nat, k ≤ 24 ∧ Coefficient53 n ∧ q = n /. (2 : Int)^k

theorem nonnegative_exponent_half_bound (m : Int) (e : Fin 8)
    (lower : -16777215 ≤ m) (upper : m ≤ 16777215) :
    Coefficient53 (2 * (m * (2 : Int)^e.val) + 1) := by
  have scale : 0 ≤ (2 : Int)^e.val ∧ (2 : Int)^e.val ≤ 128 := by
    revert e
    decide
  have lo := Int.mul_le_mul_of_nonneg_right lower scale.1
  have hi := Int.mul_le_mul_of_nonneg_right upper scale.1
  unfold Coefficient53
  simp only [show (2^53 : Int) = 9007199254740992 by decide]
  omega

theorem negative_exponent_half_bound (m : Int) (e : Fin 24)
    (lower : -16777215 ≤ m) (upper : m ≤ 16777215) :
    Coefficient53 (m + (2 : Int)^e.val) := by
  have scale : 1 ≤ (2 : Int)^e.val ∧ (2 : Int)^e.val ≤ 8388608 := by
    revert e
    decide
  unfold Coefficient53
  simp only [show (2^53 : Int) = 9007199254740992 by decide]
  omega

theorem nonnegative_exponent_half_encoding (m : Int) (e : Nat) :
    (m * (2 : Int)^e) /. 1 + (1 : Int) /. 2 =
      (2 * (m * (2 : Int)^e) + 1) /. 2 := by
  rw [Rat.divInt_add_divInt _ _ (by decide) (by decide)]
  simp [Int.mul_comm]

theorem negative_exponent_half_encoding (m : Int) (e : Nat) :
    m /. (2 : Int)^(e + 1) + (1 : Int) /. 2 =
      (m + (2 : Int)^e) /. (2 : Int)^(e + 1) := by
  have nz : (2 : Int)^(e + 1) ≠ 0 := Int.pow_ne_zero (by decide)
  rw [Rat.divInt_add_divInt _ _ nz (by decide)]
  apply (Rat.divInt_eq_divInt_iff (by simp [nz]) nz).mpr
  simp [Int.pow_succ, Int.mul_add, Int.mul_assoc,
    Int.mul_comm, Int.mul_left_comm]

theorem central_half_small_dyadic (q : Rat) (m : Int)
    (lower : -16777215 ≤ m) (upper : m ≤ 16777215)
    (encoding : (∃ e : Fin 8, q = (m * (2 : Int)^e.val) /. 1) ∨
      (∃ e : Fin 24, q = m /. (2 : Int)^(e.val + 1))) :
    SmallDyadic53 (q + (1 : Int) /. 2) := by
  rcases encoding with ⟨e, rfl⟩ | ⟨e, rfl⟩
  · exact ⟨2 * (m * (2 : Int)^e.val) + 1, 1, by decide,
      nonnegative_exponent_half_bound m e lower upper,
      nonnegative_exponent_half_encoding m e.val⟩
  · exact ⟨m + (2 : Int)^e.val, e.val + 1, by omega,
      negative_exponent_half_bound m e lower upper,
      negative_exponent_half_encoding m e.val⟩

theorem zero_cell_error_bound (p rounded d gap error : Int)
    (nonnegative : 0 ≤ error) (margin : error < gap)
    (lower : gap ≤ p) (upper : p ≤ d - gap)
    (errorLower : p - error ≤ rounded) (errorUpper : rounded ≤ p + error) :
    0 < rounded ∧ rounded < d ∧ rounded / d = 0 := by
  have positive : 0 < d := by omega
  refine ⟨by omega, by omega, ?_⟩
  apply (Int.ediv_eq_iff_of_pos positive).mpr
  simp only [Int.zero_mul, Int.zero_add]
  omega

example : (1 : Int) /. (2 : Int)^149 + (1 : Int) /. 2 ≠ (1 : Int) /. 2 := by
  have nz : (2 : Int)^149 ≠ 0 := Int.pow_ne_zero (by decide)
  rw [Rat.divInt_add_divInt _ _ nz (by decide)]
  intro equality
  have cross := (Rat.divInt_eq_divInt_iff (by simp) (by decide)).mp equality
  simp only [Int.one_mul, Int.add_mul] at cross
  omega

example (p rounded : Int) (lower : (2 : Int)^125 ≤ p)
    (upper : p ≤ (2 : Int)^150 - (2 : Int)^125)
    (errorLower : p - (2 : Int)^97 ≤ rounded)
    (errorUpper : rounded ≤ p + (2 : Int)^97) :
    rounded / (2 : Int)^150 = 0 :=
  (zero_cell_error_bound p rounded ((2 : Int)^150) ((2 : Int)^125)
    ((2 : Int)^97) (by decide) (by decide) lower upper errorLower errorUpper).2.2

example : ((2 * (8388609 : Int) + 1) / 2) = 8388609 := by decide
example : ((2 * (-8388609 : Int) + 1) / 2) = -8388609 := by decide
example : ((2 * (-1 : Int) + 2) / 4) = 0 := by decide
example : ((2 * (1 : Int) + 2) / 4) = 1 := by decide

#print axioms nonnegative_exponent_half_bound
#print axioms negative_exponent_half_bound
#print axioms nonnegative_exponent_half_encoding
#print axioms negative_exponent_half_encoding
#print axioms central_half_small_dyadic
#print axioms zero_cell_error_bound

end IntegerRounding
