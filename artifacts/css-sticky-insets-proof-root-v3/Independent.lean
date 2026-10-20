import StickyFullChallenges
namespace Independent
open StickyNumeric StickyGeometry StickyConsumers StickyRanges StickyEndpoints
open StickyEndpointCaller StickyFullEndpoint StickyFullChallenges RootCrossAxis

def later : Frame2 :=
  {ordinary with identity := 8, currentX := 90, currentY := 70, normalX := 30, normalY := 20}

theorem selected_position_is_separate_from_canonical :
    EntrySafe2 true true [later] ∧
    (machineEntry true true [later]).displacement = some ⟨8,60,⟨40,450⟩,⟨-50,40⟩⟩ ∧
    machineEvaluate (fullCaller2 true true true 50 [later]) = 500 ∧
    machineEvaluate (fullCaller2 true true false 50 [later]) = 500 := by
  decide +kernel

def noSelectedNormal : Frame2 := {later with normalX := 90, normalY := 70}

theorem selected_normal_fallback_preserves_canonical_ranges :
    EntrySafe2 true true [noSelectedNormal] ∧
    (machineEntry true true [noSelectedNormal]).displacement =
      some ⟨8,0,⟨40,450⟩,⟨-50,40⟩⟩ := by
  decide +kernel

def noCanonicalNormal : Frame2 := {later with x := {later.x with normal := 60}}

theorem canonical_normal_fallback_changes_ranges :
    EntrySafe2 true true [noCanonicalNormal] ∧
    (machineEntry true true [noCanonicalNormal]).displacement =
      some ⟨8,60,⟨50,440⟩,⟨-40,50⟩⟩ ∧
    machineEvaluate (fullCaller2 true true true 50 [noCanonicalNormal]) = 50 ∧
    machineEvaluate (fullCaller2 true true false 50 [noCanonicalNormal]) = 490 := by
  decide +kernel

def dangerousLater : Frame2 :=
  {later with currentY := machineMax, normalY := -1}

theorem later_unselected_shift_still_requires_bound :
    ¬ EntrySafe2 true true [dangerousLater] := by decide +kernel

theorem canonical_missing_offsets_skips_dangerous_later_shift :
    EntrySafe2 true true [{dangerousLater with hasOffsets := false}] ∧
    machineEntry true true [{dangerousLater with hasOffsets := false}] = absent := by
  decide +kernel

theorem canonical_inactive_axis_skips_dangerous_later_shift :
    EntrySafe2 true false [dangerousLater] ∧
    machineEntry true false [dangerousLater] = absent := by
  decide +kernel

theorem any_unexecuted_frame_data_is_ignored (axis : Bool) (frames : List Frame2) :
    EntrySafe2 false axis frames ∧ machineEntry false axis frames = absent :=
  ⟨trivial,rfl⟩

theorem both_machine_coordinates_agree (axis : Bool) (f : Frame2)
    (active : entersCore axis f = true) (safe : SelectedSafe axis f) :
    machineCore f = mathCore f := core_pair_refines f (safe active).1

theorem both_executed_shift_coordinates_agree (axis : Bool) (f : Frame2)
    (active : entersCore axis f = true) (live : hasRange (ranges axis f) = true)
    (safe : SelectedSafe axis f) : machineShift f = mathShift f :=
  shift_pair_refines f ((safe active).2.2 live)

end Independent
