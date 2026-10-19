import NumericDigits
namespace NumericEntry
open NumericDigits

def signByte (b : Byte) : Bool := b.val == 43 || b.val == 45

def stripSign (xs : List Byte) : List Byte :=
  match xs with
  | [] => []
  | b::bs => if signByte b then bs else xs

def hasSign (xs : List Byte) : Bool := xs.head?.any signByte

def dotDigit (xs : List Byte) : Bool :=
  match xs with
  | b::c::_ => b.val == 46 && digit c
  | _ => false

def nativeStart (xs : List Byte) : Bool :=
  match xs with
  | [] => false
  | b::bs =>
    if digit b then true
    else if signByte b then bs.head?.any digit || dotDigit bs
    else if b.val == 46 then bs.head?.any digit
    else false

def referenceStart (xs : List Byte) : Bool :=
  match stripSign xs with
  | [] => false
  | b::bs => referenceDigit b || (b.val == 46 && bs.head?.any referenceDigit)

theorem sign_not_digit (b : Byte) (h : signByte b = true) : digit b = false := by
  simp [signByte] at h
  simp [digit]
  omega

theorem dot_not_digit (b : Byte) (h : b.val = 46) : digit b = false := by simp [digit,h]

theorem dot_head_shape (xs : List Byte) :
    (xs.head?.any digit || dotDigit xs) =
    (match xs with | [] => false | b::bs => digit b || (b.val == 46 && bs.head?.any digit)) := by
  cases xs with
  | nil => rfl
  | cons b bs => cases bs <;> simp [dotDigit]

theorem entry_reference (xs : List Byte) : nativeStart xs = referenceStart xs := by
  have hc : referenceDigit = digit := funext (fun b => (classifier b).symm)
  cases xs with
  | nil => rfl
  | cons b bs =>
    by_cases hs : signByte b = true
    · have hd := sign_not_digit b hs
      simp [nativeStart,referenceStart,stripSign,hs,hd,hc, dot_head_shape]
    · have hs' : signByte b = false := by simpa using hs
      by_cases hb : b.val = 46 <;> cases hd : digit b <;>
        simp [nativeStart,referenceStart,stripSign,hs',hc,hb,hd]

theorem entry_nonempty (xs : List Byte) (h : nativeStart xs = true) : xs ≠ [] := by
  intro hx
  simp [hx,nativeStart] at h

theorem first_loop_nonempty (xs : List Byte) (h : nativeStart xs = true) : stripSign xs ≠ [] := by
  rw [entry_reference] at h
  intro hx
  simp [referenceStart,hx] at h

theorem signed_cover (xs : List Byte) :
    (if hasSign xs then xs.take 1 else []) ++ stripSign xs = xs := by
  cases xs with
  | nil => rfl
  | cons b bs => cases hs : signByte b <;> simp [hasSign,stripSign,hs]

theorem entry_first_digit_or_fraction (xs : List Byte) (h : nativeStart xs = true) :
    (stripSign xs).head?.any digit = true ∨ dotDigit (stripSign xs) = true := by
  have hc : referenceDigit = digit := funext (fun b => (classifier b).symm)
  rw [entry_reference] at h
  have hshape := dot_head_shape (stripSign xs)
  have hr : ((stripSign xs).head?.any digit || dotDigit (stripSign xs)) = true := by
    rw [hshape]
    simpa [referenceStart,hc] using h
  simpa using hr

#print axioms sign_not_digit
#print axioms entry_reference
#print axioms entry_nonempty
#print axioms first_loop_nonempty
#print axioms signed_cover
#print axioms entry_first_digit_or_fraction
end NumericEntry
