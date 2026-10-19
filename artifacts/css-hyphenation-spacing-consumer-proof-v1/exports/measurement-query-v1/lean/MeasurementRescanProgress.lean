import MeasurementCoordinates

namespace HyphenMeasurementRescanProgress

structure Cursor where
  position : Nat
  bufferStart : Nat
  bufferEnd : Nat
  rescanLimit : Nat
  deriving DecidableEq, Repr

def Ready (start finish : Nat) (cursor : Cursor) : Prop :=
  start ≤ cursor.position ∧ cursor.position ≤ finish ∧
  start ≤ cursor.bufferStart ∧ cursor.bufferStart ≤ cursor.bufferEnd ∧ cursor.bufferEnd ≤ finish ∧
  cursor.bufferEnd-cursor.bufferStart ≤ 100 ∧
  (cursor.bufferStart ≤ cursor.position ∨ cursor.bufferStart ≤ cursor.rescanLimit)

def initial (start finish : Nat) : Cursor :=
  ⟨start,start,min finish (start+100),start⟩

def refill (finish : Nat) (cursor : Cursor) (boundary : Nat) (rewind : Bool) : Cursor :=
  ⟨if rewind then boundary else cursor.position,cursor.position,min finish (cursor.position+100),
    if rewind then cursor.position else cursor.rescanLimit⟩

def advance (cursor : Cursor) : Cursor := {cursor with position := cursor.position+1}

def rank (finish : Nat) (cursor : Cursor) : Nat × Nat :=
  (finish-cursor.bufferEnd,finish-cursor.position)

theorem initial_ready (start finish : Nat) (ordered : start ≤ finish) : Ready start finish (initial start finish) := by
  simp only [Ready,initial]
  omega

theorem refill_ready (start finish boundary : Nat) (cursor : Cursor) (rewind : Bool)
    (ready : Ready start finish cursor) (active : cursor.position < finish)
    (boundaryBounds : start ≤ boundary ∧ boundary ≤ cursor.position) :
    Ready start finish (refill finish cursor boundary rewind) := by
  rcases ready with ⟨low,high,bufferLow,bufferOrder,bufferHigh,capacity,spacing⟩
  cases rewind <;> simp [Ready,refill] <;> omega

theorem advance_ready (start finish : Nat) (cursor : Cursor)
    (ready : Ready start finish cursor) (active : cursor.position < finish) :
    Ready start finish (advance cursor) := by
  simp only [Ready,advance] at *
  omega

theorem refill_rank_decreases (finish boundary : Nat) (cursor : Cursor) (rewind : Bool)
    (active : cursor.position < finish) (exhausted : cursor.bufferEnd ≤ cursor.position) :
    (rank finish (refill finish cursor boundary rewind)).1 < (rank finish cursor).1 := by
  simp only [rank,refill]
  omega

theorem advance_rank_decreases (finish : Nat) (cursor : Cursor) (active : cursor.position < finish) :
    (rank finish (advance cursor)).1 = (rank finish cursor).1 ∧
    (rank finish (advance cursor)).2 < (rank finish cursor).2 := by
  dsimp [rank,advance]
  constructor
  · rfl
  · omega

theorem spacing_index_safe (start finish : Nat) (cursor : Cursor)
    (ready : Ready start finish cursor) (buffered : cursor.position < cursor.bufferEnd)
    (notRescanning : cursor.rescanLimit ≤ cursor.position) :
    cursor.bufferStart ≤ cursor.position ∧ cursor.position-cursor.bufferStart < 100 := by
  unfold Ready at ready
  omega

theorem hyphen_index_safe (start finish length : Nat) (cursor : Cursor)
    (ready : Ready start finish cursor) (buffered : cursor.position < cursor.bufferEnd)
    (cover : start+length = cursor.bufferEnd) : cursor.position-start < length := by
  unfold Ready at ready
  omega

theorem exhausted_refill_covers_position (finish boundary : Nat) (cursor : Cursor) (rewind : Bool)
    (active : cursor.position < finish) (boundaryBounds : boundary ≤ cursor.position) :
    (refill finish cursor boundary rewind).position < (refill finish cursor boundary rewind).bufferEnd := by
  cases rewind <;> simp [refill] <;> omega

theorem rescan_for_increment (boundary : Nat) (bound : boundary < 2^32) :
    ((BitVec.ofNat 32 boundary - 1) + 1).toNat = boundary := by
  rw [BitVec.sub_add_cancel]
  exact Nat.mod_eq_of_lt bound

def budget (finish : Nat) (cursor : Cursor) : Nat :=
  (finish-cursor.bufferEnd)*(finish+1)+(finish-cursor.position)

theorem refill_budget_decreases (finish boundary : Nat) (cursor : Cursor) (rewind : Bool)
    (active : cursor.position < finish) (exhausted : cursor.bufferEnd ≤ cursor.position) :
    budget finish (refill finish cursor boundary rewind) < budget finish cursor := by
  have decreasing := refill_rank_decreases finish boundary cursor rewind active exhausted
  change finish-(refill finish cursor boundary rewind).bufferEnd < finish-cursor.bufferEnd at decreasing
  have multiplied := Nat.mul_le_mul_right (finish+1) (show
      (finish-(refill finish cursor boundary rewind).bufferEnd)+1 ≤ finish-cursor.bufferEnd by omega)
  rw [Nat.add_mul] at multiplied
  unfold budget
  have bound : finish-(refill finish cursor boundary rewind).position ≤ finish := Nat.sub_le _ _
  omega

theorem advance_budget_decreases (finish : Nat) (cursor : Cursor) (active : cursor.position < finish) :
    budget finish (advance cursor) < budget finish cursor := by
  dsimp [budget,advance]
  omega

inductive Transition (finish : Nat) : Cursor → Cursor → Prop where
  | next (cursor : Cursor) (active : cursor.position < finish) :
      Transition finish cursor (advance cursor)
  | refetched (cursor : Cursor) (boundary : Nat) (rewind : Bool)
      (active : cursor.position < finish) (exhausted : cursor.bufferEnd ≤ cursor.position) :
      Transition finish cursor (refill finish cursor boundary rewind)

theorem every_transition_consumes_budget (finish : Nat) (before after : Cursor)
    (step : Transition finish before after) : budget finish after < budget finish before := by
  cases step with
  | next active => exact advance_budget_decreases finish before active
  | refetched boundary rewind active exhausted =>
      exact refill_budget_decreases finish boundary before rewind active exhausted

end HyphenMeasurementRescanProgress
