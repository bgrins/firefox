import TypedSchemaLaws
import Document

namespace IndependentJsonSchemaReview
open Lean CssDerivation.FirstOrder CssDerivation.TypedCodec CssDerivation.JsonSchema

def aliases : Aliases := [("k", .nat, .nat 7), ("k", .scalar, .nat 9)]

theorem raw_right_op : readExprData [] (rightObject 0 99 "op" (.str "nat") "args" (.arr #[natJson 7])) = some (.nat 7) := by cbv
theorem raw_right_args : readExprData [] (rightObject 100 0 "args" (.arr #[natJson 7]) "op" (.str "nat")) = some (.nat 7) := by cbv
theorem raw_left_op : readExprData [] (leftObject 0 0 "op" (.str "nat") "args" (.arr #[natJson 7])) = some (.nat 7) := by cbv
theorem raw_left_args : readExprData [] (leftObject 7 21 "args" (.arr #[natJson 7]) "op" (.str "nat")) = some (.nat 7) := by cbv
theorem alias_first_match : readExprData aliases (nodeJson "use" [.str "k"]) = some (.scope .nat (.nat 7)) := by cbv
theorem alias_scope_valid : checkExprJson aliases [.nat] .nat (nodeJson "use" [.str "k"]) = some (.nat 7) := by cbv
theorem alias_scope_rejected : checkExprJson aliases [.scalar, .nat] .nat (nodeJson "use" [.str "k"]) = none := by cbv
theorem no_alias_environment : readExprData [] (nodeJson "use" [.str "k"]) = none := by cbv
theorem wrong_arity : readExprData [] (nodeJson "nat" [natJson 7, natJson 9]) = none := by cbv
theorem extra_field : readExprData [] (Json.mkObj [("op", .str "nat"), ("args", .arr #[natJson 7]), ("execute", .str "payload")]) = none := by cbv
theorem surrogate_rejected : readExprData [] (nodeJson "scalar" [natJson 0xD800]) = none := by cbv
theorem scalar_boundary : readExprData [] (nodeJson "scalar" [natJson 0x10FFFF]) = some (.scalar (Char.ofNat 0x10FFFF)) := by cbv

def duplicateOpNode : Json :=
  .obj ⟨⟨.inner 3 "op" (.str "nat")
    (.inner 1 "args" (.arr #[natJson 7]) .leaf .leaf)
    (.inner 1 "op" (.str "nat") .leaf .leaf)⟩⟩

theorem raw_duplicate_field : readExprData [] duplicateOpNode = none := by cbv
theorem raw_duplicate_only : readExprData [] (rightObject 2 1 "op" (.str "nat") "op" (.str "nat")) = none := by cbv

def illTypedNode : Json := nodeJson "add" [nodeJson "bool" [.bool true], nodeJson "nat" [natJson 1]]
theorem schema_accepts_ill_typed : ExprSchema [] illTypedNode (.add (.bool true) (.nat 1)) := by
  apply (readExprData_spec [] illTypedNode _).mp
  cbv
theorem typed_rejects_ill_typed : checkExprJson [] [] .nat illTypedNode = none := by cbv

end IndependentJsonSchemaReview
