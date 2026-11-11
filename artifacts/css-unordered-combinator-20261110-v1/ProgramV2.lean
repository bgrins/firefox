import UnorderedLaws
import ProgramLaws

namespace CssUnordered
open CssGrammar

inductive Op where
  | legacy (op : CssGrammar.Op)
  | unordered (arity : Nat)
  deriving Repr, DecidableEq

def step : Op → List Grammar → Option (List Grammar)
  | .legacy op, stack => CssGrammar.execute [op] stack
  | .unordered arity, stack =>
    if arity ≤ stack.length then
      (lower ((stack.take arity).reverse)).map (fun grammar => grammar :: stack.drop arity)
    else none

def execute : List Op → List Grammar → Option (List Grammar)
  | [], stack => some stack
  | op :: code, stack => (step op stack).bind (execute code)

def decode (code : List Op) : Option Grammar :=
  match execute code [] with
  | some [grammar] => some grammar
  | _ => none

theorem unordered_step (children stack : List Grammar) :
    step (.unordered children.length) (children.reverse ++ stack) =
      (lower children).map (fun grammar => grammar :: stack) := by
  simp [step]

theorem unordered_step_matching (children stack : List Grammar) (input rest : List String) :
    (∃ grammar, step (.unordered children.length) (children.reverse ++ stack) = some (grammar :: stack) ∧
      CssGrammar.Matches grammar input rest) ↔
    Admissible children ∧ UnorderedMatches children input rest := by
  rw [unordered_step]
  have result := lowering_spec children input rest
  cases h : lower children <;> simpa [h] using result

theorem execute_append (first second : List Op) (stack : List Grammar) :
    execute (first ++ second) stack = (execute first stack).bind (execute second) := by
  induction first generalizing stack with
  | nil => rfl
  | cons op first ih =>
    simp only [List.cons_append, execute]
    cases step op stack <;> simp [ih]

theorem rejected_prefix (first second : List Op) (stack : List Grammar)
    (rejected : execute first stack = none) : execute (first ++ second) stack = none := by
  simp [execute_append, rejected]

theorem legacy_step (op : CssGrammar.Op) (code : List CssGrammar.Op) (stack : List Grammar) :
    CssGrammar.execute (op :: code) stack =
      (CssGrammar.execute [op] stack).bind (CssGrammar.execute code) := by
  cases op <;> cases stack with
  | nil => rfl
  | cons head tail => cases tail <;> rfl

theorem legacy_execute (code : List CssGrammar.Op) (stack : List Grammar) :
    execute (code.map Op.legacy) stack = CssGrammar.execute code stack := by
  induction code generalizing stack with
  | nil => rfl
  | cons op code ih =>
    rw [List.map_cons, execute, step]
    conv => rhs; rw [legacy_step]
    cases CssGrammar.execute [op] stack <;> simp [ih]

theorem legacy_decode (code : List CssGrammar.Op) :
    decode (code.map Op.legacy) = CssGrammar.decode code := by
  unfold decode CssGrammar.decode
  rw [legacy_execute]
  cases CssGrammar.execute code [] with
  | none => rfl
  | some stack => cases stack with
    | nil => rfl
    | cons head tail => cases tail <;> rfl

theorem legacy_encode (grammar : Grammar) :
    decode ((CssGrammar.encode grammar).map Op.legacy) = some grammar := by
  rw [legacy_decode, decode_encode]

end CssUnordered
