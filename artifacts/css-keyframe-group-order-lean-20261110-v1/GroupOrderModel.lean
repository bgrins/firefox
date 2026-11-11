import Std

namespace KeyframeGroupOrder

variable {α : Type} [DecidableEq α]

def moveLast (groups : List α) (key : α) : List α :=
  groups.filter (· != key) ++ [key]

def assembleReverse : List α → List α
  | [] => []
  | key :: rest => moveLast (assembleReverse rest) key

def earliest : List α → List α
  | [] => []
  | key :: rest => key :: (earliest rest).filter (· != key)

def oldAssembleReverse : List α → List α
  | [] => []
  | key :: rest =>
    let groups := oldAssembleReverse rest
    if key ∈ groups then groups else groups ++ [key]

end KeyframeGroupOrder
