import Std
namespace MapIterator
abbrev Entry (K V : Type) := K × Option V

abbrev Node (K V : Type) := List (Entry K V)

abbrev Chain (K V : Type) := List (Node K V)
variable {K V : Type} [DecidableEq K]
def owns (n : Node K V) (k : K) : Bool := n.any (fun e => e.1 == k)

def shadow (ds : Chain K V) (k : K) : Bool := ds.any (fun n => owns n k)

def visible (ds : Chain K V) (e : Entry K V) : Bool := !shadow ds e.1

def reference : Chain K V → Node K V
  | [] => []
  | n :: ps => n ++ (reference ps).filter (fun e => !owns n e.1)

structure Cursor (K V : Type) where
  current : Node K V
  suffix : Node K V
  parents : Chain K V
  descendants : Chain K V
deriving Repr, DecidableEq

def start : Chain K V → Cursor K V
  | [] => ⟨[], [], [], []⟩
  | n :: ps => ⟨n, n, ps, []⟩

def rank (s : Cursor K V) : Nat :=
  s.suffix.length + s.parents.foldr (fun n z => n.length + 1 + z) 0

inductive Action (K V : Type) where
  | done
  | skip (next : Cursor K V)
  | yield (entry : Entry K V) (next : Cursor K V)
deriving Repr, DecidableEq

def step (s : Cursor K V) : Action K V :=
  match s.suffix with
  | e :: rest =>
    let next := { s with suffix := rest }
    if shadow s.descendants e.1 then .skip next else .yield e next
  | [] => match s.parents with
    | [] => .done
    | p :: ps => .skip ⟨p, p, ps, s.descendants ++ [s.current]⟩

def walk (ds : Chain K V) (cur suf : Node K V) (ps : Chain K V) : Node K V :=
  match suf with
  | e :: rest =>
    if shadow ds e.1 then walk ds cur rest ps
    else e :: walk ds cur rest ps
  | [] => match ps with
    | [] => []
    | p :: rest => walk ds p p rest
termination_by (ps.length, suf.length)

def drain (s : Cursor K V) : Node K V := walk s.descendants s.current s.suffix s.parents
def live (n : Node K V) : Node K V := n.filter (fun e => e.2.isSome)

def getIndex (c : Chain K V) (stored index : Nat) : Option (Entry K V) :=
  if index ≥ stored then none else (live (drain (start c)))[index]?
end MapIterator
