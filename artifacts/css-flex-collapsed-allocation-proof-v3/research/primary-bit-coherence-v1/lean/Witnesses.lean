import Publication

namespace PrimaryBit.Witnesses

def layout : Layout := ⟨fun _ => 0, fun c => c == 1⟩
def one : State := ⟨fun c => if c = 0 then some 0 else none, fun f => f == 0⟩
def world : World := ⟨empty, fun _ => some 12, fun _ => some 13, fun _ => true, false⟩

theorem inhabited : Coherent layout one ∧ Routed layout one ∧ NoAreaOwner layout := by
  refine ⟨?_, ?_, ?_⟩
  · intro f
    by_cases h : f = 0
    · subst f; rfl
    · simp [layout, one, h, Ne.symm h]
  · intro c f h _
    by_cases hc : c = 0
    · subst c; simp [one] at h; subst f; rfl
    · simp [one, hc] at h
  · intro f; rfl

theorem foreign_area_alias_is_not_own_primary :
    let s := setPrimary layout one 1 (some 3)
    s.pointer 1 = some 3 ∧ s.bit 3 = false ∧ Coherent layout s := by
  refine ⟨by decide, by decide, ?_⟩
  exact area_alias_preserves layout one 1 3 inhabited.1 inhabited.2.2 rfl

theorem alias_clear_retains_image_primary :
    let s := setPrimary layout (setPrimary layout one 1 (some 0)) 1 none
    s.pointer 0 = some 0 ∧ s.bit 0 = true ∧ s.pointer 1 = none := by decide

theorem changed_image_alias_survives_old_removal :
    let s := setPrimary layout (setPrimary layout one 1 (some 0)) 1 (some 2)
    (areaRemoved layout s 1 0).pointer 1 = some 2 := by decide

theorem own_replacement_without_clear_breaks_coherence :
    let s := setPrimary layout one 0 (some 2)
    s.bit 0 = true ∧ s.pointer 0 = some 2 ∧ ¬ Coherent layout s := by
  refine ⟨by decide, by decide, ?_⟩
  intro h
  have := h 0
  contradiction

theorem bad_replacement_old_destroy_clears_new_pointer :
    let s := setPrimary layout one 0 (some 2)
    (nativeDestroyRead layout s 0).pointer 0 = none ∧
    (pointerDestroyRead layout s 0).pointer 0 = some 2 := by decide

theorem clear_then_replace_is_coherent :
    Coherent layout (setPrimary layout (setPrimary layout one 0 none) 0 (some 2)) := by
  apply own_set_preserves
  · exact clear_preserves layout one 0 inhabited.1 inhabited.2.2 (inhabited.2.1 0)
  · rfl
  · exact Or.inl rfl

theorem transient_guard_disagreement :
    let s := (beginOwn world 0).frames
    (nativeDestroyRead layout s 0).bit 0 = true ∧
    s.pointer 0 = none ∧ s.bit 0 = true := by decide

theorem callback_replacement_breaks_completion :
    let started := beginOwn world 0
    let changed := { started with frames := writeBit started.frames 0 false }
    let finished := completeOwn changed 0 0
    finished.frames.pointer 0 = some 0 ∧ finished.frames.bit 0 = false ∧
      ¬ Coherent layout finished.frames := by
  refine ⟨by decide, by decide, ?_⟩
  intro h
  have := h 0
  contradiction

theorem completed_selected_init_is_stable :
    Coherent layout (ownProtocol world 0 0).frames ∧
    (ownProtocol world 0 0).rememberedB 0 = none ∧
    (ownProtocol world 0 0).animationUpdate = true := by
  exact ⟨own_protocol_stable layout world 0 0 (empty_coherent layout) rfl (Or.inl rfl),
    by decide, by decide⟩

theorem nonarea_foreign_pointer_is_not_coherent :
    let s := setPrimary layout empty 2 (some 0)
    s.bit 0 = true ∧ s.pointer 0 = none ∧ ¬ Coherent layout s := by
  refine ⟨by decide, by decide, ?_⟩
  intro h
  have := h 0
  contradiction

end PrimaryBit.Witnesses
