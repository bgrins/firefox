import NumericBoundary
namespace NumericReads
open NumericDigits NumericEntry NumericParts

def fractionGuardReads (xs : List Byte) : List Nat :=
  match xs with
  | b::_::_ => if b.val == 46 then [0,1] else [0]
  | _ => []

def exponentGuardReads (xs : List Byte) : List Nat :=
  match xs with
  | b::c::cs =>
    if exponentByte b then
      if digit c then [0,1]
      else if cs.isEmpty then [0,1]
      else if signByte c then [0,1,1,2] else [0,1,1]
    else [0]
  | _ => []

theorem fraction_guard_safe (xs : List Byte) :
    ∀ i ∈ fractionGuardReads xs, i < xs.length := by
  cases xs with
  | nil => simp [fractionGuardReads]
  | cons b bs => cases bs with
    | nil => simp [fractionGuardReads]
    | cons c cs => simp only [fractionGuardReads]; split <;> simp_all <;> omega

theorem exponent_guard_safe (xs : List Byte) :
    ∀ i ∈ exponentGuardReads xs, i < xs.length := by
  cases xs with
  | nil => simp [exponentGuardReads]
  | cons b bs => cases bs with
    | nil => simp [exponentGuardReads]
    | cons c cs =>
      simp only [exponentGuardReads]
      split
      · split
        · simp <;> omega
        · split
          · simp <;> omega
          · rename_i hn
            have hl : 0 < cs.length := by cases cs <;> simp_all
            split <;> simp <;> omega
      · simp <;> omega

def loopReads (xs : List Byte) : List Nat := (scan xs).reads

theorem loop_safe (xs : List Byte) : ∀ i ∈ loopReads xs, i < xs.length :=
  NumericDigits.reads_bounded xs

theorem initial_reads (xs : List Byte) (h : nativeStart xs = true) :
    0 < xs.length ∧ 0 < (stripSign xs).length := by
  have hx := entry_nonempty xs h
  have hs := first_loop_nonempty xs h
  constructor
  · exact List.length_pos_iff.mpr hx
  · exact List.length_pos_iff.mpr hs

theorem fraction_body_safe (xs : List Byte) (h : dotDigit xs = true) :
    0 < (xs.drop 1).length ∧
    ∀ i ∈ loopReads (xs.drop 1), 1+i < xs.length := by
  have he := fraction_entry xs h
  constructor
  · simp <;> omega
  · intro i hi
    have hb := loop_safe _ i hi
    simp at hb
    omega

theorem exponent_body_safe (xs : List Byte) (h : exponentGuard xs = true) :
    0 < (xs.drop 1).length ∧ 0 < (stripSign (xs.drop 1)).length ∧
    ∀ i ∈ loopReads (stripSign (xs.drop 1)),
      1 + (if hasSign (xs.drop 1) then 1 else 0) + i < xs.length := by
  have he := exponent_entry xs h
  have hn : (stripSign (xs.drop 1)) ≠ [] := by
    intro hz; rw [hz] at he; simp at he
  have hc := congrArg List.length (signed_cover (xs.drop 1))
  have hsign : (if hasSign (xs.drop 1) then (xs.drop 1).take 1 else []).length =
      (if hasSign (xs.drop 1) then 1 else 0) := by
    split
    · simp <;> omega
    · rfl
  simp only [List.length_append] at hc
  rw [hsign] at hc
  constructor
  · simp <;> omega
  constructor
  · cases hs : stripSign (xs.drop 1) <;> simp_all
  · intro i hi
    have hb := loop_safe _ i hi
    simp only [List.length_drop] at hc
    omega

theorem lifted_read (pre rest : List Byte) (i : Nat) (h : i < rest.length) :
    pre.length+i < (pre++rest).length := by simp <;> omega

#print axioms fraction_guard_safe
#print axioms exponent_guard_safe
#print axioms loop_safe
#print axioms initial_reads
#print axioms fraction_body_safe
#print axioms exponent_body_safe
#print axioms lifted_read
end NumericReads
