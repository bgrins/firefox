import Std

namespace KeyframeSourcePosition

variable {α : Type} [DecidableEq α]

def remember (positions : α → Option Nat) (entry : α × Nat) : α → Option Nat :=
  fun key => if key = entry.1 then some entry.2 else positions key

def recordPositions (entries : List (α × Nat)) : α → Option Nat :=
  entries.reverse.foldl remember (fun _ => none)

def firstPosition (entries : List (α × Nat)) (key : α) : Option Nat :=
  (entries.find? fun entry => decide (entry.1 = key)).map Prod.snd

def precedes (positions : α → Option Nat) (left right : α) : Prop :=
  ∃ a b, positions left = some a ∧ positions right = some b ∧ a < b

end KeyframeSourcePosition
