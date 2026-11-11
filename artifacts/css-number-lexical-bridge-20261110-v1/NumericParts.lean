import NumericEntry
namespace NumericParts
open NumericDigits NumericEntry

structure Part where
  text : List Byte
  digits : List Byte
  rest : List Byte
  used : Bool
  negative : Bool
  deriving DecidableEq, Repr

def emptyPart (xs : List Byte) : Part := ⟨[],[],xs,false,false⟩

def fraction (xs : List Byte) : Part :=
  if dotDigit xs then
    let r := scan (xs.drop 1)
    ⟨xs.take 1 ++ r.digits,r.digits,r.rest,true,false⟩
  else emptyPart xs

def exponentByte (b : Byte) : Bool := b.val == 69 || b.val == 101

def exponentGuard (xs : List Byte) : Bool :=
  match xs with
  | b::c::cs => exponentByte b &&
      (digit c || (signByte c && cs.head?.any digit))
  | _ => false

def exponent (xs : List Byte) : Part :=
  if exponentGuard xs then
    let tail := xs.drop 1
    let sign := if hasSign tail then tail.take 1 else []
    let r := scan (stripSign tail)
    ⟨xs.take 1 ++ sign ++ r.digits,r.digits,r.rest,true,tail.head?.any (fun b => b.val == 45)⟩
  else emptyPart xs

def picked (xs : List Byte) : List Byte := xs.takeWhile referenceDigit

def refFraction (xs : List Byte) : Part :=
  match xs with
  | [] => emptyPart xs
  | b::bs =>
    let ds := picked bs
    if b.val = 46 ∧ ds ≠ [] then
      ⟨b::ds,ds,bs.drop ds.length,true,false⟩
    else emptyPart xs

def refExponent (xs : List Byte) : Part :=
  match xs with
  | [] => emptyPart xs
  | b::bs =>
    let core := stripSign bs
    let ds := picked core
    if (b.val = 69 ∨ b.val = 101) ∧ ds ≠ [] then
      let sign := if hasSign bs then bs.take 1 else []
      ⟨b::(sign ++ ds),ds,core.drop ds.length,true,bs.head?.any (fun b => b.val == 45)⟩
    else emptyPart xs

theorem digits_picked (xs : List Byte) : (scan xs).digits = picked xs := by
  exact congrArg Prod.fst (scan_reference xs)

theorem picked_nonempty (xs : List Byte) : picked xs ≠ [] ↔ xs.head?.any digit = true := by
  cases xs with
  | nil => simp [picked]
  | cons b bs => cases hd : digit b <;> simp [picked,← classifier,hd]

theorem fraction_guard (xs : List Byte) :
    dotDigit xs = (match xs with
      | [] => false
      | b::bs => decide (b.val = 46 ∧ picked bs ≠ [])) := by
  cases xs with
  | nil => rfl
  | cons b bs =>
      cases bs <;> simp [dotDigit,picked_nonempty]
      apply Bool.eq_iff_iff.mpr
      simp

theorem exponent_guard (xs : List Byte) :
    exponentGuard xs = (match xs with
      | [] => false
      | b::bs => decide ((b.val = 69 ∨ b.val = 101) ∧ picked (stripSign bs) ≠ [])) := by
  cases xs with
  | nil => rfl
  | cons b bs =>
    cases bs with
    | nil => simp [exponentGuard,stripSign,picked]
    | cons c cs =>
      cases hs : signByte c
      · simp [exponentGuard,exponentByte,stripSign,hs,picked_nonempty]
        apply Bool.eq_iff_iff.mpr
        simp
      · have hd := sign_not_digit c hs
        simp [exponentGuard,exponentByte,stripSign,hs,picked_nonempty,hd]
        apply Bool.eq_iff_iff.mpr
        simp

theorem fraction_reference (xs : List Byte) : fraction xs = refFraction xs := by
  cases xs with
  | nil => rfl
  | cons b bs =>
    simp only [fraction, fraction_guard, refFraction, decide_eq_true_eq]
    split
    · simp [digits_picked,NumericDigits.exact_suffix]
    · rfl

theorem exponent_reference (xs : List Byte) : exponent xs = refExponent xs := by
  cases xs with
  | nil => rfl
  | cons b bs =>
    simp only [exponent, exponent_guard, refExponent, decide_eq_true_eq]
    split
    · simp [digits_picked,NumericDigits.exact_suffix]
    · rfl

theorem fraction_cover (xs : List Byte) : (fraction xs).text ++ (fraction xs).rest = xs := by
  unfold fraction
  split
  · simp only [List.append_assoc]
    rw [NumericDigits.cover]
    exact List.take_append_drop _ _
  · rfl

theorem exponent_cover (xs : List Byte) : (exponent xs).text ++ (exponent xs).rest = xs := by
  unfold exponent
  split
  · simp only [List.append_assoc]
    rw [NumericDigits.cover,signed_cover]
    exact List.take_append_drop _ _
  · rfl

theorem fraction_entry (xs : List Byte) (h : dotDigit xs = true) :
    (xs.drop 1).head?.any digit = true ∧ xs.length ≥ 2 := by
  cases xs with
  | nil => simp [dotDigit] at h
  | cons b bs => cases bs <;> simp_all [dotDigit]

theorem exponent_entry (xs : List Byte) (h : exponentGuard xs = true) :
    (stripSign (xs.drop 1)).head?.any digit = true ∧ xs.length ≥ 2 := by
  have hg := exponent_guard xs
  rw [h] at hg
  cases xs with
  | nil => simp [exponentGuard] at h
  | cons b bs =>
    cases bs with
    | nil => simp [exponentGuard] at h
    | cons c cs =>
      simp only [List.drop_succ_cons,List.drop_zero,List.length_cons]
      constructor
      · have hr : (b.val = 69 ∨ b.val = 101) ∧ picked (stripSign (c::cs)) ≠ [] := by simpa using hg.symm
        exact (picked_nonempty _).mp hr.2
      · omega

#print axioms digits_picked
#print axioms picked_nonempty
#print axioms fraction_guard
#print axioms exponent_guard
#print axioms fraction_reference
#print axioms exponent_reference
#print axioms fraction_cover
#print axioms exponent_cover
#print axioms fraction_entry
#print axioms exponent_entry
end NumericParts
