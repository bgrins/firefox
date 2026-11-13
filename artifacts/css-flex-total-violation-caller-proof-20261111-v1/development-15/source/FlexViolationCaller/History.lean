import FlexViolationCaller.NormalPass

namespace FlexViolationCaller

theorem line_remaining (line : Line) (h : CountAgrees line) :
    line.items.length - line.frozenCount = remaining line := by
  have hp := count_partition line.items
  unfold CountAgrees at h
  unfold remaining
  omega

theorem seed_fields (seed : Seed) : (seedItem seed).fields = seed.fields := by
  cases seed with
  | mk fields frozen => cases frozen <;> rfl

theorem start_fields (seeds : List Seed) (grow wantsInfo : Bool) :
    (start seeds grow wantsInfo).line.items.map ItemState.fields = seeds.map Seed.fields := by
  have he := early_exact grow (initialLine seeds) (initial_count seeds)
  change (early grow (initialLine seeds)).items.map ItemState.fields = _
  rw [he]
  simp only [initial_exact, List.map_map]
  apply List.map_congr_left
  intro seed hi
  exact (early_fields grow (seedItem seed)).trans (seed_fields seed)

theorem start_length (seeds : List Seed) (grow wantsInfo : Bool) :
    (start seeds grow wantsInfo).line.items.length = seeds.length := by
  have he := congrArg List.length (start_fields seeds grow wantsInfo)
  simpa only [List.length_map] using he

theorem history_target : HistoryTarget := by
  intro seeds grow wantsInfo state hs hh
  induction hh with
  | initial =>
    have hi := initial_target seeds grow wantsInfo hs
    have hl := start_length seeds grow wantsInfo
    have hc := hi.2.2.2.2.1
    have hp := count_partition (start seeds grow wantsInfo).line.items
    have hr := line_remaining _ hc
    refine ⟨hi.2.2.2.2, start_fields seeds grow wantsInfo, hl, hr, ?_, ?_, ?_, ?_⟩
    · change remaining (start seeds grow wantsInfo).line ≤ seeds.length - 0
      omega
    · change 0 ≤ seeds.length
      omega
    · intro hnot
      have hn : seeds.length ≠ 0 := by
        intro hz
        have he : (start seeds grow wantsInfo).line.items = [] := by
          apply List.eq_nil_of_length_eq_zero
          omega
        change (early grow (initialLine seeds)).items = [] at he
        simp only [start, he, List.isEmpty_nil, Bool.true_or] at hnot
        contradiction
      change 0 < seeds.length
      omega
    · intro hdone
      change (early grow (initialLine seeds)).items.isEmpty ||
        ((early grow (initialLine seeds)).frozenCount ==
          (early grow (initialLine seeds)).items.length && !wantsInfo) = true at hdone
      have hz : (start seeds grow wantsInfo).line.items.length = 0 ∨
          (start seeds grow wantsInfo).line.frozenCount =
            (start seeds grow wantsInfo).line.items.length := by
        rcases Bool.or_eq_true_iff.mp hdone with empty | full
        · exact Or.inl (by simpa only [List.isEmpty_iff_length_eq_zero] using empty)
        · exact Or.inr (of_decide_eq_true (Bool.and_eq_true_iff.mp full).1)
      rcases hz with hz | hz <;> omega
  | @step state values pass prior hnot hit hv he ih =>
    have hn : state.line.items.length ≤ FlexViolation.maxCount := by
      rw [ih.2.2.1]
      exact hs.1
    have hp := normalized_properties state.iteration state.line values ih.1 hv
    have hg := normalized_progress state.iteration state.line values ih.1 hv hn
    have heq : pass = normalizedPass state.iteration state.line values := by
      rw [normalized_exact _ _ _ ih.1.1 hv] at he
      exact (Option.some.inj he).symm
    subst pass
    have hl := aligned_length hp.1
    have hf := frozen_fields hp.1
    have hremain := line_remaining _ hp.2.1.1
    have hbudget : remaining (normalizedPass state.iteration state.line values).after ≤
        seeds.length - (state.iteration + 1) := by
      by_cases hz : remaining state.line = 0
      · have hmono := hg.1
        omega
      · have hd := hg.2 (by omega)
        omega
    have ha : (normalizedPass state.iteration state.line values).after.items.length = seeds.length := by
      omega
    refine ⟨hp.2.1, ?_, ha, hremain, hbudget, ?_, ?_, ?_⟩
    · exact hf.symm.trans ih.2.1
    · change state.iteration + 1 ≤ seeds.length
      omega
    · intro hnext
      change state.iteration + 1 < seeds.length
      have hfalse := Bool.or_eq_false_iff.mp hnext
      have hless : ¬(normalizedPass state.iteration state.line values).after.items.length ≤
          state.iteration + 1 := of_decide_eq_false hfalse.2
      omega
    · intro hdone
      rcases Bool.or_eq_true_iff.mp hdone with hc | hi
      · have hc' : (normalizedPass state.iteration state.line values).after.frozenCount =
            (normalizedPass state.iteration state.line values).after.items.length :=
          of_decide_eq_true hc
        omega
      · have hi' := of_decide_eq_true hi
        omega

theorem completion_target : CompletionTarget := by
  intro seeds grow wantsInfo state hs hh he
  have h := history_target seeds grow wantsInfo state hs hh
  have hz : remaining state.line = 0 := by omega
  refine ⟨?_, hz⟩
  cases hf : state.finished
  · have hn := h.2.2.2.2.2.2.1 hf
    omega
  · rfl

end FlexViolationCaller
