import FlexViolationCaller.History

namespace FlexViolationCaller

theorem pass_target : PassTarget := by
  intro seeds grow wantsInfo state values hs hh hnot hv
  have hist := history_target seeds grow wantsInfo state hs hh
  have hr := prepare_ready state.line values hist.1 hv
  have hn : state.line.items.length ≤ FlexViolation.maxCount := by
    rw [hist.2.2.1]
    exact hs.1
  have hlen := aligned_length hr.1
  have ha := ready_acquired (suppliedItems state.line.items values) (by omega) hr.2
  have hp := normalized_properties state.iteration state.line values hist.1 hv
  have hg := normalized_progress state.iteration state.line values hist.1 hv hn
  refine ⟨normalizedPass state.iteration state.line values,
    normalized_exact _ _ _ hist.1.1 hv, ha, rfl, rfl,
    clamp_list_relation _ hr.2, FlexViolation.wide_exact _ ha, rfl,
    hp.1, hp.2.1, hp.2.2, hg.2⟩

theorem fallback_list (items : List ItemState) (final : Bool)
    (hr : ∀ item ∈ items, ReadyItem item)
    (hsmall : final = true → (active items).length ≤ 1) :
    (items.map clampOne).any (fellBack
      (FlexViolation.kind (FlexViolation.total ((active items).map asItem))) final) = false := by
  apply List.any_eq_false.mpr
  intro item hi
  obtain ⟨before, hb, rfl⟩ := List.mem_map.mp hi
  unfold fellBack
  rw [clamp_frozen]
  cases hf : before.frozen
  · cases ht : final
    · simp
    · have hsel := small_selected items hr (hsmall ht) before hb hf
      simp [hsel]
  · simp

theorem fallback_target : FallbackTarget := by
  intro seeds grow wantsInfo state values pass hs hh hnot hv he
  have hist := history_target seeds grow wantsInfo state hs hh
  have hr := prepare_ready state.line values hist.1 hv
  have hactive := prepared_active_length state.line values hv
  have heq : pass = normalizedPass state.iteration state.line values := by
    rw [normalized_exact _ _ _ hist.1.1 hv] at he
    exact (Option.some.inj he).symm
  subst pass
  constructor
  · apply fallback_list _ _ hr.2
    intro hfinal
    have hiter : state.iteration + 1 = state.line.items.length := of_decide_eq_true hfinal
    have hb := hist.2.2.2.2.1
    unfold remaining at hb
    omega
  · intro hfinal
    have hb := hist.2.2.2.2.1
    have hn : state.line.items.length ≤ FlexViolation.maxCount := by
      rw [hist.2.2.1]
      exact hs.1
    have hg := normalized_progress state.iteration state.line values hist.1 hv hn
    refine ⟨by omega, ?_⟩
    by_cases hz : remaining state.line = 0
    · omega
    · have hstrict := hg.2 (by omega)
      omega

end FlexViolationCaller
