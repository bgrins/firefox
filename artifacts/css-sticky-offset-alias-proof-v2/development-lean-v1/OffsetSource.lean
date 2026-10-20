import OffsetEncoding

namespace OffsetSource

structure Input where
  side : Nat
  automatic : Bool
  resolved : Int
  basis : Int
  deriving Repr

structure Observation where
  value : Int
  queriedSide : Nat
  queries : Nat
  resolves : Nat
  seenBasis : Int
  deriving Repr, DecidableEq

def semanticInset (input : Input) : Option Int :=
  if input.automatic then none else some input.resolved

def observe (input : Input) : Observation :=
  if input.automatic then
    ⟨OffsetEncoding.autoCode, input.side, 1, 0, -1⟩
  else
    ⟨min (OffsetEncoding.autoCode - 1) input.resolved, input.side, 1, 1, input.basis⟩

def observeOld (input : Input) : Observation :=
  if input.automatic then
    ⟨OffsetEncoding.autoCode, input.side, 1, 0, -1⟩
  else
    ⟨input.resolved, input.side, 1, 1, input.basis⟩

def row (o : Observation) : List Int :=
  [o.value, Int.ofNat o.queriedSide, Int.ofNat o.queries, Int.ofNat o.resolves, o.seenBasis]

theorem source_refines_encoding (input : Input) :
    (observe input).value = OffsetEncoding.encode (semanticInset input) := by
  cases h : input.automatic <;> simp [observe, semanticInset, OffsetEncoding.encode, OffsetEncoding.reserve, h]

theorem original_refines_encoding (input : Input) :
    (observeOld input).value = OffsetEncoding.originalEncode (semanticInset input) := by
  cases h : input.automatic <;> simp [observeOld, semanticInset, OffsetEncoding.originalEncode, h]

theorem original_side_queried_once (input : Input) :
    (observe input).queriedSide = input.side ∧ (observe input).queries = 1 := by
  cases h : input.automatic <;> simp [observe, h]

theorem actual_auto_skips_numeric_resolution (input : Input) (h : input.automatic = true) :
    (observe input).resolves = 0 ∧ (observe input).seenBasis = -1 := by
  simp [observe, h]

theorem explicit_resolves_original_basis_once (input : Input) (h : input.automatic = false) :
    (observe input).resolves = 1 ∧ (observe input).seenBasis = input.basis := by
  simp [observe, h]

theorem auto_code_exactly_actual_auto (input : Input) :
    (observe input).value = OffsetEncoding.autoCode ↔ input.automatic = true := by
  rw [source_refines_encoding, OffsetEncoding.auto_exactly]
  cases h : input.automatic <;> simp [semanticInset, h]

theorem explicit_stays_explicit (input : Input) (h : input.automatic = false) :
    OffsetEncoding.decode (observe input).value = some (OffsetEncoding.reserve input.resolved) := by
  rw [source_refines_encoding]
  simp [semanticInset, h, OffsetEncoding.explicit_decode]

theorem signed_result (input : Input) (h : -2147483648 ≤ input.resolved) :
    -2147483648 ≤ (observe input).value ∧ (observe input).value ≤ 2147483647 := by
  cases ha : input.automatic
  · simpa [observe, ha, OffsetEncoding.reserve] using OffsetEncoding.signed_range input.resolved h
  · simp [observe, ha, OffsetEncoding.autoCode]

theorem nonalias_observation_preserved (input : Input) (h : input.resolved < OffsetEncoding.autoCode) :
    observe input = observeOld input := by
  have he := OffsetEncoding.nonreserved_preserved input.resolved h
  cases ha : input.automatic <;> simp [observe, observeOld, ha, ← OffsetEncoding.reserve, he]

theorem explicit_change_at_most_one (input : Input) (ha : input.automatic = false)
    (h : input.resolved ≤ OffsetEncoding.autoCode) :
    0 ≤ (observeOld input).value - (observe input).value ∧
    (observeOld input).value - (observe input).value ≤ 1 := by
  simpa [observe, observeOld, ha, OffsetEncoding.reserve] using
    OffsetEncoding.bounded_resolution_changes_at_most_one input.resolved h

theorem numeric_admission_necessary :
    (observeOld ⟨0, false, OffsetEncoding.autoCode + 100, 0⟩).value -
    (observe ⟨0, false, OffsetEncoding.autoCode + 100, 0⟩).value = 101 := by
  decide +kernel

end OffsetSource
