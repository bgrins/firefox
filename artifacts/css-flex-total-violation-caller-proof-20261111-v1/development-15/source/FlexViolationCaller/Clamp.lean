import FlexViolationCaller.Prepare
import FlexViolationCaller.Early

namespace FlexViolationCaller

def clampOne (item : ItemState) : ItemState :=
  if item.frozen then item else (clampItem item).1

def ClampRel (a b : ItemState) : Prop :=
  if a.frozen then b = a else
    b.fields = a.fields ∧ b.frozen = false ∧ b.current = FlexViolation.clamped (asItem a) ∧
    b.minFlag = decide (a.current < a.fields.minimum) ∧
    b.maxFlag = decide (a.fields.maximum < a.current)

theorem clamp_adjustment (item : ItemState) :
    (clampItem item).2 = FlexViolation.adjustment (asItem item) := by
  by_cases hm : item.current < item.fields.minimum
  · simp [clampItem, FlexViolation.adjustment, FlexViolation.clamped, asItem, hm]
  · by_cases hx : item.fields.maximum < item.current <;>
      simp [clampItem, FlexViolation.adjustment, FlexViolation.clamped, asItem, hm, hx]

theorem clamp_fields (item : ItemState) : (clampOne item).fields = item.fields := by
  unfold clampOne
  split
  · rfl
  · unfold clampItem
    split
    · rfl
    · split <;> rfl

theorem clamp_frozen (item : ItemState) : (clampOne item).frozen = item.frozen := by
  unfold clampOne
  split
  · rfl
  · unfold clampItem
    split
    · rfl
    · split <;> rfl

theorem clamp_relation (item : ItemState) (h : ReadyItem item) :
    ClampRel item (clampOne item) := by
  have flags := h.2.2.1
  have order := h.1.2.2.1
  cases hf : item.frozen
  · have hh := flags hf
    by_cases hm : item.current < item.fields.minimum
    · have hx : ¬item.fields.maximum < item.current := by omega
      simp [ClampRel, clampOne, hf, clampItem, hm, hx, hh.2, asItem, FlexViolation.clamped]
    · by_cases hx : item.fields.maximum < item.current
      · simp [ClampRel, clampOne, hf, clampItem, hm, hx, hh.1, asItem, FlexViolation.clamped]
      · simp [ClampRel, clampOne, hf, clampItem, hm, hx, hh.1, hh.2, asItem, FlexViolation.clamped]
  · simp [ClampRel, clampOne, hf]

theorem clamp_bounded (item : ItemState) (h : ReadyItem item) : Bounded (clampOne item) := by
  have hr := clamp_relation item h
  cases hf : item.frozen
  · have hh : (clampOne item).fields = item.fields ∧
        (clampOne item).frozen = false ∧
        (clampOne item).current = FlexViolation.clamped (asItem item) ∧
        (clampOne item).minFlag = decide (item.current < item.fields.minimum) ∧
        (clampOne item).maxFlag = decide (item.fields.maximum < item.current) := by
      simpa only [ClampRel, hf, Bool.false_eq_true, ite_false] using hr
    have hv := supplied_asItem item h.1 h.2.1
    have hb := FlexViolation.clamped_bounds _ hv
    unfold Bounded
    rw [hh.1, hh.2.2.1, hh.2.2.2.1, hh.2.2.2.2]
    refine ⟨h.1, hb.1, hb.2, ?_⟩
    intro bad
    have hm := of_decide_eq_true bad.1
    have hx := of_decide_eq_true bad.2
    have ho := h.1.2.2.1
    omega
  · simpa [clampOne, hf] using h.2.2.2 hf

theorem clamp_zero (items : List ItemState) (acc : Int) :
    clampWalk 0 acc items = ⟨items,0,0,acc,false⟩ := by cases items <;> rfl

theorem clamp_walk_exact (items : List ItemState) (acc : Int) :
    clampWalk (active items).length acc items =
      ⟨items.map clampOne,0,0,acc + FlexViolation.total ((active items).map asItem),false⟩ := by
  induction items generalizing acc with
  | nil => simp [active, clampWalk, FlexViolation.total]
  | cons item items ih =>
    rw [active_cons]
    cases hf : item.frozen
    · simp only [Bool.false_eq_true, ite_false, List.length_cons]
      simp only [clampWalk, hf, Bool.false_eq_true, ite_false, ih]
      simp [clampOne, hf, clamp_adjustment, FlexViolation.total_cons, Int.add_assoc]
    · simp only [ite_true]
      cases hc : (active items).length with
      | zero =>
        have ht := ih acc
        rw [hc, clamp_zero] at ht
        have hi := congrArg Walk.items ht
        have he : active items = [] := by
          cases ha : active items with
          | nil => rfl
          | cons x xs => simp [ha] at hc
        simp only at hi
        simp [clamp_zero, clampOne, hf, ← hi, he, FlexViolation.total]
      | succ n =>
        have ht := ih acc
        rw [hc] at ht
        simp [clampWalk, hf, ht, clampOne]

theorem clamp_list_relation (items : List ItemState) (h : ∀ item ∈ items, ReadyItem item) :
    ClampedFrom items (items.map clampOne) :=
  aligned_map clampOne ClampRel items (fun item hi => clamp_relation item (h item hi))

theorem clamp_list_bounded (items : List ItemState) (h : ∀ item ∈ items, ReadyItem item) :
    ∀ item ∈ items.map clampOne, Bounded item := by
  intro item hi
  obtain ⟨before, hb, rfl⟩ := List.mem_map.mp hi
  exact clamp_bounded before (h before hb)

end FlexViolationCaller
