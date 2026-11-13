import FlexViolation.Fold

namespace FlexViolation

theorem positive_adjustment (item : Item) (h : ValidItem item) :
    0 < adjustment item ↔ item.before < item.minimum := by
  have hm := h.2.2.1
  unfold adjustment clamped
  split
  · omega
  · split <;> omega

theorem negative_adjustment (item : Item) (h : ValidItem item) :
    adjustment item < 0 ↔ ¬(item.before < item.minimum) ∧ item.maximum < item.before := by
  have hm := h.2.2.1
  unfold adjustment clamped
  split
  · omega
  · split <;> omega

theorem selected_correct (value : Int) (item : Item) (h : ValidItem item) :
    selected (kind value) item = specSelected value item := by
  by_cases hz : value = 0
  · simp [kind, specSelected, selected, hz]
  · by_cases hp : 0 < value
    · simp [kind, specSelected, selected, hz, hp, positive_adjustment item h]
    · simp [kind, specSelected, selected, hz, hp, negative_adjustment item h]

theorem selection_target : SelectionTarget := by
  intro items h
  unfold frozen
  apply List.filter_congr
  intro item hi
  exact selected_correct _ item (h.2 item hi)

theorem positive_total_has_positive (items : List Item) (h : 0 < total items) :
    ∃ item ∈ items, 0 < adjustment item := by
  induction items with
  | nil => simp [total] at h
  | cons item items ih =>
    by_cases hx : 0 < adjustment item
    · exact ⟨item, by simp, hx⟩
    · have ht : 0 < total items := by rw [total_cons] at h; omega
      obtain ⟨y, hy, hp⟩ := ih ht
      exact ⟨y, by simp [hy], hp⟩

theorem negative_total_has_negative (items : List Item) (h : total items < 0) :
    ∃ item ∈ items, adjustment item < 0 := by
  induction items with
  | nil => simp [total] at h
  | cons item items ih =>
    by_cases hx : adjustment item < 0
    · exact ⟨item, by simp, hx⟩
    · have ht : total items < 0 := by rw [total_cons] at h; omega
      obtain ⟨y, hy, hp⟩ := ih ht
      exact ⟨y, by simp [hy], hp⟩

theorem progress_target : ProgressTarget := by
  intro items h hne hempty
  have hs := selection_target items h
  rw [hempty] at hs
  by_cases hz : total items = 0
  · have hf : frozen items = items := by simp [frozen, kind, hz, selected]
    exact hne (hf.symm.trans hempty)
  · by_cases hp : 0 < total items
    · obtain ⟨item, hi, ha⟩ := positive_total_has_positive items hp
      have hm : item ∈ items.filter (specSelected (total items)) := by
        simp [List.mem_filter, hi, specSelected, hz, hp, ha]
      rw [← hs] at hm
      simp at hm
    · have hn : total items < 0 := by omega
      obtain ⟨item, hi, ha⟩ := negative_total_has_negative items hn
      have hm : item ∈ items.filter (specSelected (total items)) := by
        simp [List.mem_filter, hi, specSelected, hz, hp, ha]
      rw [← hs] at hm
      simp at hm

end FlexViolation
