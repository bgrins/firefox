import FlexViolationCaller.Freeze

namespace FlexViolationCaller

theorem selected_clamped (choice : FlexViolation.FreezeKind) (item : ItemState)
    (h : ReadyItem item) (hf : item.frozen = false) :
    flagSelected choice (clampOne item) = FlexViolation.selected choice (asItem item) := by
  have hc := clamp_relation item h
  simp only [ClampRel, hf, Bool.false_eq_true, ite_false] at hc
  cases choice with
  | all => rfl
  | minimum => exact hc.2.2.2.1
  | maximum =>
    simp only [flagSelected, hc.2.2.2.2, FlexViolation.selected, asItem]
    by_cases hx : item.fields.maximum < item.current
    · have hn : ¬item.current < item.fields.minimum := by
        have ho := h.1.2.2.1
        omega
      simp [hx, hn]
    · simp [hx]

theorem single_selected (item : FlexViolation.Item) (h : FlexViolation.ValidItem item) :
    FlexViolation.selected (FlexViolation.kind (FlexViolation.adjustment item)) item = true := by
  rw [FlexViolation.selected_correct _ item h]
  unfold FlexViolation.specSelected
  by_cases hz : FlexViolation.adjustment item = 0
  · simp [hz]
  · by_cases hp : 0 < FlexViolation.adjustment item
    · simp [hz, hp]
    · have hn : FlexViolation.adjustment item < 0 := by omega
      simp [hz, hp, hn]

theorem small_selected (items : List ItemState)
    (h : ∀ item ∈ items, ReadyItem item) (hl : (active items).length ≤ 1) :
    ∀ item ∈ items, item.frozen = false →
      flagSelected (FlexViolation.kind (FlexViolation.total ((active items).map asItem)))
        (clampOne item) = true := by
  intro item hi hf
  have ha : item ∈ active items := by simp [active, hi, hf]
  rw [selected_clamped _ item (h item hi) hf]
  cases he : active items with
  | nil => simp [he] at ha
  | cons first rest =>
    cases rest with
    | nil =>
      have eq : item = first := by simpa [he] using ha
      subst first
      simpa [he, FlexViolation.total] using single_selected (asItem item)
        (supplied_asItem item (h item hi).1 (h item hi).2.1)
    | cons second rest => simp [he] at hl

end FlexViolationCaller
