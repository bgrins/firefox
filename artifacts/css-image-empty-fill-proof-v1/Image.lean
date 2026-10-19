import Mask
set_option autoImplicit false
namespace Image

inductive Preparation where
  | unavailable
  | emptySize
  | clipped
  | covered
  deriving DecidableEq, Repr

def prepare (ready positiveSize overlap : Bool) : Preparation :=
  if !ready then .unavailable
  else if !positiveSize then .emptySize
  else if !overlap then .clipped
  else .covered

def ready : Preparation → Bool
  | .unavailable => false
  | _ => true

def empty : Preparation → Bool
  | .covered => false
  | _ => true

theorem failed_precedes_size (size overlap : Bool) :
    prepare false size overlap = .unavailable := by simp [prepare]
theorem zero_size_precedes_clip (overlap : Bool) :
    prepare true false overlap = .emptySize := by simp [prepare]
theorem clipped_ready : ready (prepare true true false) = true := rfl
theorem failed_not_ready (size overlap : Bool) :
    ready (prepare false size overlap) = false := by simp [prepare, ready]
theorem preparation_ready (isReady size overlap : Bool) :
    ready (prepare isReady size overlap) = isReady := by
  cases isReady <;> cases size <;> cases overlap <;> rfl

structure Input where
  selected : Bool
  dirty : Bool
  mask : Bool
  preparation : Preparation
  allLayers : Bool
  bottom : Bool
  op : Mask.Op
  source : Rat
  deriving Repr

def effective (i : Input) : Mask.Op :=
  if i.mask && i.allLayers && i.bottom then .add else i.op

def oldStep (i : Input) (d : Rat) : Rat :=
  if i.selected && i.dirty && !empty i.preparation then
    Mask.compose (effective i) i.source d
  else d

def clear (i : Input) : Bool :=
  i.selected && i.dirty && i.mask && ready i.preparation &&
    empty i.preparation && Mask.clears (effective i)

def newStep (i : Input) (d : Rat) : Rat :=
  if clear i then 0 else oldStep i d

def specifiedStep (i : Input) (d : Rat) : Rat :=
  if i.selected && i.dirty then
    if !empty i.preparation then Mask.compose (effective i) i.source d
    else if i.mask && ready i.preparation then Mask.compose (effective i) 0 d
    else d
  else d

theorem unchanged_outside_clear (i : Input) (d : Rat) (h : clear i = false) :
    newStep i d = oldStep i d := by simp [newStep, h]

theorem clear_result (i : Input) (d : Rat) (h : clear i = true) :
    newStep i d = 0 := by simp [newStep, h]

theorem clear_requires_ready (i : Input) (h : clear i = true) :
    ready i.preparation = true := by
  simp only [clear, Bool.and_eq_true] at h
  exact h.1.1.2

theorem clear_requires_mask (i : Input) (h : clear i = true) :
    i.mask = true := by
  simp only [clear, Bool.and_eq_true] at h
  exact h.1.1.1.2

theorem new_step_spec (i : Input) (d : Rat) : newStep i d = specifiedStep i d := by
  rcases i with ⟨selected, dirty, mask, preparation, allLayers, bottom, op, source⟩
  cases selected <;> cases dirty <;> cases mask <;> cases preparation <;>
    cases allLayers <;> cases bottom <;> cases op <;>
    simp [newStep, clear, oldStep, specifiedStep, effective, empty, ready,
      Mask.clears, Mask.empty_add, Mask.empty_subtract, Mask.empty_intersect, Mask.empty_exclude]

def newFold (layers : List Input) (d : Rat) : Rat := layers.foldl (fun a i => newStep i a) d
def specifiedFold (layers : List Input) (d : Rat) : Rat := layers.foldl (fun a i => specifiedStep i a) d

theorem fold_spec (layers : List Input) (d : Rat) : newFold layers d = specifiedFold layers d := by
  induction layers generalizing d with
  | nil => rfl
  | cons i rest ih =>
    simp only [newFold, specifiedFold, List.foldl_cons]
    rw [new_step_spec]
    exact ih _

theorem lower_clear_preserves_suffix (i : Input) (suffix : List Input) (d : Rat)
    (h : clear i = true) : newFold (i :: suffix) d = newFold suffix 0 := by
  simp only [newFold, List.foldl_cons, clear_result i d h]

theorem unavailable_preserved (i : Input) (d : Rat)
    (h : i.preparation = .unavailable) : newStep i d = oldStep i d := by
  apply unchanged_outside_clear
  simp [clear, h, ready]

theorem bottom_not_cleared (i : Input) (h1 : i.mask = true)
    (h2 : i.allLayers = true) (h3 : i.bottom = true) : clear i = false := by
  simp [clear, effective, h1, h2, h3, Mask.clears]

structure PaintState where
  alpha : Rat
  result : Nat
  matrix : List Rat
  operation : Nat
  deriving DecidableEq

def transition (i : Input) (aggregatedResult : Nat) (s : PaintState) : PaintState :=
  { s with alpha := newStep i s.alpha, result := aggregatedResult }

theorem result_aggregation_preserved (i : Input) (r : Nat) (s : PaintState) :
    (transition i r s).result = r := rfl
theorem matrix_preserved (i : Input) (r : Nat) (s : PaintState) :
    (transition i r s).matrix = s.matrix := rfl
theorem operation_preserved (i : Input) (r : Nat) (s : PaintState) :
    (transition i r s).operation = s.operation := rfl

end Image
