import StickyAdmission
import ReviewChallenges

namespace StickyJoinedChallenges
open MaskedSticky StickyComposition StickyLifecycle StickyIndexed StickyMachineLifecycle StickyUpdate StickyJoined StickyAdmission

instance graphDecidable (nodes : Array Node) (first : Nat) (ids : List Nat) :
    Decidable (Graph nodes first ids) := by unfold Graph; infer_instance

theorem reviewed_cycle_rejected : admitted Review.cyclic = false := by decide +kernel

theorem reviewed_subtraction_rejected : admitted Review.huge = false := by decide +kernel

def ordinary : Input := ⟨3, 0, false, [0], #[ {Review.stableNode with next := some 1, offsets := some ⟨autoCode, autoCode, autoCode, 0⟩, currentLimits := ⟨⟨20, 0, 0, 0⟩, ⟨0, 0, 100, 100⟩⟩, ignoreLimits := ⟨⟨20, 0, 0, 0⟩, ⟨0, 0, 100, 100⟩⟩}, {Review.stableNode with first := 0, hadNormal := false, current := ⟨19, 23⟩}, {Review.stableNode with first := 2, current := ⟨81, 91⟩}]⟩

theorem ordinary_graph_valid : Graph ordinary.nodes 0 [0, 1] := by decide +kernel

theorem ordinary_full_admitted : admitted ordinary = true := by decide +kernel

theorem ordinary_independent_array :
    let r := machineRun true ordinary
    r.2.nodes[0]!.current = ⟨20, 11⟩ ∧ r.2.nodes[1]!.current = ⟨32, 23⟩ ∧
    r.2.nodes[2]!.current = ⟨81, 91⟩ ∧ r.2.exhausted = false := by decide +kernel

def firstOnly : World := ((Review.wrongContinuations orderedPosition 0).run ⟨ordinary.nodes, #[], false⟩).2

theorem wrong_caller_fails_independent_reference :
    firstOnly.nodes[1]!.current ≠
      (independentObservation ordinary).2[1]!.current := by decide +kernel

def addOverflow : Input := {ordinary with nodes := #[ {ordinary.nodes[0]! with normal := ⟨0, 0⟩, current := ⟨0, 0⟩, currentLimits := ⟨⟨1, 0, 0, 0⟩, ⟨0, 0, 100, 100⟩⟩}, {ordinary.nodes[1]! with current := ⟨2147483647, 0⟩}]}

theorem continuation_addition_rejected :
    admitted addOverflow = false ∧
    PointSafe (referenceDelta ⟨addOverflow.nodes, #[], false⟩ 0) ∧
    (machineRun true addOverflow).2.nodes[1]!.current = ⟨-2147483648, 0⟩ ∧
    (run orderedPosition true addOverflow).2.nodes[1]!.current = ⟨2147483648, 0⟩ := by
  decide +kernel

def yAddOverflow : Input := {ordinary with nodes := #[{ordinary.nodes[0]! with normal := ⟨0, 0⟩, current := ⟨0, 0⟩, offsets := some ⟨0, autoCode, autoCode, autoCode⟩, currentLimits := ⟨⟨0, 1, 0, 0⟩, ⟨0, 0, 100, 100⟩⟩}, {ordinary.nodes[1]! with current := ⟨0, 2147483647⟩}]}

theorem second_coordinate_addition_rejected :
    admitted yAddOverflow = false ∧
    (machineRun true yAddOverflow).2.nodes[1]!.current = ⟨0, -2147483648⟩ ∧
    (run orderedPosition true yAddOverflow).2.nodes[1]!.current = ⟨0, 2147483648⟩ := by
  decide +kernel

def missingNormal : Input := {ordinary with nodes := #[ {ordinary.nodes[0]! with hadNormal := false, next := none, currentLimits := ⟨⟨2147483647, 0, 1, 0⟩, ⟨0, 0, 0, 0⟩⟩}]}

theorem missing_normal_does_not_enter_geometry :
    admitted missingNormal = true ∧
    ¬ RectSafe missingNormal.nodes[0]!.currentLimits.stick ∧
    (machineRun true missingNormal).2.trace = #["normal:0:0"] := by decide +kernel

def unusedHazard : Input := {ordinary with nodes := ordinary.nodes.push {Review.hugeNode with first := 3, normal := ⟨2147483647, -2147483648⟩}}

theorem unvisited_hazard_unchanged :
    admitted unusedHazard = true ∧
    (machineRun true unusedHazard).2.nodes[3]!.current = unusedHazard.nodes[3]!.current := by
  decide +kernel

def badCanonical : Array Node := ordinary.nodes.modify 1 fun n => {n with first := 1} def badParent : Array Node := ordinary.nodes.modify 1 fun n => {n with parent := some 2}

theorem graph_canonical_and_parent_premises_needed :
    ¬ Graph badCanonical 0 [0, 1] ∧ ¬ Graph badParent 0 [0, 1] := by decide +kernel

def laterFrame : Input := {ordinary with action := 5, target := 1, nodes := ordinary.nodes.modify 1 fun n => {n with sticky := true, hasContainer := true}}

theorem later_frame_uses_canonical_delta_and_own_normal :
    admitted laterFrame = true ∧ (machineRun true laterFrame).1 = some ⟨32, 23⟩ := by
  decide +kernel

def fallback : Input := {Review.huge with action := 5, nodes := #[{Review.hugeNode with sticky := true, hasContainer := false, fallback := ⟨41, 42⟩}]}

theorem inactive_wrapper_does_not_require_translation :
    admitted fallback = true ∧ (machineRun true fallback).1 = some ⟨41, 42⟩ := by
  decide +kernel

def refreshedInput : Input := {ordinary with action := 4, reflow := true, primaries := [0, 2], nodes := ordinary.nodes.modify 0 fun n => {n with recomputed := none}}

theorem reflow_sequential_update_nonvacuity :
    admitted refreshedInput = true ∧
    (machineRun true refreshedInput).2.nodes[0]!.current = ⟨7, 11⟩ ∧
    (machineRun true refreshedInput).2.nodes[1]!.current = ⟨19, 23⟩ ∧
    (machineRun true refreshedInput).2.nodes[2]!.current = ⟨7, 11⟩ ∧
    (machineRun true refreshedInput).2.exhausted = false := by decide +kernel

def badOverflow : Input := {ordinary with action := 4, nodes := (ordinary.nodes.modify 0 fun n => {n with parent := some 2}).modify 2 fun n => {n with next := some 2}}

theorem overflow_cycle_rejected : admitted badOverflow = false := by decide +kernel

def overflowRoot : Input := {ordinary with action := 4, nodes := ordinary.nodes.modify 0 fun n => {n with parent := some ordinary.nodes.size}}

theorem synthetic_root_terminal_admitted :
    admitted overflowRoot = true ∧ (machineRun true overflowRoot).2.exhausted = false := by
  decide +kernel

theorem source_fuel_not_assumed :
    (moveChain ⟨3, 5⟩ 0 (some 0) |>.run Review.chainWorld).2.exhausted = true ∧
    (moveChain ⟨3, 5⟩ (Review.chainWorld.nodes.size + 1) (some 0)
      |>.run Review.chainWorld).2.exhausted = false := by decide +kernel

end StickyJoinedChallenges
