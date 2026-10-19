import Dispatch

namespace Emphasis.SignedLigature
open Dispatch

def Int32 (width : Int) : Prop := -2147483648 ≤ width ∧ width ≤ 2147483647

def Uint32 (count : Nat) : Prop := count < 4294967296

def apportioned (width : Int) (total selected : Nat) : Int :=
  (selected : Int) * width.tdiv (total : Int)

theorem magnitude_bound (width : Int) (total selected : Nat) (within : selected ≤ total) :
    (apportioned width total selected).natAbs ≤ width.natAbs := by
  simp only [apportioned,Int.natAbs_mul,Int.natAbs_tdiv,Int.natAbs_natCast]
  exact Nat.le_trans (Nat.mul_le_mul_right (width.natAbs/total) within)
    (Nat.mul_div_le width.natAbs total)

theorem int32_magnitude (width : Int) (valid : Int32 width) : width.natAbs ≤ 2147483648 := by
  cases width <;> simp_all [Int32] <;> omega

theorem signed64_and_binary64_exact_integer_domain (width : Int) (total selected : Nat)
    (valid : Int32 width) (within : selected ≤ total) :
    -9223372036854775808 ≤ apportioned width total selected ∧
    apportioned width total selected < 9223372036854775808 ∧
    (apportioned width total selected).natAbs < 9007199254740992 := by
  have bound := magnitude_bound width total selected within
  have wbound := int32_magnitude width valid
  have high := Int.le_natAbs (a := apportioned width total selected)
  have low := Int.le_natAbs (a := -apportioned width total selected)
  simp only [Int.natAbs_neg] at low
  omega

theorem quotient_truncates_toward_zero (width : Int) (total : Nat) :
    (width.tdiv (total : Int)).natAbs = width.natAbs/total := by
  simp only [Int.natAbs_tdiv,Int.natAbs_natCast]
  rfl

theorem signed_remainder (width : Int) (total : Nat) :
    width-apportioned width total total = width.tmod (total : Int) := by
  simp [apportioned,Int.tmod_def]

theorem signed_part_sum (width : Int) (total : Nat) (parts : List Nat) :
    (parts.map (apportioned width total)).sum = (parts.sum : Int)*width.tdiv (total : Int) := by
  induction parts with
  | nil => simp
  | cons part rest ih =>
    simp only [List.map_cons,List.sum_cons,ih,apportioned,Int.natCast_add,Int.add_mul]

theorem partition_conservation (width : Int) (total : Nat) (parts : List Nat)
    (covers : parts.sum = total) :
    (parts.map (apportioned width total)).sum + (width-apportioned width total total) = width := by
  rw [signed_part_sum,covers]
  simp only [apportioned]
  omega

theorem nonnegative_quotient_unchanged (width total : Nat) (bound : width < 4294967296) :
    quotient .legacyUnsigned32 width total = quotient .signed width total := by
  simp only [quotient]
  have modulo : (width : Int) % 4294967296 = width := Int.emod_eq_of_lt (by omega) (by omega)
  rw [modulo]
  simp only [Int.toNat_natCast,Int.ofNat_tdiv]

theorem nonnegative_product_unchanged (width total selected : Nat)
    (bound : width < 4294967296) (within : selected ≤ total) :
    product .legacyUnsigned32 selected (quotient .legacyUnsigned32 width total) =
    product .signed selected (quotient .signed width total) := by
  rw [nonnegative_quotient_unchanged width total bound]
  simp only [quotient,product,← Int.ofNat_tdiv,← Int.natCast_mul]
  have productBound := Nat.le_trans (Nat.mul_le_mul_right (width/total) within)
    (Nat.mul_div_le width total)
  exact Int.emod_eq_of_lt (by omega) (by omega)

theorem nonnegative_width_unchanged (width total selected : Nat) (final : Bool) (before after : Int)
    (bound : width < 4294967296) (within : selected ≤ total) :
    partialWidth .legacyUnsigned32 width total selected final before after =
    partialWidth .signed width total selected final before after := by
  simp only [partialWidth,
    nonnegative_product_unchanged width total selected bound within,
    nonnegative_product_unchanged width total total bound (by omega)]

end Emphasis.SignedLigature
