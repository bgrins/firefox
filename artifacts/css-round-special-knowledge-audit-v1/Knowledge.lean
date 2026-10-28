import Std

namespace RoundKnowledge

inductive Class where
  | negInf | negFinite | negZero | posZero | posFinite | posInf | nan
  deriving DecidableEq, Repr

inductive Strategy where
  | nearest | up | down | toZero
  deriving DecidableEq, Repr

def infiniteStep (s : Strategy) (a : Class) : Class :=
  match s, a with
  | .nearest, .negFinite | .nearest, .negZero
  | .toZero, .negFinite | .toZero, .negZero => .negZero
  | .nearest, _ | .toZero, _ => .posZero
  | .up, .posFinite => .posInf
  | .up, .posZero => .posZero
  | .up, _ => .negZero
  | .down, .negFinite => .negInf
  | .down, .negZero => .negZero
  | .down, _ => .posZero

def special (s : Strategy) (a b : Class) : Option Class :=
  match a, b with
  | .nan, _ | _, .nan | _, .negZero | _, .posZero => some .nan
  | .negInf, .negInf | .negInf, .posInf
  | .posInf, .negInf | .posInf, .posInf => some .nan
  | .negInf, _ => some .negInf
  | .posInf, _ => some .posInf
  | _, .negInf | _, .posInf => some (infiniteStep s a)
  | _, _ => none

theorem nan_priority (s : Strategy) (a : Class) :
    special s .nan a = some .nan ∧ special s a .nan = some .nan := by
  cases s <;> cases a <;> decide

theorem infinite_value_retained_iff (s : Strategy) (b : Class) :
    special s .posInf b = some .posInf ↔ b = .negFinite ∨ b = .posFinite := by
  cases s <;> cases b <;> decide

theorem unresolved_step_no_constant (s : Strategy) (result : Class) :
    ¬ (special s .posInf .posZero = some result ∧
       special s .posInf .posFinite = some result) := by
  cases s <;> cases result <;> decide

theorem unresolved_value_no_constant (result : Class) :
    ¬ (special .up .posFinite .posInf = some result ∧
       special .up .negFinite .posInf = some result) := by
  cases result <;> decide

example : special .up .posFinite .posInf = some .posInf := rfl
example : special .up .posZero .posInf = some .posZero := rfl
example : special .up .nan .posInf = some .nan := rfl
example : special .up .posInf .nan = some .nan := rfl

#print axioms nan_priority
#print axioms infinite_value_retained_iff
#print axioms unresolved_step_no_constant
#print axioms unresolved_value_no_constant

end RoundKnowledge
