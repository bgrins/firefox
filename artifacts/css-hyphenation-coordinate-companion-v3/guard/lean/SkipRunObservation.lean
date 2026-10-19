import SkipSearch

namespace HyphenSkipRunObservation

open HyphenSkipRanges

structure Observation where
  skipped : Bool
  length : Nat
  deriving DecidableEq, Repr

def observe (ranges : List Range) (count offset : Nat) : Observation :=
  match ranges with
  | [] => ⟨decide (offset = count),count-offset⟩
  | r::rest => if offset < r.start then observe rest r.start offset
    else if offset < r.finish then ⟨true,r.finish-offset⟩
    else ⟨decide (offset = count),count-offset⟩

theorem positive_bounded (ranges : List Range) (count offset : Nat)
    (valid : WellFormed ranges count) (inside : offset < count) :
    0 < (observe ranges count offset).length ∧
      offset+(observe ranges count offset).length ≤ count := by
  induction ranges generalizing count with
  | nil => simp only [observe]; omega
  | cons r rest ih =>
    have last := valid.1
    unfold Range.finish at last
    simp only [observe]
    split
    next before =>
      have old := ih r.start valid.2.2 before
      omega
    next after =>
      split
      next within => simp only; unfold Range.finish at within ⊢; omega
      next outside => simp only; omega

theorem omitted_prefix_bound (ranges : List Range) (count offset : Nat)
    (valid : WellFormed ranges count) : omitted ranges offset ≤ offset := by
  induction ranges generalizing count with
  | nil => simp [omitted]
  | cons r rest ih =>
    have old := ih r.start valid.2.2
    have totalOld := total_bound rest r.start valid.2.2
    rw [omitted_cons]
    by_cases before : offset < r.start
    · have zero : offset-r.start = 0 := by omega
      simp only [zero,Nat.zero_min,Nat.zero_add]
      exact old
    · have fixed := omitted_after_end rest r.start offset valid.2.2 (by omega)
      rw [fixed]
      omega

theorem observed_omitted_delta (ranges : List Range) (count offset length : Nat)
    (valid : WellFormed ranges count) (inside : offset < count)
    (bounded : length ≤ (observe ranges count offset).length) :
    omitted ranges (offset+length) = omitted ranges offset +
      (if (observe ranges count offset).skipped then length else 0) := by
  induction ranges generalizing count with
  | nil =>
    have ne : offset ≠ count := by omega
    simp [observe,omitted,ne]
  | cons r rest ih =>
    have last := valid.1
    have delta := valid.2.1
    simp only [observe] at bounded ⊢
    by_cases before : offset < r.start
    · simp only [before,↓reduceIte] at bounded ⊢
      have extent := positive_bounded rest r.start offset valid.2.2 before
      have endpoint : offset+length ≤ r.start := by omega
      have zero : offset-r.start = 0 := by omega
      have zeroEnd : offset+length-r.start = 0 := by omega
      rw [omitted_cons,omitted_cons,zero,zeroEnd]
      simp only [Nat.zero_min,Nat.zero_add]
      exact ih r.start valid.2.2 before bounded
    · simp only [before,↓reduceIte] at bounded ⊢
      have old := omitted_after_end rest r.start offset valid.2.2 (by omega)
      have endOld := omitted_after_end rest r.start (offset+length) valid.2.2 (by omega)
      rw [omitted_cons,omitted_cons,old,endOld]
      by_cases within : offset < r.finish
      · simp only [within,↓reduceIte] at bounded ⊢
        unfold Range.finish at within bounded
        omega
      · simp only [within,↓reduceIte] at bounded ⊢
        have outside : ¬ offset < r.finish := within
        have ne : offset ≠ count := by omega
        simp only [ne,decide_false,Bool.false_eq_true,↓reduceIte,Nat.add_zero]
        unfold Range.finish at outside
        omega

theorem observed_coordinate_delta (ranges : List Range) (count offset length : Nat)
    (valid : WellFormed ranges count) (inside : offset < count)
    (bounded : length ≤ (observe ranges count offset).length) :
    lookupOriginal ranges (offset+length) = lookupOriginal ranges offset +
      (if (observe ranges count offset).skipped then 0 else length) := by
  rw [selected_range_arithmetic _ _ _ valid,selected_range_arithmetic _ _ _ valid,
    observed_omitted_delta _ _ _ _ valid inside bounded]
  have omittedBound := omitted_prefix_bound ranges count offset valid
  cases (observe ranges count offset).skipped <;> simp only [Bool.false_eq_true,
    ↓reduceIte,Nat.add_zero] <;> omega

end HyphenSkipRunObservation
