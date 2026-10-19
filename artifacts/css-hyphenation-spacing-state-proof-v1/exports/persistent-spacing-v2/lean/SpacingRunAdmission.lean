import SkipRunNativeStep

namespace HyphenSpacingRunAdmission

open HyphenSkipRanges HyphenSkipRunObservation HyphenSkipRunTraversal

structure AdmittedRun (ranges : List Range) (count : Nat) (run : Run) : Prop where
  positive : 0 < run.length
  inside : run.original < count
  endBound : run.original+run.length ≤ count
  coordinate : run.transformed = lookupOriginal ranges run.original
  observation : run.skipped = (observe ranges count run.original).skipped
  withinObservation : run.length ≤ (observe ranges count run.original).length

theorem traversal_run_admission (ranges : List Range) (count : Nat)
    (valid : WellFormed ranges count) (offset remaining : Nat) :
    ∀ run ∈ traverse ranges count valid offset remaining, AdmittedRun ranges count run := by
  rw [traverse]
  split
  next active =>
    dsimp only
    intro run member
    rcases List.mem_cons.mp member with same | later
    · subst run
      have extent := positive_bounded ranges count offset valid active.1
      exact ⟨by dsimp only; omega,active.1,by dsimp only; omega,rfl,rfl,Nat.min_le_left _ _⟩
    · exact traversal_run_admission ranges count valid _ _ run later
  next inactive => simp
termination_by count-offset
decreasing_by
  all_goals
    have extent := positive_bounded ranges count offset valid (by omega)
    omega

theorem kept_inner_coordinate (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (run : Run) (admitted : AdmittedRun ranges count run) (kept : run.skipped = false)
    (original : Nat) (low : run.original ≤ original) (high : original < run.original+run.length) :
    lookupOriginal ranges original = run.transformed+(original-run.original) := by
  have lengthBound : original-run.original ≤ (observe ranges count run.original).length := by
    have := admitted.withinObservation
    omega
  have coordinate := observed_coordinate_delta ranges count run.original (original-run.original)
    valid admitted.inside lengthBound
  have exactOffset : run.original+(original-run.original) = original := by omega
  have isKept : (observe ranges count run.original).skipped = false := by rw [← admitted.observation,kept]
  simpa [exactOffset,isKept,← admitted.coordinate] using coordinate

def clusterForward (stop : Nat → Bool) (current finish : Nat) : Nat :=
  if active : current < finish then
    if stop current then current else clusterForward stop (current+1) finish
  else current
termination_by finish-current

def clusterEnd (stop : Nat → Bool) (current finish : Nat) : Nat :=
  clusterForward stop (current+1) finish - 1

theorem cluster_forward_bounds (stop : Nat → Bool) (current finish : Nat) (bound : current ≤ finish) :
    current ≤ clusterForward stop current finish ∧ clusterForward stop current finish ≤ finish := by
  rw [clusterForward]
  split
  next active =>
    split
    next stopped => exact ⟨Nat.le_refl _,bound⟩
    next continuing =>
      have later := cluster_forward_bounds stop (current+1) finish (by omega)
      omega
  next inactive => exact ⟨Nat.le_refl _,bound⟩
termination_by finish-current

theorem cluster_end_bounds (stop : Nat → Bool) (current finish : Nat) (inside : current < finish) :
    current ≤ clusterEnd stop current finish ∧ clusterEnd stop current finish < finish := by
  have search := cluster_forward_bounds stop (current+1) finish (by omega)
  unfold clusterEnd
  omega

theorem word_spacing_target (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (run : Run) (admitted : AdmittedRun ranges count run) (kept : run.skipped = false)
    (index : Nat) (indexBound : index < run.length) (stop : Nat → Bool) :
    let target := lookupOriginal ranges (clusterEnd stop (run.original+index) (run.original+run.length))
    run.transformed ≤ target ∧ target < run.transformed+run.length := by
  dsimp only
  have endpoint := cluster_end_bounds stop (run.original+index) (run.original+run.length) (by omega)
  rw [kept_inner_coordinate ranges count valid run admitted kept _ (by omega) endpoint.2]
  omega

theorem query_write_target (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (offset remaining : Nat) (bounded : offset ≤ count)
    (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges count)
    (run : Run) (member : run ∈ traverse ranges count valid offset remaining)
    (kept : run.skipped = false) (target : Nat)
    (low : run.transformed ≤ target) (high : target < run.transformed+run.length) :
    lookupOriginal ranges offset ≤ target ∧
      target-lookupOriginal ranges offset < remaining := by
  have inRun : target ∈ contribution run := by
    simp only [contribution,kept,Bool.false_eq_true,↓reduceIte,List.mem_range']
    exact ⟨target-run.transformed,by omega,by omega⟩
  have inAll : target ∈ (traverse ranges count valid offset remaining).flatMap contribution :=
    List.mem_flatMap.mpr ⟨run,member,inRun⟩
  rw [initialized_coordinates ranges count valid offset remaining bounded available] at inAll
  simp only [List.mem_range'] at inAll
  omega

theorem justification_indexes (queryStart queryEnd arrayStart arrayLength index : Nat)
    (queryAfterArray : arrayStart ≤ queryStart)
    (low : queryStart ≤ index) (high : index < min queryEnd (arrayStart+arrayLength)) :
    index-queryStart < queryEnd-queryStart ∧ index-arrayStart < arrayLength := by omega

end HyphenSpacingRunAdmission
