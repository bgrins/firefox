import SkipRunNativeStep

namespace HyphenSkipProviderClip

open HyphenSkipRanges HyphenSkipRunObservation

theorem kept_prefix_monotone (source : List Bool) (first finish : Nat) (ordered : first ≤ finish) :
    keptPrefix source first ≤ keptPrefix source finish := by
  have split := HyphenTransformedSlices.filtered_prefix_length source (fun c => !c) first finish ordered
  unfold keptPrefix
  omega

theorem original_monotone (state : State) (source : List Bool) (rep : Represents state source)
    (first finish : Nat) (ordered : first ≤ finish) (bounded : finish ≤ state.count) :
    lookupOriginal state.reversedRanges first ≤ lookupOriginal state.reversedRanges finish := by
  have lowBound : first ≤ state.count := by omega
  have low := original_iterator_refines_kept_prefix state source first rep
  have high := original_iterator_refines_kept_prefix state source finish rep
  simp only [Nat.min_eq_left lowBound,Nat.min_eq_left bounded] at low high
  rw [low,high]
  exact kept_prefix_monotone source first finish ordered

theorem strict_inverse_bound (ranges : List Range) (count offset : Nat)
    (valid : WellFormed ranges count) (bound : offset < count-total ranges) :
    lookupSkipped ranges offset < count := by
  obtain ⟨bounded,inverse⟩ := skipped_iterator_bounded_inverse ranges count offset valid (by omega)
  by_cases same : lookupSkipped ranges offset = count
  · rw [same,original_at_end ranges count valid] at inverse
    omega
  · omega

theorem inverse_is_kept (ranges : List Range) (count offset : Nat)
    (valid : WellFormed ranges count) (bound : offset < count-total ranges) :
    (observe ranges count (lookupSkipped ranges offset)).skipped = false := by
  induction ranges generalizing count with
  | nil =>
    have inside : offset < count := by simpa [total] using bound
    simp [lookupSkipped,observe,Nat.ne_of_lt inside]
  | cons r rest ih =>
    have delta := valid.2.1
    have last := valid.1
    have olderTotal := total_bound rest r.start valid.2.2
    simp only [lookupSkipped]
    split
    next before =>
      have oldBound : offset < r.start-total rest := by omega
      have inside := strict_inverse_bound rest r.start offset valid.2.2 oldBound
      simp only [observe,inside,↓reduceIte]
      exact ih r.start valid.2.2 oldBound
    next after =>
      have original := strict_inverse_bound (r::rest) count offset valid bound
      simp only [lookupSkipped,ite_eq_right after] at original
      have startBound : r.start ≤ r.finish+offset-(r.start-r.delta) := by unfold Range.finish; omega
      have finishBound : r.finish ≤ r.finish+offset-(r.start-r.delta) := by omega
      simp [observe,Nat.not_lt.mpr startBound,Nat.not_lt.mpr finishBound,Nat.ne_of_lt original]

theorem inverse_query_inside_source_slice (state : State) (source : List Bool)
    (rep : Represents state source) (first finish query : Nat)
    (ordered : first ≤ finish) (bounded : finish ≤ state.count)
    (queryLow : lookupOriginal state.reversedRanges first ≤ query)
    (queryHigh : query < lookupOriginal state.reversedRanges finish) :
    first ≤ lookupSkipped state.reversedRanges query ∧
      lookupSkipped state.reversedRanges query < finish := by
  have endBound := original_monotone state source rep finish state.count bounded (Nat.le_refl _)
  rw [original_at_end state.reversedRanges state.count rep.2.1] at endBound
  have queryBound : query < state.count-total state.reversedRanges := by omega
  have originalBound := strict_inverse_bound state.reversedRanges state.count query rep.2.1 queryBound
  have inverse := (skipped_iterator_bounded_inverse state.reversedRanges state.count query rep.2.1 (by omega)).2
  have kept := inverse_is_kept state.reversedRanges state.count query rep.2.1 queryBound
  have extent := positive_bounded state.reversedRanges state.count
    (lookupSkipped state.reversedRanges query) rep.2.1 originalBound
  constructor
  · by_cases low : first ≤ lookupSkipped state.reversedRanges query
    · exact low
    · have nextBound : lookupSkipped state.reversedRanges query+1 ≤ first := by omega
      have nextCoordinate := observed_coordinate_delta state.reversedRanges state.count
        (lookupSkipped state.reversedRanges query) 1 rep.2.1 originalBound (by omega)
      simp only [kept,Bool.false_eq_true,↓reduceIte] at nextCoordinate
      have monotone := original_monotone state source rep _ first nextBound (by omega)
      rw [nextCoordinate,inverse] at monotone
      omega
  · by_cases high : lookupSkipped state.reversedRanges query < finish
    · exact high
    · have monotone := original_monotone state source rep finish
        (lookupSkipped state.reversedRanges query) (by omega) (by omega)
      rw [inverse] at monotone
      omega

theorem capped_run_inside_slice (ranges : List Range) (count offset remaining sourceEnd : Nat)
    (valid : WellFormed ranges count) (inside : offset < count)
    (offsetBound : offset ≤ sourceEnd)
    (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges sourceEnd) :
    offset+min (observe ranges count offset).length remaining ≤ sourceEnd := by
  by_cases bounded : offset+min (observe ranges count offset).length remaining ≤ sourceEnd
  · exact bounded
  · have partialBound : sourceEnd-offset ≤ (observe ranges count offset).length := by omega
    have endpoint := observed_coordinate_delta ranges count offset (sourceEnd-offset) valid inside partialBound
    have exactOffset : offset+(sourceEnd-offset) = sourceEnd := by omega
    rw [exactOffset] at endpoint
    cases kept : (observe ranges count offset).skipped <;>
      simp only [kept,Bool.false_eq_true,↓reduceIte,Nat.add_zero] at endpoint <;> omega

theorem traversal_inside_slice (ranges : List Range) (count offset remaining sourceEnd : Nat)
    (valid : WellFormed ranges count) (offsetBound : offset ≤ sourceEnd)
    (available : lookupOriginal ranges offset+remaining ≤ lookupOriginal ranges sourceEnd) :
    ∀ run ∈ HyphenSkipRunTraversal.traverse ranges count valid offset remaining,
      offset ≤ run.original ∧ run.original+run.length ≤ sourceEnd := by
  rw [HyphenSkipRunTraversal.traverse]
  split
  next active =>
    dsimp only
    have endBound := capped_run_inside_slice ranges count offset remaining sourceEnd valid active.1 offsetBound available
    have extent := positive_bounded ranges count offset valid active.1
    have delta := observed_coordinate_delta ranges count offset
      (min (observe ranges count offset).length remaining) valid active.1 (Nat.min_le_left _ _)
    have nextAvailable : lookupOriginal ranges (offset+min (observe ranges count offset).length remaining)+
        (if (observe ranges count offset).skipped then remaining else remaining-min (observe ranges count offset).length remaining)
        ≤ lookupOriginal ranges sourceEnd := by
      cases skipped : (observe ranges count offset).skipped <;>
        simp only [skipped,Bool.false_eq_true,↓reduceIte,Nat.add_zero] at delta ⊢ <;> omega
    intro run member
    rcases List.mem_cons.mp member with same | later
    · subst run; exact ⟨Nat.le_refl _,endBound⟩
    · have old := traversal_inside_slice ranges count _ _ sourceEnd valid endBound nextAvailable run later
      exact ⟨by omega,old.2⟩
  next inactive => simp
termination_by count-offset
decreasing_by all_goals omega

theorem rebased_query_read (state : State) (source : List Bool) (rep : Represents state source)
    (first finish query localFirst localEnd : Nat) (delta : Int)
    (ordered : first ≤ finish) (bounded : finish ≤ state.count)
    (queryLow : lookupOriginal state.reversedRanges first ≤ query)
    (queryHigh : query < lookupOriginal state.reversedRanges finish)
    (firstBinding : (first : Int) = (localFirst : Int)+delta)
    (endBinding : (finish : Int) = (localEnd : Int)+delta) :
    let nativeLocal := (lookupSkipped state.reversedRanges query : Int)-delta
    (localFirst : Int) ≤ nativeLocal ∧ nativeLocal < (localEnd : Int) ∧ 0 ≤ nativeLocal := by
  have bounds := inverse_query_inside_source_slice state source rep first finish query
    ordered bounded queryLow queryHigh
  dsimp only
  omega

theorem rebased_traversal_read (state : State) (source : List Bool) (rep : Represents state source)
    (first finish query remaining localFirst localEnd : Nat) (delta : Int)
    (ordered : first ≤ finish) (bounded : finish ≤ state.count)
    (queryLow : lookupOriginal state.reversedRanges first ≤ query)
    (queryHigh : query+remaining ≤ lookupOriginal state.reversedRanges finish)
    (positive : 0 < remaining)
    (firstBinding : (first : Int) = (localFirst : Int)+delta)
    (endBinding : (finish : Int) = (localEnd : Int)+delta) :
    ∀ run ∈ HyphenSkipRunTraversal.traverse state.reversedRanges state.count rep.2.1
        (lookupSkipped state.reversedRanges query) remaining,
      let nativeLocal := ((run.original+run.length-1 : Nat) : Int)-delta
      (localFirst : Int) ≤ nativeLocal ∧ nativeLocal < (localEnd : Int) ∧ 0 ≤ nativeLocal := by
  have initialBounds := inverse_query_inside_source_slice state source rep first finish query ordered bounded
    queryLow (by omega)
  have endBound := original_monotone state source rep finish state.count bounded (Nat.le_refl _)
  rw [original_at_end state.reversedRanges state.count rep.2.1] at endBound
  have inverse := (skipped_iterator_bounded_inverse state.reversedRanges state.count query rep.2.1 (by omega)).2
  intro run member
  have sourceBounds := traversal_inside_slice state.reversedRanges state.count
    (lookupSkipped state.reversedRanges query) remaining finish rep.2.1 (by omega) (by omega) run member
  have runBounds := HyphenSkipRunTraversal.source_reads_bounded state.reversedRanges state.count rep.2.1
    (lookupSkipped state.reversedRanges query) remaining run member
  dsimp only
  omega

theorem initial_predecessor_guard (localStart length bufferLength original : Int)
    (startBound : 0 ≤ localStart) (endBound : localStart+length ≤ bufferLength)
    (guard : localStart ≤ original-1 ∧ original-1 < localStart+length) :
    0 ≤ original-1 ∧ original-1 < bufferLength := by omega

end HyphenSkipProviderClip
