import SkipRunObservation

namespace HyphenSkipRunIndexed

open HyphenSkipRanges HyphenSkipSearch HyphenSkipRunObservation

def evaluate (selected : Option Range) (next count offset : Nat) : Observation :=
  match selected with
  | none => ⟨decide (offset = count),next-offset⟩
  | some r => if offset < r.finish then ⟨true,r.finish-offset⟩
      else ⟨decide (offset = count),next-offset⟩

def walk (array : List Range) (selected : Option Range) (count offset : Nat) : Observation :=
  match array with
  | [] => evaluate selected count count offset
  | r::rest => if offset < r.start then evaluate selected r.start count offset
      else walk rest (some r) count offset

def indexed (array : List Range) (selected : Option Range) (count offset : Nat) : Observation :=
  let cut := cutIndex offset (array.map Range.start)
  let previous := if cut = 0 then selected else array[cut-1]?
  let next := (array[cut]?.map Range.start).getD count
  evaluate previous next count offset

theorem indexed_walk (array : List Range) (selected : Option Range) (count offset : Nat) :
    indexed array selected count offset = walk array selected count offset := by
  induction array generalizing selected with
  | nil => rfl
  | cons r rest ih =>
    by_cases before : offset < r.start
    · simp [indexed,cutIndex,walk,before]
    · simp only [indexed,List.map_cons,cutIndex,ite_eq_right before,walk]
      have shifted : 1+cutIndex offset (rest.map Range.start)-1 = cutIndex offset (rest.map Range.start) := by omega
      simp only [Nat.add_eq_zero_iff,Nat.one_ne_zero,false_and,↓reduceIte,shifted]
      by_cases zero : cutIndex offset (rest.map Range.start) = 0
      · rw [zero]
        have old := ih (some r)
        simpa [indexed,zero] using old
      · have predecessor : cutIndex offset (rest.map Range.start) =
            (cutIndex offset (rest.map Range.start)-1)+1 := by omega
        rw [show 1+cutIndex offset (rest.map Range.start) = cutIndex offset (rest.map Range.start)+1 by omega]
        rw [List.getElem?_cons_succ,predecessor,List.getElem?_cons_succ]
        have old := ih (some r)
        simpa [indexed,zero,← predecessor] using old

theorem walk_all_before (array : List Range) (selected : Option Range) (r : Range)
    (count offset : Nat) (allBefore : ∀ x ∈ array, x.start ≤ offset) (lastBefore : r.start ≤ offset) :
    walk (array++[r]) selected count offset = evaluate (some r) count count offset := by
  induction array generalizing selected with
  | nil => simp [walk,Nat.not_lt.mpr lastBefore]
  | cons x rest ih =>
    have head := allBefore x (by simp)
    simp only [List.cons_append,walk,ite_eq_right (Nat.not_lt.mpr head)]
    exact ih (some x) (by intro x hx; exact allBefore x (by simp [hx]))

theorem walk_append_after (array : List Range) (selected : Option Range) (r : Range)
    (count offset : Nat) (after : offset < r.start) (bound : r.start ≤ count) :
    walk (array++[r]) selected count offset =
      walk array selected r.start offset := by
  have neCount : offset ≠ count := Nat.ne_of_lt (Nat.lt_of_lt_of_le after bound)
  have neStart : offset ≠ r.start := Nat.ne_of_lt after
  induction array generalizing selected with
  | nil =>
    simp only [List.nil_append,walk,ite_eq_left after]
    cases selected <;> simp [evaluate,neCount,neStart]
  | cons x rest ih =>
    simp only [List.cons_append,walk]
    split
    next before => cases selected <;> simp [evaluate,neCount,neStart]
    next beyond => exact ih (some x)

theorem walk_observe (ranges : List Range) (count offset : Nat)
    (valid : WellFormed ranges count) :
    walk ranges.reverse none count offset = observe ranges count offset := by
  induction ranges generalizing count with
  | nil => rfl
  | cons r rest ih =>
    rw [List.reverse_cons]
    by_cases before : offset < r.start
    · have bound : r.start ≤ count := by have := valid.1; unfold Range.finish at this; omega
      rw [walk_append_after _ _ _ _ _ before bound]
      rw [ih r.start valid.2.2]
      simp [observe,before]
    · have allBefore : ∀ x ∈ rest.reverse, x.start ≤ offset := by
        intro x hx
        have old := wellformed_member_start rest r.start valid.2.2 x (List.mem_reverse.mp hx)
        omega
      rw [walk_all_before _ _ _ _ _ allBefore (by omega)]
      simp [observe,before,evaluate]

def nativeObservation (ranges : List Range) (count offset : Nat) : Observation :=
  let array := ranges.reverse
  let cut := upperSearch (fun i => (array.map Range.start)[i]?.getD 0) offset 0 array.length
  let previous := if cut = 0 then none else array[cut-1]?
  let next := (array[cut]?.map Range.start).getD count
  evaluate previous next count offset

theorem complete_indexed_observation (ranges : List Range) (count offset : Nat)
    (valid : WellFormed ranges count) :
    nativeObservation ranges count offset = observe ranges count offset := by
  have sorted := wellformed_reverse_sorted ranges count valid
  have searched := native_binary_search_sorted (ranges.reverse.map Range.start) offset
    (List.pairwise_map.mpr sorted)
  simp only [List.length_map] at searched
  unfold nativeObservation
  dsimp only
  rw [searched]
  change indexed ranges.reverse none count offset = _
  rw [indexed_walk,walk_observe ranges count offset valid]

theorem native_observation_positive (ranges : List Range) (count offset : Nat)
    (valid : WellFormed ranges count) (inside : offset < count) :
    0 < (nativeObservation ranges count offset).length ∧
      offset+(nativeObservation ranges count offset).length ≤ count := by
  rw [complete_indexed_observation ranges count offset valid]
  exact positive_bounded ranges count offset valid inside

end HyphenSkipRunIndexed
