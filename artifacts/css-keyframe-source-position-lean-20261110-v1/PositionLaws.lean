import PositionModel

namespace KeyframeSourcePosition

variable {α : Type} [DecidableEq α]

theorem remembered_key (positions : α → Option Nat) (key : α) (position : Nat) :
    remember positions (key, position) key = some position := by
  simp [remember]

theorem other_keys_preserved (positions : α → Option Nat) (key other : α)
    (position : Nat) (different : other ≠ key) :
    remember positions (key, position) other = positions other := by
  simp [remember, different]

theorem record_cons (entry : α × Nat) (entries : List (α × Nat)) (key : α) :
    recordPositions (entry :: entries) key =
      if key = entry.1 then some entry.2 else recordPositions entries key := by
  simp [recordPositions, List.foldl_append, remember]

theorem record_matches_first (entries : List (α × Nat)) (key : α) :
    recordPositions entries key = firstPosition entries key := by
  induction entries with
  | nil => rfl
  | cons entry entries ih =>
    rw [record_cons]
    by_cases h : key = entry.1
    · simp [firstPosition, h]
    · simp [firstPosition, h, Ne.symm h, ih]

theorem enumerated_input (keys : List α) (key : α) :
    recordPositions keys.zipIdx key =
      (keys.zipIdx.find? fun entry => decide (entry.1 = key)).map Prod.snd :=
  record_matches_first _ _

theorem present_exactly_for_groups (entries : List (α × Nat)) (key : α) :
    (recordPositions entries key).isSome = true ↔ key ∈ entries.map Prod.fst := by
  induction entries with
  | nil => simp [recordPositions]
  | cons entry entries ih =>
    rw [record_cons]
    by_cases h : key = entry.1
    · simp [h]
    · simp [h, ih]

theorem comparison_matches_first (entries : List (α × Nat)) (left right : α) :
    precedes (recordPositions entries) left right ↔
      precedes (firstPosition entries) left right := by
  simp only [precedes, record_matches_first]

theorem metadata_consumer (entries : List (α × Nat))
    (consume : (α → Option Nat) → β) :
    consume (recordPositions entries) = consume (firstPosition entries) := by
  congr 1
  funext key
  exact record_matches_first entries key

theorem repeat_positions :
    (recordPositions ([0, 1, 2, 1] : List Nat).zipIdx 0,
      recordPositions ([0, 1, 2, 1] : List Nat).zipIdx 1,
      recordPositions ([0, 1, 2, 1] : List Nat).zipIdx 2) =
      (some 0, some 1, some 2) := by decide

theorem repeated_groups_positions :
    (recordPositions ([0, 1, 2, 1, 0] : List Nat).zipIdx 0,
      recordPositions ([0, 1, 2, 1, 0] : List Nat).zipIdx 1,
      recordPositions ([0, 1, 2, 1, 0] : List Nat).zipIdx 2) =
      (some 0, some 1, some 2) := by decide

theorem absent_key :
    recordPositions ([0, 1, 2, 1, 0] : List Nat).zipIdx 3 = none := by decide

end KeyframeSourcePosition
