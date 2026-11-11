import Reader

namespace CssDerivation.JsonSchema
open Lean FirstOrder TypedCodec

mutual
  theorem readExpr_complete {aliases j e} (schema : ExprSchema aliases j e) :
      readExpr aliases j = some ⟨e, schema⟩ := by
    cases schema with
    | node shape arguments =>
      cases shape <;>
        simp only [rightObject, leftObject, readExpr.eq_def] <;>
        rw [readExprArguments_complete arguments] <;> rfl
  termination_by (sizeOf e, 1)
  decreasing_by all_goals simp_wf; all_goals simp_all only; all_goals omega

  theorem readExprArguments_complete {aliases op args e} (schema : ExprArguments aliases op args e) :
      readExprArguments aliases op args = some ⟨e, schema⟩ := by
    cases schema with
    | nat h => rw [readExprArguments.eq_1]; split <;> simp_all <;> grind
    | scalar h valid => rw [readExprArguments.eq_2]; split <;> simp_all <;> grind
    | bool b => rw [readExprArguments]
    | var h => rw [readExprArguments.eq_4]; split <;> simp_all <;> grind
    | nil => rw [readExprArguments]
    | unit => rw [readExprArguments]
    | use h => rw [readExprArguments.eq_7]; split <;> simp_all <;> grind
    | code ha =>
      rw [readExprArguments, readExpr_complete ha]; rfl
    | scalarOf ha =>
      rw [readExprArguments, readExpr_complete ha]; rfl
    | add ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | sub ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | mul ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | leNat ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | ltNat ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | eqNat ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | leChar ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | eqChar ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | and ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | or ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | cons ha hb =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb]; rfl
    | ite ha hb hc =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb, readExpr_complete hc]; rfl
    | foldNat ha hb hc =>
      rw [readExprArguments, readExpr_complete ha, readExpr_complete hb, readExpr_complete hc]; rfl
  termination_by (sizeOf e, 0)
  decreasing_by all_goals simp_wf; all_goals simp_all only; all_goals omega
end

mutual
  theorem readStmt_complete {aliases j p} (schema : StmtSchema aliases j p) :
      readStmt aliases j = some ⟨p, schema⟩ := by
    cases schema with
    | node shape arguments =>
      cases shape <;>
        simp only [rightObject, leftObject, readStmt.eq_def] <;>
        rw [readStmtArguments_complete arguments] <;> rfl
  termination_by (sizeOf p, 1)
  decreasing_by all_goals simp_wf; all_goals simp_all only; all_goals omega

  theorem readStmtArguments_complete {aliases op args p} (schema : StmtArguments aliases op args p) :
      readStmtArguments aliases op args = some ⟨p, schema⟩ := by
    cases schema with
    | ret he => rw [readStmtArguments, readExpr_complete he]; rfl
    | letE he hp => rw [readStmtArguments, readExpr_complete he, readStmt_complete hp]; rfl
    | read ha hb => rw [readStmtArguments, readStmt_complete ha, readStmt_complete hb]; rfl
    | scan hn he hp =>
      rw [readStmtArguments]
      rw [readExpr_complete he, readStmt_complete hp]
      split <;> simp_all <;> grind
    | raiseError hp => rw [readStmtArguments, readStmt_complete hp]; rfl
    | branch he ha hb =>
      rw [readStmtArguments, readExpr_complete he, readStmt_complete ha, readStmt_complete hb]; rfl
  termination_by (sizeOf p, 0)
  decreasing_by all_goals simp_wf; all_goals simp_all only; all_goals omega
end

theorem readExprData_spec (aliases : Aliases) (j : Json) (e : DataExpr) :
    readExprData aliases j = some e ↔ ExprSchema aliases j e := by
  constructor
  · intro accepted
    cases h : readExpr aliases j with
    | none => simp [readExprData, h] at accepted
    | some value =>
      have same : value.val = e := by simpa [readExprData, h] using accepted
      exact same ▸ value.property
  · intro schema
    simp [readExprData, readExpr_complete schema]

theorem readStmtData_spec (aliases : Aliases) (j : Json) (p : DataStmt) :
    readStmtData aliases j = some p ↔ StmtSchema aliases j p := by
  constructor
  · intro accepted
    cases h : readStmt aliases j with
    | none => simp [readStmtData, h] at accepted
    | some value =>
      have same : value.val = p := by simpa [readStmtData, h] using accepted
      exact same ▸ value.property
  · intro schema
    simp [readStmtData, readStmt_complete schema]

end CssDerivation.JsonSchema
