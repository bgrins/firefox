import CssDerivation.Examples.EscapeDocument

namespace CssDerivation.JsonSchema
open Lean FirstOrder TypedCodec
set_option cbv.warning false

def expressionValue (Γ : List Ty) (t : Ty) (env : Env Γ) (j : Json) (aliases : Aliases := []) : Option t.Value :=
  (checkExprJson aliases Γ t j).map (fun e => eval e env)

theorem right_op_layout :
    expressionValue [] .nat .nil (rightObject 2 1 "op" (.str "nat") "args" (.arr #[7])) = some 7 := by cbv

theorem right_args_layout :
    expressionValue [] .nat .nil (rightObject 2 1 "args" (.arr #[7]) "op" (.str "nat")) = some 7 := by cbv

theorem left_op_layout :
    expressionValue [] .nat .nil (leftObject 2 1 "op" (.str "nat") "args" (.arr #[7])) = some 7 := by cbv

theorem left_args_layout :
    expressionValue [] .nat .nil (leftObject 2 1 "args" (.arr #[7]) "op" (.str "nat")) = some 7 := by cbv

theorem arbitrary_cache_sizes :
    expressionValue [] .nat .nil (rightObject 0 999 "op" (.str "nat") "args" (.arr #[7])) = some 7 := by cbv

theorem duplicate_raw_keys_rejected :
    (readExprData [] (rightObject 2 1 "op" (.str "nat") "op" (.arr #[7]))).isNone = true := by cbv

theorem extra_field_rejected :
    (readExprData [] (json% {"op":"nat","args":[7],"code":"extra"})).isNone = true := by cbv

theorem unknown_tag_rejected :
    (readExprData [] (nodeJson "arbitraryLean" [])).isNone = true := by cbv

theorem wrong_arity_rejected :
    (readExprData [] (nodeJson "sub" [nodeJson "nat" [7]])).isNone = true := by cbv

theorem wrong_primitive_rejected :
    (readExprData [] (nodeJson "nat" [.bool true])).isNone = true := by cbv

theorem wrong_field_type_rejected :
    (readExprData [] (json% {"op":"nat","args":7})).isNone = true := by cbv

theorem negative_natural_rejected :
    (readExprData [] (json% {"op":"nat","args":[-1]})).isNone = true := by cbv

theorem invalid_scalar_surrogate :
    (readExprData [] (nodeJson "scalar" [55296])).isNone = true := by cbv

theorem invalid_scalar_upper_bound :
    (readExprData [] (nodeJson "scalar" [1114112])).isNone = true := by cbv

theorem scalar_wrapping_not_admitted :
    (readExprData [] (nodeJson "scalar" [4294967361])).isNone = true := by cbv

theorem scalar_maximum_admitted :
    ((checkExprJson [] [] .scalar (nodeJson "scalar" [1114111])).map
      (fun e => Char.toNat (eval e .nil))) = some 1114111 := by cbv

theorem subtraction_roles_preserved :
    expressionValue [] .nat .nil (encodeExprJson (.sub (.nat 7) (.nat 2) : Expr [] .nat)) = some 5 := by cbv

theorem same_typed_variable_index_preserved :
    expressionValue [.nat,.nat] .nat (.cons 3 (.cons 7 .nil))
      (encodeExprJson (.var (.there .here) : Expr [.nat,.nat] .nat)) = some 7 := by cbv

theorem wrong_result_type_rejected :
    (checkExprJson [] [] .bool (nodeJson "nat" [7])).isNone = true := by cbv

theorem wrong_operand_type_rejected :
    (checkExprJson [] [] .nat (nodeJson "add" [nodeJson "bool" [.bool true],nodeJson "nat" [7]])).isNone = true := by cbv

theorem out_of_scope_rejected :
    (checkExprJson [] [] .nat (nodeJson "var" [0])).isNone = true := by cbv

def foldExample : Expr [] .nat :=
  .foldNat (.cons (.scalar 'A') .nil) (.nat 5) (.add (.code (.var .here)) (.var (.there .here)))

theorem fold_binder_order_preserved :
    expressionValue [] .nat .nil (encodeExprJson foldExample) = some 70 := by cbv

theorem wrong_fold_step_type_rejected :
    (checkExprJson [] [] .nat (nodeJson "foldNat"
      [nodeJson "nil" [], nodeJson "nat" [0], nodeJson "var" [0]])).isNone = true := by cbv

def repeatedAliases : Aliases := [("same", .nat, .nat 3), ("same", .nat, .nat 7)]

theorem first_alias_match_preserved :
    expressionValue [.nat] .nat (.cons 99 .nil) (nodeJson "use" [.str "same"]) repeatedAliases = some 3 := by cbv

theorem first_alias_does_not_skip_bad_head :
    (checkExprJson [("same",.bool,.nat 3),("same",.nat,.nat 7)] [.nat] .nat
      (nodeJson "use" [.str "same"])).isNone = true := by cbv

theorem alias_missing_head_rejected :
    (checkExprJson repeatedAliases [] .nat (nodeJson "use" [.str "same"])).isNone = true := by cbv

theorem unknown_alias_rejected :
    (readExprData repeatedAliases (nodeJson "use" [.str "missing"])).isNone = true := by cbv

theorem alias_cycle_definition_rejected :
    (readDefinition (json% {"hexExpr":{"op":"use","args":["hexExpr"]}})
      "hexExpr" .scalar .bool).isNone = true := by cbv

theorem alias_tail_capture_definition_rejected :
    (readDefinition (json% {"hexExpr":{"op":"eqChar","args":[{"op":"var","args":[1]},{"op":"scalar","args":[0]}]}})
      "hexExpr" .scalar .bool).isNone = true := by cbv

theorem alias_singleton_reference_admitted :
    (readDefinition (json% {"hexExpr":{"op":"eqChar","args":[{"op":"var","args":[0]},{"op":"scalar","args":[0]}]}})
      "hexExpr" .scalar .bool).isSome = true := by cbv

def scanExample : Stmt [] .chars := .scan 1 (.bool true) (.ret (.var .here))

theorem scan_budget_preserved :
    ((checkStmtJson [] [] .chars (encodeStmtJson scanExample)).map
      (fun p => (interpret p .nil ⟨['a','b'],false⟩).1)) = some ['a'] := by cbv

theorem read_eof_scope_rejected :
    (checkStmtJson [] [] .scalar (json% {"op":"read","args":[
      {"op":"ret","args":[{"op":"var","args":[0]}]},
      {"op":"ret","args":[{"op":"var","args":[0]}]}]})).isNone = true := by cbv

theorem read_present_scope_admitted :
    ((checkStmtJson [] [] .scalar (json% {"op":"read","args":[
      {"op":"ret","args":[{"op":"scalar","args":[65533]}]},
      {"op":"ret","args":[{"op":"var","args":[0]}]}]})).map
      (fun p => (FirstOrder.execute p ['A','!']).value.toNat)) = some 65 := by cbv

theorem fixture_hex :
    runDocument TypedCodec.fixture ['4','1','!'] = some ⟨'A',['!'],false⟩ := by
  rw [fixture_execution]; decide

theorem fixture_eof :
    runDocument TypedCodec.fixture [] = some ⟨Char.ofNat 65533,[],true⟩ := by
  rw [fixture_execution]; decide

end CssDerivation.JsonSchema
