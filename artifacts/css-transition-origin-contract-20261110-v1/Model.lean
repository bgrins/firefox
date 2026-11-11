import Std

namespace TransitionOrigin

inductive Origin where
  | transition | animation
  deriving DecidableEq, BEq, Repr

structure Effect (Property Value : Type) where
  registered : Bool
  current : Bool
  inEffect : Bool
  origin : Origin
  targets : Property → Bool
  sample : Property → Option Value

abbrev Policy (Property Value : Type) := Effect Property Value → Bool

def registeredPolicy : Policy P V := fun _ => true

def inEffectPolicy : Policy P V := fun effect => effect.inEffect

def eligible (policy : Policy P V) (property : P) (effect : Effect P V) : Bool :=
  effect.registered && effect.targets property && policy effect

def hasClass (policy : Policy P V) (property : P) (origin : Origin)
    (effects : List (Effect P V)) : Bool :=
  effects.any (fun effect => eligible policy property effect && decide (effect.origin = origin))

def compositorGuardMask (property : P) (effects : List (Effect P V)) : Bool :=
  hasClass registeredPolicy property .animation effects

def selectOrigin (policy : Policy P V) (property : P) (effects : List (Effect P V)) : Option Origin :=
  if hasClass policy property .animation effects then some .animation
  else if hasClass policy property .transition effects then some .transition else none

def HasClass (policy : Policy P V) (property : P) (origin : Origin)
    (effects : List (Effect P V)) : Prop :=
  ∃ effect ∈ effects, effect.registered = true ∧ effect.targets property = true ∧
    policy effect = true ∧ effect.origin = origin

def Selected (policy : Policy P V) (property : P) (effects : List (Effect P V)) : Option Origin → Prop
  | some .animation => HasClass policy property .animation effects
  | some .transition => ¬ HasClass policy property .animation effects ∧ HasClass policy property .transition effects
  | none => ¬ HasClass policy property .animation effects ∧ ¬ HasClass policy property .transition effects

def sampleFor (property : P) (effect : Effect P V) : Option V :=
  if effect.registered && effect.targets property then effect.sample property else none

def step (combine : V → V → V) (property : P) (state : V × Bool) (effect : Effect P V) : V × Bool :=
  match sampleFor property effect with
  | none => state
  | some sample => (combine state.1 sample, true)

def composite (combine : V → V → V) (property : P) (underlying : V)
    (effects : List (Effect P V)) : Option V :=
  let state := effects.foldl (step combine property) (underlying, false)
  if state.2 then some state.1 else none

def insertion (policy : Policy P V) (combine : V → V → V) (property : P) (underlying : V)
    (effects : List (Effect P V)) : Option (Origin × V) :=
  match selectOrigin policy property effects, composite combine property underlying effects with
  | some origin, some value => some (origin, value)
  | _, _ => none

def cascade (ordinary : V) (important : Option V) : Option (Origin × V) → V
  | some (.transition, value) => value
  | some (.animation, value) => important.getD value
  | none => important.getD ordinary

def render (policy : Policy P V) (combine : V → V → V) (property : P)
    (underlying ordinary : V) (important : Option V) (effects : List (Effect P V)) : V :=
  cascade ordinary important (insertion policy combine property underlying effects)

def Coherent (effect : Effect P V) : Prop :=
  (effect.registered = true → effect.current = true ∨ effect.inEffect = true) ∧
  (effect.inEffect = false → ∀ property, effect.sample property = none)

end TransitionOrigin
