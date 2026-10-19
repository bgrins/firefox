import Ownership
import RangeProvider

namespace HyphenRangeAdmission
open HyphenOwnership
open HyphenRangeProvider

structure Submission where
  range : StyledRange
  sink : Nat
  deriving DecidableEq, Repr

def character (describe : Cell → Character) (limits : Limits) (cell : Cell) : Character :=
  { describe cell with limits := limits }

def cellEvent (describe : Cell → Character) (limits : Limits) (cell : Cell) : Event :=
  if cell.segmentSpace then .boundary else .contribute (character describe limits cell)

def cellsEvents (describe : Cell → Character) (limits : Limits) (cells : List Cell) : List Event :=
  (cells.filter fun cell => !cell.skipped).map (cellEvent describe limits)

def leadingEvents (range : StyledRange) : List Event :=
  if compressedLeadingSpace range.cells then [.invisibleWhitespace] else []

def rangeEvents (policies : Nat → Limits) (describe : Cell → Character)
    (range : StyledRange) : List Event :=
  .setLimits (policies range.policy) ::
    leadingEvents range ++ cellsEvents describe (policies range.policy) range.cells

def submissionEvents (policies : Nat → Limits) (describe : Cell → Character)
    (ranges : List Submission) : List Event :=
  ranges.flatMap (fun r => rangeEvents policies describe r.range) ++
    ranges.map (fun r => .finalize r.sink)

theorem admitted_append (s : State) (left right : List Event) :
    admitted s (left ++ right) ↔ admitted s left ∧ admitted (run s left) right := by
  induction left generalizing s with
  | nil => simp [admitted, run]
  | cons e es ih =>
    simp only [List.cons_append, admitted, run, List.foldl_cons]
    rw [ih]
    exact and_assoc.symm

theorem cell_preserves_current (s : State) (describe : Cell → Character)
    (limits : Limits) (cell : Cell) :
    (step s (cellEvent describe limits cell)).current = s.current := by
  simp only [cellEvent]
  split <;> rfl

theorem cell_supplied (s : State) (describe : Cell → Character)
    (limits : Limits) (cell : Cell) (h : s.current = limits) :
    suppliedCorrectly s (cellEvent describe limits cell) := by
  simp only [cellEvent]
  split
  · trivial
  · simpa [suppliedCorrectly, character] using h.symm

theorem cells_admitted (s : State) (describe : Cell → Character)
    (limits : Limits) (cells : List Cell) (h : s.current = limits) :
    admitted s (cells.map (cellEvent describe limits)) ∧
      (run s (cells.map (cellEvent describe limits))).current = limits := by
  induction cells generalizing s with
  | nil => exact ⟨trivial, h⟩
  | cons c cs ih =>
    have hc := cell_supplied s describe limits c h
    have hn : (step s (cellEvent describe limits c)).current = limits := by
      rw [cell_preserves_current, h]
    have ht := ih (step s (cellEvent describe limits c)) hn
    exact ⟨⟨hc, ht.1⟩, ht.2⟩

theorem leadingEvents_admitted (s : State) (range : StyledRange) :
    admitted s (leadingEvents range) ∧ (run s (leadingEvents range)).current = s.current := by
  unfold leadingEvents
  split <;> simp [admitted, run, step, flush, suppliedCorrectly]

theorem range_admitted (s : State) (policies : Nat → Limits)
    (describe : Cell → Character) (range : StyledRange) :
    admitted s (rangeEvents policies describe range) := by
  change True ∧ admitted (step s (.setLimits (policies range.policy))) _
  constructor
  · trivial
  apply (admitted_append _ _ _).mpr
  have hp := leadingEvents_admitted (step s (.setLimits (policies range.policy))) range
  constructor
  · exact hp.1
  · apply (cells_admitted _ describe _ _ _).1
    exact hp.2

theorem ranges_admitted (s : State) (policies : Nat → Limits)
    (describe : Cell → Character) (ranges : List Submission) :
    admitted s (ranges.flatMap (fun r => rangeEvents policies describe r.range)) := by
  induction ranges generalizing s with
  | nil => trivial
  | cons r rs ih =>
    rw [List.flatMap_cons, admitted_append]
    exact ⟨range_admitted s policies describe r.range, ih _⟩

theorem finalization_admitted (s : State) (ranges : List Submission) :
    admitted s (ranges.map (fun r => .finalize r.sink)) := by
  induction ranges generalizing s with
  | nil => trivial
  | cons r rs ih => exact ⟨trivial, ih _⟩

theorem generated_admitted (s : State) (policies : Nat → Limits)
    (describe : Cell → Character) (ranges : List Submission) :
    admitted s (submissionEvents policies describe ranges) := by
  rw [submissionEvents, admitted_append]
  exact ⟨ranges_admitted s policies describe ranges, finalization_admitted _ ranges⟩

theorem generated_native_refinement (s : State) (policies : Nat → Limits)
    (describe : Cell → Character) (ranges : List Submission) :
    nativeRun s (submissionEvents policies describe ranges) =
      run s (submissionEvents policies describe ranges) :=
  supplied_trace_refinement _ _ (generated_admitted s policies describe ranges)

theorem generated_capture_coherent (s : State) (policies : Nat → Limits)
    (describe : Cell → Character) (ranges : List Submission) (h : coherent s) :
    coherent (nativeRun s (submissionEvents policies describe ranges)) :=
  native_capture_policy _ _ h (generated_admitted s policies describe ranges)

theorem generated_uniform_word (s : State) (policies : Nat → Limits)
    (describe : Cell → Character) (ranges : List Submission) (h : coherent s)
    (c : Character) (rest : List Character) (limits : Limits)
    (pending : (nativeRun s (submissionEvents policies describe ranges)).pending = c :: rest)
    (uniform : ∀ x ∈ c :: rest, x.limits = limits) :
    (nativeRun s (submissionEvents policies describe ranges)).captured = some limits :=
  uniform_native_owner _ _ h (generated_admitted s policies describe ranges)
    c rest limits pending uniform

#print axioms generated_admitted
#print axioms generated_native_refinement
#print axioms generated_capture_coherent
#print axioms generated_uniform_word
end HyphenRangeAdmission
