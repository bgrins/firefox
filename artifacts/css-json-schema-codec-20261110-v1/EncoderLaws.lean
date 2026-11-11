import Encoder
import SchemaLaws

namespace CssDerivation.JsonSchema
open Lean FirstOrder TypedCodec

theorem scalar_from_char (c : Char) : scalarAllowed c.toNat := c.valid

theorem natJson_value (n : Nat) : (natJson n).getNat? = .ok n := rfl

theorem encodeExprJson_schema (aliases : Aliases) (e : Expr Γ t) :
    ExprSchema aliases (encodeExprJson e) (encodeExpr e) := by
  induction e with
  | nat n => exact .node (.rightArgs 2 1 _ _) (.nat (natJson_value n))
  | scalar c =>
    simpa only [encodeExprJson, encodeExpr, nodeJson, Char.ofNat_toNat] using
      (ExprSchema.node (Node.rightArgs 2 1 "scalar" [natJson c.toNat])
        (ExprArguments.scalar (natJson_value c.toNat) (scalar_from_char c)))
  | bool b => exact .node (.rightArgs 2 1 _ _) (.bool b)
  | var v => exact .node (.rightArgs 2 1 _ _) (.var (natJson_value (encodeVar v)))
  | nil => exact .node (.rightArgs 2 1 _ _) .nil
  | unit => exact .node (.rightArgs 2 1 _ _) .unit
  | code a ha => exact .node (.rightArgs 2 1 _ _) (.code ha)
  | scalarOf a ha => exact .node (.rightArgs 2 1 _ _) (.scalarOf ha)
  | add a b ha hb => exact .node (.rightArgs 2 1 _ _) (.add ha hb)
  | sub a b ha hb => exact .node (.rightArgs 2 1 _ _) (.sub ha hb)
  | mul a b ha hb => exact .node (.rightArgs 2 1 _ _) (.mul ha hb)
  | leNat a b ha hb => exact .node (.rightArgs 2 1 _ _) (.leNat ha hb)
  | ltNat a b ha hb => exact .node (.rightArgs 2 1 _ _) (.ltNat ha hb)
  | eqNat a b ha hb => exact .node (.rightArgs 2 1 _ _) (.eqNat ha hb)
  | leChar a b ha hb => exact .node (.rightArgs 2 1 _ _) (.leChar ha hb)
  | eqChar a b ha hb => exact .node (.rightArgs 2 1 _ _) (.eqChar ha hb)
  | and a b ha hb => exact .node (.rightArgs 2 1 _ _) (.and ha hb)
  | or a b ha hb => exact .node (.rightArgs 2 1 _ _) (.or ha hb)
  | cons a b ha hb => exact .node (.rightArgs 2 1 _ _) (.cons ha hb)
  | ite a b c ha hb hc => exact .node (.rightArgs 2 1 _ _) (.ite ha hb hc)
  | foldNat a b c ha hb hc => exact .node (.rightArgs 2 1 _ _) (.foldNat ha hb hc)

theorem encodeStmtJson_schema (aliases : Aliases) (p : Stmt Γ t) :
    StmtSchema aliases (encodeStmtJson p) (encodeStmt p) := by
  induction p with
  | ret e => exact .node (.rightArgs 2 1 _ _) (.ret (encodeExprJson_schema aliases e))
  | letE e p hp => exact .node (.rightArgs 2 1 _ _) (.letE (encodeExprJson_schema aliases e) hp)
  | read a b ha hb => exact .node (.rightArgs 2 1 _ _) (.read ha hb)
  | scan n e p hp => exact .node (.rightArgs 2 1 _ _) (.scan (natJson_value n) (encodeExprJson_schema aliases e) hp)
  | raiseError p hp => exact .node (.rightArgs 2 1 _ _) (.raiseError hp)
  | branch e a b ha hb => exact .node (.rightArgs 2 1 _ _) (.branch (encodeExprJson_schema aliases e) ha hb)

theorem expression_json_roundtrip (aliases : Aliases) (e : Expr Γ t) :
    checkExprJson aliases Γ t (encodeExprJson e) = some e := by
  rw [checkExprJson, (readExprData_spec _ _ _).mpr (encodeExprJson_schema aliases e)]
  exact checkExpr_roundtrip e

theorem statement_json_roundtrip (aliases : Aliases) (p : Stmt Γ t) :
    checkStmtJson aliases Γ t (encodeStmtJson p) = some p := by
  rw [checkStmtJson, (readStmtData_spec _ _ _).mpr (encodeStmtJson_schema aliases p)]
  exact checkStmt_roundtrip p

theorem accepted_expression_schema (aliases : Aliases) (j : Json) (e : Expr Γ t)
    (accepted : checkExprJson aliases Γ t j = some e) :
    ∃ raw, ExprSchema aliases j raw ∧ encodeExpr e = normalizeExpr raw := by
  cases h : readExprData aliases j with
  | none => simp [checkExprJson, h] at accepted
  | some raw =>
    have checked : TypedCodec.checkExpr Γ t raw = some e := by simpa [checkExprJson, h] using accepted
    exact ⟨raw, (readExprData_spec _ _ _).mp h, checkExpr_faithful raw e checked⟩

theorem accepted_statement_schema (aliases : Aliases) (j : Json) (p : Stmt Γ t)
    (accepted : checkStmtJson aliases Γ t j = some p) :
    ∃ raw, StmtSchema aliases j raw ∧ encodeStmt p = normalizeStmt raw := by
  cases h : readStmtData aliases j with
  | none => simp [checkStmtJson, h] at accepted
  | some raw =>
    have checked : TypedCodec.checkStmt Γ t raw = some p := by simpa [checkStmtJson, h] using accepted
    exact ⟨raw, (readStmtData_spec _ _ _).mp h, checkStmt_faithful raw p checked⟩

end CssDerivation.JsonSchema
