import Std
namespace TaintShortcut
structure Value (P : Type) where
  payload : P
  attr : Bool
deriving DecidableEq, Repr
abbrev State (P : Type) := Option (Value P)
def payloadSame (cmp : P → P → Bool) : State P → State P → Bool
  | none, none => true
  | some a, some b => cmp a.payload b.payload
  | _, _ => false
def metadataSame (cmp : P → P → Bool) : State P → State P → Bool
  | none, none => true
  | some a, some b => cmp a.payload b.payload && (a.attr == b.attr)
  | _, _ => false
def PayloadSound (cmp : P → P → Bool) : Prop := ∀ a b, cmp a b = true → a = b
def mapUpdate (same : State P → State P → Bool) (unique : Bool) (old next : State P) : State P :=
  if unique then next else if same old next then old else next
structure Incoming (P : Type) where
  payload : P
  syntaxAttr : Bool
  explicitAttr : Bool
  hasReferences : Bool
  eligible : Bool
deriving Repr
def declaredValue (d : Incoming P) : Value P := ⟨d.payload, d.syntaxAttr || d.explicitAttr⟩
def pipeline (gateSame mapSame : State P → State P → Bool)
    (resolve : Incoming P → State P) (unique : Bool) (old : State P) (d : Incoming P) : State P :=
  if d.eligible && gateSame old (some (declaredValue d)) then old
  else mapUpdate mapSame unique old (resolve d)
def repaired (cmp : P → P → Bool) (resolve : Incoming P → State P)
    (unique : Bool) (old : State P) (d : Incoming P) : State P :=
  pipeline (metadataSame cmp) (payloadSame cmp) resolve unique old d
def ReferenceFreeProvider (resolve : Incoming P → State P) : Prop :=
  ∀ d, d.eligible = true → d.hasReferences = false → resolve d = some (declaredValue d)
def EligibleDomain (d : Incoming P) : Prop := d.eligible = true → d.hasReferences = false
def observeURL (parse : P → Option U) : State P → Option U
  | none => none
  | some v => if v.attr then none else parse v.payload
structure Op (P : Type) where
  input : Incoming P
  unique : Bool
def optimizedHistory (cmp : P → P → Bool) (resolve : Incoming P → State P) :
    State P → List (Op P) → State P
  | s, [] => s
  | s, op :: rest => optimizedHistory cmp resolve
      (repaired cmp resolve op.unique s op.input) rest
def referenceHistory (resolve : Incoming P → State P) : State P → List (Op P) → State P
  | s, [] => s
  | _, op :: rest => referenceHistory resolve (resolve op.input) rest
end TaintShortcut
