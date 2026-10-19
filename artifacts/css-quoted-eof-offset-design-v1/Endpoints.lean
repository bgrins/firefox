import Std

namespace QuotedEOF

def mapBoundary (deleted endOffset : Nat) : Nat :=
  if endOffset ≤ deleted then endOffset else endOffset - 1

def recordedEnd (sourceLength suffixLength : Nat) (removed : Bool) : Nat :=
  sourceLength + suffixLength - (if removed then 1 else 0)

theorem preceding_unchanged (deleted endOffset : Nat) (h : endOffset ≤ deleted) :
    mapBoundary deleted endOffset = endOffset := by simp [mapBoundary, h]

theorem enclosing_shifted (sourceLength suffixLength : Nat)
    (hn : 0 < sourceLength) :
    mapBoundary (sourceLength - 1) (sourceLength + suffixLength) =
      recordedEnd sourceLength suffixLength true := by
  simp only [mapBoundary, recordedEnd, ↓reduceIte]
  split <;> omega

theorem no_edit (sourceLength suffixLength : Nat) :
    recordedEnd sourceLength suffixLength false = sourceLength + suffixLength := by
  simp [recordedEnd]

theorem serialized_prefix_length (sourceLength suffixLength : Nat)
    (hn : 0 < sourceLength) :
    recordedEnd sourceLength suffixLength true = sourceLength - 1 + suffixLength := by
  simp only [recordedEnd, ↓reduceIte]
  omega

theorem nested_end_bounded (sourceLength suffixLength finalSuffix : Nat)
    (h : suffixLength ≤ finalSuffix) :
    recordedEnd sourceLength suffixLength true ≤
      recordedEnd sourceLength finalSuffix true := by
  simp only [recordedEnd, ↓reduceIte]
  omega

theorem fallback_slice_bounded (sourceLength suffixLength finalSuffix start : Nat)
    (hn : 0 < sourceLength) (hs : 1 ≤ suffixLength)
    (hf : suffixLength ≤ finalSuffix) (ha : start ≤ sourceLength - 1) :
    start ≤ recordedEnd sourceLength suffixLength true - 1 ∧
    recordedEnd sourceLength suffixLength true - 1 ≤
      recordedEnd sourceLength finalSuffix true := by
  simp only [recordedEnd, ↓reduceIte]
  omega

def construct (sourceLength : Nat) : List (Nat × Bool) → List Nat
  | [] => []
  | (suffixLength, removed) :: rest =>
    recordedEnd sourceLength suffixLength removed :: construct sourceLength rest

theorem arbitrary_enclosing_chain (sourceLength : Nat) (suffixes : List Nat)
    (hn : 0 < sourceLength) :
    construct sourceLength (suffixes.map (fun n => (n, true))) =
      suffixes.map (fun n => sourceLength - 1 + n) := by
  induction suffixes with
  | nil => rfl
  | cons n ns ih =>
    simp only [List.map_cons, construct, serialized_prefix_length _ _ hn, ih]

theorem earlier_sibling_chain (deleted : Nat) (ends : List Nat)
    (h : ∀ e ∈ ends, e ≤ deleted) :
    ends.map (mapBoundary deleted) = ends := by
  induction ends with
  | nil => rfl
  | cons e es ih =>
    have he : e ≤ deleted := h e (by simp)
    have hs : ∀ x ∈ es, x ≤ deleted := by
      intro x hx
      exact h x (by simp [hx])
    simp only [List.map_cons, preceding_unchanged _ _ he, ih hs]

theorem original_outer_end_exceeds_storage (sourceLength finalSuffix : Nat)
    (hn : 0 < sourceLength) :
    sourceLength + finalSuffix > recordedEnd sourceLength finalSuffix true := by
  simp only [recordedEnd, ↓reduceIte]
  omega

theorem witness : recordedEnd 23 2 true = 24 ∧ 25 > 24 ∧
    mapBoundary 22 19 = 19 := by decide

#print axioms preceding_unchanged
#print axioms enclosing_shifted
#print axioms no_edit
#print axioms serialized_prefix_length
#print axioms nested_end_bounded
#print axioms fallback_slice_bounded
#print axioms arbitrary_enclosing_chain
#print axioms earlier_sibling_chain
#print axioms original_outer_end_exceeds_storage
#print axioms witness

end QuotedEOF
