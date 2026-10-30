import Std

namespace NowrapSuppression

variable {α : Type}

def mask (none : α) (suppress : Bool) (value : α) : α :=
  if suppress then none else value

def positional (none : α) (initial inside : Bool) : Nat → List α → List α
  | _, [] => []
  | offset, value :: rest =>
      mask none (if offset = 0 then initial else inside) value ::
      positional none initial inside (offset + 1) rest

def helper (none : α) (initial inside : Bool) (offset : Nat) : List α → List α
  | [] => []
  | value :: rest =>
      if offset = 0 then
        mask none initial value :: rest.map (mask none inside)
      else
        (value :: rest).map (mask none inside)

theorem positional_positive (none : α) (initial inside : Bool)
    (values : List α) (offset : Nat) (positive : offset ≠ 0) :
    positional none initial inside offset values = values.map (mask none inside) := by
  induction values generalizing offset with
  | nil => rfl
  | cons value rest ih =>
      simp [positional, positive, ih (offset + 1) (by omega)]

theorem helper_refines (none : α) (initial inside : Bool)
    (offset : Nat) (values : List α) :
    helper none initial inside offset values = positional none initial inside offset values := by
  cases values with
  | nil => rfl
  | cons value rest =>
      by_cases h : offset = 0
      · subst offset
        simp [helper, positional, positional_positive]
      · simp [helper, positional_positive, h]

theorem zero_length (none : α) (initial inside : Bool) (offset : Nat) :
    helper none initial inside offset [] = [] := rfl

theorem output_length (none : α) (initial inside : Bool)
    (offset : Nat) (values : List α) :
    (helper none initial inside offset values).length = values.length := by
  cases values <;> simp [helper]
  split <;> simp

theorem initial_position (none value : α) (initial inside : Bool) (rest : List α) :
    (helper none initial inside 0 (value :: rest)).head? = some (mask none initial value) := by
  simp [helper]

theorem interior_positions (none : α) (initial inside : Bool)
    (offset : Nat) (positive : offset ≠ 0) (values : List α) :
    helper none initial inside offset values = values.map (mask none inside) := by
  rw [helper_refines, positional_positive none initial inside values offset positive]

theorem positional_append (none : α) (initial inside : Bool)
    (offset : Nat) (left right : List α) :
    positional none initial inside offset (left ++ right) =
      positional none initial inside offset left ++
      positional none initial inside (offset + left.length) right := by
  induction left generalizing offset with
  | nil => simp [positional]
  | cons value rest ih =>
      simp [positional, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

theorem partition_consistency (none : α) (initial inside : Bool)
    (offset : Nat) (left right : List α) :
    helper none initial inside offset (left ++ right) =
      helper none initial inside offset left ++
      helper none initial inside (offset + left.length) right := by
  simp only [helper_refines]
  exact positional_append none initial inside offset left right

end NowrapSuppression
