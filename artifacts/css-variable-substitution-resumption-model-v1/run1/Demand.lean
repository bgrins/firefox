import CssSemantics.VariablesBase

namespace DemandFallback

inductive Expr where
  | literal (tokens : List String)
  | reference (name : String)
  | fallback (name : String) (otherwise : Expr)
  deriving DecidableEq, Repr

def Expr.legacy : Expr → CssSemantics.VariableExpr String
  | .literal tokens => .literal tokens
  | .reference name => .reference name
  | .fallback name otherwise => .fallback name otherwise.legacy

inductive Work where
  | property (name : String)
  | expression (expr : Expr)

structure Result where
  value : Option (List String)
  cyclic : List String
  reads : List String
  deriving DecidableEq, Repr

def finish (name : String) (r : Result) : Result :=
  { r with value := if name ∈ r.cyclic then none else r.value,
           reads := name :: r.reads }

def eval (lookup : String → Option Expr) : Nat → List String → List String → Work → Option Result
  | 0, _, _, _ => none
  | fuel + 1, stack, cyclic, .property name =>
      if name ∈ stack then
        some ⟨none, stack.takeWhile (· != name) ++ [name] ++ cyclic, [name]⟩
      else match lookup name with
        | none => some ⟨none, cyclic, [name]⟩
        | some expr => (eval lookup fuel (name :: stack) cyclic (.expression expr)).map (finish name)
  | _ + 1, _, cyclic, .expression (.literal tokens) => some ⟨some tokens, cyclic, []⟩
  | fuel + 1, stack, cyclic, .expression (.reference name) =>
      eval lookup fuel stack cyclic (.property name)
  | fuel + 1, stack, cyclic, .expression (.fallback name otherwise) => do
      let primary ← eval lookup fuel stack cyclic (.property name)
      match primary.value with
      | some _ => pure primary
      | none =>
          let alternate ← eval lookup fuel stack primary.cyclic (.expression otherwise)
          pure { alternate with reads := primary.reads ++ alternate.reads }

theorem successful_primary_skips_any_fallback
    (lookup : String → Option Expr) (fuel : Nat) (stack cyclic : List String)
    (name : String) (fallback : Expr) (r : Result) (tokens : List String)
    (primary : eval lookup fuel stack cyclic (.property name) = some r)
    (valid : r.value = some tokens) :
    eval lookup (fuel + 1) stack cyclic (.expression (.fallback name fallback)) = some r := by
  simp [eval, primary, valid]

theorem fallback_replacement_irrelevant
    (lookup : String → Option Expr) (fuel : Nat) (stack cyclic : List String)
    (name : String) (left right : Expr) (r : Result) (tokens : List String)
    (primary : eval lookup fuel stack cyclic (.property name) = some r)
    (valid : r.value = some tokens) :
    eval lookup (fuel + 1) stack cyclic (.expression (.fallback name left)) =
      eval lookup (fuel + 1) stack cyclic (.expression (.fallback name right)) := by
  rw [successful_primary_skips_any_fallback lookup fuel stack cyclic name left r tokens primary valid,
      successful_primary_skips_any_fallback lookup fuel stack cyclic name right r tokens primary valid]

theorem marked_guard_cannot_be_rescued (name : String) (r : Result)
    (marked : name ∈ r.cyclic) : (finish name r).value = none := by
  simp [finish, marked]

theorem successful_literal_lookup_ignores_arbitrary_fallback
    (lookup : String → Option Expr) (name : String) (tokens : List String)
    (fallback : Expr) (bound : lookup name = some (.literal tokens)) :
    eval lookup 3 [] [] (.expression (.fallback name fallback)) =
      some ⟨some tokens, [], [name]⟩ := by
  simp [eval, bound, finish]

theorem bound_guard_observes_nested_mark
    (lookup : String → Option Expr) (fuel : Nat) (stack cyclic : List String)
    (name : String) (expr : Expr) (r : Result)
    (fresh : name ∉ stack) (bound : lookup name = some expr)
    (body : eval lookup fuel (name :: stack) cyclic (.expression expr) = some r)
    (marked : name ∈ r.cyclic) :
    eval lookup (fuel + 1) stack cyclic (.property name) =
      some { r with value := none, reads := name :: r.reads } := by
  simp [eval, fresh, bound, body, finish, marked]

def witnessExpr : Expr := .fallback "--ok" (.reference "--x")

def witness : CssSemantics.VariableBindings String where
  entries := [("--ok", .literal ["10px"]), ("--x", witnessExpr.legacy)]
  unique := by decide

theorem historical_witness_cyclic : witness.Cyclic "--x" := by
  apply witness.fallback_self_cycle (name := "--x") (target := "--ok")
    (expression := .reference "--x")
  · simp [witness, witnessExpr, Expr.legacy]
  · exact .named

theorem historical_witness_invalid : witness.computeWithBase (fun _ => none) "--x" = none :=
  witness.computeWithBase_cyclic (fun _ => none) "--x" historical_witness_cyclic

def currentLookup (name : String) : Option Expr :=
  if name = "--ok" then some (.literal ["10px"])
  else if name = "--x" then some witnessExpr else none

theorem current_witness_value :
    eval currentLookup 5 [] [] (.property "--x") =
      some ⟨some ["10px"], [], ["--x", "--ok"]⟩ := by
  decide +kernel

theorem historical_and_demand_disagree :
    witness.computeWithBase (fun _ => none) "--x" ≠
      ((eval currentLookup 5 [] [] (.property "--x")).getD ⟨none, [], []⟩).value := by
  rw [historical_witness_invalid, current_witness_value]
  decide

end DemandFallback
