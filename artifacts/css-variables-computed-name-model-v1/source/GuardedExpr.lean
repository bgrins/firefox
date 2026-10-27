import CssSemantics.Variables

namespace CssSemantics
namespace GuardedExpr

def combine (left right : Option (List Token)) : Option (List Token) := do
  let first ← left
  let second ← right
  pure (first ++ second)

def evaluate (resolve : State → String → Option (List Token) × State)
    (state : State) : VariableExpr Token → Option (List Token) × State
  | .literal tokens => (some tokens, state)
  | .append left right =>
      let first := evaluate resolve state left
      let second := evaluate resolve first.2 right
      (combine first.1 second.1, second.2)
  | .reference name => resolve state name
  | .fallback name expression =>
      let result := resolve state name
      match result.1 with
      | some tokens => (some tokens, result.2)
      | none => evaluate resolve result.2 expression

inductive Evaluates (Resolve : State → String → Option (List Token) → State → Prop) :
    State → VariableExpr Token → Option (List Token) → State → Prop where
  | literal : Evaluates Resolve state (.literal tokens) (some tokens) state
  | append : Evaluates Resolve start left first middle →
      Evaluates Resolve middle right second finish →
      Evaluates Resolve start (.append left right) (combine first second) finish
  | reference : Resolve start name value finish →
      Evaluates Resolve start (.reference name) value finish
  | fallbackValue : Resolve start name (some tokens) finish →
      Evaluates Resolve start (.fallback name expression) (some tokens) finish
  | fallback : Resolve start name none middle →
      Evaluates Resolve middle expression value finish →
      Evaluates Resolve start (.fallback name expression) value finish

variable {State Token : Type}
variable {resolve : State → String → Option (List Token) × State}
variable {Resolve : State → String → Option (List Token) → State → Prop}

theorem Evaluates.result
    (correspondence : ∀ state name value finish,
      Resolve state name value finish → resolve state name = (value, finish))
    (h : Evaluates Resolve start expression value finish) :
    evaluate resolve start expression = (value, finish) := by
  induction h with
  | literal => rfl
  | append _ _ first second => simp [evaluate, first, second]
  | reference h => exact correspondence _ _ _ _ h
  | fallbackValue h => simp [evaluate, correspondence _ _ _ _ h]
  | fallback h _ ih => simp [evaluate, correspondence _ _ _ _ h, ih]

theorem evaluate_spec
    (correspondence : ∀ state name,
      Resolve state name (resolve state name).1 (resolve state name).2)
    (expression : VariableExpr Token) (state : State) :
    Evaluates Resolve state expression (evaluate resolve state expression).1
      (evaluate resolve state expression).2 := by
  induction expression generalizing state with
  | literal tokens => exact .literal
  | append left right ihLeft ihRight => exact .append (ihLeft state) (ihRight _)
  | reference name => exact .reference (correspondence state name)
  | fallback name expression ih =>
    cases h : resolve state name with
    | mk value finish =>
      have hr := correspondence state name
      rw [h] at hr
      cases value with
      | some tokens => simpa [evaluate, h] using Evaluates.fallbackValue (expression := expression) hr
      | none => simpa [evaluate, h] using Evaluates.fallback hr (ih finish)

theorem evaluate_iff
    (correspondence : ∀ state name value finish,
      resolve state name = (value, finish) ↔ Resolve state name value finish)
    (expression : VariableExpr Token) (state : State) (value : Option (List Token))
    (finish : State) :
    evaluate resolve state expression = (value, finish) ↔
      Evaluates Resolve state expression value finish := by
  constructor
  · intro h
    have result := evaluate_spec (resolve := resolve) (Resolve := Resolve)
      (fun state name => (correspondence state name _ _).mp rfl) expression state
    simpa [h] using result
  · exact Evaluates.result (fun state name value finish =>
      (correspondence state name value finish).mpr)

theorem Evaluates.unique
    (correspondence : ∀ state name value finish,
      Resolve state name value finish → resolve state name = (value, finish))
    (left : Evaluates Resolve start expression a first)
    (right : Evaluates Resolve start expression b second) :
    (a, first) = (b, second) :=
  (left.result correspondence).symm.trans (right.result correspondence)

theorem evaluate_preserves (invariant : State → Prop)
    (preserves : ∀ state name, invariant state → invariant (resolve state name).2)
    (expression : VariableExpr Token) (state : State) (h : invariant state) :
    invariant (evaluate resolve state expression).2 := by
  induction expression generalizing state with
  | literal tokens => exact h
  | append left right ihLeft ihRight => exact ihRight _ (ihLeft state h)
  | reference name => exact preserves state name h
  | fallback name expression ih =>
    have preserved := preserves state name h
    cases hr : resolve state name with
    | mk value finish =>
      rw [hr] at preserved
      cases value with
      | none => simpa [evaluate, hr] using ih finish preserved
      | some tokens => simpa [evaluate, hr] using preserved

theorem append_after_failure
    (leftResult : evaluate resolve state left = (none, middle)) :
    evaluate resolve state (.append left right) =
      (none, (evaluate resolve middle right).2) := by
  simp [evaluate, leftResult, combine]

theorem evaluate_pure (environment : String → Option (List Token))
    (state : State) (expression : VariableExpr Token) :
    evaluate (fun current name => (environment name, current)) state expression =
      (expression.substitute environment, state) := by
  induction expression generalizing state with
  | literal tokens => rfl
  | append left right ihLeft ihRight =>
    simp only [evaluate, ihLeft, ihRight, VariableExpr.substitute, combine]
  | reference name => rfl
  | fallback name expression ih =>
    simp only [evaluate, VariableExpr.substitute]
    cases environment name with
    | some tokens => rfl
    | none => exact ih state

end GuardedExpr
end CssSemantics
