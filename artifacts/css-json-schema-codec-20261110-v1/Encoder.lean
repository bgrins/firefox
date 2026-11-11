import Reader

namespace CssDerivation.JsonSchema
open Lean FirstOrder TypedCodec

def nodeJson (op : String) (args : List Json) : Json :=
  rightObject 2 1 "args" (.arr args.toArray) "op" (.str op)

def natJson (n : Nat) : Json := .num (.fromNat n)

def encodeExprJson : Expr Γ t → Json
  | .nat n => nodeJson "nat" [natJson n]
  | .scalar c => nodeJson "scalar" [natJson c.toNat]
  | .bool b => nodeJson "bool" [.bool b]
  | .var v => nodeJson "var" [natJson (encodeVar v)]
  | .nil => nodeJson "nil" []
  | .unit => nodeJson "unit" []
  | .code a => nodeJson "code" [encodeExprJson a]
  | .scalarOf a => nodeJson "scalarOf" [encodeExprJson a]
  | .add a b => nodeJson "add" [encodeExprJson a, encodeExprJson b]
  | .sub a b => nodeJson "sub" [encodeExprJson a, encodeExprJson b]
  | .mul a b => nodeJson "mul" [encodeExprJson a, encodeExprJson b]
  | .leNat a b => nodeJson "leNat" [encodeExprJson a, encodeExprJson b]
  | .ltNat a b => nodeJson "ltNat" [encodeExprJson a, encodeExprJson b]
  | .eqNat a b => nodeJson "eqNat" [encodeExprJson a, encodeExprJson b]
  | .leChar a b => nodeJson "leChar" [encodeExprJson a, encodeExprJson b]
  | .eqChar a b => nodeJson "eqChar" [encodeExprJson a, encodeExprJson b]
  | .and a b => nodeJson "and" [encodeExprJson a, encodeExprJson b]
  | .or a b => nodeJson "or" [encodeExprJson a, encodeExprJson b]
  | .cons a b => nodeJson "cons" [encodeExprJson a, encodeExprJson b]
  | .ite a b c => nodeJson "ite" [encodeExprJson a, encodeExprJson b, encodeExprJson c]
  | .foldNat a b c => nodeJson "foldNat" [encodeExprJson a, encodeExprJson b, encodeExprJson c]

def encodeStmtJson : Stmt Γ t → Json
  | .ret e => nodeJson "ret" [encodeExprJson e]
  | .letE e p => nodeJson "letE" [encodeExprJson e, encodeStmtJson p]
  | .read a b => nodeJson "read" [encodeStmtJson a, encodeStmtJson b]
  | .scan n e p => nodeJson "scan" [natJson n, encodeExprJson e, encodeStmtJson p]
  | .raiseError p => nodeJson "raiseError" [encodeStmtJson p]
  | .branch e a b => nodeJson "branch" [encodeExprJson e, encodeStmtJson a, encodeStmtJson b]

def checkExprJson (aliases : Aliases) (Γ : List Ty) (t : Ty) (j : Json) : Option (Expr Γ t) :=
  (readExprData aliases j).bind (TypedCodec.checkExpr Γ t)

def checkStmtJson (aliases : Aliases) (Γ : List Ty) (t : Ty) (j : Json) : Option (Stmt Γ t) :=
  (readStmtData aliases j).bind (TypedCodec.checkStmt Γ t)

end CssDerivation.JsonSchema
