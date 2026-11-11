import Std

namespace RangeGroupSlots

def Above (position : Nat) (slots : List Nat) : Prop :=
  ∀ p ∈ slots, position < p

theorem empty_aligned : ([] : List Nat).length = 0 := rfl

theorem create_aligned (positions : List Nat) (count position : Nat)
    (aligned : positions.length = count) :
    (positions ++ [position]).length = count + 1 := by simp [aligned]

theorem reuse_aligned (positions : List Nat) (count index position : Nat)
    (aligned : positions.length = count) :
    (positions.set index position).length = count := by simp [aligned]

theorem reuse_index_valid (positions : List Nat) (count index : Nat)
    (aligned : positions.length = count) (valid : index < count) :
    index < positions.length := by omega

theorem new_sentinel_is_not_old_slot (positions : List Nat) (count : Nat)
    (aligned : positions.length = count) :
    ¬ count + 1 < positions.length := by omega

theorem old_match_differs_from_new_sentinel (index count : Nat)
    (valid : index < count) : index ≠ count + 1 := by omega

theorem above_fresh (position : Nat) (positions : List Nat)
    (above : Above position positions) : position ∉ positions := by
  intro member
  have := above position member
  omega

theorem fresh_set_nodup (positions : List Nat) (index position : Nat)
    (unique : positions.Nodup) (fresh : position ∉ positions) :
    (positions.set index position).Nodup := by
  induction positions generalizing index with
  | nil => simp
  | cons head tail ih =>
    have uniqueParts := List.nodup_cons.mp unique
    have freshTail : position ∉ tail := by
      intro member
      exact fresh (List.mem_cons_of_mem head member)
    cases index with
    | zero =>
      simpa using List.nodup_cons.mpr ⟨freshTail, uniqueParts.2⟩
    | succ index =>
      simp only [List.set, List.nodup_cons]
      refine ⟨?_, ih index uniqueParts.2 freshTail⟩
      intro member
      rcases List.mem_or_eq_of_mem_set member with member | same
      · exact uniqueParts.1 member
      · exact fresh (by simp [← same])

theorem create_unique (positions : List Nat) (position : Nat)
    (unique : positions.Nodup) (above : Above position positions) :
    (positions ++ [position]).Nodup := by
  simp [List.nodup_append, unique]
  intro a member same
  subst a
  exact above_fresh position positions above member

theorem reuse_unique (positions : List Nat) (index position : Nat)
    (unique : positions.Nodup) (above : Above position positions) :
    (positions.set index position).Nodup :=
  fresh_set_nodup positions index position unique (above_fresh position positions above)

theorem create_above_next (positions : List Nat) (position next : Nat)
    (above : Above position positions) (descending : next < position) :
    Above next (positions ++ [position]) := by
  intro p member
  simp only [List.mem_append, List.mem_singleton] at member
  rcases member with member | same
  · exact Nat.lt_trans descending (above p member)
  · simpa [same] using descending

theorem reuse_above_next (positions : List Nat) (index position next : Nat)
    (above : Above position positions) (descending : next < position) :
    Above next (positions.set index position) := by
  intro p member
  rcases List.mem_or_eq_of_mem_set member with member | same
  · exact Nat.lt_trans descending (above p member)
  · simpa [same] using descending

theorem update_is_minimum (position old : Nat) (descending : position < old) :
    min position old = position := Nat.min_eq_left (Nat.le_of_lt descending)

theorem zip_preserves_frame_count (frames : List α) (positions : List Nat)
    (aligned : frames.length = positions.length) :
    (frames.zip positions).length = frames.length := by simp [aligned]

end RangeGroupSlots
