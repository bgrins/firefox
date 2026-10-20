import Rules
namespace Fragmentation

structure Decoration where
  startExtent : Nat
  endExtent : Nat
  cloned : Bool
  deriving DecidableEq, Repr
structure Input where
  types : BreakTypes
  content : List Atom
  opportunities : List Opportunity
  decorations : List Decoration := []
  capacity : Nat
  deriving DecidableEq, Repr

def decorationExtent (s : Stage) (d : Decoration) : Nat :=
  if d.cloned then match s with
    | .endClone => d.startExtent
    | .bothClone => 0
    | _ => d.startExtent + d.endExtent
  else d.startExtent + d.endExtent

def extent (s : Stage) (i : Input) (cut : Nat) : Nat :=
  ((i.content.take cut).map Atom.extent).sum + (i.decorations.map (decorationExtent s)).sum

def zeroBox (a : Atom) : Bool :=
  match a.kind with | .box _ => a.extent == 0 | _ => false

def nextZeroBox (i : Input) (cut : Nat) : Bool :=
  (i.content.drop cut).head?.any zeroBox

def finishFits (s : Stage) (i : Input) : Bool :=
  i.content.isEmpty || decide (extent s i i.content.length ≤ i.capacity)

def fits (s : Stage) (i : Input) (p : Opportunity) : Bool :=
  decide (0 < p.cut) && decide (p.cut < i.content.length) &&
  decide (extent s i p.cut ≤ i.capacity) && !nextZeroBox i p.cut

def candidate (s : Stage) (i : Input) (p : Opportunity) : Bool :=
  ordinary s i.types i.content p && fits s i p

def GridPlacement (s : Stage) (i : Input) (p : Opportunity) : Prop :=
  Ordinary s i.types i.content p ∧ 0 < p.cut ∧ p.cut < i.content.length ∧
  ((i.content.take p.cut).map Atom.extent).sum +
    (i.decorations.map (decorationExtent s)).sum ≤ i.capacity ∧
  nextZeroBox i p.cut = false

def GridFeasible (s : Stage) (i : Input) : Prop :=
  (i.content = [] ∨ extent s i i.content.length ≤ i.capacity) ∨
  ∃ p ∈ i.opportunities, GridPlacement s i p

inductive Choice where
  | finish | cut (p : Opportunity)
  deriving DecidableEq, Repr

def evaluate (s : Stage) (i : Input) : Option Choice :=
  if finishFits s i then some .finish
  else (i.opportunities.find? (candidate s i)).map Choice.cut

def ValidChoice (s : Stage) (i : Input) : Choice → Prop
  | .finish => i.content = [] ∨ extent s i i.content.length ≤ i.capacity
  | .cut p => p ∈ i.opportunities ∧ GridPlacement s i p

end Fragmentation
