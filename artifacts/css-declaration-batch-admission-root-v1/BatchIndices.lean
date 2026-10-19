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

end BatchIndices
