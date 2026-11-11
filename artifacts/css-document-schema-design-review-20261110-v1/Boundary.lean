import Prototype

namespace CssDerivation.DocumentReview
open FirstOrder TypedCodec DocumentDesign

theorem accepted_body_evaluates_without_tail_capture
    (data : DataExpr) (e : Expr [head] result)
    (normalized : normalizeExpr data = data)
    (accepted : checkExpr [head] result data = some e)
    (value : head.Value) (tail : Env Δ) :
    (checkExpr (head :: Δ) result (.scope head data)).map
      (fun body => eval body (.cons value tail)) =
      some (eval e (.cons value .nil)) := by
  rw [validated_data_rechecks data e normalized accepted Δ]
  simp only [Option.map_some]
  rw [scoped_alias_independent]

theorem different_tail_shapes_and_values_do_not_matter
    (e : Expr [head] result) (value : head.Value)
    (left : Env Γ) (right : Env Δ) :
    eval (weakenExpr Γ e) (.cons value left) =
      eval (weakenExpr Δ e) (.cons value right) := by
  rw [scoped_alias_independent, scoped_alias_independent]

end CssDerivation.DocumentReview
