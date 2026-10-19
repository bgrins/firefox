namespace SubstitutedInherit

structure State (Value Flags : Type) where
  value : Option Value
  resetDependency : Bool
  otherFlags : Flags

def resolve (fixed root inherits : Bool) (initial parent : Option V)
    (s : State V F) : State V F :=
  if root then { s with value := initial }
  else { s with value := parent,
                resetDependency := s.resetDependency || (false) }

structure Observations where
  ordinaryChanged : Bool
  ordinaryInheritedEqual : Bool
  inheritedCustomEqual : Bool
  resetCustomEqual : Bool

structure Difference where
  changed : Bool
  resetOnly : Bool
  deriving DecidableEq, Repr

def difference (o : Observations) : Difference :=
  let changed := o.ordinaryChanged
  let resetOnly := o.ordinaryInheritedEqual
  if !o.inheritedCustomEqual then ⟨true, false⟩
  else if !o.resetCustomEqual then ⟨true, resetOnly⟩
  else ⟨changed, resetOnly⟩

structure Hint where
  unconditional : Bool
  conditionalReset : Bool
  deriving DecidableEq, Repr

def childrenHint (d : Difference) (otherForce resetForce : Bool) : Hint :=
  if !d.changed then ⟨otherForce, false⟩
  else if d.resetOnly then
    if resetForce then ⟨true, false⟩ else ⟨otherForce, true⟩
  else ⟨true, false⟩

def recascade (h : Hint) (s : State V F) : Bool :=
  h.unconditional || (h.conditionalReset && s.resetDependency)

def resetEventHint (changed : Bool) : Hint :=
  childrenHint (difference ⟨false, true, true, !changed⟩) false false

structure Event (Value : Type) where
  parent : Option Value
  changed : Bool

def refresh (fixed : Bool) (e : Event V) (s : State V F) : State V F :=
  if recascade (resetEventHint e.changed) s then
    resolve fixed false false none e.parent s
  else s

def EventReady (parent : Option V) (e : Event V) : Prop :=
  e.changed = false → e.parent = parent

def HistoryReady : Option V → List (Event V) → Prop
  | _, [] => True
  | parent, e :: es => EventReady parent e ∧ HistoryReady e.parent es

def run (fixed : Bool) : List (Event V) → State V F → State V F
  | [], s => s
  | e :: es, s => run fixed es (refresh fixed e s)

def expected : Option V → List (Event V) → Option V
  | parent, [] => parent
  | _, e :: es => expected e.parent es

def witness : State Nat Nat := ⟨some 10, false, 73⟩
def absent : State Nat Nat := ⟨none, false, 73⟩
def events : List (Event Nat) := [⟨some 20, true⟩, ⟨none, true⟩]


end SubstitutedInherit
