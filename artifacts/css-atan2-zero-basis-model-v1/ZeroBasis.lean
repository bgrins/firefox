namespace Atan2ZeroBasis

def coefficientRotation (negativeY negativeX : Bool) : Nat :=
  if negativeX then (if negativeY then 225 else 135)
  else (if negativeY then 315 else 45)

def resolvedRotation (basis : Nat) (negativeY negativeX : Bool) : Nat :=
  if basis = 0 then (if negativeX then 180 else 0)
  else coefficientRotation negativeY negativeX

theorem nonzero_basis_suffices (basis : Nat) (negativeY negativeX : Bool)
    (ready : basis ≠ 0) :
    resolvedRotation basis negativeY negativeX = coefficientRotation negativeY negativeX := by
  simp [resolvedRotation, ready]

theorem zero_basis_differs (negativeY negativeX : Bool) :
    resolvedRotation 0 negativeY negativeX ≠ coefficientRotation negativeY negativeX := by
  cases negativeY <;> cases negativeX <;> decide

theorem folding_exact_iff (basis : Nat) (negativeY negativeX : Bool) :
    resolvedRotation basis negativeY negativeX = coefficientRotation negativeY negativeX ↔
      basis ≠ 0 := by
  constructor
  · intro equal zero
    subst basis
    exact zero_basis_differs negativeY negativeX equal
  · exact nonzero_basis_suffices basis negativeY negativeX

theorem sampled_positive_context_is_insufficient :
    resolvedRotation 10 false false = coefficientRotation false false ∧
    resolvedRotation 0 false false ≠ coefficientRotation false false := by
  decide

end Atan2ZeroBasis
