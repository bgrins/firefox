import CssSemantics.CssNumberInput
import Init.Data.Rat

namespace CssSemantics.CssNumberValue

open CssNumberParts CssNumberSyntax

inductive TypeFlag where
  | integer
  | number
  deriving DecidableEq, Repr

structure Value where
  significand : Int
  scale : Int
  deriving DecidableEq, Repr

def digitsValue (digits : List Char) : Nat :=
  digits.foldl (fun value c => value * 10 + (c.toNat - '0'.toNat)) 0

def signed : Option Sign → Nat → Int
  | some .minus, value => -(value : Int)
  | _, value => value

def fractionDigits (decimal : Decimal) : List Char := decimal.fraction.getD []

def exponentValue (decimal : Decimal) : Int :=
  match decimal.exponent with
  | none => 0
  | some (sign, digits) => signed sign (digitsValue digits)

def ofDecimal (decimal : Decimal) : Value :=
  ⟨signed decimal.sign (digitsValue (decimal.integer ++ fractionDigits decimal)),
    exponentValue decimal - (fractionDigits decimal).length⟩

def typeFlag (decimal : Decimal) : TypeFlag :=
  if decimal.fraction.isSome || decimal.exponent.isSome then .number else .integer

def Value.toRat (value : Value) : Rat := (value.significand : Rat) * (10 : Rat) ^ value.scale

def signRat : Option Sign → Rat → Rat
  | some .minus, value => -value
  | _, value => value

def numberPart (decimal : Decimal) : Rat :=
  signRat decimal.sign ((digitsValue decimal.integer : Rat) +
    (digitsValue (fractionDigits decimal) : Rat) / (10 : Rat) ^ (fractionDigits decimal).length)

def meaning (decimal : Decimal) : Rat := numberPart decimal * (10 : Rat) ^ exponentValue decimal

theorem digitsFold_initial (digits : List Char) (initial : Nat) :
    digits.foldl (fun value c => value * 10 + (c.toNat - '0'.toNat)) initial =
      initial * 10 ^ digits.length + digitsValue digits := by
  induction digits generalizing initial with
  | nil => simp [digitsValue]
  | cons c digits ih =>
      simp only [List.foldl_cons, digitsValue, List.length_cons, Nat.zero_mul, Nat.zero_add] at ih ⊢
      rw [ih (initial * 10 + (c.toNat - '0'.toNat)), ih (c.toNat - '0'.toNat)]
      simp only [Nat.pow_succ, Nat.add_mul, Nat.mul_assoc, Nat.add_assoc]
      rw [Nat.mul_comm 10 (10 ^ digits.length)]

theorem digitsValue_append (first second : List Char) :
    digitsValue (first ++ second) = digitsValue first * 10 ^ second.length + digitsValue second := by
  rw [digitsValue, List.foldl_append]
  exact digitsFold_initial second _

theorem typeFlag_integer_iff (decimal : Decimal) : typeFlag decimal = .integer ↔
    decimal.fraction = none ∧ decimal.exponent = none := by
  cases fraction : decimal.fraction <;> cases exponent : decimal.exponent <;>
    simp [typeFlag, fraction, exponent]

theorem signed_cast (sign : Option Sign) (value : Nat) :
    (signed sign value : Rat) = signRat sign (value : Rat) := by
  cases sign with
  | none => rfl
  | some sign => cases sign <;> simp [signed, signRat, Rat.intCast_natCast]

theorem signRat_mul (sign : Option Sign) (left right : Rat) :
    signRat sign left * right = signRat sign (left * right) := by
  cases sign with
  | none => rfl
  | some sign => cases sign <;> simp [signRat, Rat.neg_mul]

theorem scale_power (exponent : Int) (width : Nat) :
    (10 : Rat) ^ (exponent - width) = ((10 : Rat) ^ width)⁻¹ * (10 : Rat) ^ exponent := by
  have equal : exponent - width = -(width : Int) + exponent := by omega
  rw [equal, Rat.zpow_add (by decide), Rat.zpow_neg, Rat.zpow_natCast]

theorem significand_fraction (sign : Option Sign) (integer fraction width : Nat) :
    signRat sign (((integer : Rat) * (10 : Rat) ^ width) + (fraction : Rat)) * ((10 : Rat) ^ width)⁻¹ =
      signRat sign ((integer : Rat) + (fraction : Rat) / (10 : Rat) ^ width) := by
  have nonzero : (10 : Rat) ^ width ≠ 0 := by
    intro equal
    have positive := Rat.pow_pos (n := width) (by decide : (0 : Rat) < 10)
    simp [equal] at positive
  rw [signRat_mul, Rat.add_mul, Rat.mul_assoc, Rat.mul_inv_cancel _ nonzero, Rat.mul_one, Rat.div_def]

theorem ofDecimal_meaning (decimal : Decimal) : (ofDecimal decimal).toRat = meaning decimal := by
  simp only [Value.toRat, ofDecimal, digitsValue_append, signed_cast, Rat.natCast_add,
    Rat.natCast_mul, Rat.natCast_pow, Rat.natCast_ofNat, scale_power]
  rw [← Rat.mul_assoc, significand_fraction]
  rfl

end CssSemantics.CssNumberValue
