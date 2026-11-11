import CssDerivation.Examples.GenericEscapeDocument
import CssDerivation.Codec.Document.AliasLaws
import CssDerivation.Tests.DocumentInputs

namespace CssDerivation.DocumentSchema.Cases
open Lean FirstOrder TypedCodec JsonSchema Examples
set_option cbv.warning false
set_option maxRecDepth 30000
set_option maxHeartbeats 4000000

theorem empty_profile_accepted : valueOf [] emptyDocument = some 65 := by cbv

theorem arbitrary_name_profile_accepted : valueOf [nextSignature] nextDocument = some 65 := by cbv

theorem fold_binders_preserved : valueOf [⟨"sum", .nat, .nat⟩] foldDocument = some 10 := by cbv

theorem duplicate_signature_guard_required :
    (readDefinitions duplicateProfile duplicateExploit).isNone = true := by cbv

theorem duplicate_keys_rejected :
    (readDefinitions [nextSignature] (rightObject 2 1 "next" nextBody "next" nextBody)).isNone = true := by cbv

theorem missing_definition_rejected :
    (readDefinitions [nextSignature] (.mkObj [])).isNone = true := by cbv

theorem extra_definition_rejected :
    (readDefinitions [nextSignature] duplicateExploit).isNone = true := by cbv

theorem wrong_declared_result_rejected :
    (readDefinitions wrongResultProfile nextDefinitions).isNone = true := by cbv

theorem wrong_declared_input_rejected :
    (readDefinitions [⟨"next", .scalar, .scalar⟩] nextDefinitions).isNone = true := by cbv

theorem singleton_capture_rejected :
    (readDefinitions [nextSignature] (.mkObj [("next", nodeJson "scalarOf" [nodeJson "var" [1]])])).isNone = true := by cbv

theorem singleton_head_accepted :
    (readDefinitions [nextSignature] (.mkObj [("next", nodeJson "scalarOf" [nodeJson "var" [0]])])).isSome = true := by cbv

theorem self_reference_rejected :
    (readDefinitions [nextSignature] (.mkObj [("next", nodeJson "use" [.str "next"])])).isNone = true := by cbv

theorem forward_reference_rejected :
    (readDefinitions [nextSignature, ⟨"later", .nat, .scalar⟩]
      (.mkObj [("next", nodeJson "use" [.str "later"]), ("later", nextBody)])).isNone = true := by cbv

theorem unknown_use_rejected :
    (readDocumentWith [] .scalar (document (.mkObj []) (nodeJson "ret" [nodeJson "use" [.str "absent"]]))).isNone = true := by cbv

theorem wrong_use_head_rejected :
    (readDocumentWith [nextSignature] .scalar (document nextDefinitions
      (nodeJson "letE" [nodeJson "scalar" [65], nodeJson "ret" [nodeJson "use" [.str "next"]]]))).isNone = true := by cbv

theorem source_map_is_inert :
    valueOf [] (document (.mkObj []) (nodeJson "ret" [nodeJson "scalar" [65]])
      (nodeJson "ret" [nodeJson "scalar" [66]])) = some 65 := by cbv

theorem source_map_must_be_object :
    (readDocumentWith [] .scalar (document (.mkObj []) (nodeJson "ret" [nodeJson "scalar" [65]]) .null)).isNone = true := by cbv

theorem extra_outer_field_rejected :
    (readDocumentWith [] .scalar (.mkObj [("schema", 1), ("definitions", .mkObj []),
      ("program", nodeJson "ret" [nodeJson "scalar" [65]]), ("source_map", .mkObj []),
      ("extra", .null)])).isNone = true := by cbv

theorem raw_membership_is_not_lookup :
    fieldsExactly (rightObject 2 1 "z" .null "a" .null) ["a", "z"] = true ∧
    field (rightObject 2 1 "z" .null "a" .null) "a" = none := by cbv

theorem alias_order_preserved :
    ((readDefinitions [nextSignature, ⟨"second", .nat, .scalar⟩]
      (.mkObj [("second", nextBody), ("next", nextBody)])).map (fun aliases => aliases.map Prod.fst)) =
      some ["next", "second"] := by cbv

end CssDerivation.DocumentSchema.Cases
