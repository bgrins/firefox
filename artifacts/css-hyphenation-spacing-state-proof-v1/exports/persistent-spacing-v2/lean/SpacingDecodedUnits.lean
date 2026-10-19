import SpacingPhases
import SkipProviderClip

namespace HyphenSpacingDecodedUnits

open HyphenSkipRanges HyphenSkipRunObservation HyphenSkipRunTraversal HyphenSpacingRunAdmission
open HyphenSpacingValues

structure Providers where
  canBefore : Nat → Bool
  canAfter : Nat → Bool
  cursiveAt : Nat → Bool
  baseCursiveAt : Nat → Bool
  wordSpaceAt : Nat → Bool
  classAt : Nat → Nat
  clusterStart : Nat → Bool
  clusterStop : Nat → Bool
  textIncludesCJK : Bool
  frameStart : Nat

def fromRun (ranges : List Range) (queryStart : Nat) (providers : Providers)
    (run : Run) (index : Nat) : HyphenSpacingValues.Unit :=
  let original := run.original+index
  let transformed := run.transformed+index
  let wordEnd := clusterEnd providers.clusterStop original (run.original+run.length)
  ⟨transformed-queryStart,lookupOriginal ranges wordEnd-queryStart,
    providers.canBefore transformed,providers.canAfter transformed,
    providers.cursiveAt original,providers.baseCursiveAt original,
    providers.wordSpaceAt original,
    (providers.textIncludesCJK || original == providers.frameStart) && providers.clusterStart transformed,
    providers.classAt original⟩

def runUnits (ranges : List Range) (queryStart : Nat) (providers : Providers)
    (run : Run) : List HyphenSpacingValues.Unit :=
  if run.skipped then [] else (List.range run.length).map (fromRun ranges queryStart providers run)

def queryUnits (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (offset remaining : Nat) (providers : Providers) : List HyphenSpacingValues.Unit :=
  (traverse ranges count valid offset remaining).flatMap
    (runUnits ranges (lookupOriginal ranges offset) providers)

theorem constructed_unit_bounds (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (offset remaining : Nat) (providers : Providers) (bounded : offset ≤ count)
    (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges count)
    (run : Run) (member : run ∈ traverse ranges count valid offset remaining)
    (kept : run.skipped = false) (index : Nat) (inside : index < run.length) :
    (fromRun ranges (lookupOriginal ranges offset) providers run index).index < remaining ∧
      (fromRun ranges (lookupOriginal ranges offset) providers run index).wordTarget < remaining := by
  have admitted := traversal_run_admission ranges count valid offset remaining run member
  have direct := query_write_target ranges count valid offset remaining bounded available run member kept
    (run.transformed+index) (by omega) (by omega)
  have target := word_spacing_target ranges count valid run admitted kept index inside providers.clusterStop
  have word := query_write_target ranges count valid offset remaining bounded available run member kept
    _ target.1 target.2
  exact ⟨direct.2,word.2⟩

theorem complete_unit_bounds (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (offset remaining : Nat) (providers : Providers) (bounded : offset ≤ count)
    (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges count) :
    ∀ unit ∈ queryUnits ranges count valid offset remaining providers,
      unit.index < remaining ∧ unit.wordTarget < remaining := by
  intro unit member
  simp only [queryUnits,List.mem_flatMap] at member
  obtain ⟨run,runMember,unitMember⟩ := member
  unfold runUnits at unitMember
  split at unitMember
  next skipped => simp at unitMember
  next kept =>
    obtain ⟨index,indexMember,equal⟩ := List.mem_map.mp unitMember
    subst unit
    exact constructed_unit_bounds ranges count valid offset remaining providers bounded available run runMember
      (by simpa using kept) index (List.mem_range.mp indexMember)

theorem decoded_inner_coordinate (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (run : Run) (admitted : AdmittedRun ranges count run) (kept : run.skipped = false)
    (index : Nat) (inside : index < run.length) :
    lookupOriginal ranges (run.original+index) = run.transformed+index := by
  simpa using kept_inner_coordinate ranges count valid run admitted kept (run.original+index) (by omega) (by omega)

theorem constructed_trace_bounded (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (offset remaining : Nat) (providers : Providers) (config : Config Value) (control : Control)
    (bounded : offset ≤ count) (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges count) :
    Bounded remaining (referenceTrace config control (queryUnits ranges count valid offset remaining providers)) :=
  trace_bounds config control _ remaining (complete_unit_bounds ranges count valid offset remaining providers bounded available)

theorem spacing_preserves_outside (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (offset remaining : Nat) (providers : Providers) (config : Config Value) (state : NativeState Value)
    (bounded : offset ≤ count) (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges count)
    (index : Nat) (outside : remaining ≤ index) (side : Side) :
    (nativeLoop config state (queryUnits ranges count valid offset remaining providers)).store index side =
      state.store index side := by
  rw [whole_loop_reference]
  exact writes_leave_outside _ _ _ remaining index side
    (constructed_trace_bounded _ _ _ _ _ _ _ _ bounded available) outside


def clusterBackward (stop : Nat → Bool) (first current : Nat) : Nat :=
  if active : first < current then
    if stop current then current else clusterBackward stop first (current-1)
  else current
termination_by current

theorem cluster_backward_bounds (stop : Nat → Bool) (first current : Nat) (lower : first ≤ current) :
    first ≤ clusterBackward stop first current ∧ clusterBackward stop first current ≤ current := by
  rw [clusterBackward]
  split
  next active =>
    split
    next stopped => exact ⟨lower,Nat.le_refl _⟩
    next moving =>
      have previous := cluster_backward_bounds stop first (current-1) (by omega)
      omega
  next done => exact ⟨lower,Nat.le_refl _⟩
termination_by current

theorem base_scalar_read_inside_run (stop : Nat → Bool) (run : Run) (index : Nat)
    (inside : index < run.length) :
    run.original ≤ clusterBackward stop run.original (run.original+index) ∧
      clusterBackward stop run.original (run.original+index) < run.original+run.length := by
  have bound := cluster_backward_bounds stop run.original (run.original+index) (by omega)
  omega

end HyphenSpacingDecodedUnits
