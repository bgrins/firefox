import Std

namespace CounterProvenance

def minimum : Int := -2147483648
def maximum : Int := 2147483647
def InRange (n : Int) : Prop := minimum ≤ n ∧ n ≤ maximum

inductive Integer where
  | inlineValue (n : Int)
  | boxedMath (resolved : Int)
  deriving DecidableEq, Repr

def resolve : Integer → Int
  | .inlineValue n | .boxedMath n => n

def get : Integer → Option Int
  | .inlineValue n => some n
  | .boxedMath _ => none

def authored : Integer → Integer
  | .inlineValue n => .inlineValue (if n = minimum then minimum + 1 else n)
  | .boxedMath n => .boxedMath n

def clampExplicit (n : Int) : Int :=
  if n < minimum + 1 then minimum + 1 else n

def compute (value : Integer) : Int :=
  if get value = some minimum then resolve value
  else clampExplicit (resolve value)

def fromRaw (value : Int) : Integer := .inlineValue value

inductive Mode where
  | increment | set | reset | reversedReset
  deriving DecidableEq, Repr

def omitted : Mode → Integer
  | .increment => .inlineValue 1
  | .set | .reset => .inlineValue 0
  | .reversedReset => .inlineValue minimum

def parse (mode : Mode) : Option Integer → Integer
  | none => omitted mode
  | some value => authored value

theorem authored_normalizes (value : Integer) :
    compute (authored value) = clampExplicit (resolve value) := by
  cases value with
  | inlineValue n =>
    by_cases h : n = minimum
    · subst n; simp [authored, compute, get, resolve, clampExplicit, minimum]
    · simp [authored, compute, get, resolve, h]
  | boxedMath n => simp [authored, compute, get, resolve]

theorem authored_preserves_nonmarker (value : Integer)
    (range : InRange (resolve value)) (notMarker : resolve value ≠ minimum) :
    compute (authored value) = resolve value := by
  rw [authored_normalizes]
  unfold InRange at range
  unfold clampExplicit
  split <;> omega

theorem parsed_domain (mode : Mode) (input : Option Integer)
    (bounded : ∀ value, input = some value → InRange (resolve value)) :
    InRange (compute (parse mode input)) ∧
    (compute (parse mode input) = minimum ↔
      input = none ∧ mode = .reversedReset) := by
  cases input with
  | none => cases mode <;> simp [InRange, compute, parse, omitted, get, resolve, clampExplicit, minimum, maximum]
  | some value =>
    have hv := bounded value rfl
    simp only [parse, authored_normalizes]
    unfold InRange minimum maximum at *
    simp only [Option.some_ne_none, false_and, iff_false]
    constructor
    · constructor <;> (unfold clampExplicit minimum; split <;> omega)
    · unfold clampExplicit minimum; split <;> omega

theorem raw_roundtrip (n : Int) (bounded : InRange n) :
    compute (fromRaw n) = n := by
  by_cases h : n = minimum
  · subst n; simp [compute, fromRaw, get, resolve]
  · simp [compute, fromRaw, get, resolve, h]
    unfold InRange clampExplicit at *
    split <;> omega

theorem marker_observation (value : Integer) :
    get value = some minimum ↔ compute value = minimum := by
  cases value with
  | inlineValue n =>
    by_cases h : n = minimum
    · subst n; simp [compute, get, resolve]
    · simp [compute, get, resolve, h]
      unfold clampExplicit
      split <;> omega
  | boxedMath n =>
    simp [compute, get, resolve]
    unfold clampExplicit
    split <;> omega

example : InRange (minimum + 1) ∧ InRange (minimum + 1 - 1) ∧
    compute (fromRaw (minimum + 1 - 1)) = minimum := by
  unfold InRange minimum maximum compute fromRaw get resolve
  decide +kernel

#print axioms authored_normalizes
#print axioms authored_preserves_nonmarker
#print axioms parsed_domain
#print axioms raw_roundtrip
#print axioms marker_observation
end CounterProvenance
