import FlexViolation.Model

namespace FlexViolation

def PrefixTarget : Prop :=
  ∀ items, Acquired items → ∀ n ≤ items.length,
    Fits64 (total (items.take n))

def DifferenceTarget : Prop :=
  ∀ item, ValidItem item →
    Fits32 (clamped item) ∧ Fits64 (adjustment item) ∧
    -(2 ^ 32 - 1) ≤ adjustment item ∧ adjustment item ≤ 2 ^ 32 - 1

def FoldTarget : Prop :=
  ∀ items, Acquired items → wideFold items = some (total items)

def SelectionTarget : Prop :=
  ∀ items, Acquired items →
    frozen items = items.filter (specSelected (total items))

def ProgressTarget : Prop :=
  ∀ items, Acquired items → items ≠ [] → frozen items ≠ []

def CompatibilityTarget : Prop :=
  ∀ items value, Acquired items → oldFold items = some value →
    value = total items ∧ wideFold items = some value

def WitnessTarget : Prop :=
  Acquired positiveWitness ∧
  total positiveWitness = 2400000000 ∧
  kind (total positiveWitness) = .minimum ∧
  (frozen positiveWitness).map Item.identity = [1, 2, 3, 4] ∧
  kind (wrap32 (total positiveWitness)) = .maximum ∧
  positiveWitness.filter (selected (kind (wrap32 (total positiveWitness)))) = [] ∧
  Acquired subtractionWitness ∧ total subtractionWitness = max32 ∧
  oldFold subtractionWitness = none ∧ wideFold subtractionWitness = some max32

def UniversalTarget : Prop :=
  PrefixTarget ∧ DifferenceTarget ∧ FoldTarget ∧ SelectionTarget ∧
  ProgressTarget ∧ CompatibilityTarget ∧ WitnessTarget

end FlexViolation
