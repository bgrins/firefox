import FlexViolation.Bounds

namespace FlexViolation

theorem fold_success_exact (lower upper : Int) (items : List Item)
    (initial result : Int) (h : checkedFold lower upper initial items = some result) :
    result = initial + total items := by
  induction items generalizing initial with
  | nil => simpa [checkedFold, total] using h.symm
  | cons item items ih =>
    simp only [checkedFold] at h
    split at h
    · have ht := ih (initial + adjustment item) h
      rw [total_cons]
      omega
    · simp at h

theorem fold_of_ranges (lower upper : Int) (items : List Item) (initial : Int)
    (hd : ∀ item ∈ items, lower ≤ adjustment item ∧ adjustment item ≤ upper)
    (hp : ∀ n ≤ items.length,
      lower ≤ initial + total (items.take n) ∧
      initial + total (items.take n) ≤ upper) :
    checkedFold lower upper initial items = some (initial + total items) := by
  induction items generalizing initial with
  | nil => simp [checkedFold, total]
  | cons item items ih =>
    have hx := hd item (by simp)
    have hf := hp 1 (by simp)
    simp [total] at hf
    have ht : ∀ n ≤ items.length,
        lower ≤ initial + adjustment item + total (items.take n) ∧
        initial + adjustment item + total (items.take n) ≤ upper := by
      intro n hn
      have hh := hp (n + 1) (by simp; omega)
      simpa [List.take_succ_cons, total_cons, Int.add_assoc] using hh
    have hr := ih (initial + adjustment item) (fun y hy => hd y (by simp [hy])) ht
    simpa [checkedFold, hx.1, hx.2, hf.1, hf.2, total_cons, Int.add_assoc] using hr

theorem wide_exact (items : List Item) (h : Acquired items) :
    wideFold items = some (total items) := by
  have hd : ∀ item ∈ items, min64 ≤ adjustment item ∧ adjustment item ≤ max64 := by
    intro item hi
    exact adjustment_fits item (h.2 item hi)
  have hp : ∀ n ≤ items.length,
      min64 ≤ 0 + total (items.take n) ∧ 0 + total (items.take n) ≤ max64 := by
    intro n hn
    simpa [Fits64] using prefix_range items h n hn
  simpa [wideFold] using fold_of_ranges min64 max64 items 0 hd hp

theorem fold_target : FoldTarget := wide_exact

theorem compatibility_target : CompatibilityTarget := by
  intro items value h ho
  have he := fold_success_exact min32 max32 items 0 value ho
  have he' : value = total items := by simpa using he
  exact ⟨he', (wide_exact items h).trans (congrArg some he'.symm)⟩

end FlexViolation
