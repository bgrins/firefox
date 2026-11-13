import FlexViolationCaller.Select

namespace FlexViolationCaller

theorem count_map_same (f : ItemState → ItemState) (items : List ItemState)
    (hf : ∀ item, (f item).frozen = item.frozen) :
    countedFrozen (items.map f) = countedFrozen items := by
  induction items with
  | nil => rfl
  | cons item items ih => simp only [List.map_cons, count_cons, hf, ih]

theorem active_map_length (f : ItemState → ItemState) (items : List ItemState)
    (hf : ∀ item, (f item).frozen = item.frozen) :
    (active (items.map f)).length = (active items).length := by
  have h1 := count_partition (items.map f)
  have h2 := count_partition items
  rw [count_map_same f items hf, List.length_map] at h1
  omega

theorem ready_acquired (items : List ItemState) (hn : items.length ≤ FlexViolation.maxCount)
    (hr : ∀ item ∈ items, ReadyItem item) : FlexViolation.Acquired ((active items).map asItem) := by
  refine ⟨?_, ?_⟩
  · have hp := count_partition items
    simp only [List.length_map]
    omega
  · intro item hi
    obtain ⟨before, hb, rfl⟩ := List.mem_map.mp hi
    have hm : before ∈ items := (List.mem_filter.mp hb).1
    exact supplied_asItem before (hr before hm).1 (hr before hm).2.1

theorem clamp_preserves (items : List ItemState) :
    FrozenPreserved items (items.map clampOne) := by
  apply aligned_map
  intro item hi
  exact ⟨(clamp_fields item).symm, by intro hf; simp [clampOne, hf]⟩

theorem newCount_positive (f : ItemState → ItemState) (items : List ItemState)
    (item : ItemState) (hi : item ∈ items) (hf : item.frozen = false)
    (ht : (f item).frozen = true) : 0 < newCount f items := by
  induction items with
  | nil => simp at hi
  | cons first rest ih =>
    rcases List.mem_cons.mp hi with rfl | hi
    · simp [newCount, hf, ht]
    · have hp := ih hi
      unfold newCount
      omega

theorem finish_selected (choice : FlexViolation.FreezeKind) (finalIteration : Bool)
    (item : ItemState) (hf : item.frozen = false) (hs : flagSelected choice item = true) :
    (finishOne choice finalIteration item).frozen = true := by
  simp [finishOne, hf, hs, freeze]

theorem finish_progress (items : List ItemState) (finalIteration : Bool)
    (hn : items.length ≤ FlexViolation.maxCount) (hr : ∀ item ∈ items, ReadyItem item)
    (hp : 0 < (active items).length) :
    0 < newCount (finishOne (FlexViolation.kind (FlexViolation.total ((active items).map asItem)))
      finalIteration) (items.map clampOne) := by
  have ha := ready_acquired items hn hr
  have hne : (active items).map asItem ≠ [] := by
    intro he
    have hz := congrArg List.length he
    simp only [List.length_map, List.length_nil] at hz
    omega
  have hs := FlexViolation.progress_target _ ha hne
  have hex : ∃ item, item ∈ FlexViolation.frozen ((active items).map asItem) := by
    cases he : FlexViolation.frozen ((active items).map asItem) with
    | nil => exact False.elim (hs he)
    | cons item rest => exact ⟨item, by simp [he]⟩
  obtain ⟨item, hi⟩ := hex
  obtain ⟨hm, hsel⟩ := List.mem_filter.mp hi
  obtain ⟨before, hb, rfl⟩ := List.mem_map.mp hm
  have hb' := List.mem_filter.mp hb
  have hf : before.frozen = false := by simpa using hb'.2
  apply newCount_positive _ _ (clampOne before) (List.mem_map.mpr ⟨before, hb'.1, rfl⟩)
    (by rw [clamp_frozen]; exact hf)
  apply finish_selected _ _ _ (by rw [clamp_frozen]; exact hf)
  rw [selected_clamped _ before (hr before hb'.1) hf]
  exact hsel

end FlexViolationCaller
