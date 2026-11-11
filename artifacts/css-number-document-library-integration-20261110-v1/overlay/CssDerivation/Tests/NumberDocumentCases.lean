import CssDerivation.Examples.NumberDocument

namespace CssDerivation.ParserJson.Cases
open Lean FirstOrder TypedCodec JsonSchema ParserIR NumberTransfer
set_option cbv.warning false
set_option maxRecDepth 30000
set_option maxHeartbeats 4000000

def takeA : Parser (.base .scalar) := .take (.eqChar (.var .here) (.scalar 'a'))
def takeB : Parser (.base .scalar) := .take (.eqChar (.var .here) (.scalar 'b'))
def raisedUnit : Parser (.base .unit) := .legacy (.raiseError (.ret .unit))
def failureAfterRaise : Parser (.base .scalar) := .right raisedUnit takeB

theorem legacy_nat : decodeParser (.base .nat)
    (encodeParser (.legacy (.ret (.nat 7)))) = some (.legacy (.ret (.nat 7))) := by cbv

theorem take_remainder : executeDocument (.base .scalar) (encodeDocument takeA) ⟨"ax".toList, false⟩ =
    some (some 'a', ⟨"x".toList, false⟩) := by cbv

theorem scan_remainder : executeDocument (.base .chars) (encodeDocument digitsTree) ⟨"123x".toList, true⟩ =
    some (some "123".toList, ⟨"x".toList, true⟩) := by cbv

theorem scan_empty_success : executeDocument (.base .chars) (encodeDocument digitsTree) ⟨[], false⟩ =
    some (some [], ⟨[], false⟩) := by cbv

theorem nonempty_empty_failure : executeDocument (.base .chars) (encodeDocument nonemptyDigitsTree) ⟨[], false⟩ =
    some (none, ⟨[], false⟩) := by cbv

theorem pair_order : executeDocument (.pair (.base .scalar) (.base .scalar))
    (encodeDocument (.pair takeA takeB)) ⟨"ab!".toList, false⟩ =
    some (some ('a', 'b'), ⟨"!".toList, false⟩) := by cbv

theorem pair_failure_restores_consumption : executeDocument (.pair (.base .scalar) (.base .scalar))
    (encodeDocument (.pair takeA takeB)) ⟨"ax".toList, false⟩ =
    some (none, ⟨"ax".toList, false⟩) := by cbv

theorem right_failure_restores_error : executeDocument (.base .scalar)
    (encodeDocument failureAfterRaise) ⟨"a".toList, false⟩ =
    some (none, ⟨"a".toList, false⟩) := by cbv

theorem optional_failure_restores_both : executeDocument (.optional (.base .scalar))
    (encodeDocument (.optional (.right (.pair takeA raisedUnit) takeB))) ⟨"ax".toList, false⟩ =
    some (some none, ⟨"ax".toList, false⟩) := by cbv

theorem legacy_success_retains_error : executeDocument (.base .unit)
    (encodeDocument raisedUnit) ⟨"a".toList, false⟩ =
    some (some (), ⟨"a".toList, true⟩) := by cbv

theorem unknown_parser_refused : decodeParser (.base .scalar) (nodeJson "takeAll" []) = none := by cbv

theorem parser_alias_refused : decodeParser (.base .scalar) (nodeJson "use" [.str "takeA"]) = none := by cbv

theorem predicate_alias_refused : decodeParser (.base .scalar)
    (nodeJson "take" [nodeJson "use" [.str "digitPredicate"]]) = none := by cbv

theorem legacy_alias_refused : decodeParser (.base .nat)
    (nodeJson "legacy" [.str "nat", nodeJson "ret" [nodeJson "use" [.str "n"]]]) = none := by cbv

theorem legacy_unknown_type_refused : decodeParser (.base .nat)
    (nodeJson "legacy" [.str "integer", encodeStmtJson (.ret (.nat 0) : Stmt [] .nat)]) = none := by cbv

theorem take_wrong_arity_refused : decodeParser (.base .scalar)
    (nodeJson "take" [encodeExprJson (.bool true : Predicate), .null]) = none := by cbv

theorem nonempty_scalar_refused : decodeParser (.base .chars)
    (nodeJson "nonempty" [encodeParser takeA]) = none := by cbv

theorem non_boolean_predicate_refused : decodeParser (.base .scalar)
    (nodeJson "take" [encodeExprJson (.nat 1 : Expr [.scalar] .nat)]) = none := by cbv

theorem predicate_tail_capture_refused : decodeParser (.base .scalar)
    (nodeJson "take" [nodeJson "eqChar" [nodeJson "var" [natJson 1], nodeJson "scalar" [natJson 97]]]) = none := by cbv

theorem wrong_expected_shape_refused : decodeParser (.base .chars) (encodeParser takeA) = none := by cbv

theorem wrong_number_shape_refused : readDocument NumberShape (encodeDocument takeA) = none := by cbv

theorem wrong_version_refused : readDocument (.base .scalar)
    (Json.mkObj [("schema", .str "css-parser-ir-v2"), ("program", encodeParser takeA),
      ("source_map", Json.mkObj [])]) = none := by cbv

theorem definitions_field_refused : readDocument (.base .scalar)
    (Json.mkObj [("schema", .str "css-parser-ir-v1"), ("program", encodeParser takeA),
      ("source_map", Json.mkObj []), ("definitions", Json.mkObj [])]) = none := by cbv

theorem non_object_source_map_refused : readDocument (.base .scalar)
    (Json.mkObj [("schema", .str "css-parser-ir-v1"), ("program", encodeParser takeA),
      ("source_map", .null)]) = none := by cbv

theorem negative_zero_retained : numberValue numberFixture ⟨"-0".toList, false⟩ =
    some (⟨0, 0, false, some '-'⟩, ⟨[], false⟩) := by cbv

theorem incomplete_fraction_rollback : numberValue numberFixture ⟨"1.".toList, true⟩ =
    some (⟨1, 0, false, none⟩, ⟨".".toList, true⟩) := by cbv

theorem incomplete_exponent_rollback : numberValue numberFixture ⟨"1e+".toList, false⟩ =
    some (⟨1, 0, false, none⟩, ⟨"e+".toList, false⟩) := by cbv

theorem fractional_exponent_exact : numberValue numberFixture ⟨"-12.30e-2x".toList, false⟩ =
    some (⟨-1230, -4, true, some '-'⟩, ⟨"x".toList, false⟩) := by cbv

theorem original_rejects_repeated_exponent_marker : numberValue numberFixture ⟨"1ee2".toList, false⟩ =
    some (⟨1, 0, false, none⟩, ⟨"ee2".toList, false⟩) := by cbv

theorem changed_program_accepts_repeated_marker : numberValue changedFixture ⟨"1ee2".toList, false⟩ =
    some (⟨1, 2, true, none⟩, ⟨[], false⟩) := by cbv

end CssDerivation.ParserJson.Cases
