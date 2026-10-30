import SpecialValueObserver

namespace LogDispatch

inductive Argument where
  | one | other
  deriving DecidableEq

inductive Base where
  | one | zero | negative | nan | positiveOther
  deriving DecidableEq

inductive Action where
  | nan | positiveZero | delegate
  deriving DecidableEq

def positive : Base → Bool
  | .one | .positiveOther => true
  | _ => false

def source (a : Argument) (b : Base) : Action :=
  if b == .one then .nan
  else if a == .one && positive b then .positiveZero
  else .delegate

def clearRules : Argument → Base → Action
  | _, .one => .nan
  | .one, .positiveOther => .positiveZero
  | _, _ => .delegate

def evaluate {R : Type} (nan zero : R) (host : Argument → Base → R)
    (a : Argument) (b : Base) : R :=
  match source a b with
  | .nan => nan
  | .positiveZero => zero
  | .delegate => host a b

theorem source_matches_clear_rules (a : Argument) (b : Base) :
    source a b = clearRules a b := by
  cases a <;> cases b <;> decide

theorem base_one_invalid {R : Type} (nan zero : R) (host : Argument → Base → R)
    (a : Argument) : evaluate nan zero host a .one = nan := by
  cases a <;> rfl

theorem argument_one_positive_zero {R : Type} (nan zero : R)
    (host : Argument → Base → R) :
    evaluate nan zero host .one .positiveOther = zero := rfl

theorem invalid_base_precedes_argument_one {R : Type} (nan zero : R)
    (host : Argument → Base → R) : evaluate nan zero host .one .one = nan := rfl

theorem zero_base_delegates {R : Type} (nan zero : R)
    (host : Argument → Base → R) (a : Argument) :
    evaluate nan zero host a .zero = host a .zero := by
  cases a <;> rfl

theorem negative_base_delegates {R : Type} (nan zero : R)
    (host : Argument → Base → R) (a : Argument) :
    evaluate nan zero host a .negative = host a .negative := by
  cases a <;> rfl

theorem nan_base_delegates {R : Type} (nan zero : R)
    (host : Argument → Base → R) (a : Argument) :
    evaluate nan zero host a .nan = host a .nan := by
  cases a <;> rfl

theorem other_argument_positive_base_delegates {R : Type} (nan zero : R)
    (host : Argument → Base → R) :
    evaluate nan zero host .other .positiveOther = host .other .positiveOther := rfl

theorem clear_results_independent_of_host {R : Type} (nan zero : R)
    (first second : Argument → Base → R) (a : Argument) (b : Base)
    (h : clearRules a b ≠ .delegate) :
    evaluate nan zero first a b = evaluate nan zero second a b := by
  cases a <;> cases b <;> simp_all [clearRules, evaluate, source, positive]

open SpecialValueObserver

theorem base_one_observed_as_nan (host : Argument → Base → Value) (a : Argument) :
    observe (evaluate Value.nan Value.posZero host a .one) = observe Value.nan := by
  rw [base_one_invalid]

theorem argument_one_observed_as_positive_zero (host : Argument → Base → Value) :
    observe (evaluate Value.nan Value.posZero host .one .positiveOther) =
      observe Value.posZero := rfl

theorem negative_zero_leak_is_observable :
    observe Value.negZero ≠ observe Value.posZero := by decide

def reversedOrder (a : Argument) (b : Base) : Action :=
  if a == .one && positive b then .positiveZero
  else if b == .one then .nan
  else .delegate

end LogDispatch
