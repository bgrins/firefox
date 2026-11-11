import CssSemantics.CssNumberSyntax
import NumericLexical

set_option maxRecDepth 4096
set_option maxHeartbeats 4000000

namespace CssNumberLexicalBridge
open NumericDigits CssSemantics.CssNumberParts

def scalar (b : Byte) : Char := Char.ofNat b.val

def scalars (source : List Byte) : List Char := source.map scalar

@[simp] theorem scalars_nil : scalars [] = [] := rfl

@[simp] theorem scalars_cons (b : Byte) (bs : List Byte) : scalars (b :: bs) = scalar b :: scalars bs := rfl

@[simp] theorem scalars_empty (source : List Byte) : scalars source = [] ↔ source = [] := by simp [scalars]

@[simp] theorem scalars_drop (source : List Byte) (n : Nat) : scalars (source.drop n) = (scalars source).drop n := by
  simp [scalars]

def codes (source : List Char) : List Nat := source.map Char.toNat

def NormalizedASCII (source : List Byte) : Prop :=
  ∀ b ∈ source, b.val < 128 ∧ b.val ≠ 0 ∧ b.val ≠ 13 ∧ b.val ≠ 12

def outerSign : List Byte → Option Sign
  | [] => none
  | b :: _ => if b.val = 43 then some .plus else if b.val = 45 then some .minus else none

theorem scalar_nat (b : Byte) : (scalar b).toNat = b.val := by revert b; decide

theorem scalar_digit (b : Byte) : (scalar b).isDigit = NumericDigits.digit b := by revert b; decide

theorem scalar_plus (b : Byte) : scalar b = '+' ↔ b.val = 43 := by revert b; decide

theorem scalar_minus (b : Byte) : scalar b = '-' ↔ b.val = 45 := by revert b; decide

theorem scalar_dot (b : Byte) : scalar b = '.' ↔ b.val = 46 := by revert b; decide

theorem scalar_exponent (b : Byte) : (scalar b = 'e' ∨ scalar b = 'E') ↔ (b.val = 69 ∨ b.val = 101) := by
  revert b; decide

theorem scalars_codes (source : List Byte) : codes (scalars source) = source.map Fin.val := by
  simp [codes, scalars, List.map_map, Function.comp_def, scalar_nat]

theorem scalars_length (source : List Byte) : (scalars source).length = source.length := by simp [scalars]

theorem sign_bridge (source : List Byte) :
    CssSemantics.CssNumberParts.sign (scalars source) = (outerSign source, scalars (NumericEntry.stripSign source)) := by
  cases source with
  | nil => rfl
  | cons b bs =>
    by_cases plus : b.val = 43
    · have pc := (scalar_plus b).mpr plus
      simp [scalars, CssSemantics.CssNumberParts.sign, outerSign, NumericEntry.stripSign,
        NumericEntry.signByte, plus, pc]
    · by_cases minus : b.val = 45
      · have mc := (scalar_minus b).mpr minus
        simp [scalars, CssSemantics.CssNumberParts.sign, outerSign, NumericEntry.stripSign,
          NumericEntry.signByte, minus, mc]
      · have pc : scalar b ≠ '+' := by simpa [scalar_plus] using plus
        have mc : scalar b ≠ '-' := by simpa [scalar_minus] using minus
        simp [scalars, CssSemantics.CssNumberParts.sign, outerSign, NumericEntry.stripSign,
          NumericEntry.signByte, plus, minus, pc, mc]

theorem outer_sign_presence (source : List Byte) :
    (outerSign source).isSome = NumericEntry.hasSign source := by
  cases source with
  | nil => rfl
  | cons b bs =>
    by_cases plus : b.val = 43 <;> by_cases minus : b.val = 45 <;>
      simp [outerSign, NumericEntry.hasSign, NumericEntry.signByte, plus, minus]

theorem scan_bridge (source : List Byte) :
    takeDigits (scalars source) = (scalars (NumericDigits.scan source).digits, scalars (NumericDigits.scan source).rest) := by
  induction source with
  | nil => rfl
  | cons b bs ih =>
    cases hd : NumericDigits.digit b <;>
      simp [takeDigits, NumericDigits.scan, scalar_digit, hd, ih]

theorem picked_bridge (source : List Byte) :
    takeDigits (scalars source) =
      (scalars (NumericParts.picked source), scalars (source.drop (NumericParts.picked source).length)) := by
  rw [scan_bridge, NumericDigits.exact_suffix, NumericParts.digits_picked]

end CssNumberLexicalBridge
