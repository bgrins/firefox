import Codec

namespace CssDerivation.TypedCodec
open FirstOrder

@[simp] theorem expect_same {F : Ty → Type} (e : F t) :
    expect t ⟨t, e⟩ = some e := by simp [expect]

@[simp] theorem inferVar_encode (v : Var Γ t) :
    inferVar Γ (encodeVar v) = some ⟨t, v⟩ := by
  induction v with
  | here => rfl
  | there v ih => simp [encodeVar, inferVar, ih]

theorem decodeVar_encode (v : Var Γ t) :
    decodeVar Γ t (encodeVar v) = some v := by
  simp [decodeVar]

@[simp] theorem inferExpr_encode (e : Expr Γ t) :
    inferExpr Γ (encodeExpr e) = some ⟨t, e⟩ := by
  induction e <;> simp_all [encodeExpr, inferExpr]

@[simp] theorem decodeExpr_encode (e : Expr Γ t) :
    decodeExpr Γ t (encodeExpr e) = some e := by
  simp [decodeExpr]

theorem decodeStmt_encode (p : Stmt Γ t) :
    decodeStmt Γ t (encodeStmt p) = some p := by
  induction p <;> simp_all [encodeStmt, decodeStmt]

@[simp] theorem normalize_encodeExpr (e : Expr Γ t) :
    normalizeExpr (encodeExpr e) = encodeExpr e := by
  induction e <;> simp_all [encodeExpr, normalizeExpr]

@[simp] theorem normalize_encodeStmt (p : Stmt Γ t) :
    normalizeStmt (encodeStmt p) = encodeStmt p := by
  induction p <;> simp_all [encodeStmt, normalizeStmt]

theorem checkExpr_roundtrip (e : Expr Γ t) :
    checkExpr Γ t (encodeExpr e) = some e := by
  simp [checkExpr]

theorem checkStmt_roundtrip (p : Stmt Γ t) :
    checkStmt Γ t (encodeStmt p) = some p := by
  simp [checkStmt, decodeStmt_encode]

theorem checkExpr_faithful (data : DataExpr) (e : Expr Γ t)
    (accepted : checkExpr Γ t data = some e) :
    encodeExpr e = normalizeExpr data := by
  unfold checkExpr at accepted
  cases h : decodeExpr Γ t data with
  | none => simp [h] at accepted
  | some actual =>
    rw [h] at accepted
    change (if _ then some actual else none) = _ at accepted
    split at accepted
    next faithful => cases Option.some.inj accepted; exact faithful
    next => contradiction

theorem checkStmt_faithful (data : DataStmt) (p : Stmt Γ t)
    (accepted : checkStmt Γ t data = some p) :
    encodeStmt p = normalizeStmt data := by
  unfold checkStmt at accepted
  cases h : decodeStmt Γ t data with
  | none => simp [h] at accepted
  | some actual =>
    rw [h] at accepted
    change (if _ then some actual else none) = _ at accepted
    split at accepted
    next faithful => cases Option.some.inj accepted; exact faithful
    next => contradiction

theorem scope_mismatch_rejected (Γ : List Ty) (head : Ty) (e : DataExpr)
    (mismatch : Γ.head? ≠ some head) : inferExpr Γ (.scope head e) = none := by
  simp [inferExpr, mismatch]

end CssDerivation.TypedCodec
