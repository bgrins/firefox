import Caller
namespace Integration
open HexPrefix

theorem affected_rejected (input : List Nat) (h : IdentifierStart.affected input = true) :
    IdentifierStart.corrected input = false := by
  cases input with
  | nil => simp [IdentifierStart.affected] at h
  | cons b tail =>
    by_cases hb : b = 45
    · subst b
      cases tail with
      | nil => simp [IdentifierStart.affected] at h
      | cons c rest =>
        by_cases hc : c = 92
        · subst c
          cases rest with
          | nil => simp [IdentifierStart.affected] at h
          | cons d suffix =>
            exact IdentifierStart.fixed_rejects suffix d h
        · simp [IdentifierStart.affected,hc] at h
    · simp [IdentifierStart.affected,hb] at h

theorem corrected_implies_original (input : List Nat)
    (h : IdentifierStart.corrected input = true) : IdentifierStart.native input = true := by
  cases ha : IdentifierStart.affected input with
  | false => rw [IdentifierStart.unchanged_outside input ha]; exact h
  | true => simp [affected_rejected input ha] at h

theorem repaired_ident_progress (owned : Bool) (xs : List Byte)
    (h : IdentifierStart.corrected (xs.map Fin.val) = true) :
    0 < (Name.run owned xs).count :=
  Caller.original_ident_progress owned xs (corrected_implies_original _ h)

theorem repaired_ident_boundary (owned : Bool) (xs : List Byte)
    (h : IdentifierStart.corrected (xs.map Fin.val) = true) :
    0 < (Name.run owned xs).count ∧ Boundary.marker xs (Name.run owned xs).count :=
  Caller.original_ident_boundary owned xs (corrected_implies_original _ h)

theorem strict_reduction :
    IdentifierStart.native [45,92,10] = true ∧
    IdentifierStart.corrected [45,92,10] = false := by decide

#print axioms affected_rejected
#print axioms corrected_implies_original
#print axioms repaired_ident_progress
#print axioms repaired_ident_boundary
#print axioms strict_reduction
end Integration
