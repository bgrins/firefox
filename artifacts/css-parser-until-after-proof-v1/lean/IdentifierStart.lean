import Std

namespace IdentifierStart

def newline (b : Nat) : Bool := b == 10 || b == 12 || b == 13

def nativeAscii (b : Nat) : Bool :=
  (97 ≤ b && b ≤ 122) || (65 ≤ b && b ≤ 90) || b == 95 || b == 0

def newlineAt (input : List Nat) (offset : Nat) : Bool :=
  match input[offset]? with | none => false | some b => newline b

def native (input : List Nat) : Bool :=
  match input with
  | [] => false
  | b :: rest =>
    if nativeAscii b then true
    else if b == 45 then
      match rest with
      | [] => false
      | c :: _ => if nativeAscii c || c == 45 then true
                  else if c == 92 then !newlineAt input 1
                  else !(c < 128)
    else if b == 92 then !newlineAt input 1
    else !(b < 128)

def specStart (b : Nat) : Bool :=
  decide (b = 0 ∨ b = 95 ∨ 65 ≤ b ∧ b ≤ 90 ∨ 97 ≤ b ∧ b ≤ 122 ∨ 128 ≤ b)

def validEscape (input : List Nat) : Bool :=
  match input with
  | 92 :: 10 :: _ | 92 :: 12 :: _ | 92 :: 13 :: _ => false
  | 92 :: _ => true
  | _ => false

def reference (input : List Nat) : Bool :=
  match input with
  | [] => false
  | b :: rest =>
    if b = 45 then
      match rest with
      | [] => false
      | c :: _ => specStart c || c == 45 || validEscape rest
    else if b = 92 then validEscape input
    else specStart b

def corrected (input : List Nat) : Bool :=
  match input with
  | [] => false
  | b :: rest =>
    if nativeAscii b then true
    else if b == 45 then
      match rest with
      | [] => false
      | c :: _ => if nativeAscii c || c == 45 then true
                  else if c == 92 then !newlineAt input 2
                  else !(c < 128)
    else if b == 92 then !newlineAt input 1
    else !(b < 128)

theorem ascii_classification (b : Nat) :
    (nativeAscii b || !(b < 128)) = specStart b := by
  apply Bool.eq_iff_iff.mpr
  simp [nativeAscii, specStart]
  omega

theorem bad_admission_lf (tail : List Nat) :
    native (45 :: 92 :: 10 :: tail) = true ∧ reference (45 :: 92 :: 10 :: tail) = false := by
  simp [native, nativeAscii, newlineAt, newline, reference, specStart, validEscape]

theorem bad_admission_cr (tail : List Nat) :
    native (45 :: 92 :: 13 :: tail) = true ∧ reference (45 :: 92 :: 13 :: tail) = false := by
  simp [native, nativeAscii, newlineAt, newline, reference, specStart, validEscape]

theorem bad_admission_ff (tail : List Nat) :
    native (45 :: 92 :: 12 :: tail) = true ∧ reference (45 :: 92 :: 12 :: tail) = false := by
  simp [native, nativeAscii, newlineAt, newline, reference, specStart, validEscape]

example : corrected [45,92,10] = false := by decide
example : corrected [45,92,13] = false := by decide
example : corrected [45,92,12] = false := by decide
example : native [45,45,92,10] = true ∧ reference [45,45,92,10] = true := by decide
example : native [92,10] = false ∧ reference [92,10] = false := by decide



theorem escape_shape (b : Nat) (tail : List Nat) :
    validEscape (b :: tail) = (b == 92 && !newlineAt tail 0) := by
  by_cases hb : b = 92
  · subst b
    cases tail with
    | nil => rfl
    | cons c rest =>
      by_cases h10 : c = 10 <;> by_cases h12 : c = 12 <;> by_cases h13 : c = 13 <;>
        simp_all [validEscape, newlineAt, newline]
  · cases tail <;> simp_all [validEscape, newlineAt]

theorem corrected_reference (input : List Nat) : corrected input = reference input := by
  cases input with
  | nil => rfl
  | cons b tail =>
    by_cases hb45 : b = 45 <;> by_cases hb92 : b = 92
    · omega
    · subst b
      cases tail with
      | nil => rfl
      | cons c rest =>
        by_cases hc45 : c = 45 <;> by_cases hc92 : c = 92 <;>
          simp_all [corrected, reference, escape_shape, newlineAt, nativeAscii, specStart]
        all_goals apply Bool.eq_iff_iff.mpr; simp; omega
    · subst b
      simp [corrected, reference, nativeAscii, escape_shape, newlineAt]
    · simp only [corrected, reference, hb45, hb92, ite_false, beq_iff_eq]
      simp
      have h := ascii_classification b
      cases ha : nativeAscii b <;> simp_all

def affected (input : List Nat) : Bool :=
  match input with
  | 45 :: 92 :: c :: _ => newline c
  | _ => false

theorem exact_change (input : List Nat) :
    (native input != corrected input) = affected input := by
  cases input with
  | nil => rfl
  | cons b tail =>
    by_cases hb : b = 45
    · subst b
      cases tail with
      | nil => rfl
      | cons c rest =>
        by_cases hc : c = 92
        · subst c
          cases rest <;> simp [native, corrected, affected, nativeAscii, newlineAt, newline]
        · simp [native, corrected, affected, hc, nativeAscii]
    · simp [native, corrected, affected, hb]

theorem unchanged_outside (input : List Nat) (h : affected input = false) :
    native input = corrected input := by
  have e := exact_change input
  simpa [h] using e

theorem fixed_rejects (tail : List Nat) (c : Nat) (h : newline c = true) :
    corrected (45 :: 92 :: c :: tail) = false := by
  simp [corrected, nativeAscii, newlineAt, h]

#print axioms ascii_classification
#print axioms bad_admission_lf
#print axioms bad_admission_cr
#print axioms bad_admission_ff
#print axioms corrected_reference
#print axioms exact_change
#print axioms unchanged_outside
#print axioms fixed_rejects
end IdentifierStart
