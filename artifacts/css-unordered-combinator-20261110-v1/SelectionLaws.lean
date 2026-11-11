import Selections

namespace CssUnordered

theorem insertions_spec (item : α) (source result : List α) :
    result ∈ insertions item source ↔
      ∃ before after, source = before ++ after ∧ result = before ++ item :: after := by
  induction source generalizing result with
  | nil =>
    constructor
    · intro member
      have equal : result = [item] := by simpa [insertions] using member
      exact ⟨[], [], rfl, equal⟩
    · rintro ⟨before, after, empty, equal⟩
      obtain ⟨rfl, rfl⟩ := List.append_eq_nil_iff.mp empty.symm
      simpa [insertions] using equal
  | cons head tail ih =>
    constructor
    · intro member
      simp only [insertions, List.mem_cons, List.mem_map] at member
      rcases member with equal | ⟨rest, member, equal⟩
      · exact ⟨[], head :: tail, rfl, equal⟩
      · obtain ⟨before, after, sourceEq, resultEq⟩ := ih rest |>.mp member
        exact ⟨head :: before, after, by simp [sourceEq], by simp [← equal, resultEq]⟩
    · rintro ⟨before, after, sourceEq, resultEq⟩
      cases before with
      | nil => simp_all [insertions]
      | cons first rest =>
        simp only [List.cons_append, List.cons.injEq] at sourceEq
        obtain ⟨rfl, sourceEq⟩ := sourceEq
        subst result
        simp only [insertions, List.mem_cons, List.mem_map]
        exact Or.inr ⟨rest ++ item :: after, (ih _).mpr ⟨rest, after, sourceEq, rfl⟩, rfl⟩

theorem orders_spec (source : List α) (unique : source.Nodup) (result : List α) :
    result ∈ orders source ↔ result.Nodup ∧ result ⊆ source := by
  induction source generalizing result with
  | nil =>
    constructor
    · intro member
      have equal : result = [] := by simpa [orders] using member
      subst result
      simp
    · rintro ⟨_, subset⟩
      have equal : result = [] := List.subset_nil.mp subset
      simpa [orders] using equal
  | cons head tail ih =>
    obtain ⟨notHead, tailUnique⟩ := List.nodup_cons.mp unique
    constructor
    · intro member
      simp only [orders, List.mem_append, List.mem_flatMap] at member
      rcases member with member | ⟨smaller, member, inserted⟩
      · obtain ⟨resultUnique, subset⟩ := (ih tailUnique result).mp member
        exact ⟨resultUnique, fun item h => List.mem_cons_of_mem head (subset h)⟩
      · obtain ⟨smallerUnique, subset⟩ := (ih tailUnique smaller).mp member
        obtain ⟨before, after, rfl, rfl⟩ := (insertions_spec head smaller result).mp inserted
        have noHead : head ∉ before ++ after := fun h => notHead (subset h)
        have fullUnique : (head :: (before ++ after)).Nodup := List.nodup_cons.mpr ⟨noHead, smallerUnique⟩
        refine ⟨List.perm_middle.nodup_iff.mpr fullUnique, ?_⟩
        intro item member
        simp only [List.mem_append, List.mem_cons] at member
        rcases member with left | rfl | right
        · exact List.mem_cons_of_mem head (subset (List.mem_append_left after left))
        · exact List.mem_cons_self
        · exact List.mem_cons_of_mem head (subset (List.mem_append_right before right))
    · rintro ⟨resultUnique, subset⟩
      by_cases present : head ∈ result
      · obtain ⟨before, after, rfl⟩ := List.mem_iff_append.mp present
        have reordered : (head :: (before ++ after)).Nodup := List.perm_middle.nodup_iff.mp resultUnique
        obtain ⟨noHead, smallerUnique⟩ := List.nodup_cons.mp reordered
        have smallerSubset : before ++ after ⊆ tail := by
          intro item member
          have inFull : item ∈ before ++ head :: after := by
            simp only [List.mem_append, List.mem_cons] at *
            rcases member with left | right
            · exact Or.inl left
            · exact Or.inr (Or.inr right)
          rcases List.mem_cons.mp (subset inFull) with same | inTail
          · subst item; exact False.elim (noHead member)
          · exact inTail
        simp only [orders, List.mem_append, List.mem_flatMap]
        exact Or.inr ⟨before ++ after, (ih tailUnique _).mpr ⟨smallerUnique, smallerSubset⟩,
          (insertions_spec _ _ _).mpr ⟨before, after, rfl, rfl⟩⟩
      · have smallerSubset : result ⊆ tail := by
          intro item member
          rcases List.mem_cons.mp (subset member) with same | inTail
          · subst item; exact False.elim (present member)
          · exact inTail
        simp only [orders, List.mem_append]
        exact Or.inl ((ih tailUnique _).mpr ⟨resultUnique, smallerSubset⟩)

theorem index_orders_spec (indices : List (Fin size)) :
    indices ∈ orders (List.finRange size) ↔ indices.Nodup := by
  rw [orders_spec _ (List.nodup_finRange size)]
  constructor
  · exact And.left
  · intro unique; exact ⟨unique, fun index _ => List.mem_finRange index⟩

end CssUnordered
