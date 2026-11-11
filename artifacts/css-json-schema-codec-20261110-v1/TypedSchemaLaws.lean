import EncoderLaws

namespace CssDerivation.JsonSchema
open Lean FirstOrder TypedCodec

mutual
  theorem alias_free_expression_normalized {j e} (schema : ExprSchema [] j e) :
      normalizeExpr e = e := by
    cases schema with
    | node _ arguments => exact alias_free_arguments_normalized arguments
  termination_by (sizeOf e, 1)
  decreasing_by all_goals simp_wf; all_goals simp_all only; all_goals omega

  theorem alias_free_arguments_normalized {op args e} (schema : ExprArguments [] op args e) :
      normalizeExpr e = e := by
    cases schema with
    | nat _ => rfl
    | scalar _ _ => rfl
    | bool _ => rfl
    | var _ => rfl
    | nil => rfl
    | unit => rfl
    | use h => simp at h
    | code ha =>
      simp only [normalizeExpr, alias_free_expression_normalized ha]
    | scalarOf ha =>
      simp only [normalizeExpr, alias_free_expression_normalized ha]
    | add ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | sub ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | mul ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | leNat ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | ltNat ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | eqNat ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | leChar ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | eqChar ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | and ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | or ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | cons ha hb =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb]
    | ite ha hb hc =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb, alias_free_expression_normalized hc]
    | foldNat ha hb hc =>
      simp only [normalizeExpr, alias_free_expression_normalized ha, alias_free_expression_normalized hb, alias_free_expression_normalized hc]
  termination_by (sizeOf e, 0)
  decreasing_by all_goals simp_wf; all_goals simp_all only; all_goals omega
end

mutual
  theorem alias_free_statement_normalized {j p} (schema : StmtSchema [] j p) :
      normalizeStmt p = p := by
    cases schema with
    | node _ arguments => exact alias_free_statement_arguments_normalized arguments
  termination_by (sizeOf p, 1)
  decreasing_by all_goals simp_wf; all_goals simp_all only; all_goals omega

  theorem alias_free_statement_arguments_normalized {op args p} (schema : StmtArguments [] op args p) :
      normalizeStmt p = p := by
    cases schema with
    | ret he => simp only [normalizeStmt, alias_free_expression_normalized he]
    | letE he hp => simp only [normalizeStmt, alias_free_expression_normalized he, alias_free_statement_normalized hp]
    | read ha hb => simp only [normalizeStmt, alias_free_statement_normalized ha, alias_free_statement_normalized hb]
    | scan _ he hp => simp only [normalizeStmt, alias_free_expression_normalized he, alias_free_statement_normalized hp]
    | raiseError hp => simp only [normalizeStmt, alias_free_statement_normalized hp]
    | branch he ha hb =>
      simp only [normalizeStmt, alias_free_expression_normalized he,
        alias_free_statement_normalized ha, alias_free_statement_normalized hb]
  termination_by (sizeOf p, 0)
  decreasing_by all_goals simp_wf; all_goals simp_all only; all_goals omega
end

theorem alias_free_expression_json_spec (j : Json) (e : Expr Γ t) :
    checkExprJson [] Γ t j = some e ↔ ExprSchema [] j (encodeExpr e) := by
  constructor
  · intro accepted
    obtain ⟨raw, schema, encoded⟩ := accepted_expression_schema [] j e accepted
    rw [alias_free_expression_normalized schema] at encoded
    rw [← encoded] at schema
    exact schema
  · intro schema
    rw [checkExprJson, (readExprData_spec _ _ _).mpr schema]
    exact checkExpr_roundtrip e

theorem alias_free_statement_json_spec (j : Json) (p : Stmt Γ t) :
    checkStmtJson [] Γ t j = some p ↔ StmtSchema [] j (encodeStmt p) := by
  constructor
  · intro accepted
    obtain ⟨raw, schema, encoded⟩ := accepted_statement_schema [] j p accepted
    rw [alias_free_statement_normalized schema] at encoded
    rw [← encoded] at schema
    exact schema
  · intro schema
    rw [checkStmtJson, (readStmtData_spec _ _ _).mpr schema]
    exact checkStmt_roundtrip p

theorem expression_schema_deterministic {aliases j a b}
    (first : ExprSchema aliases j a) (second : ExprSchema aliases j b) : a = b := by
  exact Option.some.inj (((readExprData_spec _ _ _).mpr first).symm.trans ((readExprData_spec _ _ _).mpr second))

theorem statement_schema_deterministic {aliases j a b}
    (first : StmtSchema aliases j a) (second : StmtSchema aliases j b) : a = b := by
  exact Option.some.inj (((readStmtData_spec _ _ _).mpr first).symm.trans ((readStmtData_spec _ _ _).mpr second))

end CssDerivation.JsonSchema
