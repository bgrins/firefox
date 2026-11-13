import FlexCollect.Model

namespace FlexPolicy

def oldBreak (threshold limit nextTotal : Rat) : Bool :=
  decide (limit ≤ nextTotal ∨ threshold < nextTotal)

def patchedBreak (threshold limit oldTotal nextTotal : Rat) : Bool :=
  decide (threshold < oldTotal ∨ limit ≤ nextTotal ∨ threshold < nextTotal)

def loop {α : Type} (size : α → Rat) (gap : Rat) (cut : Rat → Rat → Bool)
    (current : List α) (total : Rat) : List α → List (List α)
  | [] => if current.isEmpty then [] else [current]
  | x :: xs =>
    let appended := current ++ [x]
    if appended.length > 1 then
      let nextTotal := total + size x + gap
      if cut total nextTotal then
        current :: loop size gap cut [x] (size x) xs
      else loop size gap cut appended nextTotal xs
    else loop size gap cut appended (size x) xs

def old {α : Type} (size : α → Rat) (threshold gap limit : Rat) (input : List α) :
    List (List α) :=
  loop size gap (fun _ next => oldBreak threshold limit next) [] 0 input

def patched {α : Type} (size : α → Rat) (threshold gap limit : Rat) (input : List α) :
    List (List α) :=
  loop size gap (patchedBreak threshold limit) [] 0 input

def Ready {α : Type} (size : α → Rat) (threshold gap : Rat) (line : List α) : Prop :=
  line ≠ [] ∧ ((∃ x, line = [x] ∧ threshold < size x) ∨
    FlexCollect.PrefixesFit size threshold gap line)

end FlexPolicy
