namespace CssAnimationTaint

structure Payload where
  tokens : List Nat
  attributeTainted : Bool
  deriving DecidableEq, Repr

structure Binding where
  value : Option Payload
  animationTainted : Bool
  deriving DecidableEq, Repr

abbrev Environment := Nat → Binding

inductive Destination where
  | animatable
  | nonanimatable
  deriving DecidableEq, Repr

inductive Expression where
  | literal (value : Payload)
  | reference (name : Nat) (fallback : Option Expression)
  deriving Repr

structure Result where
  value : Option Payload
  reads : List Nat
  deriving DecidableEq, Repr

def available (destination : Destination) (binding : Binding) : Option Payload :=
  if binding.animationTainted && destination == .nonanimatable then none
  else binding.value

def evaluate (environment : Environment) (destination : Destination) : Expression → Result
  | .literal value => ⟨some value, []⟩
  | .reference name fallback =>
    match available destination (environment name) with
    | some value => ⟨some value, [name]⟩
    | none =>
      match fallback with
      | none => ⟨none, [name]⟩
      | some expression =>
        let result := evaluate environment destination expression
        ⟨result.value, name :: result.reads⟩

def Allowed (destination : Destination) (binding : Binding) : Prop :=
  binding.animationTainted = false ∨ destination = .animatable

inductive Derives (environment : Environment) (destination : Destination) :
    Expression → Result → Prop where
  | literal (value) : Derives environment destination (.literal value) ⟨some value, []⟩
  | hit (name fallback value)
      (permitted : Allowed destination (environment name))
      (present : (environment name).value = some value) :
      Derives environment destination (.reference name fallback) ⟨some value, [name]⟩
  | missing (name)
      (unavailable : ¬ Allowed destination (environment name) ∨
        (environment name).value = none) :
      Derives environment destination (.reference name none) ⟨none, [name]⟩
  | fallback (name expression result)
      (unavailable : ¬ Allowed destination (environment name) ∨
        (environment name).value = none)
      (nested : Derives environment destination expression result) :
      Derives environment destination (.reference name (some expression))
        ⟨result.value, name :: result.reads⟩

inductive Infectious (seed : Nat → Prop) (references : Nat → Nat → Prop) : Nat → Prop where
  | seed (name) : seed name → Infectious seed references name
  | reference (name dependency) : references name dependency →
      Infectious seed references dependency → Infectious seed references name

end CssAnimationTaint
