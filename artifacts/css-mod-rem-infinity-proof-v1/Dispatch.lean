namespace ModRemInfinity

inductive Op where
  | mod | rem
  deriving DecidableEq, Repr

inductive Finite (α : Type) where
  | zero (negative : Bool)
  | nonzero (negative : Bool) (magnitude : α)
  deriving DecidableEq, Repr

inductive Number (α : Type) where
  | finite (value : Finite α)
  | infinity (negative : Bool)
  | nan
  deriving DecidableEq, Repr

def finiteSign : Finite α → Bool
  | .zero s | .nonzero s _ => s

def sign : Number α → Bool
  | .finite a => finiteSign a
  | .infinity s => s
  | .nan => false

def isFinite : Number α → Bool
  | .finite _ => true
  | _ => false

def isInfinite : Number α → Bool
  | .infinity _ => true
  | _ => false

abbrev FiniteBackend (α : Type) := Op → Finite α → Bool → α → Number α
abbrev Formula (α : Type) := Op → Number α → Number α → Number α

def css (arithmetic : FiniteBackend α) (op : Op) : Number α → Number α → Number α
  | .nan, _ | _, .nan => .nan
  | .infinity _, _ => .nan
  | .finite _, .finite (.zero _) => .nan
  | .finite a, .finite (.nonzero s magnitude) => arithmetic op a s magnitude
  | .finite a, .infinity s =>
      match op with
      | .rem => .finite a
      | .mod => if finiteSign a = s then .finite a else .nan

def formulaTable (arithmetic : FiniteBackend α) (op : Op) :
    Number α → Number α → Number α
  | .finite a, .finite (.nonzero s magnitude) => arithmetic op a s magnitude
  | _, _ => .nan

def FormulaContract (formula : Formula α) (arithmetic : FiniteBackend α) : Prop :=
  ∀ op a b, formula op a b = formulaTable arithmetic op a b

def native (formula : Formula α) (op : Op) (a b : Number α) : Number α :=
  if op = .mod ∧ isInfinite b ∧ sign a ≠ sign b then .nan
  else if isFinite a && isInfinite b then a
  else formula op a b

def oldNative (formula : Formula α) (op : Op) (a b : Number α) : Number α :=
  if op = .mod ∧ isInfinite b ∧ sign a ≠ sign b then .nan
  else formula op a b

theorem dispatch_refinement
    (specArithmetic nativeArithmetic : FiniteBackend α) (formula : Formula α)
    (finiteAgreement : ∀ op a s m, nativeArithmetic op a s m = specArithmetic op a s m)
    (formulaAgreement : FormulaContract formula nativeArithmetic)
    (op : Op) (a b : Number α) :
    native formula op a b = css specArithmetic op a b := by
  unfold FormulaContract at formulaAgreement
  cases op <;> cases a with
  | nan => cases b <;> simp [formulaAgreement, finiteAgreement, native, css, isFinite, isInfinite, sign,
      FormulaContract, formulaTable]
  | infinity s => cases s <;> cases b <;> simp [formulaAgreement, finiteAgreement, native, css, isFinite,
      isInfinite, sign, FormulaContract, formulaTable]
  | finite a =>
      cases a with
      | zero s =>
          cases s <;> cases b with
          | nan => simp [formulaAgreement, finiteAgreement, native, css, isFinite, isInfinite, sign, finiteSign,
              FormulaContract, formulaTable]
          | infinity t => cases t <;> simp [formulaAgreement, finiteAgreement, native, css, isFinite, isInfinite,
              sign, finiteSign, FormulaContract, formulaTable]
          | finite b => cases b <;> simp [formulaAgreement, finiteAgreement, native, css, isFinite, isInfinite,
              sign, finiteSign, FormulaContract, formulaTable]
      | nonzero s m =>
          cases s <;> cases b with
          | nan => simp [formulaAgreement, finiteAgreement, native, css, isFinite, isInfinite, sign, finiteSign,
              FormulaContract, formulaTable]
          | infinity t => cases t <;> simp [formulaAgreement, finiteAgreement, native, css, isFinite, isInfinite,
              sign, finiteSign, FormulaContract, formulaTable]
          | finite b => cases b <;> simp [formulaAgreement, finiteAgreement, native, css, isFinite, isInfinite,
              sign, finiteSign, FormulaContract, formulaTable]

theorem rem_infinite_identity (formula : Formula α) (a : Finite α) (s : Bool) :
    native formula .rem (.finite a) (.infinity s) = .finite a := by
  simp [native, isFinite, isInfinite]

theorem mod_same_sign_identity (formula : Formula α) (a : Finite α) :
    native formula .mod (.finite a) (.infinity (finiteSign a)) = .finite a := by
  simp [native, isFinite, isInfinite, sign]

theorem mod_opposite_sign_nan (formula : Formula α) (a : Finite α) :
    native formula .mod (.finite a) (.infinity (!finiteSign a)) = .nan := by
  cases h : finiteSign a <;> simp [native, isInfinite, sign, h]

theorem generated_negative_zero_preserved (formula : Formula α) :
    native formula .rem (.finite (.zero true)) (.infinity false) =
      .finite (.zero true) := by
  exact rem_infinite_identity formula (.zero true) false

theorem infinite_dividend_rejected
    (arithmetic : FiniteBackend α) (formula : Formula α)
    (contract : FormulaContract formula arithmetic) (op : Op) (s : Bool) (b : Number α) :
    native formula op (.infinity s) b = .nan := by
  rw [dispatch_refinement arithmetic arithmetic formula (by intros; rfl) contract]
  cases b <;> rfl

theorem nan_infectious_left
    (arithmetic : FiniteBackend α) (formula : Formula α)
    (contract : FormulaContract formula arithmetic) (op : Op) (b : Number α) :
    native formula op .nan b = .nan := by
  rw [dispatch_refinement arithmetic arithmetic formula (by intros; rfl) contract]
  cases b <;> rfl

theorem nan_infectious_right
    (arithmetic : FiniteBackend α) (formula : Formula α)
    (contract : FormulaContract formula arithmetic) (op : Op) (a : Number α) :
    native formula op a .nan = .nan := by
  rw [dispatch_refinement arithmetic arithmetic formula (by intros; rfl) contract]
  cases a <;> rfl

theorem zero_divisor_rejected
    (arithmetic : FiniteBackend α) (formula : Formula α)
    (contract : FormulaContract formula arithmetic) (op : Op) (a : Number α) (s : Bool) :
    native formula op a (.finite (.zero s)) = .nan := by
  rw [dispatch_refinement arithmetic arithmetic formula (by intros; rfl) contract]
  cases a <;> rfl

theorem finite_backend_unchanged (formula : Formula α) (op : Op)
    (a : Finite α) (s : Bool) (m : α) :
    native formula op (.finite a) (.finite (.nonzero s m)) =
      formula op (.finite a) (.finite (.nonzero s m)) := by
  simp [native, isFinite, isInfinite]

theorem old_mod_fails_nonzero
    (arithmetic : FiniteBackend α) (formula : Formula α)
    (contract : FormulaContract formula arithmetic) (s : Bool) (m : α) :
    oldNative formula .mod (.finite (.nonzero s m)) (.infinity s) ≠
      css arithmetic .mod (.finite (.nonzero s m)) (.infinity s) := by
  unfold FormulaContract at contract
  simp [oldNative, css, isInfinite, sign, finiteSign, contract, formulaTable]

theorem old_rem_fails_nonzero
    (arithmetic : FiniteBackend α) (formula : Formula α)
    (contract : FormulaContract formula arithmetic) (s t : Bool) (m : α) :
    oldNative formula .rem (.finite (.nonzero s m)) (.infinity t) ≠
      css arithmetic .rem (.finite (.nonzero s m)) (.infinity t) := by
  unfold FormulaContract at contract
  simp [oldNative, css, isInfinite, sign, finiteSign, contract, formulaTable]

#print axioms dispatch_refinement
#print axioms rem_infinite_identity
#print axioms mod_same_sign_identity
#print axioms mod_opposite_sign_nan
#print axioms generated_negative_zero_preserved
#print axioms infinite_dividend_rejected
#print axioms nan_infectious_left
#print axioms nan_infectious_right
#print axioms zero_divisor_rejected
#print axioms finite_backend_unchanged
#print axioms old_mod_fails_nonzero
#print axioms old_rem_fails_nonzero

end ModRemInfinity
