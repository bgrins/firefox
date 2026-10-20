import StickyFullEndpoint
import RootCrossAxis
namespace StickyFullChallenges
open StickyNumeric StickyGeometry StickyConsumers StickyEndpoints StickyEndpointCaller StickyFullEndpoint RootCrossAxis

theorem rejects_root_shift : ¬ EntrySafe2 true true [shiftFrame] := by decide +kernel

theorem rejects_root_core : ¬ EntrySafe2 true true [coreFrame] := by decide +kernel

theorem rejects_coordinate_bounded_core : ¬ EntrySafe2 true true [boundedFrame] := by decide +kernel

theorem old_premises_remain_insufficient :
    EntrySafe true ([boundedFrame].map (project true)) ∧
    CallerSafe false 50 (nativeTimeline true ([boundedFrame].map (project true))) ∧
    ¬ EntrySafe2 true true [boundedFrame] := by decide +kernel

theorem no_container_no_execution (axis : Bool) (frames : List Frame2) :
    EntrySafe2 false axis frames ∧ machineEntry false axis frames = absent := by
  exact ⟨trivial,rfl⟩

theorem no_selected_no_execution (axis : Bool) (frames : List Frame2)
    (h : nativeScan eligible2 none frames = .absent) :
    EntrySafe2 true axis frames ∧ machineEntry true axis frames = absent := by
  simp [EntrySafe2,machineEntry,h]

theorem multiple_no_execution (axis : Bool) (frames : List Frame2)
    (h : nativeScan eligible2 none frames = .multiple) :
    EntrySafe2 true axis frames ∧ machineEntry true axis frames = absent := by
  simp [EntrySafe2,machineEntry,h]

theorem selected_early_return (axis : Bool) (f : Frame2) (h : entersCore axis f = false) :
    SelectedSafe axis f ∧ machineSelected axis f = absent := by
  simp [SelectedSafe,machineSelected,h]

theorem root_witness_early_returns :
    ∀ f ∈ [shiftFrame,coreFrame,boundedFrame],
      EntrySafe2 false true [f] ∧
      EntrySafe2 true true [{f with sticky := false}] ∧
      EntrySafe2 true true [f,f] ∧
      EntrySafe2 true true [{f with hasOffsets := false}] ∧
      EntrySafe2 true true [{f with x := {f.x with insets := ⟨none,none⟩}}] := by
  decide +kernel

def ordinary : Frame2 := {sampleFrame with x := horizontal}

theorem ordinary_entry_inhabited :
    EntrySafe2 true true [ordinary] ∧
    EntrySafe2 true false [ordinary] ∧
    (machineEntry true true [ordinary]).displacement = some ⟨7,10,⟨40,450⟩,⟨-50,40⟩⟩ := by
  decide +kernel

theorem ordinary_two_axis_caller :
    machineEvaluate (fullCaller2 true true false 50 [ordinary]) = 500 ∧
    machineEvaluate (fullCaller2 true true true 50 [ordinary]) = 500 := by
  decide +kernel

def swapFrame (f : Frame2) : Frame2 :=
  {f with x := f.y, y := f.x, xEndFar := f.yEndFar, yEndFar := f.xEndFar, currentX := f.currentY, currentY := f.currentX, normalX := f.normalY, normalY := f.normalX}

theorem opposite_selection_rejects :
    ∀ f ∈ [shiftFrame,coreFrame,boundedFrame], ¬ EntrySafe2 true false [swapFrame f] := by
  decide +kernel

theorem opposite_selection_positive :
    EntrySafe2 true false [swapFrame ordinary] ∧
    (machineEntry true false [swapFrame ordinary]).displacement =
      (machineEntry true true [ordinary]).displacement := by decide +kernel

theorem selected_core_demands_both (axis : Bool) (f : Frame2)
    (guard : entersCore axis f = true) (safe : SelectedSafe axis f) :
    StickyMachineGeometry.ArithmeticSafe (coreCodes f).1 ∧
    StickyMachineGeometry.ArithmeticSafe (coreCodes f).2 := (safe guard).1

theorem selected_shift_demands_both (axis : Bool) (f : Frame2)
    (guard : entersCore axis f = true) (live : hasRange (ranges axis f) = true)
    (safe : SelectedSafe axis f) :
    Admitted (shiftCodes f).1 ∧ Admitted (shiftCodes f).2 := (safe guard).2.2 live

theorem executed_shift_bound (axis : Bool) (f : Frame2)
    (guard : entersCore axis f = true) (live : hasRange (ranges axis f) = true)
    (safe : SelectedSafe axis f) :
    InMachine (mathShift f).1 ∧ InMachine (mathShift f).2 := by
  have h := selected_shift_demands_both axis f guard live safe
  exact ⟨admitted_result_bound _ h.1,admitted_result_bound _ h.2⟩

end StickyFullChallenges
