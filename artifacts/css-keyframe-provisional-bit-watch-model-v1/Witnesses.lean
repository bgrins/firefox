import Provisional

namespace ProvisionalWatches

def allocatedEmpty : Option (List Nat) := some []
def emptyPair : Nat × AttributeWatches.Watch := (1, ⟨7, allocatedEmpty.getD []⟩)
def provisionalPair : Nat × AttributeWatchBits.BitWatch := (1, ⟨7, allocatedEmpty.isSome⟩)
def requiredPair : Nat × AttributeWatches.Watch := (1, ⟨7, [11]⟩)
def clearedPair : Nat × AttributeWatchBits.BitWatch := (1, ⟨7, false⟩)
def missingEntry : AttributeWatches.Entry := ⟨7, 5, [⟨11, none⟩]⟩
def extraHistory : List Event :=
  [.completedInstall 1 ⟨7, 5, []⟩ allocatedEmpty.isSome, .provisional (fun id => id == 1),
   .completed (.change 7 99)]
def survivorHistory : List Event :=
  [.completed (.install 1 missingEntry), .completed (.install 2 ⟨7, 5, [⟨12, none⟩]⟩),
   .provisional (fun _ => true), .completed (.remove 1), .completed (.change 7 12)]
def replacementHistory : List Event :=
  [.completed (.install 1 missingEntry), .provisional (fun _ => true),
   .completed (.install 1 ⟨7, 5, []⟩), .completed (.change 7 11)]

theorem allocated_empty_is_conservative : PairRel emptyPair provisionalPair := by
  unfold PairRel
  decide +kernel

theorem provisional_empty_permits_extra_update :
    (fineRun extraHistory).pending = [] ∧ (coarseRun extraHistory).pending = [7] := by
  decide +kernel

theorem absent_survivor_remains_admitted :
    (fineRun survivorHistory).pending = [7] ∧ (coarseRun survivorHistory).pending = [7] := by
  decide +kernel

theorem completed_empty_replacement_clears_obsolete_bit :
    (fineRun replacementHistory).pending = [] ∧ (coarseRun replacementHistory).pending = [] := by
  decide +kernel

theorem clearing_required_bit_breaks_relation : ¬ PairRel requiredPair clearedPair := by
  unfold PairRel
  decide +kernel

end ProvisionalWatches
