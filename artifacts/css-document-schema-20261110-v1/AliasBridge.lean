import DefinitionLaws
import Prototype

namespace CssDerivation.DocumentSchema
open Lean FirstOrder TypedCodec JsonSchema DocumentDesign

theorem definition_member {definitions signatures aliases}
    (relation : DefinitionListSchema definitions signatures aliases)
    {alias} (member : alias ∈ aliases) :
    ∃ signature ∈ signatures, DefinitionSchema signature definitions alias := by
  induction relation generalizing alias with
  | nil => simp at member
  | cons one later ih =>
    rcases List.mem_cons.mp member with same | member
    · subst alias
      exact ⟨_, by simp, one⟩
    · obtain ⟨signature, member, definition⟩ := ih member
      exact ⟨signature, by simp [member], definition⟩

theorem definition_data_normalized (signature : Signature) (definitions : Json) (data : DataExpr)
    (accepted : readDefinition definitions signature.name signature.head signature.result =
      some (signature.name, signature.head, data)) : normalizeExpr data = data := by
  obtain ⟨source, e, field, schema, same⟩ := (definition_spec _ _ _).mp accepted
  have encoded : data = encodeExpr e := congrArg (fun entry => entry.2.2) same
  rw [encoded]
  exact normalize_encodeExpr e

theorem selected_alias_semantics {signatures definitions aliases name alias}
    (accepted : readDefinitions signatures definitions = some aliases)
    (selected : aliases.find? (fun entry => entry.1 == name) = some alias) :
    ∃ signature ∈ signatures, ∃ e : Expr [signature.head] signature.result,
      alias = (signature.name, signature.head, encodeExpr e) ∧ signature.name = name ∧
      ∀ (Δ : List Ty) (value : signature.head.Value) (tail : Env Δ),
        (checkExprJson aliases (signature.head :: Δ) signature.result
          (nodeJson "use" [.str name])).map (fun decoded => eval decoded (.cons value tail)) =
          some (eval e (.cons value .nil)) := by
  have aligned := ((definitions_spec _ _ _).mp accepted).2.2
  obtain ⟨signature, member, source, e, field, schema, same⟩ :=
    definition_member aligned (List.mem_of_find?_eq_some selected)
  have sameName : signature.name = name := by
    have found := List.find?_some selected
    simpa [same] using found
  refine ⟨signature, member, e, same, sameName, ?_⟩
  intro Δ value tail
  have chosen : aliases.find? (fun entry => entry.1 == signature.name) =
      some (signature.name, signature.head, encodeExpr e) := by
    simpa [sameName, same] using selected
  have useSchema : ExprSchema aliases (nodeJson "use" [.str signature.name])
      (.scope signature.head (encodeExpr e)) :=
    .node (.rightArgs 2 1 _ _) (.use chosen)
  rw [← sameName, checkExprJson, (readExprData_spec _ _ _).mpr useSchema]
  simp only [Option.bind_some, scoped_alias_rechecks, Option.map_some]
  rw [scoped_alias_independent]

end CssDerivation.DocumentSchema
