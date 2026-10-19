import SkipRunIndexed
import HyphenationProviderWrites

namespace HyphenSkipRunNativeStep

open HyphenSkipRanges HyphenSkipRunObservation HyphenSkipRunIndexed HyphenSkipRunTraversal

structure Iterator where
  original : Nat
  remaining : Nat
  runLength : Nat
  skipped : Bool
  deriving DecidableEq, Repr

def advancePrevious (state : Iterator) : Iterator :=
  if state.runLength = 0 then state else
    {state with original := state.original+state.runLength, remaining := if state.skipped then state.remaining else state.remaining-state.runLength}

def nextRun (ranges : List Range) (count : Nat) (state : Iterator) : Option Iterator :=
  let ready := advancePrevious state
  if ready.remaining = 0 then none else
    let observation := nativeObservation ranges count ready.original
    some {ready with runLength := min observation.length ready.remaining,skipped := observation.skipped}

def emitted (ranges : List Range) (state : Iterator) : Run :=
  ⟨state.original,lookupOriginal ranges state.original,state.runLength,state.skipped⟩

theorem initial_advance (offset remaining : Nat) :
    advancePrevious ⟨offset,remaining,0,false⟩ = ⟨offset,remaining,0,false⟩ := rfl

theorem next_run_exact (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (state : Iterator) (active : 0 < (advancePrevious state).remaining) :
    nextRun ranges count state = some
      {(advancePrevious state) with
        runLength := min (observe ranges count (advancePrevious state).original).length
          (advancePrevious state).remaining,
        skipped := (observe ranges count (advancePrevious state).original).skipped} := by
  simp only [nextRun,Nat.ne_of_gt active,↓reduceIte]
  rw [complete_indexed_observation ranges count _ valid]

theorem next_run_advances (ranges : List Range) (count : Nat) (valid : WellFormed ranges count)
    (state : Iterator) (active : 0 < (advancePrevious state).remaining)
    (inside : (advancePrevious state).original < count) :
    let ready := advancePrevious state
    let observation := observe ranges count ready.original
    let length := min observation.length ready.remaining
    let output : Iterator := {ready with runLength := length,skipped := observation.skipped}
    nextRun ranges count state = some output ∧
      0 < output.runLength ∧ output.original+output.runLength ≤ count ∧
      (advancePrevious output).original = ready.original+length ∧
      (advancePrevious output).remaining =
        (if observation.skipped then ready.remaining else ready.remaining-length) := by
  dsimp only
  have extent := positive_bounded ranges count (advancePrevious state).original valid inside
  have amount : 0 < min (observe ranges count (advancePrevious state).original).length
      (advancePrevious state).remaining := by omega
  refine ⟨next_run_exact ranges count valid state active,amount,by omega,?_,?_⟩
  · rw [advancePrevious]
    simp only [Nat.ne_of_gt amount,↓reduceIte]
  · rw [advancePrevious]
    simp only [Nat.ne_of_gt amount,↓reduceIte]

theorem query_start_admission (ranges : List Range) (count start length : Nat)
    (valid : WellFormed ranges count) (queryBound : start+length ≤ count-total ranges) :
    lookupSkipped ranges start ≤ count ∧
      lookupOriginal ranges (lookupSkipped ranges start) = start ∧
      lookupOriginal ranges (lookupSkipped ranges start)+length ≤ lookupOriginal ranges count := by
  obtain ⟨bounded,inverse⟩ := skipped_iterator_bounded_inverse ranges count start valid (by omega)
  refine ⟨bounded,inverse,?_⟩
  rw [inverse,original_at_end ranges count valid]
  exact queryBound

theorem automatic_original_read_bound (ranges : List Range) (count start length index : Nat)
    (valid : WellFormed ranges count) (queryBound : start+length ≤ count-total ranges)
    (indexBound : index < length) :
    lookupSkipped ranges (start+index) < count := by
  obtain ⟨bounded,inverse⟩ := skipped_iterator_bounded_inverse ranges count (start+index) valid (by omega)
  by_cases same : lookupSkipped ranges (start+index) = count
  · rw [same,original_at_end ranges count valid] at inverse
    omega
  · omega

theorem initialized_native_query (ranges : List Range) (count start length : Nat)
    (valid : WellFormed ranges count) (queryBound : start+length ≤ count-total ranges) :
    (traverse ranges count valid (lookupSkipped ranges start) length).flatMap contribution =
      List.range' start length := by
  obtain ⟨bounded,inverse,available⟩ := query_start_admission ranges count start length valid queryBound
  rw [initialized_coordinates ranges count valid _ _ bounded available,inverse]

theorem complete_provider_query_length (inputs : HyphenationProviderWrites.Inputs)
    (wrap enabled allowSoft : Bool) (ranges : List Range) (count start length : Nat)
    (valid : WellFormed ranges count) (queryBound : start+length ≤ count-total ranges) :
    (HyphenationProviderWrites.provide inputs wrap enabled allowSoft length start
      (traverse ranges count valid (lookupSkipped ranges start) length)).length = length := by
  obtain ⟨bounded,inverse,available⟩ := query_start_admission ranges count start length valid queryBound
  simpa only [inverse] using HyphenationProviderWrites.full_provider_length inputs wrap enabled allowSoft ranges count valid
    _ _ bounded available

end HyphenSkipRunNativeStep
