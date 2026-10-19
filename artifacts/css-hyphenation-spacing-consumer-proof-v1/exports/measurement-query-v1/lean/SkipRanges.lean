import TransformedSlices

namespace HyphenSkipRanges

structure Range where
  start : Nat
  length : Nat
  delta : Nat
  deriving DecidableEq, Repr

def Range.finish (r : Range) : Nat := r.start+r.length

def Range.nextDelta (r : Range) : Nat := r.delta+r.length

def total : List Range → Nat
  | [] => 0
  | r::rest => r.length+total rest

def omitted (ranges : List Range) (offset : Nat) : Nat :=
  ranges.foldr (fun r n => min (offset-r.start) r.length+n) 0

def WellFormed : List Range → Nat → Prop
  | [],_ => True
  | r::rest,count => r.finish ≤ count ∧ r.delta = total rest ∧ WellFormed rest r.start

structure State where
  count : Nat
  reversedRanges : List Range
  deriving DecidableEq, Repr

def keep (s : State) (n : Nat) : State := {s with count := s.count+n}

def skip (s : State) (n : Nat) : State :=
  match s.reversedRanges with
  | [] => ⟨s.count+n,[⟨s.count,n,0⟩]⟩
  | r::rest => if r.finish = s.count then
      ⟨s.count+n,{r with length := r.length+n}::rest⟩
    else ⟨s.count+n,⟨s.count,n,r.nextDelta⟩::r::rest⟩

def skippedPrefix (source : List Bool) (offset : Nat) : Nat :=
  ((source.take offset).filter id).length

def Represents (s : State) (source : List Bool) : Prop :=
  s.count = source.length ∧ WellFormed s.reversedRanges s.count ∧
    ∀ offset, omitted s.reversedRanges offset = skippedPrefix source offset

theorem omitted_cons (r : Range) (rest : List Range) (offset : Nat) :
    omitted (r::rest) offset = min (offset-r.start) r.length+omitted rest offset := rfl

theorem wellformed_weaken (ranges : List Range) (old new : Nat)
    (h : WellFormed ranges old) (bound : old ≤ new) : WellFormed ranges new := by
  cases ranges with
  | nil => trivial
  | cons r rest => exact ⟨by have := h.1; omega,h.2⟩

theorem omitted_after_end (ranges : List Range) (count offset : Nat)
    (h : WellFormed ranges count) (bound : count ≤ offset) :
    omitted ranges offset = total ranges := by
  induction ranges generalizing count with
  | nil => rfl
  | cons r rest ih =>
    obtain ⟨last,delta,older⟩ := h
    have interval : min (offset-r.start) r.length = r.length := by
      unfold Range.finish at last
      omega
    rw [omitted_cons,interval,ih r.start older (by unfold Range.finish at last; omega)]
    rfl

theorem skipped_prefix_append (source : List Bool) (n offset : Nat) :
    skippedPrefix (source++List.replicate n true) offset =
      skippedPrefix source offset+min (offset-source.length) n := by
  simp [skippedPrefix,List.take_append,List.take_replicate]

theorem kept_prefix_append (source : List Bool) (n offset : Nat) :
    skippedPrefix (source++List.replicate n false) offset = skippedPrefix source offset := by
  simp [skippedPrefix,List.take_append,List.take_replicate]

theorem empty_represents : Represents ⟨0,[]⟩ [] := by simp [Represents,WellFormed,omitted,skippedPrefix]

theorem keep_represents (s : State) (source : List Bool) (n : Nat) (h : Represents s source) :
    Represents (keep s n) (source++List.replicate n false) := by
  refine ⟨by simp [keep,h.1],wellformed_weaken _ _ _ h.2.1 (by simp [keep]),?_⟩
  intro offset
  simpa [keep,kept_prefix_append] using h.2.2 offset

theorem skip_represents (s : State) (source : List Bool) (n : Nat) (h : Represents s source) :
    Represents (skip s n) (source++List.replicate n true) := by
  obtain ⟨count,valid,meaning⟩ := h
  cases ranges : s.reversedRanges with
  | nil =>
    simp only [skip,ranges]
    refine ⟨by simp [count],by simp [WellFormed,Range.finish,total],?_⟩
    intro offset
    have old := meaning offset
    simp only [ranges,omitted,List.foldr_nil] at old
    simp [omitted,skipped_prefix_append,← count,← old]
  | cons r rest =>
    rw [ranges] at valid
    obtain ⟨last,delta,older⟩ := valid
    simp only [skip,ranges]
    split
    next adjacent =>
      refine ⟨by simp [count],⟨by simp [Range.finish] at *; omega,delta,older⟩,?_⟩
      intro offset
      have old := meaning offset
      rw [ranges,omitted_cons] at old
      rw [omitted_cons,skipped_prefix_append,← count,← old]
      simp only
      unfold Range.finish at adjacent
      omega
    next separate =>
      refine ⟨by simp [count],⟨by simp [Range.finish],by simp [Range.nextDelta,total,delta,Nat.add_comm],?_⟩,?_⟩
      · exact ⟨last,delta,older⟩
      · intro offset
        have old := meaning offset
        rw [ranges] at old
        rw [omitted_cons,skipped_prefix_append,← count,← old]
        simp [Nat.add_comm]

inductive Operation where
  | keep (length : Nat)
  | skip (length : Nat)
  deriving DecidableEq, Repr

def apply (state : State) : Operation → State
  | .keep n => keep state n
  | .skip n => skip state n

def meaning : Operation → List Bool
  | .keep n => List.replicate n false
  | .skip n => List.replicate n true

def build (state : State) : List Operation → State
  | [] => state
  | op::rest => build (apply state op) rest

theorem arbitrary_builder_operations (state : State) (source : List Bool) (ops : List Operation)
    (h : Represents state source) :
    Represents (build state ops) (source++ops.flatMap meaning) := by
  induction ops generalizing state source with
  | nil => simpa [build] using h
  | cons op rest ih =>
    have step : Represents (apply state op) (source++meaning op) := by
      cases op with
      | keep n => exact keep_represents _ _ _ h
      | skip n => exact skip_represents _ _ _ h
    simpa [build,List.append_assoc] using ih _ _ step

theorem constructor_builder_represents (ops : List Operation) :
    Represents (build ⟨0,[]⟩ ops) (ops.flatMap meaning) := by
  simpa using arbitrary_builder_operations _ _ ops empty_represents

def lookupOriginal (ranges : List Range) (offset : Nat) : Nat :=
  match ranges with
  | [] => offset
  | r::rest => if offset < r.start then lookupOriginal rest offset
    else if offset < r.finish then r.start-r.delta
    else offset-r.nextDelta

theorem total_bound (ranges : List Range) (count : Nat) (h : WellFormed ranges count) :
    total ranges ≤ count := by
  induction ranges generalizing count with
  | nil => simp [total]
  | cons r rest ih =>
    have older := ih _ h.2.2
    have last := h.1
    simp only [total]
    unfold Range.finish at last
    omega

theorem selected_range_arithmetic (ranges : List Range) (count offset : Nat)
    (h : WellFormed ranges count) :
    lookupOriginal ranges offset = offset-omitted ranges offset := by
  induction ranges generalizing count with
  | nil => simp [lookupOriginal,omitted]
  | cons r rest ih =>
    obtain ⟨last,delta,older⟩ := h
    unfold lookupOriginal
    split
    next before =>
      rw [ih _ older,omitted_cons]
      have zero : offset-r.start = 0 := by omega
      simp [zero]
    next after =>
      have previous := omitted_after_end rest r.start offset older (by omega)
      have deltaBound := total_bound rest r.start older
      rw [omitted_cons,previous,← delta]
      split
      next inside =>
        unfold Range.finish at inside
        omega
      next outside =>
        unfold Range.finish at outside
        unfold Range.nextDelta
        omega

theorem complementary_filter_lengths (source : List Bool) :
    (source.filter id).length + (source.filter fun x => !x).length = source.length := by
  induction source with
  | nil => rfl
  | cons x rest ih => cases x <;> simp_all <;> omega

def keptPrefix (source : List Bool) (offset : Nat) : Nat :=
  ((source.take offset).filter fun x => !x).length

theorem kept_prefix_count (source : List Bool) (offset : Nat) :
    keptPrefix source offset = min offset source.length-skippedPrefix source offset := by
  have count := complementary_filter_lengths (source.take offset)
  simp only [List.length_take] at count
  unfold keptPrefix skippedPrefix
  omega

theorem skipped_prefix_clamp (source : List Bool) (offset : Nat) :
    skippedPrefix source (min offset source.length) = skippedPrefix source offset := by
  unfold skippedPrefix
  congr 2
  simp

theorem original_iterator_refines_kept_prefix (state : State) (source : List Bool)
    (offset : Nat) (h : Represents state source) :
    lookupOriginal state.reversedRanges (min offset state.count) = keptPrefix source offset := by
  rw [selected_range_arithmetic _ _ _ h.2.1,h.2.2,h.1,skipped_prefix_clamp,kept_prefix_count]

theorem constructor_original_coordinate (ops : List Operation) (offset : Nat) :
    let state := build ⟨0,[]⟩ ops
    lookupOriginal state.reversedRanges (min offset state.count) =
      keptPrefix (ops.flatMap meaning) offset :=
  original_iterator_refines_kept_prefix _ _ _ (constructor_builder_represents ops)

def lookupSkipped (ranges : List Range) (offset : Nat) : Nat :=
  match ranges with
  | [] => offset
  | r::rest => if offset < r.start-r.delta then lookupSkipped rest offset
    else r.finish+offset-(r.start-r.delta)

theorem original_at_end (ranges : List Range) (count : Nat) (h : WellFormed ranges count) :
    lookupOriginal ranges count = count-total ranges := by
  rw [selected_range_arithmetic _ _ _ h,omitted_after_end _ _ _ h (Nat.le_refl _)]

theorem skipped_iterator_bounded_inverse (ranges : List Range) (count offset : Nat)
    (h : WellFormed ranges count) (bound : offset ≤ count-total ranges) :
    lookupSkipped ranges offset ≤ count ∧
      lookupOriginal ranges (lookupSkipped ranges offset) = offset := by
  induction ranges generalizing count with
  | nil => simpa [lookupSkipped,lookupOriginal,total] using bound
  | cons r rest ih =>
    obtain ⟨last,delta,older⟩ := h
    have deltaBound := total_bound rest r.start older
    unfold lookupSkipped
    split
    next before =>
      have oldBound : offset ≤ r.start-total rest := by omega
      obtain ⟨originalBound,roundtrip⟩ := ih _ older oldBound
      have strict : lookupSkipped rest offset < r.start := by
        by_cases hs : lookupSkipped rest offset < r.start
        · exact hs
        have same : lookupSkipped rest offset = r.start := by omega
        rw [same,original_at_end _ _ older] at roundtrip
        omega
      refine ⟨by unfold Range.finish at last; omega,?_⟩
      simp [lookupOriginal,strict,roundtrip]
    next after =>
      have nonemptyTotal := total_bound (r::rest) count ⟨last,delta,older⟩
      simp only [total] at bound nonemptyTotal
      unfold Range.finish at last ⊢
      refine ⟨by omega,?_⟩
      unfold lookupOriginal
      have lower : r.start ≤ r.start+r.length+offset-(r.start-r.delta) := by omega
      have endBound : r.start+r.length ≤ r.start+r.length+offset-(r.start-r.delta) := by omega
      simp only [Nat.not_lt.mpr lower,↓reduceIte,Range.finish,Nat.not_lt.mpr endBound,Range.nextDelta]
      omega

theorem constructor_skipped_coordinate (ops : List Operation) (offset : Nat)
    (bound : offset ≤ ((ops.flatMap meaning).filter fun x => !x).length) :
    let state := build ⟨0,[]⟩ ops
    lookupSkipped state.reversedRanges offset ≤ state.count ∧
      keptPrefix (ops.flatMap meaning) (lookupSkipped state.reversedRanges offset) = offset := by
  dsimp only
  have rep := constructor_builder_represents ops
  have totalMeaning := rep.2.2 (ops.flatMap meaning).length
  rw [← rep.1,omitted_after_end _ _ _ rep.2.1 (Nat.le_refl _)] at totalMeaning
  have counts := complementary_filter_lengths (ops.flatMap meaning)
  have complete : skippedPrefix (ops.flatMap meaning) (build ⟨0,[]⟩ ops).count =
      ((ops.flatMap meaning).filter id).length := by rw [rep.1]; simp only [skippedPrefix,List.take_length]
  rw [complete] at totalMeaning
  have nativeBound : offset ≤ (build ⟨0,[]⟩ ops).count-total (build ⟨0,[]⟩ ops).reversedRanges := by
    rw [rep.1,totalMeaning]
    omega
  obtain ⟨bounded,roundtrip⟩ := skipped_iterator_bounded_inverse _ _ _ rep.2.1 nativeBound
  refine ⟨bounded,?_⟩
  have coordinate := original_iterator_refines_kept_prefix _ _
    (lookupSkipped (build ⟨0,[]⟩ ops).reversedRanges offset) rep
  rw [Nat.min_eq_left bounded,roundtrip] at coordinate
  exact coordinate.symm

end HyphenSkipRanges
