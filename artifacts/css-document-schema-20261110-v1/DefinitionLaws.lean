import KeyLaws

namespace CssDerivation.DocumentSchema
open Lean FirstOrder TypedCodec JsonSchema

theorem definition_spec (signature : Signature) (definitions : Json)
    (alias : String × Ty × DataExpr) :
    readDefinition definitions signature.name signature.head signature.result = some alias ↔
      DefinitionSchema signature definitions alias := by
  constructor
  · intro accepted
    cases sourceRead : field definitions signature.name with
    | none => simp [readDefinition, sourceRead] at accepted
    | some source =>
      cases dataRead : readExprData [] source with
      | none => simp [readDefinition, sourceRead, dataRead] at accepted
      | some data =>
        cases checked : checkExpr [signature.head] signature.result data with
        | none => simp [readDefinition, sourceRead, dataRead, checked] at accepted
        | some e =>
          have schema := (readExprData_spec _ _ _).mp dataRead
          have encoded := checkExpr_faithful data e checked
          rw [alias_free_expression_normalized schema] at encoded
          have same : (signature.name, signature.head, data) = alias := by
            simpa [readDefinition, sourceRead, dataRead, checked] using accepted
          refine ⟨source, e, (field_spec _ _ _).mp sourceRead, ?_, ?_⟩
          · simpa [encoded] using schema
          · simpa [encoded] using same.symm
  · rintro ⟨source, e, sourceField, schema, rfl⟩
    have sourceRead := (field_spec _ _ _).mpr sourceField
    have dataRead := (readExprData_spec _ _ _).mpr schema
    simp [readDefinition, sourceRead, dataRead, checkExpr_roundtrip]

theorem definition_list_spec (signatures : List Signature) (definitions : Json)
    (aliases : Aliases) :
    readDefinitionList signatures definitions = some aliases ↔
      DefinitionListSchema definitions signatures aliases := by
  induction signatures generalizing aliases with
  | nil =>
    constructor
    · intro accepted
      have same : aliases = [] := by simpa [readDefinitionList] using accepted.symm
      subst aliases
      exact .nil
    · intro relation
      cases relation
      rfl
  | cons signature rest ih =>
    constructor
    · intro accepted
      cases one : readDefinition definitions signature.name signature.head signature.result with
      | none => simp [readDefinitionList, one] at accepted
      | some alias =>
        cases later : readDefinitionList rest definitions with
        | none => simp [readDefinitionList, one, later] at accepted
        | some tail =>
          have same : alias :: tail = aliases := by
            simpa [readDefinitionList, one, later] using accepted
          subst aliases
          exact .cons ((definition_spec _ _ _).mp one) ((ih _).mp later)
    · intro relation
      cases relation with
      | cons one later =>
        simp [readDefinitionList, (definition_spec _ _ _).mpr one, (ih _).mpr later]

theorem definitions_spec (signatures : List Signature) (definitions : Json)
    (aliases : Aliases) :
    readDefinitions signatures definitions = some aliases ↔
      DefinitionsSchema signatures definitions aliases := by
  constructor
  · intro accepted
    by_cases unique : (signatures.map Signature.name).Nodup
    · by_cases keys : fieldsExactly definitions (signatures.map Signature.name) = true
      · refine ⟨unique, (exact_keys_spec _ _ unique).mp keys, ?_⟩
        apply (definition_list_spec _ _ _).mp
        simpa [readDefinitions, unique, keys] using accepted
      · simp [readDefinitions, unique, keys] at accepted
    · simp [readDefinitions, unique] at accepted
  · rintro ⟨unique, keys, aligned⟩
    simp [readDefinitions, unique, (exact_keys_spec _ _ unique).mpr keys,
      (definition_list_spec _ _ _).mpr aligned]

theorem definition_names {definitions signatures aliases}
    (relation : DefinitionListSchema definitions signatures aliases) :
    aliases.map Prod.fst = signatures.map Signature.name := by
  induction relation with
  | nil => rfl
  | cons one _ ih =>
    obtain ⟨source, e, field, schema, rfl⟩ := one
    simp only [List.map_cons, ih]

theorem admitted_alias_names {signatures definitions aliases}
    (accepted : readDefinitions signatures definitions = some aliases) :
    aliases.map Prod.fst = signatures.map Signature.name ∧ (aliases.map Prod.fst).Nodup := by
  obtain ⟨unique, _, relation⟩ := (definitions_spec _ _ _).mp accepted
  have names := definition_names relation
  exact ⟨names, names.symm ▸ unique⟩

end CssDerivation.DocumentSchema
