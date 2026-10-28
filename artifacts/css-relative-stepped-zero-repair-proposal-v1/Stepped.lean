namespace RelativeStepped

inductive Op where
  | mod | rem | nearest
  deriving DecidableEq, Repr

def coefficient : Op → Nat
  | .mod | .rem => 1
  | .nearest => 4

def operation (op : Op) (basis : Nat) : Option Nat :=
  if basis = 0 then none else
    some (match op with
      | .mod | .rem => (3 * basis) % (2 * basis)
      | .nearest => ((3 * basis + basis) / (2 * basis)) * (2 * basis))

def observe (bias : Nat) : Option Nat → Nat
  | none => 0
  | some length => bias + length

def folded (op : Op) (basis : Nat) : Option Nat :=
  some (coefficient op * basis)

inductive Decision where
  | defer | evaluate (basis : Nat)
  deriving DecidableEq, Repr

def schedule : Option Nat → Decision
  | none => .defer
  | some basis => .evaluate basis

theorem zero_basis_witness (op : Op) (bias : Nat) (nonzero : bias ≠ 0) :
    observe bias (operation op 0) ≠ observe bias (folded op 0) := by
  simp [observe, operation, folded, Ne.symm nonzero]

theorem positive_controls :
    ([Op.mod, .rem, .nearest].all fun op =>
      (List.range 64).all fun n => operation op (n + 1) == folded op (n + 1)) = true := by
  decide +kernel

theorem exact_recovery :
    ([Op.mod, .rem, .nearest].map fun op =>
      [10, 0, 10].map fun basis => observe 10 (operation op basis)) =
    [[20, 0, 20], [20, 0, 20], [50, 0, 50]] := by decide +kernel

theorem unknown_basis_defers : schedule none = .defer := rfl

theorem evaluation_requires_known_basis (knowledge : Option Nat) (basis : Nat)
    (chosen : schedule knowledge = .evaluate basis) : knowledge = some basis := by
  cases knowledge with
  | none => cases chosen
  | some actual => simp [schedule] at chosen; subst actual; rfl

#print axioms zero_basis_witness
#print axioms positive_controls
#print axioms exact_recovery
#print axioms unknown_basis_defers
#print axioms evaluation_requires_known_basis
end RelativeStepped
