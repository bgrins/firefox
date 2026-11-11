import CssDerivation.Examples.NumberDocument

namespace NumberDocumentReview
open Lean CssDerivation CssDerivation.FirstOrder CssDerivation.TypedCodec
open CssDerivation.JsonSchema CssDerivation.ParserIR CssDerivation.ParserJson
set_option cbv.warning false
set_option maxRecDepth 30000
set_option maxHeartbeats 4000000

theorem right_op_any_cache (outer inner : Nat) (p : Predicate) :
    decodeParser (.base .scalar)
      (rightObject outer inner "op" (.str "take") "args" (.arr #[encodeExprJson p])) =
      some (.take p) := by
  apply (decodeParser_spec _ _).mpr
  exact .node (.rightOp outer inner _ _) (.take (encodeExprJson_schema [] p))

theorem right_args_any_cache (outer inner : Nat) (p : Predicate) :
    decodeParser (.base .scalar)
      (rightObject outer inner "args" (.arr #[encodeExprJson p]) "op" (.str "take")) =
      some (.take p) := by
  apply (decodeParser_spec _ _).mpr
  exact .node (.rightArgs outer inner _ _) (.take (encodeExprJson_schema [] p))

theorem left_op_any_cache (outer inner : Nat) (p : Predicate) :
    decodeParser (.base .scalar)
      (leftObject outer inner "op" (.str "take") "args" (.arr #[encodeExprJson p])) =
      some (.take p) := by
  apply (decodeParser_spec _ _).mpr
  exact .node (.leftOp outer inner _ _) (.take (encodeExprJson_schema [] p))

theorem left_args_any_cache (outer inner : Nat) (p : Predicate) :
    decodeParser (.base .scalar)
      (leftObject outer inner "args" (.arr #[encodeExprJson p]) "op" (.str "take")) =
      some (.take p) := by
  apply (decodeParser_spec _ _).mpr
  exact .node (.leftArgs outer inner _ _) (.take (encodeExprJson_schema [] p))

theorem raw_duplicate_fields_refused :
    decodeParser (.base .scalar)
      (rightObject 2 1 "op" (.str "take") "op" (.arr #[nodeJson "bool" [.bool true]])) = none := by cbv

theorem raw_extra_field_refused :
    decodeParser (.base .scalar)
      (Json.mkObj [("op", .str "take"), ("args", .arr #[nodeJson "bool" [.bool true]]),
        ("extra", .null)]) = none := by cbv

theorem legacy_cannot_capture_predicate_argument :
    decodeParser (.base .bool)
      (nodeJson "legacy" [.str "bool", nodeJson "ret" [nodeJson "eqChar"
        [nodeJson "var" [natJson 0], nodeJson "scalar" [natJson 97]]]]) = none := by cbv

theorem invalid_envelope_is_decode_failure :
    executeDocument (.base .chars) (Json.mkObj []) ⟨[], true⟩ = none := by cbv

theorem accepted_empty_nonempty_is_parse_failure :
    executeDocument (.base .chars) (encodeDocument (.nonempty (.scan (.bool true))))
      ⟨[], true⟩ = some (none, ⟨[], true⟩) := by cbv

theorem changed_accepts_missing_exponent_marker :
    numberValue changedFixture ⟨"1+2".toList, true⟩ =
      some (⟨1, 2, true, none⟩, ⟨[], true⟩) := by cbv

theorem original_retains_missing_exponent_marker :
    numberValue numberFixture ⟨"1+2".toList, true⟩ =
      some (⟨1, 0, false, none⟩, ⟨"+2".toList, true⟩) := by cbv

theorem shape_acceptance_does_not_identify_css :
    ∃ j, (readDocument NumberTransfer.NumberShape j).isSome = true ∧
      numberValue j ⟨"1+2".toList, true⟩ ≠
        numberValue numberFixture ⟨"1+2".toList, true⟩ := by
  refine ⟨changedFixture, ?_, ?_⟩
  · cbv
  · rw [changed_accepts_missing_exponent_marker, original_retains_missing_exponent_marker]
    decide

end NumberDocumentReview
