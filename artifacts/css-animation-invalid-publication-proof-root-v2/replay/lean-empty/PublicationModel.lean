import Std
namespace InvalidPublication

structure Endpoint (K P : Type) where
  name : K
  value : Option P
  deriving DecidableEq, Repr

inductive Action (D P : Type) where
  | invalid
  | payload (declaration : D)
  | initial
  | revert
  | provided (value : Option P) (references : Bool)
  deriving DecidableEq, Repr

structure Entry (K D P : Type) where
  name : K
  action : Action D P
  revertAllowed : Bool := true
  flagsIncluded : Bool := true
  deriving DecidableEq, Repr

structure Environment (K D P : Type) where
  inherits : K → Bool
  initial : K → Option P
  encode : P → D
  compute : D → P

structure State (K P : Type) where
  values : Bool → K → Option P
  seen : K → Bool
  cycles : Bool

def convert (encode : P → D) (e : Endpoint K P) : Entry K D P :=
  ⟨e.name, match e.value with
    | none => .invalid
    | some p => .payload (encode p), true, true⟩

def originalConvert (encode : P → D) (e : Endpoint K P) : Entry K D P :=
  ⟨e.name, match e.value with
    | none => .initial
    | some p => .payload (encode p), true, true⟩

def fromDeclaration (env : Environment K D P) (e : Entry K D P) : Option (Endpoint K P) :=
  match e.action with
  | .invalid => some ⟨e.name, none⟩
  | .payload d => some ⟨e.name, some (env.compute d)⟩
  | .initial => some ⟨e.name, env.initial e.name⟩
  | .provided v _ => some ⟨e.name, v⟩
  | .revert => none

def publication (encode : P → D) : Option (Endpoint K P) → List (Entry K D P)
  | none => []
  | some e => [convert encode e]

def mayAffect (env : Environment K D P) (e : Entry K D P) : Bool :=
  match e.action with
  | .initial => env.inherits e.name
  | _ => true

def references : Action D P → Bool
  | .provided _ b => b
  | _ => false

def put [DecidableEq K] (s : State K P) (partition : Bool) (k : K)
    (v : Option P) : State K P :=
  { s with values := fun r q => if r = partition ∧ q = k then v else s.values r q }

def mark [DecidableEq K] (s : State K P) (k : K) : State K P :=
  { s with seen := fun q => if q = k then true else s.seen q }

def unmark [DecidableEq K] (s : State K P) (k : K) : State K P :=
  { s with seen := fun q => if q = k then false else s.seen q }

def step [DecidableEq K] (env : Environment K D P) (s : State K P)
    (e : Entry K D P) : State K P :=
  if !e.revertAllowed then s
  else if !e.flagsIncluded then s
  else if s.seen e.name then s
  else if !mayAffect env e then mark s e.name
  else
    let marked := mark { s with cycles := s.cycles || references e.action } e.name
    match e.action with
    | .invalid => put marked (env.inherits e.name) e.name none
    | .payload d => put marked (env.inherits e.name) e.name (some (env.compute d))
    | .initial => put marked (env.inherits e.name) e.name (env.initial e.name)
    | .provided v _ => put marked (env.inherits e.name) e.name v
    | .revert => unmark marked e.name

def run [DecidableEq K] (env : Environment K D P) (s : State K P) :
    List (Entry K D P) → State K P
  | [] => s
  | e :: rest => run env (step env s e) rest

def admitted (s : State K P) (e : Entry K D P) : Prop :=
  e.revertAllowed = true ∧ e.flagsIncluded = true ∧ s.seen e.name = false

inductive Observation (P : Type) where
  | fallback
  | value (payload : P)
  deriving DecidableEq, Repr

def referenceObservation : Option P → Observation P
  | none => .fallback
  | some p => .value p

def fallbackResult (fallback : P) : Option P → P
  | none => fallback
  | some p => p

def selected (env : Environment K D P) (s : State K P) (k : K) : Option P :=
  s.values (env.inherits k) k

def PayloadPreserved (env : Environment K D P) : Prop :=
  ∀ p, env.compute (env.encode p) = p

end InvalidPublication
