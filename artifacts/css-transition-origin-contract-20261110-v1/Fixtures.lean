import Model

namespace TransitionOrigin.Cases

inductive Property where
  | opacity | width
  deriving DecidableEq, BEq, Repr

inductive Value where
  | ordinary | transitionSample | animationSample | important
  deriving DecidableEq, BEq, Repr

def replace (_ sample : Value) : Value := sample

def forwardNoFill (delay duration time : Nat) (origin : Origin) (value : Value) : Effect Property Value :=
  let current := decide (time < delay + duration)
  let inEffect := decide (delay ≤ time ∧ time < delay + duration)
  { registered := current || inEffect, current, inEffect, origin,
    targets := fun property => decide (property = .opacity),
    sample := fun _ => if inEffect then some value else none }

def transition := forwardNoFill 0 10 5 .transition .transitionSample
def delayed := forwardNoFill 10 10 0 .animation .animationSample
def active := forwardNoFill 10 10 15 .animation .animationSample
def cancelled : Effect Property Value := { delayed with registered := false, current := false }
def unrelated : Effect Property Value := { delayed with targets := fun property => decide (property = .width) }
def emptyInEffect : Effect Property Value := { active with sample := fun _ => none }

def style (policy : Policy Property Value) (effects : List (Effect Property Value)) : Value :=
  render policy replace .opacity .important .ordinary (some .important) effects

end TransitionOrigin.Cases
