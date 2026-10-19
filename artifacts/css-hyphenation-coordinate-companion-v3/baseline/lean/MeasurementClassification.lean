import MeasurementRescanProgress

namespace HyphenMeasurementClassification

inductive Kind where
  | none | explicit | soft | autoWithManual | autoWithoutManual
  deriving DecidableEq, Repr

structure Word where
  boundary : Nat
  manual : Bool := false
  auto : Bool := false
  explicit : Bool := false
  deriving DecidableEq, Repr

structure State where
  word : Word
  buffer : List Kind
  deriving DecidableEq, Repr

def rewriteRange (origin low high : Nat) (fromKind toKind : Kind) (buffer : List Kind) : List Kind :=
  buffer.mapIdx fun index value =>
    if low ≤ origin+index ∧ origin+index < high ∧ value = fromKind then toKind else value

def step (origin index runLength : Nat) (separator : Bool) (state : State) : State := Id.run do
  let mut result := state
  if result.buffer[index-origin]?.getD .none == .explicit && !result.word.explicit then
    result := {result with word.explicit := true}
  if !result.word.manual &&
      (result.buffer[index-origin]?.getD .none == .soft || result.buffer[index-origin]?.getD .none == .explicit) then
    result := {result with word.manual := true}
    if result.word.auto then
      result := {result with buffer := rewriteRange origin result.word.boundary index .autoWithoutManual .autoWithManual result.buffer}
  if result.buffer[index-origin]?.getD .none == .autoWithoutManual then
    result := {result with word.auto := true}
    if result.word.manual then
      result := {result with buffer := result.buffer.set (index-origin) .autoWithManual}
  if separator || index+1 == runLength then
    if !result.word.auto && result.word.explicit then
      result := {result with buffer := rewriteRange origin result.word.boundary (index+1) .explicit .none result.buffer}
    result := {result with word := ⟨index,false,false,false⟩}
  return result

def range (origin first finish runLength : Nat) (separator : Nat → Bool) (state : State) : State :=
  ((List.range (finish-min first state.word.boundary)).map (min first state.word.boundary+·)).foldl
    (fun state index => step origin index runLength (separator index) state) state

theorem rewrite_length (origin low high : Nat) (fromKind toKind : Kind) (buffer : List Kind) :
    (rewriteRange origin low high fromKind toKind buffer).length = buffer.length := by
  simp [rewriteRange]

theorem step_boundary (origin index runLength : Nat) (separator : Bool) (state : State) :
    (step origin index runLength separator state).word.boundary =
      if separator || index+1 == runLength then index else state.word.boundary := by
  simp only [step,Id.run,Pure.pure]
  repeat first | rfl | split

theorem step_length (origin index runLength : Nat) (separator : Bool) (state : State) :
    (step origin index runLength separator state).buffer.length = state.buffer.length := by
  simp only [step,Id.run,Pure.pure]
  repeat first | rfl | split | simp only [rewrite_length,List.length_set]

theorem step_boundary_bounds (origin index runLength finish : Nat) (separator : Bool) (state : State)
    (oldBounds : origin ≤ state.word.boundary ∧ state.word.boundary ≤ finish)
    (indexBounds : origin ≤ index ∧ index < finish) :
    origin ≤ (step origin index runLength separator state).word.boundary ∧
      (step origin index runLength separator state).word.boundary ≤ finish := by
  rw [step_boundary]
  split <;> omega

theorem fold_boundary_bounds (origin runLength finish : Nat) (separator : Nat → Bool)
    (indices : List Nat) (state : State)
    (oldBounds : origin ≤ state.word.boundary ∧ state.word.boundary ≤ finish)
    (indexBounds : ∀ index ∈ indices, origin ≤ index ∧ index < finish) :
    origin ≤ (indices.foldl (fun state index => step origin index runLength (separator index) state) state).word.boundary ∧
      (indices.foldl (fun state index => step origin index runLength (separator index) state) state).word.boundary ≤ finish := by
  induction indices generalizing state with
  | nil => exact oldBounds
  | cons index rest ih =>
    apply ih (step origin index runLength (separator index) state)
    · exact step_boundary_bounds origin index runLength finish (separator index) state oldBounds (indexBounds index (by simp))
    · intro next member; exact indexBounds next (by simp [member])

theorem fold_length (origin runLength : Nat) (separator : Nat → Bool) (indices : List Nat) (state : State) :
    (indices.foldl (fun state index => step origin index runLength (separator index) state) state).buffer.length =
      state.buffer.length := by
  induction indices generalizing state with
  | nil => rfl
  | cons index rest ih =>
    rw [List.foldl_cons,ih,step_length]

theorem complete_range_bounds (origin first finish runLength : Nat) (separator : Nat → Bool) (state : State)
    (oldBounds : origin ≤ state.word.boundary ∧ state.word.boundary ≤ finish)
    (firstBound : origin ≤ first) :
    origin ≤ (range origin first finish runLength separator state).word.boundary ∧
      (range origin first finish runLength separator state).word.boundary ≤ finish := by
  unfold range
  apply fold_boundary_bounds origin runLength finish separator _ state oldBounds
  intro index member
  obtain ⟨relative,inside,rfl⟩ := List.mem_map.mp member
  have bound := List.mem_range.mp inside
  omega

theorem complete_range_length (origin first finish runLength : Nat) (separator : Nat → Bool) (state : State) :
    (range origin first finish runLength separator state).buffer.length = state.buffer.length :=
  fold_length origin runLength separator _ state

theorem complete_range_read_bound (origin first finish : Nat) (state : State)
    (oldBounds : origin ≤ state.word.boundary ∧ state.word.boundary ≤ finish)
    (firstBound : origin ≤ first) (cover : finish-origin ≤ state.buffer.length)
    (index : Nat) (member : index ∈ (List.range (finish-min first state.word.boundary)).map
      (min first state.word.boundary+·)) : index-origin < state.buffer.length := by
  obtain ⟨relative,inside,rfl⟩ := List.mem_map.mp member
  have bound := List.mem_range.mp inside
  omega

theorem manual_reclassification_witness :
    (range 0 0 3 3 (fun _ => false) ⟨⟨0,false,false,false⟩,[.autoWithoutManual,.none,.soft]⟩).buffer =
      [.autoWithManual,.none,.soft] ∧
    (range 0 0 3 3 (fun _ => false) ⟨⟨0,false,false,false⟩,[.none,.explicit,.none]⟩).buffer =
      [.none,.none,.none] := by decide

end HyphenMeasurementClassification
