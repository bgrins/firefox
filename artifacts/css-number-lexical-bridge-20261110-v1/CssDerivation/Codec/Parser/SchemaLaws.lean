import CssDerivation.Codec.Parser.Reader

namespace CssDerivation.ParserJson
open Lean FirstOrder TypedCodec JsonSchema ParserIR

theorem readType_complete {j t} (schema : TypeSchema j t) :
    readType j = some ⟨t, schema⟩ := by cases schema <;> rfl

theorem readPredicate_complete {j p} (schema : ExprSchema [] j (encodeExpr p)) :
    readPredicate j = some ⟨p, schema⟩ := by
  have accepted := (alias_free_expression_json_spec j p).mpr schema
  unfold readPredicate certify
  split <;> simp_all <;> grind

theorem readLegacy_complete {j t} {p : Stmt [] t}
    (schema : StmtSchema [] j (encodeStmt p)) :
    readLegacy t j = some ⟨p, schema⟩ := by
  have accepted := (alias_free_statement_json_spec j p).mpr schema
  unfold readLegacy certify
  split <;> simp_all <;> grind

theorem node_arguments_smaller {j op args} (node : Node j op args) :
    sizeOf args < sizeOf j := by
  cases node <;> simp [rightObject, leftObject] <;> omega

mutual
  theorem readParser_complete {j shape} {p : Parser shape} (schema : ParserSchema j p) :
      readParser j = some ⟨shape, p, schema⟩ := by
    cases schema with
    | node node arguments =>
      cases node <;>
        simp only [rightObject, leftObject, readParser.eq_def] <;>
        rw [readArguments_complete arguments] <;> rfl
  termination_by sizeOf j
  decreasing_by
    all_goals simp_wf
    all_goals apply node_arguments_smaller
    all_goals assumption

  theorem readArguments_complete {op args shape} {p : Parser shape}
      (schema : ParserArguments op args p) :
      readArguments op args = some ⟨shape, p, schema⟩ := by
    cases schema with
    | legacy ht hp =>
      rw [readArguments, readType_complete ht]
      simp only [Option.bind_eq_bind, Option.bind_some]
      rw [readLegacy_complete hp]; rfl
    | take hp => rw [readArguments, readPredicate_complete hp]; rfl
    | scan hp => rw [readArguments, readPredicate_complete hp]; rfl
    | nonempty hp => rw [readArguments, readParser_complete hp]
    | pair ha hb => rw [readArguments, readParser_complete ha, readParser_complete hb]; rfl
    | right ha hb => rw [readArguments, readParser_complete ha, readParser_complete hb]; rfl
    | optional hp => rw [readArguments, readParser_complete hp]; rfl
  termination_by sizeOf args
  decreasing_by all_goals simp_wf; all_goals simp_all only; all_goals omega
end

theorem decodeParser_spec {shape} (j : Json) (p : Parser shape) :
    decodeParser shape j = some p ↔ ParserSchema j p := by
  constructor
  · intro accepted
    cases h : readParser j with
    | none => simp [decodeParser, h] at accepted
    | some parsed =>
      rcases parsed with ⟨actual, q, schema⟩
      by_cases same : actual = shape
      · subst actual
        have eq : q = p := by simpa [decodeParser, h, expectParser] using accepted
        exact eq ▸ schema
      · simp [decodeParser, h, expectParser, same] at accepted
  · intro schema
    simp [decodeParser, readParser_complete schema, expectParser]

end CssDerivation.ParserJson
