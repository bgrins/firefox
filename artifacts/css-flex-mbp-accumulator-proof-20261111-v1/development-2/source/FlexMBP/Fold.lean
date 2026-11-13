import FlexMBP.Bounds

namespace FlexMBP

theorem checkedAdd_exact (lower upper left right result : Int)
    (h : checkedAdd lower upper left right = some result) : result = left + right := by
  unfold checkedAdd at h
  split at h <;> simp_all

theorem fold_success_exact {α : Type} (mbp : α → Int) (lower upper : Int)
    (items : List α) (initial result : Int)
    (h : fold mbp lower upper initial items = some result) :
    result = initial + sum mbp items := by
  induction items generalizing initial with
  | nil => simpa [fold, sum] using h.symm
  | cons item items ih =>
    cases hn : checkedAdd lower upper initial (mbp item) with
    | none => simp [fold, hn] at h
    | some next =>
      have ht : fold mbp lower upper next items = some result := by
        simpa [fold, hn] using h
      have he := checkedAdd_exact lower upper initial (mbp item) next hn
      have hr := ih next ht
      rw [sum_cons]
      omega

theorem fold_of_prefixes {α : Type} (mbp : α → Int) (lower upper : Int)
    (items : List α) (initial : Int)
    (h : ∀ n ≤ items.length,
      lower ≤ initial + sum mbp (items.take n) ∧
      initial + sum mbp (items.take n) ≤ upper) :
    fold mbp lower upper initial items = some (initial + sum mbp items) := by
  induction items generalizing initial with
  | nil => simp [fold, sum]
  | cons item items ih =>
    have hfirst := h 1 (by simp)
    simp [sum] at hfirst
    have hn : checkedAdd lower upper initial (mbp item) = some (initial + mbp item) := by
      simp [checkedAdd, hfirst]
    have htail : ∀ n ≤ items.length,
        lower ≤ initial + mbp item + sum mbp (items.take n) ∧
        initial + mbp item + sum mbp (items.take n) ≤ upper := by
      intro n hlen
      have hp := h (n + 1) (by simp; omega)
      simpa [List.take_succ_cons, sum_cons, Int.add_assoc] using hp
    simpa [fold, hn, sum_cons, Int.add_assoc] using ih (initial + mbp item) htail

theorem wide_exact {α : Type} (mbp : α → Int) (items : List α)
    (h : Acquired mbp items) : wideFold mbp items = some (sum mbp items) := by
  have hp : ∀ n ≤ items.length,
      min64 ≤ 0 + sum mbp (items.take n) ∧
      0 + sum mbp (items.take n) ≤ max64 := by
    intro n hn
    simpa using prefix_range mbp items h n hn
  simpa [wideFold] using fold_of_prefixes mbp min64 max64 items 0 hp

theorem accumulator_target : AccumulatorTarget := by
  intro α mbp items h
  have hs := wide_exact mbp items h
  exact ⟨hs, by simp [accumulate, hs]⟩

theorem old_compatibility_target : OldCompatibilityTarget := by
  intro α mbp items total h ho
  have ht := fold_success_exact mbp min32 max32 items 0 total ho
  simpa using (wide_exact mbp items h).trans (by simp [ht])

end FlexMBP
