import Laws
import Selections

namespace CssUnordered
open CssGrammar

def MatchList : List Grammar → List String → List String → Prop
  | [], input, rest => input = rest
  | head :: tail, input, rest => ∃ middle, Matches head input middle ∧ MatchList tail middle rest

def UnorderedMatches (children : List Grammar) (input rest : List String) : Prop :=
  ∃ indices : List (Fin children.length), indices ≠ [] ∧ indices.Nodup ∧
    MatchList (indices.map children.get) input rest

def nullable (grammar : Grammar) : Bool := accepts grammar []

def valid (children : List Grammar) : Bool :=
  decide (2 ≤ children.length) && children.all (fun child => !nullable child)

def Admissible (children : List Grammar) : Prop :=
  2 ≤ children.length ∧ ∀ child ∈ children, ¬ Matches child [] []

def sequence (first : Grammar) : List Grammar → Grammar
  | [] => first
  | head :: tail => .seq first (sequence head tail)

def sequence? : List Grammar → Option Grammar
  | [] => none
  | head :: tail => some (sequence head tail)

def alternatives (first : Grammar) : List Grammar → Grammar
  | [] => first
  | head :: tail => .alt first (alternatives head tail)

def alternatives? : List Grammar → Option Grammar
  | [] => none
  | head :: tail => some (alternatives head tail)

def plans (children : List Grammar) : List Grammar :=
  (orders (List.finRange children.length)).filterMap
    (fun indices => sequence? (indices.map children.get))

def lower (children : List Grammar) : Option Grammar :=
  if valid children then alternatives? (plans children) else none

def run (children : List Grammar) (input : List String) : List (List String) :=
  match lower children with
  | none => []
  | some grammar => CssGrammar.run grammar input

end CssUnordered
