import FlexMBP.Fold

namespace FlexMBP

theorem checkedAdd_range (lower upper left right result : Int)
    (h : checkedAdd lower upper left right = some result) :
    lower ≤ result ∧ result ≤ upper := by
  dsimp [checkedAdd] at h
  split at h <;> simp_all

theorem fold_success_range {α : Type} (mbp : α → Int) (lower upper : Int)
    (items : List α) (initial result : Int)
    (hi : lower ≤ initial ∧ initial ≤ upper)
    (h : fold mbp lower upper initial items = some result) :
    lower ≤ result ∧ result ≤ upper := by
  induction items generalizing initial with
  | nil => simpa [fold] using h ▸ hi
  | cons item items ih =>
    cases hn : checkedAdd lower upper initial (mbp item) with
    | none => simp [fold, hn] at h
    | some next =>
      exact ih next (checkedAdd_range lower upper initial (mbp item) next hn)
        (by simpa [fold, hn] using h)

theorem sum_replicate (value : Int) (count : Nat) :
    sum id (List.replicate count value) = value * (count : Int) := by
  induction count with
  | zero => simp [sum]
  | succ count ih =>
    simp [List.replicate_succ, sum_cons, ih, Int.mul_add, Int.add_comm]

theorem old_replicate_safe (magnitude : Int) (count : Nat)
    (hm : 0 ≤ magnitude) (hl : min32 ≤ -magnitude * (count : Int)) :
    oldFold id (List.replicate count (-magnitude)) =
      some (-magnitude * (count : Int)) := by
  have hp : ∀ k ≤ (List.replicate count (-magnitude)).length,
      min32 ≤ 0 + sum id ((List.replicate count (-magnitude)).take k) ∧
      0 + sum id ((List.replicate count (-magnitude)).take k) ≤ max32 := by
    intro k hk
    have hkn : k ≤ count := by simpa using hk
    have hki : (k : Int) ≤ count := by omega
    have hmul := Int.mul_le_mul_of_nonneg_left hki hm
    have hnonneg := Int.mul_nonneg hm (Int.natCast_nonneg k)
    simp only [List.take_replicate, Nat.min_eq_left hkn, sum_replicate, Int.zero_add]
    simp only [Int.neg_mul] at *
    constructor
    · omega
    · simp [max32]
      omega
  simpa [oldFold, sum_replicate] using
    fold_of_prefixes id min32 max32 (List.replicate count (-magnitude)) 0 hp

theorem old_replicate_rejected (magnitude : Int) (count : Nat)
    (hl : -magnitude * (count : Int) < min32) :
    oldFold id (List.replicate count (-magnitude)) = none := by
  cases he : oldFold id (List.replicate count (-magnitude)) with
  | none => rfl
  | some result =>
    have hex := fold_success_exact id min32 max32 (List.replicate count (-magnitude)) 0 result he
    have hr := fold_success_range id min32 max32 (List.replicate count (-magnitude)) 0 result
      (by simp [min32, max32]) he
    simp [sum_replicate] at hex
    omega

theorem boundary_from_bounds (magnitude : Int) (lastSafe : Nat)
    (hm : 0 ≤ magnitude) (hs : min32 ≤ -magnitude * (lastSafe : Int))
    (hf : -magnitude * ((lastSafe + 1 : Nat) : Int) < min32) :
    FirstRejectedBoundary magnitude lastSafe := by
  constructor
  · intro count hc
    have hmuls := Int.mul_le_mul_of_nonneg_left (show (count : Int) ≤ lastSafe by omega) hm
    apply old_replicate_safe magnitude count hm
    simp only [Int.neg_mul] at *
    omega
  · exact old_replicate_rejected magnitude (lastSafe + 1) hf

theorem boundary_target : BoundaryTarget := by
  refine ⟨?_, ?_, ?_⟩
  · apply boundary_from_bounds 60000 35791 <;> decide
  · apply boundary_from_bounds 6000000 357 <;> decide
  · apply boundary_from_bounds 600000000 3 <;> decide

end FlexMBP
