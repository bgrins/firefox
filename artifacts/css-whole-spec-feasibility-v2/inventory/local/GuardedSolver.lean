import CssSemantics.GuardedCompletion

namespace CssSemantics.GuardedSolver

def resolve (base : String → Option (List Token))
    (remaining : List (String × VariableExpr Token)) (active marked : List String)
    (name : String) : Option (List Token) × List String :=
  GuardedCompletion.resolve (fun _ value => value) base remaining active marked name

abbrev Resolves (bindings : VariableBindings Token) (base : String → Option (List Token)) :=
  GuardedCompletion.Resolves bindings (fun _ value => value) base

abbrev Evaluates (bindings : VariableBindings Token) (base : String → Option (List Token)) :=
  GuardedCompletion.Evaluates bindings (fun _ value => value) base

variable {Token : Type}
variable {bindings : VariableBindings Token} {base : String → Option (List Token)}

theorem evaluates_iff_generic (expression : VariableExpr Token) (active start : List String)
    (value : Option (List Token)) (finish : List String) :
    Evaluates bindings base active start expression value finish ↔
      GuardedExpr.Evaluates (Resolves bindings base active) start expression value finish :=
  GuardedCompletion.evaluates_iff_generic expression active start value finish

theorem resolve_iff (remaining : List (String × VariableExpr Token))
    (active : List String)
    (agreement : ∀ name, name ∉ active → remaining.lookup name = bindings.lookup name)
    (marked : List String) (name : String) (value : Option (List Token)) (finish : List String) :
    resolve base remaining active marked name = (value, finish) ↔
      Resolves bindings base active marked name value finish :=
  GuardedCompletion.resolve_iff remaining active agreement marked name value finish

theorem resolve_marks (remaining : List (String × VariableExpr Token))
    (active marked : List String) (name : String)
    (contained : ∀ mark, mark ∈ marked → mark ∈ active) :
    (∀ mark, mark ∈ (resolve base remaining active marked name).2 → mark ∈ active) ∧
    (∀ mark, mark ∈ marked → mark ∈ (resolve base remaining active marked name).2) :=
  GuardedCompletion.resolve_marks remaining active marked name contained

def compute (bindings : VariableBindings Token) (base : String → Option (List Token))
    (name : String) : Option (List Token) :=
  GuardedCompletion.compute bindings (fun _ value => value) base name

theorem resolve_fresh_marks (bindings : VariableBindings Token)
    (base : String → Option (List Token)) (name : String) :
    (resolve base bindings.entries [] [] name).2 = [] :=
  GuardedCompletion.resolve_fresh_marks bindings (fun _ value => value) base name

theorem compute_iff (bindings : VariableBindings Token)
    (base : String → Option (List Token)) (name : String) (value : Option (List Token)) :
    compute bindings base name = value ↔ Resolves bindings base [] [] name value [] :=
  GuardedCompletion.compute_iff bindings (fun _ value => value) base name value

theorem Resolves.unique (left : Resolves bindings base active marked name a first)
    (right : Resolves bindings base active marked name b second) :
    (a, first) = (b, second) :=
  GuardedCompletion.Resolves.unique left right

theorem Evaluates.unique (left : Evaluates bindings base active marked expression a first)
    (right : Evaluates bindings base active marked expression b second) :
    (a, first) = (b, second) :=
  GuardedCompletion.Evaluates.unique left right

theorem compute_eq_completion (bindings : VariableBindings Token)
    (base : String → Option (List Token)) (name : String) :
    compute bindings base name = GuardedCompletion.compute bindings (fun _ value => value) base name := rfl

end CssSemantics.GuardedSolver
