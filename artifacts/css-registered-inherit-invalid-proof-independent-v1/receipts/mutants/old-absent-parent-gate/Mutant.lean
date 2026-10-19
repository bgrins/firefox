namespace RegisteredInherit

abbrev Store (Key Value : Type) := Bool → Key → Option Value

structure Context (Key Value : Type) where
  name : Key
  inherited : Bool
  root : Bool
  initial : Option Value
  parent : Store Key Value

structure State (Key Value Flags : Type) where
  values : Store Key Value
  inheritsResetStyle : Bool
  otherFlags : Flags

def selected (c : Context K V) (s : State K V F) : Option V :=
  s.values c.inherited c.name

def seed (c : Context K V) : Option V :=
  if c.root then c.initial
  else if c.inherited then c.parent true c.name else c.initial

def Ready (c : Context K V) (s : State K V F) : Prop :=
  selected c s = seed c ∧ (c.root = true → c.parent false c.name = none)

def expected (c : Context K V) : Option V :=
  if c.root then c.initial else c.parent c.inherited c.name

def put [DecidableEq K] (c : Context K V) (s : State K V F) (value : Option V) : State K V F :=
  { s with values := fun bucket key =>
      if bucket = c.inherited ∧ key = c.name then value else s.values bucket key }

def gate (fixed : Bool) (c : Context K V) (s : State K V F) : Bool :=
  if c.inherited then false
  else match selected c s with
    | none => true
    | some _ => if fixed then (c.parent false c.name).isSome else (c.parent false c.name).isSome

def update [DecidableEq K] (fixed : Bool) (c : Context K V) (s : State K V F) : State K V F :=
  let s := { s with inheritsResetStyle := true }
  match c.parent false c.name with
  | some value => put c s (some value)
  | none => if fixed then put c s none else s

def run [DecidableEq K] (gateFixed updateFixed : Bool) (c : Context K V) (s : State K V F) : State K V F :=
  if gate gateFixed c s then update updateFixed c s else s

def witness (root := false) : Context Nat Nat :=
  ⟨0, false, root, some 7, fun _ _ => none⟩

def start : State Nat Nat Nat :=
  ⟨fun bucket key => if bucket = false ∧ key = 0 then some 7 else some 99, false, 13⟩


end RegisteredInherit
