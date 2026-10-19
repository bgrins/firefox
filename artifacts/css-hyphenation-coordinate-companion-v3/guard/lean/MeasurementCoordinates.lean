namespace MeasurementCoordinates

def requiresRescan (boundary chunkStart : Nat) : Bool := boundary < chunkStart

theorem offset_invariance (boundary chunkStart offset : Nat) :
    requiresRescan (boundary + offset) (chunkStart + offset) = requiresRescan boundary chunkStart := by
  simp [requiresRescan]

theorem relative_buffer_equivalence (start boundary chunkStart length : Nat)
    (boundaryInRun : start ≤ boundary) (bufferCover : chunkStart = start + length) :
    requiresRescan boundary chunkStart = decide (boundary - start < length) := by
  have equivalence : boundary < chunkStart ↔ boundary - start < length := by omega
  simp only [requiresRescan,equivalence]

theorem zero_start_unchanged (boundary length : Nat) :
    requiresRescan boundary (0 + length) = decide (boundary < length) := by simp [requiresRescan]

theorem changed_boundary_witness :
    requiresRescan 260 340 = true ∧ decide (260 < 100) = false := by decide

structure Buffer where
  start : Nat
  coveredEnd : Nat
  length : Nat
  deriving DecidableEq, Repr

def Covers (buffer : Buffer) : Prop :=
  buffer.start ≤ buffer.coveredEnd ∧ buffer.coveredEnd = buffer.start + buffer.length

def initialBuffer (start count : Nat) : Buffer := ⟨start,start+count,count⟩
def refill (buffer : Buffer) (nextEnd : Nat) : Buffer :=
  ⟨buffer.start,nextEnd,buffer.length+(nextEnd-buffer.coveredEnd)⟩

theorem initial_cover (start count : Nat) : Covers (initialBuffer start count) := by
  simp [Covers,initialBuffer]

theorem refill_cover (buffer : Buffer) (nextEnd : Nat) (cover : Covers buffer)
    (monotone : buffer.coveredEnd ≤ nextEnd) : Covers (refill buffer nextEnd) := by
  simp only [Covers,refill] at *
  omega

def applyRefills : Buffer → List Nat → Buffer
  | buffer,[] => buffer
  | buffer,nextEnd::rest => applyRefills (refill buffer nextEnd) rest

def AdmittedRefills : Buffer → List Nat → Prop
  | _,[] => True
  | buffer,nextEnd::rest => buffer.coveredEnd ≤ nextEnd ∧ AdmittedRefills (refill buffer nextEnd) rest

theorem finite_refill_cover (buffer : Buffer) (ends : List Nat) (cover : Covers buffer)
    (admitted : AdmittedRefills buffer ends) : Covers (applyRefills buffer ends) := by
  induction ends generalizing buffer with
  | nil => exact cover
  | cons next rest ih =>
    exact ih (refill buffer next) (refill_cover buffer next cover admitted.1) admitted.2

theorem refill_guard_coordinate_binding (buffer : Buffer) (boundary : Nat)
    (cover : Covers buffer) (boundaryInRun : buffer.start ≤ boundary) :
    requiresRescan boundary buffer.coveredEnd = decide (boundary - buffer.start < buffer.length) :=
  relative_buffer_equivalence buffer.start boundary buffer.coveredEnd buffer.length boundaryInRun cover.2

theorem guarded_rescan_in_fetched_range (buffer : Buffer) (boundary : Nat)
    (cover : Covers buffer) (boundaryInRun : buffer.start ≤ boundary)
    (selected : requiresRescan boundary buffer.coveredEnd = true) :
    boundary - buffer.start < buffer.length := by
  rw [refill_guard_coordinate_binding buffer boundary cover boundaryInRun] at selected
  exact of_decide_eq_true selected

end MeasurementCoordinates
