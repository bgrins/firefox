import Std
set_option autoImplicit false
namespace Mask

inductive Op where
  | add | subtract | intersect | exclude
  deriving DecidableEq, Repr

def compose (op : Op) (s d : Rat) : Rat := match op with
  | .add => s + d * (1 - s)
  | .subtract => s * (1 - d)
  | .intersect => s * d
  | .exclude => s * (1 - d) + d * (1 - s)

def clears : Op → Bool
  | .subtract | .intersect => true
  | .add | .exclude => false

def emptyDispatch (op : Op) (d : Rat) : Rat := if clears op then 0 else d

theorem empty_add (d : Rat) : compose .add 0 d = d := by
  simp only [compose, Rat.sub_eq_add_neg, Rat.neg_zero, Rat.add_zero, Rat.mul_one, Rat.zero_add]
theorem empty_subtract (d : Rat) : compose .subtract 0 d = 0 := by
  exact Rat.zero_mul _
theorem empty_intersect (d : Rat) : compose .intersect 0 d = 0 := by
  exact Rat.zero_mul _
theorem empty_exclude (d : Rat) : compose .exclude 0 d = d := by
  simp only [compose, Rat.sub_eq_add_neg, Rat.neg_zero, Rat.add_zero, Rat.mul_one, Rat.zero_mul, Rat.zero_add]
theorem empty_equivalence (op : Op) (d : Rat) : compose op 0 d = emptyDispatch op d := by
  cases op <;> simp only [emptyDispatch, clears, Bool.false_eq_true, ite_false, ite_true,
    empty_add, empty_subtract, empty_intersect, empty_exclude]
theorem empty_noop (op : Op) (d : Rat) (h : clears op = false) : compose op 0 d = d := by
  rw [empty_equivalence]; simp [emptyDispatch, h]
theorem empty_clear (op : Op) (d : Rat) (h : clears op = true) : compose op 0 d = 0 := by
  rw [empty_equivalence]; simp [emptyDispatch, h]
theorem skip_changes_nonzero (op : Op) (d : Rat) (h : clears op = true) (nonzero : d ≠ 0) :
    compose op 0 d ≠ d := by
  rw [empty_clear op d h]; exact Ne.symm nonzero

theorem over_zero (s : Rat) : compose .add s 0 = s := by
  simp only [compose, Rat.zero_mul, Rat.add_zero]
theorem out_zero (s : Rat) : compose .subtract s 0 = s := by
  simp only [compose, Rat.sub_eq_add_neg, Rat.neg_zero, Rat.add_zero, Rat.mul_one]
theorem in_zero (s : Rat) : compose .intersect s 0 = 0 := by exact Rat.mul_zero _
theorem xor_zero (s : Rat) : compose .exclude s 0 = s := by
  simp only [compose, Rat.sub_eq_add_neg, Rat.neg_zero, Rat.add_zero, Rat.mul_one, Rat.zero_mul, Rat.add_zero]

structure Layer where
  op : Op
  source : Rat
  deriving DecidableEq, Repr

def step (d : Rat) (l : Layer) : Rat := compose l.op l.source d

def fold (layers : List Layer) (d : Rat) : Rat := layers.foldl step d

def optimizedStep (d : Rat) (l : Layer) : Rat :=
  if l.source = 0 then emptyDispatch l.op d else step d l

def optimizedFold (layers : List Layer) (d : Rat) : Rat := layers.foldl optimizedStep d

theorem optimized_step (d : Rat) (l : Layer) : optimizedStep d l = step d l := by
  unfold optimizedStep
  split
  · rename_i h; simp only [step, h, empty_equivalence]
  · rfl

theorem optimized_fold (layers : List Layer) (d : Rat) : optimizedFold layers d = fold layers d := by
  induction layers generalizing d with
  | nil => rfl
  | cons l rest ih =>
    simp only [optimizedFold, fold, List.foldl_cons]
    rw [optimized_step]
    exact ih _

theorem fold_append (xs ys : List Layer) (d : Rat) : fold (xs ++ ys) d = fold ys (fold xs d) := by
  exact List.foldl_append

theorem substitute_equal_step (lower suffix : List Layer) (left right : Layer) (d : Rat)
    (h : ∀ initial, step initial left = step initial right) :
    fold (lower ++ left :: suffix) d = fold (lower ++ right :: suffix) d := by
  rw [fold_append, fold_append]
  simp only [fold, List.foldl_cons]
  rw [h]

theorem empty_in_arbitrary_stack (lower suffix : List Layer) (op : Op) (d : Rat) :
    fold (lower ++ ⟨op, 0⟩ :: suffix) d = fold suffix (emptyDispatch op (fold lower d)) := by
  rw [fold_append]
  simp only [fold, List.foldl_cons, step, empty_equivalence]

theorem noop_in_arbitrary_stack (lower suffix : List Layer) (op : Op) (d : Rat)
    (h : clears op = false) :
    fold (lower ++ ⟨op, 0⟩ :: suffix) d = fold (lower ++ suffix) d := by
  rw [empty_in_arbitrary_stack, fold_append]
  simp [emptyDispatch, h]

theorem clear_erases_prefix (lower suffix : List Layer) (op : Op) (d : Rat)
    (h : clears op = true) :
    fold (lower ++ ⟨op, 0⟩ :: suffix) d = fold suffix 0 := by
  rw [empty_in_arbitrary_stack]; simp [emptyDispatch, h]

theorem later_layer_recovers (lower suffix : List Layer) (op : Op) (d s : Rat)
    (h : clears op = true) :
    fold (lower ++ ⟨op, 0⟩ :: ⟨.add, s⟩ :: suffix) d = fold suffix s := by
  rw [clear_erases_prefix lower _ op d h]
  simp only [fold, List.foldl_cons, step, over_zero]

def paintStack : List Layer → Rat
  | [] => 0
  | bottom :: above => fold above (compose .add bottom.source 0)

theorem bottom_operator_ignored (above : List Layer) (left right : Op) (s : Rat) :
    paintStack (⟨left, s⟩ :: above) = paintStack (⟨right, s⟩ :: above) := rfl

theorem bottom_empty (above : List Layer) (op : Op) :
    paintStack (⟨op, 0⟩ :: above) = fold above 0 := by
  simp only [paintStack, over_zero]

theorem bottom_source (above : List Layer) (op : Op) (s : Rat) :
    paintStack (⟨op, s⟩ :: above) = fold above s := by
  simp only [paintStack, over_zero]

inductive Failure where
  | reference | allocation | snapshot
  deriving DecidableEq, Repr

inductive Outcome where
  | surface (alpha : Rat)
  | emptyArea
  | failure (reason : Failure)
  deriving DecidableEq, Repr

def sourceOutcome (referenceOK areaEmpty allocationOK snapshotOK : Bool) (alpha : Rat) : Outcome :=
  if !referenceOK then .failure .reference
  else if areaEmpty then .emptyArea
  else if !allocationOK then .failure .allocation
  else if !snapshotOK then .failure .snapshot
  else .surface alpha

def reportsEmpty : Outcome → Bool
  | .emptyArea => true
  | _ => false

def dispatch (bottom : Bool) (op : Op) (outcome : Outcome) (d : Rat) : Rat :=
  let effective := if bottom then Op.add else op
  match outcome with
  | .surface s => compose effective s d
  | .emptyArea => emptyDispatch effective d
  | .failure _ => d

theorem reference_precedes_empty (area allocation snapshot : Bool) (alpha : Rat) :
    sourceOutcome false area allocation snapshot alpha = .failure .reference := by
  simp [sourceOutcome]
theorem accepted_empty (allocation snapshot : Bool) (alpha : Rat) :
    sourceOutcome true true allocation snapshot alpha = .emptyArea := by simp [sourceOutcome]
theorem failure_not_empty (reason : Failure) : reportsEmpty (.failure reason) = false := rfl
theorem surface_not_empty (alpha : Rat) : reportsEmpty (.surface alpha) = false := rfl
theorem empty_output : reportsEmpty .emptyArea = true := rfl
theorem failure_preserved (bottom : Bool) (op : Op) (reason : Failure) (d : Rat) :
    dispatch bottom op (.failure reason) d = d := rfl
theorem bottom_empty_preserved (op : Op) (d : Rat) : dispatch true op .emptyArea d = d := rfl
theorem empty_as_surface (bottom : Bool) (op : Op) (d : Rat) :
    dispatch bottom op .emptyArea d = dispatch bottom op (.surface 0) d := by
  simp only [dispatch, empty_equivalence]

theorem failure_and_empty_differ :
    dispatch false .intersect (.failure .allocation) 1 = 1 ∧
    dispatch false .intersect .emptyArea 1 = 0 := by decide

theorem three_layer_recovery :
    paintStack [⟨.add, 1/2⟩, ⟨.intersect, 0⟩, ⟨.add, 1/2⟩] = 1/2 := by
  simp only [paintStack, fold, List.foldl_cons, List.foldl_nil, step, empty_intersect, over_zero]

theorem output_classification (referenceOK areaEmpty allocationOK snapshotOK : Bool) (a : Rat) :
    reportsEmpty (sourceOutcome referenceOK areaEmpty allocationOK snapshotOK a) =
      (referenceOK && areaEmpty) := by
  cases referenceOK <;> cases areaEmpty <;> cases allocationOK <;> cases snapshotOK <;> rfl

def writeOutput (requested previous : Bool) (outcome : Outcome) : Bool :=
  if requested then reportsEmpty outcome else previous

theorem absent_output_preserved (previous : Bool) (outcome : Outcome) :
    writeOutput false previous outcome = previous := rfl

theorem requested_output_initialized (previous : Bool) (outcome : Outcome) :
    writeOutput true previous outcome = reportsEmpty outcome := rfl

end Mask
