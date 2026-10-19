import Std

namespace BatchIndices

def removeIndices (xs : List α) (positions : List Nat) : List α :=
  positions.foldl List.eraseIdx xs

def earlierRemovals (positions : List Nat) (index : Nat) : List Nat :=
  positions.filter (fun p => p < index)

theorem lower_lookup_preserved (xs : List α) (positions : List Nat) (index : Nat)
    (higher : ∀ p ∈ positions, index < p) :
    (removeIndices xs positions)[index]? = xs[index]? := by
  induction positions generalizing xs with
  | nil => rfl
  | cons p rest ih =>
    change (removeIndices (xs.eraseIdx p) rest)[index]? = xs[index]?
    rw [ih _ (by intro q hq; exact higher q (by simp [hq]))]
    exact List.getElem?_eraseIdx_of_lt (higher p (by simp))

theorem earlier_count_le_index (positions : List Nat) (index : Nat)
    (unique : positions.Nodup) :
    (earlierRemovals positions index).length ≤ index := by
  have hn : (earlierRemovals positions index).Nodup := unique.filter _
  have hs : earlierRemovals positions index ⊆ List.range index := by
    intro p hp
    have hlt : p < index := by simpa [earlierRemovals] using (List.mem_filter.mp hp).2
    exact List.mem_range.mpr hlt
  simpa using hn.length_le_of_subset hs

theorem rank_correction_no_underflow (positions : List Nat) (index : Nat)
    (unique : positions.Nodup) :
    index - (earlierRemovals positions index).length +
      (earlierRemovals positions index).length = index := by
  have := earlier_count_le_index positions index unique
  omega


theorem descending_rank_lookup (xs : List α) (positions : List Nat) (index : Nat)
    (hd : positions.Pairwise (fun a b => b < a)) (hn : index ∉ positions) :
    (removeIndices xs positions)[index - (earlierRemovals positions index).length]? = xs[index]? := by
  induction positions generalizing xs index with
  | nil => rfl
  | cons p rest ih =>
    have hp := (List.pairwise_cons.mp hd).1
    have ht := (List.pairwise_cons.mp hd).2
    have hne : index ≠ p := by intro h; exact hn (by simp [h])
    have hnr : index ∉ rest := by intro h; exact hn (by simp [h])
    by_cases hlow : p < index
    · have hr : earlierRemovals rest index = rest := by
        apply List.filter_eq_self.mpr
        intro q hq; simp; exact Nat.lt_trans (hp q hq) hlow
      have hr' : earlierRemovals rest (index-1) = rest := by
        apply List.filter_eq_self.mpr
        intro q hq; simp; have := hp q hq; omega
      have hni : index-1 ∉ rest := by
        intro hm; have := hp (index-1) hm; omega
      have hix : index - (rest.length+1) = (index-1)-rest.length := by omega
      simp only [removeIndices, List.foldl_cons]
      have he : earlierRemovals (p::rest) index = p::rest := by
        simp [earlierRemovals, hlow, show rest.filter (fun q => q < index) = rest from hr]
      rw [he, List.length_cons, hix]
      change (removeIndices (xs.eraseIdx p) rest)[(index-1)-rest.length]? = xs[index]?
      have hi := ih (xs.eraseIdx p) (index-1) ht hni
      rw [hr'] at hi
      rw [hi]
      rw [List.getElem?_eraseIdx_of_ge (by omega : p ≤ index-1)]
      have hz : index-1+1 = index := by omega
      rw [hz]
    · have hhigh : index < p := by omega
      have he : earlierRemovals (p::rest) index = earlierRemovals rest index := by
        simp [earlierRemovals, hlow]
      simp only [removeIndices, List.foldl_cons]
      rw [he]
      change (removeIndices (xs.eraseIdx p) rest)[index-(earlierRemovals rest index).length]? = xs[index]?
      rw [ih _ _ ht hnr, List.getElem?_eraseIdx_of_lt hhigh]

theorem map_remove_indices (f : α → β) (xs : List α) (positions : List Nat) :
    (removeIndices xs positions).map f = removeIndices (xs.map f) positions := by
  have er : ∀ (xs : List α) (n : Nat), (xs.eraseIdx n).map f = (xs.map f).eraseIdx n := by
    intro xs n
    simp [List.eraseIdx_eq_take_drop_succ, List.map_take, List.map_drop]
  induction positions generalizing xs with
  | nil => rfl
  | cons p rest ih =>
    simp only [removeIndices, List.foldl_cons]
    change (removeIndices (xs.eraseIdx p) rest).map f = removeIndices ((xs.map f).eraseIdx p) rest
    rw [ih, er]

theorem removal_preserves_nodup (xs : List α) (positions : List Nat) (hu : xs.Nodup) :
    (removeIndices xs positions).Nodup := by
  induction positions generalizing xs with
  | nil => exact hu
  | cons p rest ih => exact ih _ (hu.eraseIdx p)

end BatchIndices
