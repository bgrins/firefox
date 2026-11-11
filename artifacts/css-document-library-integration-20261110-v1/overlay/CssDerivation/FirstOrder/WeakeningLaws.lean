import CssDerivation.FirstOrder.Weakening

namespace CssDerivation.DocumentDesign
open FirstOrder TypedCodec

theorem variable_erasure (v : Var Γ t) (Δ : List Ty) :
    encodeVar (weakenVar Δ v) = encodeVar v := by
  induction v <;> simp_all [weakenVar, encodeVar]

theorem expression_erasure (e : Expr Γ t) (Δ : List Ty) :
    encodeExpr (weakenExpr Δ e) = encodeExpr e := by
  induction e <;> simp_all [weakenExpr, encodeExpr, variable_erasure]

theorem lookup_weakening (v : Var Γ t) (env : Env Γ) (tail : Env Δ) :
    lookup (weakenVar Δ v) (appendEnv env tail) = lookup v env := by
  induction v with
  | here => cases env; rfl
  | there v ih => cases env; simpa [weakenVar, appendEnv, lookup] using ih _

theorem evaluation_weakening (e : Expr Γ t) (env : Env Γ) (tail : Env Δ) :
    eval (weakenExpr Δ e) (appendEnv env tail) = eval e env := by
  induction e with
  | foldNat xs z step ihxs ihz ihstep =>
    simp only [weakenExpr, eval, ihxs, ihz]
    have same : (fun acc c => eval (weakenExpr Δ step)
        (.cons c (.cons acc (appendEnv env tail)))) =
        (fun acc c => eval step (.cons c (.cons acc env))) := by
      funext acc c
      exact ihstep (.cons c (.cons acc env))
    rw [same]
  | _ => simp_all [weakenExpr, eval, lookup_weakening]

theorem scoped_alias_rechecks (e : Expr [head] result) (Δ : List Ty) :
    checkExpr (head :: Δ) result (.scope head (encodeExpr e)) =
      some (weakenExpr Δ e) := by
  have encoded := expression_erasure e Δ
  rw [← encoded]
  simp [checkExpr, decodeExpr, inferExpr, normalizeExpr]

theorem scoped_alias_independent (e : Expr [head] result) (value : head.Value)
    (tail : Env Δ) :
    eval (weakenExpr Δ e) (.cons value tail) = eval e (.cons value .nil) := by
  exact evaluation_weakening e (.cons value .nil) tail

theorem validated_data_rechecks (data : DataExpr) (e : Expr [head] result)
    (normalized : normalizeExpr data = data)
    (accepted : checkExpr [head] result data = some e) (Δ : List Ty) :
    checkExpr (head :: Δ) result (.scope head data) = some (weakenExpr Δ e) := by
  have equal := checkExpr_faithful data e accepted
  rw [normalized] at equal
  rw [← equal]
  exact scoped_alias_rechecks e Δ

end CssDerivation.DocumentDesign
