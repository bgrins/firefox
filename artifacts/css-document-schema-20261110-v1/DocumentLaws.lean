import DefinitionLaws

namespace CssDerivation.DocumentSchema
open Lean FirstOrder TypedCodec JsonSchema

theorem natural_option_spec (j : Json) (n : Nat) :
    j.getNat?.toOption = some n ↔ j.getNat? = .ok n := by
  cases j.getNat? <;> simp [Except.toOption]

theorem object_option_sound (j : Json) (value)
    (accepted : j.getObj?.toOption = some value) : ObjectValue j := by
  cases j <;> simp [Json.getObj?, Except.toOption] at accepted
  exact ⟨_, rfl⟩

theorem outer_keys_unique : outerKeys.Nodup := by decide

theorem document_sound (signatures : List Signature) (result : Ty)
    (j : Json) (p : Stmt [] result)
    (accepted : readDocumentWith signatures result j = some p) :
    DocumentSchema signatures result j p := by
  by_cases keys : fieldsExactly j outerKeys = true
  · simp only [readDocumentWith, keys, Bool.not_true, Bool.false_eq_true, ite_false,
      Option.bind_eq_bind, Option.bind_eq_some_iff] at accepted
    obtain ⟨version, versionField, accepted⟩ := accepted
    by_cases versionOk : version.getNat?.toOption = some 1
    · simp only [versionOk] at accepted
      change (field j "definitions").bind _ = some p at accepted
      simp only [Option.bind_eq_some_iff] at accepted
      obtain ⟨definitions, definitionField, aliases, aliasesRead, sourceMap, sourceMapField,
        map, sourceMapRead, source, sourceField, programRead⟩ := accepted
      obtain ⟨raw, schema, encoded⟩ := accepted_statement_schema aliases source p programRead
      exact ⟨version, definitions, sourceMap, source, aliases, raw,
        (exact_keys_spec _ _ outer_keys_unique).mp keys,
        (field_spec _ _ _).mp versionField, (natural_option_spec _ _).mp versionOk,
        (field_spec _ _ _).mp definitionField, (definitions_spec _ _ _).mp aliasesRead,
        (field_spec _ _ _).mp sourceMapField, object_option_sound _ _ sourceMapRead,
        (field_spec _ _ _).mp sourceField, schema, encoded⟩
    · simp [versionOk] at accepted
  · simp [readDocumentWith, keys] at accepted

theorem option_guard_bind (test : Bool) (action : Option α) (next : α → Option β) :
    (if test then action else none).bind next =
      (if !test then none else action.bind next) := by
  cases test <;> rfl

theorem escape_wrapper_equivalent (j : Json) :
    readEscapeDocument j = JsonSchema.readDocument j := by
  simp [readEscapeDocument, readDocumentWith, escapeSignatures, readDefinitions,
    readDefinitionList, outerKeys, JsonSchema.readDocument, option_guard_bind, Option.bind_assoc]

end CssDerivation.DocumentSchema
