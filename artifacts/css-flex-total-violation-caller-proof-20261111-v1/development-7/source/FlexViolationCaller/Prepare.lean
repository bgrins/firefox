import FlexViolationCaller.Aligned

namespace FlexViolationCaller

def FrameSame (a b : ItemState) : Prop :=
  a.fields = b.fields ∧ a.frozen = b.frozen ∧ a.minFlag = b.minFlag ∧
  a.maxFlag = b.maxFlag ∧ (a.frozen = true → b = a)

def ReadyItem (item : ItemState) : Prop :=
  FieldsValid item.fields ∧ FlexViolation.Fits32 item.current ∧
  (item.frozen = false → item.minFlag = false ∧ item.maxFlag = false) ∧
  (item.frozen = true → Bounded item)

def assign (item : ItemState) (value : Int) : ItemState :=
  if item.frozen then item else { item with current := value }

theorem supplied_cons (item : ItemState) (items : List ItemState) (value : Int) (values : List Int) :
    suppliedItems (item :: items) (value :: values) = assign item value :: suppliedItems items values := by
  simp [suppliedItems, assign]

theorem supplied_reset (items : List ItemState) (values : List Int) :
    suppliedItems (resetBase items) values = suppliedItems items values := by
  induction items generalizing values with
  | nil => simp [resetBase, suppliedItems]
  | cons item items ih =>
    cases values with
    | nil => simp [suppliedItems]
    | cons value values =>
      simp only [resetBase, List.map_cons]
      rw [supplied_cons, supplied_cons]
      have ht := ih values
      change assign (if item.frozen then item else {item with current := item.fields.base}) value ::
        suppliedItems (resetBase items) values = assign item value :: suppliedItems items values
      rw [ht]
      cases h : item.frozen <;> simp [assign, h]

theorem assign_frame (item : ItemState) (value : Int) : FrameSame item (assign item value) := by
  cases h : item.frozen <;> simp [FrameSame, assign, h]

theorem supplied_frame (items : List ItemState) (values : List Int) (h : values.length = items.length) :
    Aligned FrameSame items (suppliedItems items values) := by
  induction items generalizing values with
  | nil => cases values <;> simp_all [suppliedItems, Aligned]
  | cons item items ih =>
    cases values with
    | nil => simp at h
    | cons value values =>
      rw [supplied_cons]
      exact ⟨assign_frame item value, ih values (by simpa using h)⟩

theorem frame_frozen {xs ys : List ItemState} (h : Aligned FrameSame xs ys) :
    FrozenPreserved xs ys := aligned_imp h (fun _ _ h => ⟨h.1,h.2.2.2.2⟩)

theorem frame_count {xs ys : List ItemState} (h : Aligned FrameSame xs ys) :
    countedFrozen xs = countedFrozen ys := by
  induction xs generalizing ys with
  | nil => cases ys <;> simp_all [Aligned, countedFrozen]
  | cons x xs ih =>
    cases ys with
    | nil => simp [Aligned] at h
    | cons y ys =>
      rw [count_cons, count_cons, h.1.2.1, ih h.2]

theorem assign_ready (item : ItemState) (value : Int) (hb : Bounded item)
    (hf : item.frozen = false → item.minFlag = false ∧ item.maxFlag = false)
    (hv : item.frozen = false → FlexViolation.Fits32 value) : ReadyItem (assign item value) := by
  cases h : item.frozen
  · simp only [assign, h, Bool.false_eq_true, ite_false]
    exact ⟨hb.1, hv h, fun _ => hf h, by simp⟩
  · simpa [assign, h, ReadyItem] using
      And.intro hb.1 (And.intro (bounded_asItem item hb).1 hb)

theorem supplied_ready (items : List ItemState) (values : List Int)
    (hl : values.length = items.length)
    (hb : ∀ item ∈ items, Bounded item) (hf : Fresh items)
    (hv : ∀ pair ∈ items.zip values, pair.1.frozen = false → FlexViolation.Fits32 pair.2) :
    ∀ item ∈ suppliedItems items values, ReadyItem item := by
  induction items generalizing values with
  | nil => simp [suppliedItems]
  | cons item items ih =>
    cases values with
    | nil => simp at hl
    | cons value values =>
      rw [supplied_cons]
      intro result hr
      rcases List.mem_cons.mp hr with rfl | hr
      · exact assign_ready item value (hb item (by simp)) (hf item (by simp))
          (hv (item,value) (by simp))
      · exact ih values (by simpa using hl)
          (fun x hx => hb x (by simp [hx]))
          (fun x hx => hf x (by simp [hx]))
          (fun x hx => hv x (by simp [hx])) result hr

theorem prepare_exact (line : Line) (values : List Int) (h : ProviderValid line values) :
    prepare line values = some ⟨suppliedItems line.items values, line.frozenCount⟩ := by
  simp only [prepare, h.1, ite_true, supplied_reset]

theorem prepare_ready (line : Line) (values : List Int) (hl : LineValid line)
    (hv : ProviderValid line values) :
    Aligned FrameSame line.items (suppliedItems line.items values) ∧
    ∀ item ∈ suppliedItems line.items values, ReadyItem item :=
  ⟨supplied_frame _ _ hv.1, supplied_ready _ _ hv.1 hl.2.2 hl.2.1 hv.2⟩

end FlexViolationCaller
