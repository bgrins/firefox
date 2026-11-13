import FlexViolation.Target

namespace FlexViolation

theorem clamped_bounds (item : Item) (h : ValidItem item) :
    item.minimum ≤ clamped item ∧ clamped item ≤ item.maximum := by
  unfold clamped
  have hm := h.2.2.1
  split
  · exact ⟨Int.le_refl _, hm⟩
  · split <;> omega

theorem clamped_fits (item : Item) (h : ValidItem item) : Fits32 (clamped item) := by
  have hc := clamped_bounds item h
  simp only [ValidItem, Fits32, min32, max32] at *
  omega

theorem adjustment_bounds (item : Item) (h : ValidItem item) :
    -(2 ^ 32 - 1) ≤ adjustment item ∧ adjustment item ≤ 2 ^ 32 - 1 := by
  have hc := clamped_fits item h
  simp only [ValidItem, Fits32, min32, max32, adjustment] at *
  omega

theorem adjustment_fits (item : Item) (h : ValidItem item) : Fits64 (adjustment item) := by
  have ha := adjustment_bounds item h
  simp only [Fits64, min64, max64]
  omega

theorem difference_target : DifferenceTarget := by
  intro item h
  exact ⟨clamped_fits item h, adjustment_fits item h, adjustment_bounds item h⟩

theorem total_nil : total [] = 0 := by simp [total]

theorem total_cons (item : Item) (items : List Item) :
    total (item :: items) = adjustment item + total items := by simp [total]

theorem total_bounds (items : List Item)
    (h : ∀ item ∈ items, ValidItem item) :
    -(2 ^ 32 - 1) * (items.length : Int) ≤ total items ∧
    total items ≤ (2 ^ 32 - 1) * (items.length : Int) := by
  induction items with
  | nil => simp [total]
  | cons item items ih =>
    have hx := adjustment_bounds item (h item (by simp))
    have ht := ih (fun y hy => h y (by simp [hy]))
    simp only [total_cons, List.length_cons, Int.natCast_add, Int.natCast_one]
    simp only [Int.mul_add, Int.mul_one]
    omega

theorem range_from_count (n : Nat) (value : Int) (hn : n ≤ maxCount)
    (hl : -(2 ^ 32 - 1) * (n : Int) ≤ value)
    (hu : value ≤ (2 ^ 32 - 1) * (n : Int)) : Fits64 value := by
  simp [Fits64, min64, max64, maxCount] at *
  omega

theorem prefix_range (items : List Item) (h : Acquired items)
    (n : Nat) (hn : n ≤ items.length) : Fits64 (total (items.take n)) := by
  have hb := total_bounds (items.take n)
    (fun item hi => h.2 item (List.mem_of_mem_take hi))
  have hl : (items.take n).length = n := by simp [List.length_take, Nat.min_eq_left hn]
  rw [hl] at hb
  exact range_from_count n _ (Nat.le_trans hn h.1) hb.1 hb.2

theorem prefix_target : PrefixTarget := prefix_range

end FlexViolation
