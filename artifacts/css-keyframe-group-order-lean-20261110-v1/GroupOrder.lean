import GroupOrderModel

namespace KeyframeGroupOrder

variable {α : Type} [DecidableEq α]

theorem reverse_refines_earliest (keys : List α) :
    (assembleReverse keys).reverse = earliest keys := by
  induction keys with
  | nil => rfl
  | cons key rest ih =>
    simp only [assembleReverse, moveLast, List.reverse_append, List.reverse_cons,
      List.reverse_nil, List.nil_append, List.singleton_append, earliest]
    rw [← List.filter_reverse, ih]

theorem earliest_filter (keys : List α) (p : α → Bool) :
    earliest (keys.filter p) = (earliest keys).filter p := by
  induction keys with
  | nil => rfl
  | cons key rest ih =>
    by_cases h : p key = true
    · simp [h, earliest, ih, List.filter_filter,
        Bool.and_comm]
    · have hp : p key = false := Bool.eq_false_iff.mpr h
      simp [hp, earliest, ih, List.filter_filter]
      apply List.filter_congr
      intro a _
      by_cases ha : a = key
      · subst a; simp [hp]
      · simp [ha]

theorem earliest_eq_eraseDups (keys : List α) :
    earliest keys = keys.eraseDups := by
  cases keys with
  | nil => rfl
  | cons key rest =>
    rw [earliest, List.eraseDups_cons, ← earliest_filter]
    congr 1
    exact earliest_eq_eraseDups _
termination_by keys.length
decreasing_by exact Nat.lt_succ_of_le (List.length_filter_le _ rest)

theorem final_order (keys : List α) :
    (assembleReverse keys).reverse = keys.eraseDups := by
  rw [reverse_refines_earliest, earliest_eq_eraseDups]

theorem assemble_is_reverse_loop (keys : List α) :
    assembleReverse keys = keys.reverse.foldl moveLast [] := by
  rw [List.foldl_reverse]
  induction keys with
  | nil => rfl
  | cons key rest ih => simp only [assembleReverse, List.foldr_cons, ih]

theorem reverse_loop_order (keys : List α) :
    (keys.reverse.foldl moveLast []).reverse = keys.eraseDups := by
  rw [← assemble_is_reverse_loop, final_order]

theorem earliest_nodup (keys : List α) : (earliest keys).Nodup := by
  induction keys with
  | nil => simp [earliest]
  | cons key rest ih =>
    simp only [earliest, List.nodup_cons]
    exact ⟨by simp, ih.filter _⟩

theorem unique_groups (keys : List α) :
    (keys.reverse.foldl moveLast []).reverse.Nodup := by
  rw [← assemble_is_reverse_loop, reverse_refines_earliest]
  exact earliest_nodup keys

theorem membership (keys : List α) (key : α) :
    key ∈ (assembleReverse keys).reverse ↔ key ∈ keys := by
  rw [final_order, List.mem_eraseDups]

theorem filter_absent (keys : List α) (key : α) (absent : key ∉ keys) :
    keys.filter (· != key) = keys := by
  apply List.filter_eq_self.mpr
  intro a ha
  have : a ≠ key := fun h => absent (h ▸ ha)
  simpa using this

theorem move_existing_rotation (before after : List α) (key : α)
    (hb : key ∉ before) (ha : key ∉ after) :
    moveLast (before ++ [key] ++ after) key = before ++ after ++ [key] := by
  simp [moveLast, List.filter_append, filter_absent before key hb,
    filter_absent after key ha]

theorem append_new_group (groups : List α) (key : α) (h : key ∉ groups) :
    moveLast groups key = groups ++ [key] := by
  rw [moveLast, filter_absent groups key h]

theorem old_order_counterexample :
    (oldAssembleReverse [0, 1, 2, 1]).reverse ≠ [0, 1, 2] := by decide

theorem repeated_group_order :
    (assembleReverse [0, 1, 2, 1]).reverse = [0, 1, 2] := by decide

theorem interleaved_offsets_order :
    (assembleReverse [(0, 0), (0, 1), (0, 2), (0, 1), (1, 0)]).reverse =
      [(0, 0), (0, 1), (0, 2), (1, 0)] := by decide

end KeyframeGroupOrder
