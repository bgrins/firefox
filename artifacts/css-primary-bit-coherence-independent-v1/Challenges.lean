import InitialDispatch
import Witnesses

namespace IndependentPrimary
open PrimaryBit PrimaryBit.Witnesses

def foreign : State := publish one 2 (some 0)

theorem coherent_not_routed : Coherent layout foreign ∧ ¬ Routed layout foreign := by
  constructor
  · intro f
    by_cases h : f = 0
    · subst f; rfl
    · simp [foreign, publish, layout, one, h, Ne.symm h]
  · intro h
    have bad := h 2 0 (by rfl) (by rfl)
    contradiction

theorem clear_foreign_pointer_breaks_owner_bit :
    (setPrimary layout foreign 2 none).pointer 0 = some 0 ∧
    (setPrimary layout foreign 2 none).bit 0 = false ∧
    ¬ Coherent layout (setPrimary layout foreign 2 none) := by
  refine ⟨by decide, by decide, ?_⟩
  intro h
  have bad := h 0
  contradiction

def areaOwner : Layout := ⟨fun f => if f = 0 then 1 else 0, fun c => c == 1⟩
def areaOwn : State := setPrimary areaOwner empty 1 (some 0)

theorem owned_area_initialization_is_coherent : Coherent areaOwner areaOwn := by
  exact own_set_preserves areaOwner empty 1 0 (empty_coherent areaOwner) rfl (Or.inl rfl)

theorem replacing_owned_area_with_alias_needs_restriction :
    ¬ Coherent areaOwner (setPrimary areaOwner areaOwn 1 (some 2)) := by
  intro h
  have bad := h 0
  contradiction

def reowned : Layout := ⟨fun _ => 2, layout.area⟩

theorem changing_ownership_is_not_a_history_step : ¬ Coherent reowned one := by
  intro h
  have bad := h 0
  contradiction

def begun : State := (beginOwn world 0).frames

def nativeEarly (s : State) (f : Frame) : List Nat := if s.bit f then [f] else []
def pointerEarly (l : Layout) (s : State) (f : Frame) : List Nat :=
  if s.pointer (l.owner f) = some f then [f] else []

theorem gap_projected_updates_can_equal_despite_different_guards :
    nativeDestroyRead layout begun 0 = pointerDestroyRead layout begun 0 ∧
    nativeEarly begun 0 ≠ pointerEarly layout begun 0 := by
  constructor
  · simp [nativeDestroyRead, pointerDestroyRead, begun, beginOwn, world, empty,
      writeBit, layout, setPrimary, publish]
  · decide

theorem coherent_guards_agree_for_arbitrary_effects {α : Type}
    (l : Layout) (s : State) (f : Frame) (yes no : α)
    (h : Coherent l s) :
    (if s.bit f then yes else no) =
      (if s.pointer (l.owner f) = some f then yes else no) := by
  simp [h f]

def cleared : State := setPrimary layout one 0 none
def replaced : State := setPrimary layout cleared 0 (some 2)

theorem legitimate_callback_history_can_change_primary : History layout one replaced := by
  exact History.next (History.next (History.refl one) (Step.clear one 0))
    (Step.own cleared 0 2 rfl (Or.inl rfl))

theorem old_destroy_after_admitted_replacement_keeps_new :
    nativeDestroyRead layout replaced 0 = pointerDestroyRead layout replaced 0 ∧
    (nativeDestroyRead layout replaced 0).pointer 0 = some 2 := by
  refine ⟨history_destroy_read_agrees layout one replaced 0 inhabited.2.2
    inhabited.1 inhabited.2.1 legitimate_callback_history_can_change_primary, by decide⟩

theorem selected_init_does_not_erase_other_content :
    (ordinaryInit world 0).rememberedB 7 = some 12 ∧
    (ordinaryInit world 0).rememberedI 7 = some 13 ∧
    (ordinaryInit world 0).observed 7 = true := by decide

theorem suppressed_anchor_and_sticky_remain_selected_effects :
    initialEffects { plainFacts with anchorNames := true, nonDisplay := true, sticky := true } = initialEffects plainFacts := rfl

theorem auto_registration_is_not_a_silent_noop :
    runEffects 0 (initialEffects { plainFacts with autoVisibility := true }) world = none := rfl

#print axioms coherent_not_routed
#print axioms clear_foreign_pointer_breaks_owner_bit
#print axioms owned_area_initialization_is_coherent
#print axioms replacing_owned_area_with_alias_needs_restriction
#print axioms changing_ownership_is_not_a_history_step
#print axioms gap_projected_updates_can_equal_despite_different_guards
#print axioms coherent_guards_agree_for_arbitrary_effects
#print axioms legitimate_callback_history_can_change_primary
#print axioms old_destroy_after_admitted_replacement_keeps_new
#print axioms selected_init_does_not_erase_other_content
#print axioms suppressed_anchor_and_sticky_remain_selected_effects
#print axioms auto_registration_is_not_a_silent_noop
end IndependentPrimary
