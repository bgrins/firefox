namespace SpecialValueObserver

inductive Value where
  | nan | negInf | negZero | posZero | posInf
  deriving DecidableEq, Repr

open Value

def negate : Value → Value
  | nan => nan
  | negInf => posInf
  | posInf => negInf
  | negZero => posZero
  | posZero => negZero

def reciprocal : Value → Value
  | nan => nan
  | negInf => negZero
  | posInf => posZero
  | negZero => negInf
  | posZero => posInf

def opacity : Value → Bool
  | posInf => true
  | _ => false

def pair (v : Value) : Bool × Bool :=
  (opacity v, opacity (negate v))

def observe (v : Value) : (Bool × Bool) × (Bool × Bool) :=
  (pair v, pair (reciprocal v))

theorem positive_zero_passes_nan_pair : pair posZero = pair nan := rfl

theorem negative_zero_passes_nan_pair : pair negZero = pair nan := rfl

theorem nan_pair_ambiguous (v : Value) :
    pair v = pair nan ↔ v = nan ∨ v = negZero ∨ v = posZero := by
  cases v <;> decide

theorem observation_injective (a b : Value) :
    observe a = observe b ↔ a = b := by
  cases a <;> cases b <;> decide

theorem nan_observer_exact (v : Value) :
    observe v = ((false, false), (false, false)) ↔ v = nan := by
  cases v <;> decide

theorem positive_zero_observer_exact (v : Value) :
    observe v = ((false, false), (true, false)) ↔ v = posZero := by
  cases v <;> decide

theorem negative_zero_observer_exact (v : Value) :
    observe v = ((false, false), (false, true)) ↔ v = negZero := by
  cases v <;> decide

theorem positive_infinity_observer_exact (v : Value) :
    observe v = ((true, false), (false, false)) ↔ v = posInf := by
  cases v <;> decide

theorem negative_infinity_observer_exact (v : Value) :
    observe v = ((false, true), (false, false)) ↔ v = negInf := by
  cases v <;> decide

end SpecialValueObserver
