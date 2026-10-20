import CssSemantics.CssCalculationTyping
import CssSemantics.CssFiniteScalar

namespace CssSemantics.CssNumericEnvironment

open CssFiniteScalar CssCalculationTyping

structure Basis where
  target : Dimension
  value : Scalar
  deriving DecidableEq, Repr

structure Environment where
  basis : Option Basis
  unitFactor : String → Option Rat

def empty : Environment := ⟨none, fun _ => none⟩

instance (value : Scalar) : Decidable value.Valid :=
  inferInstanceAs (Decidable (value.negativeZero = true → value.value = 0))

def resolveBasis (types : CssCalculationType.Context) (environment : Environment) : Option Basis :=
  match environment.basis with
  | none => none
  | some basis =>
    if types.percentage = some basis.target.toBase ∧ basis.value.Valid then some basis else none

def Available (types : CssCalculationType.Context) (environment : Environment) (basis : Basis) : Prop :=
  environment.basis = some basis ∧ types.percentage = some basis.target.toBase ∧ basis.value.Valid

theorem resolveBasis_iff (types environment basis) :
    resolveBasis types environment = some basis ↔ Available types environment basis := by
  unfold resolveBasis Available
  split
  · simp_all
  · split <;> simp_all
    all_goals rintro rfl <;> simp_all

theorem Available.unique {types environment first last}
    (left : Available types environment first) (right : Available types environment last) : first = last :=
  Option.some.inj (left.1.symm.trans right.1)

theorem Available.valid {types environment basis} (available : Available types environment basis) :
    basis.value.Valid := available.2.2

theorem Available.target {types environment basis} (available : Available types environment basis) :
    types.percentage = some basis.target.toBase := available.2.1

theorem Available.nonpercent {types environment basis} (available : Available types environment basis) :
    types.percentage ≠ some .percent := by
  rw [available.target]
  cases basis.target <;> decide

def coefficient (value : CssNumberValue.Value) : Scalar := source (value.toRat / 100)

def resolvePercentage (types : CssCalculationType.Context) (environment : Environment)
    (value : CssNumberValue.Value) : Option Scalar :=
  (resolveBasis types environment).map fun basis => multiply (coefficient value) basis.value

def ResolvedPercentage (types : CssCalculationType.Context) (environment : Environment)
    (value : CssNumberValue.Value) (result : Scalar) : Prop :=
  ∃ basis, Available types environment basis ∧ Product (coefficient value) basis.value result

theorem resolvePercentage_iff (types environment value result) :
    resolvePercentage types environment value = some result ↔ ResolvedPercentage types environment value result := by
  simp only [resolvePercentage, Option.map_eq_some_iff, ResolvedPercentage, resolveBasis_iff, multiply_iff]

theorem ResolvedPercentage.valid {types environment value result}
    (resolved : ResolvedPercentage types environment value result) : result.Valid := by
  obtain ⟨basis, _, product⟩ := resolved
  rw [← product.result]
  exact multiply_valid _ _

theorem ResolvedPercentage.origin {types environment value result}
    (resolved : ResolvedPercentage types environment value result) :
    ∃ basis, Available types environment basis ∧ result.value = (value.toRat / 100) * basis.value.value := by
  obtain ⟨basis, available, product⟩ := resolved
  exact ⟨basis, available, by rw [← product.result]; rfl⟩

theorem resolveBasis_empty (types) : resolveBasis types empty = none := rfl

theorem resolvePercentage_empty (types value) : resolvePercentage types empty value = none := rfl

end CssSemantics.CssNumericEnvironment
