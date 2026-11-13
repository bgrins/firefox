import FlexViolationCaller.Pass

namespace FlexViolationCaller

theorem finish_bit (choice : FlexViolation.FreezeKind) (final : Bool) (item : ItemState)
    (hf : item.frozen = false) (hall : final = true → flagSelected choice item = true) :
    (finishOne choice final item).frozen = flagSelected choice item := by
  cases hs : flagSelected choice item
  · have ht : final = false := by
      cases ht : final
      · rfl
      · have hh := hall ht
        rw [hs] at hh
        contradiction
    simp [finishOne, hf, hs, ht]
  · simp [finishOne, hf, hs, freeze]

theorem selected_map (items : List ItemState) (f : ItemState → ItemState)
    (choice : FlexViolation.FreezeKind)
    (hbit : ∀ item ∈ items, item.frozen = false →
      (f item).frozen = FlexViolation.selected choice (asItem item)) :
    newlySelected items (items.map f) =
      ((active items).map asItem).filter (FlexViolation.selected choice) := by
  induction items with
  | nil => rfl
  | cons item items ih =>
    have ht := ih (fun x hx => hbit x (by simp [hx]))
    cases hf : item.frozen
    · have hb := hbit item (by simp) hf
      simp only [newlySelected, List.map_cons, List.zip_cons_cons, List.filter_cons,
        hf, Bool.not_false, Bool.true_and, hb, active_cons, Bool.false_eq_true, ite_false]
      cases hs : FlexViolation.selected choice (asItem item) <;>
        simp_all [newlySelected]
    · simp [newlySelected, hf, active_cons, ht]

theorem selection_target : SelectionTarget := by
  intro seeds grow wantsInfo state values pass hs hh hnot hv he
  have hist := history_target seeds grow wantsInfo state hs hh
  have hr := prepare_ready state.line values hist.1 hv
  have hactive := prepared_active_length state.line values hv
  have heq : pass = normalizedPass state.iteration state.line values := by
    rw [normalized_exact _ _ _ hist.1.1 hv] at he
    exact (Option.some.inj he).symm
  subst pass
  let xs := suppliedItems state.line.items values
  let choice := FlexViolation.kind (FlexViolation.total ((active xs).map asItem))
  let final := state.iteration + 1 == state.line.items.length
  change newlySelected xs ((xs.map clampOne).map (finishOne choice final)) = _
  rw [List.map_map]
  apply selected_map
  intro item hi hf
  change (finishOne choice final (clampOne item)).frozen = _
  rw [finish_bit choice final (clampOne item) (by rw [clamp_frozen]; exact hf)]
  · exact selected_clamped choice item (hr.2 item hi) hf
  · intro hfinal
    have hiter : state.iteration + 1 = state.line.items.length := of_decide_eq_true hfinal
    have hb := hist.2.2.2.2.1
    unfold remaining at hb
    apply small_selected xs hr.2 (by dsimp [xs]; omega) item hi hf

end FlexViolationCaller
