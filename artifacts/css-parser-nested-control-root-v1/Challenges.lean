import LinkEmpty
import RawSafety
set_option autoImplicit false
namespace RootNestedChallenges
open PublicCache

def stalled (p : Nat) : Lexeme := ⟨.other, ⟨p, none⟩⟩
def initial : State := constructor ⟨none, none⟩

theorem progress_is_not_automatic : ¬ PublicCleanup.Progress 1 stalled := by
  intro h
  have impossible := h 0 (by decide)
  simp [stalled] at impossible

theorem pending_none_does_not_imply_recovery_completion :
    let result := RawRecovery.recover [97] stalled [] [] initial
    result.cursor.pending = none ∧ RawRecovery.stopped [97] [] result.cursor = false := by
  decide +kernel

theorem finite_byte_fuel_does_not_repair_nonprogress :
    (PublicCleanup.run 1 stalled [] 1 [.parenthesis] initial).complete = false := by
  decide +kernel

def entered : NestedControl.State :=
  ⟨{initial with cursor := ⟨0, some .parenthesis⟩}, [], 0, 75⟩
def changeLimit (s : NestedControl.State) : Bool × NestedControl.State :=
  (false, {s with limit := 9})

theorem arbitrary_callback_limit_persists :
    (LinkEmpty.nested [] stalled [] changeLimit entered).2.limit = 9 := by
  decide +kernel

theorem arbitrary_callback_still_restores_outer_stop_depth :
    let result := (LinkEmpty.nested [] stalled [] changeLimit entered).2
    result.stops = entered.stops ∧ result.depth = entered.depth := by
  decide +kernel

#print axioms progress_is_not_automatic
#print axioms pending_none_does_not_imply_recovery_completion
#print axioms finite_byte_fuel_does_not_repair_nonprogress
#print axioms arbitrary_callback_limit_persists
#print axioms arbitrary_callback_still_restores_outer_stop_depth
end RootNestedChallenges
