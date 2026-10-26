import Std

namespace KeyframeContext

def interpolate (a b progress : Rat) : Rat := a + progress * (b - a)

def discrete (a b progress : Rat) : Rat := if progress < 1 / 2 then a else b

inductive Expression where
  | literal : Rat → Expression
  | provider

def evaluate (context : Rat) : Expression → Rat
  | .literal value => value
  | .provider => context

def current (a b : Rat) (start finish : Expression) (progress : Rat) : Rat :=
  let context := discrete a b progress
  interpolate (evaluate context start) (evaluate context finish) progress

def endpointLocal (a b : Rat) (start finish : Expression) (progress : Rat) : Rat :=
  interpolate (evaluate a start) (evaluate b finish) progress

theorem interpolate_same (value progress : Rat) : interpolate value value progress = value := by
  unfold interpolate
  grind

theorem shared_provider_current (a b progress : Rat) :
    current a b .provider .provider progress = discrete a b progress := by
  exact interpolate_same _ _

theorem shared_provider_endpoint (a b progress : Rat) :
    endpointLocal a b .provider .provider progress = interpolate a b progress := rfl

theorem literal_context_independent (a b x y progress : Rat) :
    current a b (.literal x) (.literal y) progress =
    endpointLocal a b (.literal x) (.literal y) progress := rfl

theorem unchanged_provider (a : Rat) (start finish : Expression) (progress : Rat) :
    current a a start finish progress = endpointLocal a a start finish progress := by
  simp [current, endpointLocal, discrete]

theorem midpoint_disagrees (a b : Rat) (different : a ≠ b) :
    current a b .provider .provider (1/2) ≠
    endpointLocal a b .provider .provider (1/2) := by
  rw [shared_provider_current, shared_provider_endpoint]
  simp only [discrete, show ¬ (1/2 : Rat) < 1/2 by decide +kernel, ↓reduceIte]
  unfold interpolate
  intro equal
  apply different
  grind

def sampleTimes : List Rat := [0, 1/4, 1/2, 3/4, 1]
def currentSamples : List Rat := sampleTimes.map (current (1/4) (3/4) .provider .provider)
def localSamples : List Rat := sampleTimes.map (endpointLocal (1/4) (3/4) .provider .provider)

example : currentSamples = [1/4, 1/4, 3/4, 3/4, 3/4] := by decide +kernel
example : localSamples = [1/4, 3/8, 1/2, 5/8, 3/4] := by decide +kernel
example : currentSamples ≠ localSamples := by decide +kernel
example : sampleTimes.map (current (1/4) (1/4) .provider .provider) =
    sampleTimes.map (endpointLocal (1/4) (1/4) .provider .provider) := by decide +kernel

example : sampleTimes.map (current (1/4) (3/4) (.literal (1/4)) (.literal (3/4))) =
    [1/4, 3/8, 1/2, 5/8, 3/4] := by decide +kernel

end KeyframeContext
