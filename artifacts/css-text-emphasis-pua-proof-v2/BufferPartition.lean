import Emphasis

namespace Emphasis.Partition

def applyGroups : List (List Glyph) → List Bool → List (List Glyph)
  | [], _ => []
  | group::rest, flags =>
    applyFlags group (flags.take group.length) :: applyGroups rest (flags.drop group.length)

theorem group_application (groups : List (List Glyph)) (flags : List Bool)
    (h : groups.flatten.length = flags.length) :
    (applyGroups groups flags).flatten = applyFlags groups.flatten flags := by
  induction groups generalizing flags with
  | nil => simp [applyGroups, applyFlags]
  | cons group rest ih =>
    have bound : group.length ≤ flags.length := by simp only [List.flatten_cons, List.length_append] at h; omega
    have takeLength : group.length = (flags.take group.length).length := by simp [List.length_take, Nat.min_eq_left bound]
    have restLength : rest.flatten.length = (flags.drop group.length).length := by
      simp only [List.flatten_cons, List.length_append] at h
      simp only [List.length_drop]
      omega
    simp only [applyGroups, List.flatten_cons]
    rw [ih _ restLength]
    unfold applyFlags
    conv => rhs; rw [← List.take_append_drop group.length flags]
    rw [List.zipWith_append takeLength]

theorem partition_fields_preserved (groups : List (List Glyph)) (flags : List Bool)
    (h : groups.flatten.length = flags.length) :
    ((applyGroups groups flags).flatten).map unaffected = groups.flatten.map unaffected := by
  rw [group_application groups flags h]
  exact apply_buffer_preserves groups.flatten flags h

theorem partition_eligibility_derived (groups : List (List Glyph)) (flags : List Bool)
    (h : groups.flatten.length = flags.length) :
    ((applyGroups groups flags).flatten).map charMay =
      List.zipWith (fun g f => charMay g && f) groups.flatten flags := by
  rw [group_application groups flags h, apply_buffer_eligibility]

theorem complete_decoding_partition (eligible : Nat → Bool) (text : List Unit)
    (groups : List (List Glyph)) (h : groups.flatten.length = text.length) :
    ((applyGroups groups (loopFlags eligible text)).flatten).map unaffected =
      groups.flatten.map unaffected ∧
    ((applyGroups groups (loopFlags eligible text)).flatten).map charMay =
      List.zipWith (fun g f => charMay g && f) groups.flatten (directFlags eligible text) := by
  have lengths : groups.flatten.length = (loopFlags eligible text).length := by rw [flags_length]; exact h
  constructor
  · exact partition_fields_preserved groups _ lengths
  · rw [partition_eligibility_derived groups _ lengths, flags_refinement]

end Emphasis.Partition
