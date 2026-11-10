import Fixture

namespace CssDerivation.TypedCodec
open FirstOrder Lean

def decodeJsonExpr (Γ : List Ty) (t : Ty) (j : Json) : Option (Expr Γ t) := do
  let data ← (foldJson [] j).atom.expression
  checkExpr Γ t data

def decodeJsonStmt (Γ : List Ty) (t : Ty) (j : Json) : Option (Stmt Γ t) := do
  let data ← (foldJson [] j).atom.statement
  checkStmt Γ t data

def expressionValue (Γ : List Ty) (t : Ty) (env : Env Γ) (e : DataExpr) : Option t.Value :=
  (decodeExpr Γ t e).map (fun e => eval e env)

theorem context_shadow :
    expressionValue [.nat, .nat] .nat (.cons 3 (.cons 7 .nil)) (.var 1) = some 7 := by decide

theorem out_of_scope : (decodeExpr [] .nat (.var 0)).isNone = true := by decide

theorem wrong_type : (decodeExpr [.bool] .nat (.var 0)).isNone = true := by decide

theorem bad_operand :
    (decodeExpr [] .nat (.add (.bool true) (.nat 1))).isNone = true := by decide

theorem mixed_branches :
    (inferExpr [] (.ite (.bool true) (.nat 1) (.bool false))).isNone = true := by decide

theorem fold_locals :
    expressionValue [] .nat .nil
      (.foldNat (.cons (.scalar 'A') .nil) (.nat 5) (.add (.code (.var 0)) (.var 1))) = some 70 := by decide

theorem alias_wrong_head :
    (inferExpr [.bool] (.scope .nat (.bool true))).isNone = true := by decide

theorem alias_missing_head :
    (inferExpr [] (.scope .nat (.nat 3))).isNone = true := by decide

theorem alias_tail :
    expressionValue [.nat, .bool] .nat (.cons 8 (.cons true .nil))
      (.scope .nat (.var 0)) = some 8 := by decide

theorem json_wrong_arity :
    (decodeJsonExpr [] .nat (json% {"op":"add", "args":[{"op":"nat","args":[1]}]})).isNone = true := by decide

theorem json_unknown_tag :
    (decodeJsonExpr [] .nat (json% {"op":"mystery", "args":[]})).isNone = true := by decide

theorem json_extra_field :
    (decodeJsonExpr [] .nat (json% {"op":"nat", "args":[1], "code":"arbitrary Lean"})).isNone = true := by decide

theorem json_wrong_primitive :
    (decodeJsonExpr [] .nat (json% {"op":"nat", "args":[true]})).isNone = true := by decide

theorem json_negative_nat :
    (decodeJsonExpr [] .nat (json% {"op":"nat", "args":[-1]})).isNone = true := by decide

theorem json_surrogate :
    (decodeJsonExpr [] .scalar (json% {"op":"scalar", "args":[55296]})).isNone = true := by decide

theorem json_above_scalar :
    (decodeJsonExpr [] .scalar (json% {"op":"scalar", "args":[1114112]})).isNone = true := by decide

theorem json_max_scalar :
    ((decodeJsonExpr [] .scalar (json% {"op":"scalar", "args":[1114111]})).map
      (fun e => Char.toNat (eval e .nil))) = some 1114111 := by decide

theorem json_unknown_alias :
    (foldJson [] (json% {"op":"use", "args":["unknown"]})).atom.expression.isNone = true := by decide

theorem json_alias_cycle :
    (definition (json% {"hexExpr":{"op":"use", "args":["hexExpr"]}})
      "hexExpr" .scalar .bool).isNone = true := by decide

theorem json_alias_outer_capture :
    (definition (json% {"hexExpr":{"op":"var", "args":[1]}})
      "hexExpr" .scalar .bool).isNone = true := by decide

theorem json_stmt_wrong_result :
    (decodeJsonStmt [] .scalar (json% {"op":"ret", "args":[{"op":"nat", "args":[1]}]})).isNone = true := by decide

theorem json_read_scope :
    ((decodeJsonStmt [] .scalar (json% {"op":"read", "args":[
      {"op":"ret","args":[{"op":"scalar","args":[65533]}]},
      {"op":"ret","args":[{"op":"var","args":[0]}]}]})).map
      (fun p => (FirstOrder.execute p ['A','!']).value.toNat)) = some 65 := by decide

theorem json_eof_scope :
    (decodeJsonStmt [] .scalar (json% {"op":"read", "args":[
      {"op":"ret","args":[{"op":"var","args":[0]}]},
      {"op":"ret","args":[{"op":"var","args":[0]}]}]})).isNone = true := by decide

theorem json_scan_scope :
    (decodeJsonStmt [] .chars (json% {"op":"scan", "args":[1,
      {"op":"bool","args":[true]},
      {"op":"ret","args":[{"op":"var","args":[0]}]}]})).isSome = true := by decide

theorem json_let_scope :
    ((decodeJsonStmt [] .nat (json% {"op":"letE", "args":[
      {"op":"nat","args":[7]},
      {"op":"ret","args":[{"op":"var","args":[0]}]}]})).map
      (fun p => (interpret p .nil ⟨[],false⟩).1)) = some 7 := by decide

theorem fixture_hex :
    runDocument fixture ['4','1','!'] = some ⟨'A',['!'],false⟩ := by
  rw [fixture_execution]; decide

theorem fixture_eof :
    runDocument fixture [] = some ⟨Char.ofNat 65533,[],true⟩ := by
  rw [fixture_execution]; decide

theorem fixture_one_terminator :
    runDocument fixture ['4','1',' ',' ','!'] = some ⟨'A',[' ','!'],false⟩ := by
  rw [fixture_execution]; decide

end CssDerivation.TypedCodec
