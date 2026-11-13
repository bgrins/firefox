import FlexCollect.Model

namespace FlexCollect

def UniversalTarget : Prop :=
  (∀ (α : Type) (size : α → Rat) threshold gap input lines,
    collect size threshold gap input = lines ↔ Collected size threshold gap input lines) ∧
  (∀ (α : Type) (size : α → Rat) threshold gap input,
    (collect size threshold gap input).flatten = input) ∧
  (∀ (α : Type) (size : α → Rat) threshold gap input line,
    line ∈ collect size threshold gap input → line ≠ []) ∧
  (∀ (α : Type) (size : α → Rat) threshold gap input,
    (collect size threshold gap input).length ≤ input.length) ∧
  (∀ (α : Type) (size : α → Rat) threshold gap input left right,
    Collected size threshold gap input left →
    Collected size threshold gap input right → left = right) ∧
  (∀ (α : Type) (input : List α), (nowrap input).flatten = input)

def WitnessTargets : Prop :=
  collect id 100 0 ([150, -50] : List Rat) = [[150], [-50]] ∧
  collect id 100 0 ([80, 30, -50] : List Rat) = [[80], [30, -50]] ∧
  collect id 100 0 ([-50, 150] : List Rat) = [[-50, 150]] ∧
  collect id 100 0 ([100, 0, 0] : List Rat) = [[100, 0, 0]] ∧
  collect id 100 10 ([100, 0] : List Rat) = [[100], [0]] ∧
  collect id 100 10 ([100, -10] : List Rat) = [[100, -10]] ∧
  collect id (7/4) (1/4) ([1, 1/2] : List Rat) = [[1, 1/2]]

end FlexCollect
