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
  | 45 :: rest =>
      match rest with
      | [] => false
      | c :: _ => specStart c || c == 45 || validEscape rest
  | 92 :: _ => validEscape input
  | b :: _ => specStart b

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

#print axioms ascii_classification
#print axioms bad_admission_lf
#print axioms bad_admission_cr
#print axioms bad_admission_ff
end IdentifierStart
