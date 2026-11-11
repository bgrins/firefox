import CssDerivation.Codec.Document.Laws
import CssDerivation.Codec.Document.AliasLaws
import CssDerivation.Tests.DocumentInputs

namespace CssDerivation.DocumentReview
open Lean FirstOrder TypedCodec JsonSchema DocumentSchema
set_option cbv.warning false
set_option maxRecDepth 30000

theorem accepted_definition_count_is_signature_count
    (accepted : readDefinitions signatures definitions = some aliases) :
    aliases.length = signatures.length := by
  have names := (admitted_alias_names accepted).1
  simpa using congrArg List.length names

def signature : Signature := ⟨"seven", .nat, .nat⟩
def definitions : Json := .mkObj [("seven", nodeJson "nat" [7])]
def useProgram : Json := nodeJson "ret" [nodeJson "use" [.str "seven"]]
def document : Json := Examples.document definitions useProgram
def aliases : Aliases := [("seven", .nat, .nat 7)]

theorem constant_alias_without_input_is_refused :
    readDocumentWith [signature] .nat document = none := by cbv

theorem normalized_document_relation_still_holds :
    DocumentSchema [signature] .nat document (.ret (.nat 7)) := by
  refine ⟨1, definitions, .mkObj [], useProgram, aliases,
    .ret (.scope .nat (.nat 7)), ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · exact (exact_keys_spec _ _ outer_keys_unique).mp (by cbv)
  · cbv
  · cbv
  · cbv
  · exact (definitions_spec _ _ _).mp (by cbv)
  · cbv
  · exact ⟨_, rfl⟩
  · cbv
  · exact (readStmtData_spec _ _ _).mp (by cbv)
  · rfl

theorem document_relation_does_not_imply_acceptance :
    ¬ (∀ signatures result j (p : Stmt [] result),
      DocumentSchema signatures result j p →
      readDocumentWith signatures result j = some p) := by
  intro converse
  have accepted := converse [signature] .nat document (.ret (.nat 7))
    normalized_document_relation_still_holds
  rw [constant_alias_without_input_is_refused] at accepted
  cases accepted

end CssDerivation.DocumentReview
