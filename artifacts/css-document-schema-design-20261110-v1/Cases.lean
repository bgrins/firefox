import Prototype

namespace CssDerivation.DocumentDesign
open FirstOrder TypedCodec

def accumulatedAlias : Expr [.nat] .nat :=
  .foldNat (.cons (.scalar 'x') .nil) (.nat 3)
    (.add (.var (.there .here)) (.var (.there (.there .here))))

theorem tail_is_unused :
    eval (weakenExpr [.nat] accumulatedAlias) (.cons 7 (.cons 900 .nil)) = 10 := by decide

theorem singleton_rejects_capture :
    (checkExpr [.nat] .nat (.var 1)).isNone = true := by decide

theorem ambient_check_alone_allows_capture :
    ((checkExpr [.nat, .nat] .nat (.scope .nat (.var 1))).map
      (fun e => eval e (.cons 7 (.cons 900 .nil)))) = some 900 := by decide

theorem wrong_scope_head_rejected :
    (checkExpr [.scalar, .nat] .nat (.scope .nat (.nat 7))).isNone = true := by decide

end CssDerivation.DocumentDesign
