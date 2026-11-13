import FlexViolationCaller.Clamp

namespace FlexViolationCaller

def finishOne (choice : FlexViolation.FreezeKind) (finalIteration : Bool) (item : ItemState) : ItemState :=
  if item.frozen then item
  else if flagSelected choice item then
    { freeze item with
      minFlag := item.minFlag
      maxFlag := !item.minFlag && item.maxFlag }
  else if finalIteration then freeze item
  else { item with minFlag := false, maxFlag := false }

def fellBack (choice : FlexViolation.FreezeKind) (finalIteration : Bool) (item : ItemState) : Bool :=
  !item.frozen && !flagSelected choice item && finalIteration

theorem finish_frozen (choice : FlexViolation.FreezeKind) (finalIteration : Bool)
    (item : ItemState) (h : item.frozen = true) : finishOne choice finalIteration item = item := by
  simp [finishOne, h]

theorem finish_fields (choice : FlexViolation.FreezeKind) (finalIteration : Bool) (item : ItemState) :
    (finishOne choice finalIteration item).fields = item.fields := by
  unfold finishOne
  split
  · rfl
  · split
    · rfl
    · split <;> rfl

theorem finish_current (choice : FlexViolation.FreezeKind) (finalIteration : Bool) (item : ItemState) :
    (finishOne choice finalIteration item).current = item.current := by
  unfold finishOne
  split
  · rfl
  · split
    · rfl
    · split <;> rfl

theorem finish_bounded (choice : FlexViolation.FreezeKind) (finalIteration : Bool)
    (item : ItemState) (h : Bounded item) : Bounded (finishOne choice finalIteration item) := by
  unfold finishOne
  split
  · exact h
  · split
    · refine ⟨h.1, h.2.1, h.2.2.1, ?_⟩
      cases item.minFlag <;> cases item.maxFlag <;> decide
    · split <;> exact ⟨h.1, h.2.1, h.2.2.1, by decide⟩

theorem finish_fresh (choice : FlexViolation.FreezeKind) (finalIteration : Bool)
    (items : List ItemState) : Fresh (items.map (finishOne choice finalIteration)) := by
  intro item hi
  obtain ⟨before, hb, rfl⟩ := List.mem_map.mp hi
  unfold finishOne
  split
  · intro hn
    contradiction
  · split
    · simp [freeze]
    · split <;> simp [freeze]

theorem finish_preserves (choice : FlexViolation.FreezeKind) (finalIteration : Bool)
    (items : List ItemState) : FrozenPreserved items (items.map (finishOne choice finalIteration)) := by
  apply aligned_map
  intro item hi
  exact ⟨(finish_fields choice finalIteration item).symm, finish_frozen choice finalIteration item⟩

theorem freeze_zero (choice : FlexViolation.FreezeKind) (finalIteration : Bool) (items : List ItemState) :
    freezeWalk choice finalIteration 0 items = ⟨items,0,0,0,false⟩ := by cases items <;> rfl

theorem freeze_walk_exact (choice : FlexViolation.FreezeKind) (finalIteration : Bool)
    (items : List ItemState) :
    freezeWalk choice finalIteration (active items).length items =
      ⟨items.map (finishOne choice finalIteration),0,
        newCount (finishOne choice finalIteration) items,0,
        items.any (fellBack choice finalIteration)⟩ := by
  induction items with
  | nil => rfl
  | cons item items ih =>
    rw [active_cons]
    cases hf : item.frozen
    · simp only [Bool.false_eq_true, ite_false, List.length_cons]
      simp only [freezeWalk, hf, Bool.false_eq_true, ite_false, ih]
      simp [finishOne, hf, newCount, fellBack, Bool.or_comm]
    · simp only [ite_true]
      cases hc : (active items).length with
      | zero =>
        rw [hc, freeze_zero] at ih
        have hi := congrArg Walk.items ih
        have hn := congrArg Walk.newlyFrozen ih
        have hb := congrArg Walk.fallback ih
        simp only at hi hn hb
        simp [freeze_zero, finishOne, hf, ← hi, newCount, ← hn, fellBack, ← hb]
      | succ n =>
        rw [hc] at ih
        simp [freezeWalk, hf, ih, finishOne, newCount, fellBack]

end FlexViolationCaller
