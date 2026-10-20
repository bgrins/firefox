import StickyAdmission
namespace IndependentReview
open MaskedSticky StickyComposition StickyLifecycle StickyIndexed StickyMachineLifecycle StickyUpdate StickyJoined StickyAdmission

def leftOnly : Margin := ⟨autoCode, autoCode, autoCode, 0⟩
def driver : Node := {hadNormal := true, normal := ⟨0, 0⟩, current := ⟨0, 0⟩, next := some 1, offsets := some leftOnly, recomputed := some leftOnly, currentLimits := ⟨⟨1, 0, 0, 0⟩, ⟨0, 0, 100, 100⟩⟩}
def follower : Node := {current := ⟨2147483646, 0⟩}
def sequential : Input := ⟨4, 0, false, [0, 0], #[driver, follower]⟩
def start : World := ⟨sequential.nodes, #[], false⟩

theorem initial_safety_does_not_imply_sequential_safety :
    ReadyList sequential.nodes false (chains sequential.nodes) (overs sequential.nodes) [0, 0] ∧
    ContinuationSafe start 0 [0, 1] ∧
    ¬ BatchSafe false (chains sequential.nodes) sequential.nodes [0, 0] ∧
    admitted sequential = false := by decide +kernel

theorem first_step_safe_second_step_overflows :
    (primaryReference sequential.nodes false 0 [0, 1])[1]!.current = ⟨2147483647, 0⟩ ∧
    (run orderedPosition true sequential).2.nodes[1]!.current = ⟨2147483648, 0⟩ ∧
    (machineRun true sequential).2.nodes[1]!.current = ⟨-2147483648, 0⟩ := by decide +kernel

def bounded : Input := {sequential with nodes := #[driver, {follower with current := ⟨2147483645, 0⟩}]}
theorem sequential_bound_is_nonvacuous :
    admitted bounded = true ∧
    (machineRun true bounded).2.nodes[1]!.current = ⟨2147483647, 0⟩ ∧
    (machineRun true bounded).2.exhausted = false := by decide +kernel

def refreshedCase : Input := ⟨4, 0, true, [0], #[{driver with offsets := none}, {follower with current := ⟨20, 7⟩}]⟩
theorem refresh_precedes_geometry_and_movement :
    admitted refreshedCase = true ∧
    (machineRun true refreshedCase).2.nodes[0]!.current = ⟨1, 0⟩ ∧
    (machineRun true refreshedCase).2.nodes[1]!.current = ⟨21, 7⟩ ∧
    (machineRun true {refreshedCase with reflow := false}).2.nodes[1]!.current = ⟨20, 7⟩ := by decide +kernel

def skipped : Input := ⟨4, 0, true, [0], #[{driver with hadNormal := false, next := none, currentLimits := ⟨⟨2147483647, 0, 1, 0⟩, ⟨0, 0, 0, 0⟩⟩, offsets := none}]⟩
theorem absent_normal_refreshes_but_skips_hazard :
    admitted skipped = true ∧
    (machineRun true skipped).2.nodes[0]!.offsets = some leftOnly ∧
    (machineRun true skipped).2.trace =
      #["subtree:1", "order:0", "recompute:0", "normal:0:0", "flush"] := by decide +kernel

def rootChain : Input := ⟨4, 0, false, [0], #[{driver with hadNormal := false, next := none, parent := some 1}, {follower with next := some 2}]⟩
theorem synthetic_root_request_terminates_before_lookup :
    admitted rootChain = true ∧
    (machineRun true rootChain).2.trace =
      #["subtree:-1", "order:0", "normal:0:0", "overflow:1", "next:1:2",
        "overflow:2", "next:2:-1", "flush"] ∧
    (machineRun true rootChain).2.exhausted = false := by decide +kernel

def rootParent : Input := {rootChain with nodes := rootChain.nodes.modify 0 fun n => {n with parent := some 2}}
theorem reflow_root_suppresses_parent_request :
    admitted {rootParent with reflow := true} = true ∧
    (machineRun true {rootParent with reflow := true}).2.trace =
      #["subtree:2", "order:0", "recompute:0", "normal:0:0", "flush"] ∧
    (machineRun true rootParent).2.trace =
      #["subtree:-1", "order:0", "normal:0:0", "overflow:2", "next:2:-1", "flush"] := by decide +kernel

def invalidRoot : Input := {rootParent with nodes := rootParent.nodes.modify 0 fun n => {n with parent := some 3}}
theorem index_above_synthetic_root_is_rejected : admitted invalidRoot = false := by decide +kernel

theorem complete_sequential_array_join (repeatLookup reflow : Bool) (primaries : List Nat)
    (nodes : Array Node) (trace : Array String) (chainMap overflowMap : Nat → List Nat)
    (hg : ReadyList nodes reflow chainMap overflowMap primaries)
    (hs : BatchSafe reflow chainMap nodes primaries) :
    let out := ((machineUpdate repeatLookup reflow primaries).run ⟨nodes, trace, false⟩).2
    out.nodes = updateReference reflow chainMap nodes primaries ∧
    out.exhausted = false ∧ Linked nodes out.nodes :=
  complete_machine_update repeatLookup reflow primaries _ chainMap overflowMap hg hs

theorem complete_array_join_preserves_arbitrary_unvisited_record
    (d : Point) (w : World) (start : Option Nat) (ids : List Nat)
    (hc : Chain w.nodes start ids) (hs : LoopSafe w ids d)
    (i : Nat) (hi : i < w.nodes.size) (hn : i ∉ ids) :
    ((machineMoveChain d (w.nodes.size + 1) start).run w).2.nodes[i]! = w.nodes[i]! := by
  have h := machine_common_translation d ids start w hc hs
  simpa [hn] using h.2.2 i hi
end IndependentReview
