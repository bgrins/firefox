import FlexViolationCaller.Base

namespace FlexViolationCaller

def newCount (f : ItemState → ItemState) : List ItemState → Nat
  | [] => 0
  | item :: rest => newCount f rest + if item.frozen then 0 else if (f item).frozen then 1 else 0

theorem early_frozen (grow : Bool) (item : ItemState) (h : item.frozen = true) :
    earlyItem grow item = item := by simp [earlyItem, h]

theorem early_outcome (grow : Bool) (item : ItemState) :
    earlyItem grow item = item ∨ earlyItem grow item =
      { freeze item with
        minFlag := decide (item.fields.base < item.current)
        maxFlag := decide (item.fields.base > item.current) } := by
  unfold earlyItem
  split
  · exact Or.inl rfl
  · split <;> split
    · exact Or.inr rfl
    · exact Or.inl rfl
    · exact Or.inr rfl
    · exact Or.inl rfl

theorem early_fields (grow : Bool) (item : ItemState) :
    (earlyItem grow item).fields = item.fields := by
  rcases early_outcome grow item with h | h <;> rw [h] <;> rfl

theorem early_current (grow : Bool) (item : ItemState) :
    (earlyItem grow item).current = item.current := by
  rcases early_outcome grow item with h | h <;> rw [h] <;> rfl

theorem early_bounded (grow : Bool) (item : ItemState) (h : Bounded item) :
    Bounded (earlyItem grow item) := by
  rcases early_outcome grow item with he | he <;> rw [he]
  · exact h
  · refine ⟨h.1, h.2.1, h.2.2.1, ?_⟩
    simp only [freeze, Bool.decide_eq_true]
    omega

theorem early_fresh (grow : Bool) (items : List ItemState) (h : Fresh items) :
    Fresh (items.map (earlyItem grow)) := by
  intro item hi
  obtain ⟨before, hb, rfl⟩ := List.mem_map.mp hi
  have hf := h before hb
  rcases early_outcome grow before with he | he <;> rw [he]
  · exact hf
  · simp [freeze]

theorem newCount_partition (f : ItemState → ItemState) (items : List ItemState)
    (hf : ∀ item, item.frozen = true → f item = item) :
    countedFrozen (items.map f) = countedFrozen items + newCount f items := by
  induction items with
  | nil => simp [countedFrozen, newCount]
  | cons item items ih =>
    simp only [List.map_cons, count_cons, newCount]
    cases h : item.frozen
    · simp only [Bool.false_eq_true, ite_false, Nat.zero_add, ih]
      cases (f item).frozen <;> simp <;> omega
    · simp only [hf item h, h, ite_true, ih]
      omega

theorem early_zero (grow : Bool) (items : List ItemState) :
    earlyWalk grow 0 items = ⟨items,0,0,0,false⟩ := by cases items <;> rfl

theorem early_walk_exact (grow : Bool) (items : List ItemState) :
    earlyWalk grow (active items).length items =
      ⟨items.map (earlyItem grow),0,newCount (earlyItem grow) items,0,false⟩ := by
  induction items with
  | nil => rfl
  | cons item items ih =>
    rw [active_cons]
    cases h : item.frozen
    · simp only [Bool.false_eq_true, ite_false, List.length_cons]
      simp only [earlyWalk, h, Bool.false_eq_true, ite_false, ih, List.map_cons, newCount]
    · simp only [ite_true]
      cases hc : (active items).length with
      | zero =>
        rw [hc, early_zero] at ih
        have hi := congrArg Walk.items ih
        have hn := congrArg Walk.newlyFrozen ih
        simp only [early_zero, List.map_cons, early_frozen grow item h, newCount, h, ite_true]
        simp only at hi hn
        rw [← hi, ← hn]
      | succ n =>
        rw [hc] at ih
        simp only [earlyWalk, h, ite_true, ih, List.map_cons, early_frozen grow item h,
          newCount, Nat.add_zero]

theorem early_exact (grow : Bool) (line : Line) (h : CountAgrees line) :
    early grow line = ⟨line.items.map (earlyItem grow),
      countedFrozen (line.items.map (earlyItem grow))⟩ := by
  have hp := count_partition line.items
  have he : line.items.length - line.frozenCount = (active line.items).length := by
    unfold CountAgrees at h
    omega
  simp only [early, he, early_walk_exact]
  unfold CountAgrees at h
  rw [h, ← newCount_partition (earlyItem grow) line.items (early_frozen grow)]

theorem initial_target : InitialTarget := by
  intro seeds grow wantsInfo h
  have hi := initial_valid seeds h
  have he := early_exact grow (initialLine seeds) hi.1
  have hp := count_partition (initialLine seeds).items
  have hl : (initialLine seeds).items.length - (initialLine seeds).frozenCount =
      (active (initialLine seeds).items).length := by
    have hc := hi.1
    unfold CountAgrees at hc
    omega
  refine ⟨hi.1, ?_, ?_, ?_, ?_⟩
  · simp [initial_exact]
  · rw [hl, early_walk_exact]
  · change (early grow (initialLine seeds)).items = _
    rw [he]
    simp only [initial_exact]
  · simp only [start, he]
    refine ⟨rfl, early_fresh grow _ hi.2.1, ?_⟩
    intro item hm
    obtain ⟨before, hb, rfl⟩ := List.mem_map.mp hm
    exact early_bounded grow before (hi.2.2 before hb)

end FlexViolationCaller
