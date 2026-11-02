import Std

namespace CssSemantics

inductive VariableExpr (Token : Type) where
  | literal (tokens : List Token)
  | append (left right : VariableExpr Token)
  | reference (name : String)
  | fallback (name : String) (expression : VariableExpr Token)
  deriving DecidableEq, Repr

namespace VariableExpr

inductive References : VariableExpr Token → String → Prop where
  | named : References (.reference name) name
  | fallbackNamed : References (.fallback name expression) name
  | fallback : References expression name → References (.fallback target expression) name
  | left : References left name → References (.append left right) name
  | right : References right name → References (.append left right) name

def references : VariableExpr Token → List String
  | .literal _ => []
  | .append left right => left.references ++ right.references
  | .reference name => [name]
  | .fallback name expression => name :: expression.references

theorem references_iff (expression : VariableExpr Token) (name : String) :
    name ∈ expression.references ↔ expression.References name := by
  induction expression with
  | literal tokens => constructor <;> intro h <;> cases h
  | append left right ihLeft ihRight =>
    simp only [references, List.mem_append, ihLeft, ihRight]
    constructor
    · intro h
      rcases h with h | h
      · exact .left h
      · exact .right h
    · intro h
      cases h with
      | left h => exact Or.inl h
      | right h => exact Or.inr h
  | reference target =>
    simp only [references, List.mem_singleton]
    constructor
    · rintro rfl; exact .named
    · intro h; cases h; rfl
  | fallback target expression ih =>
    simp only [references, List.mem_cons, ih]
    constructor
    · rintro (rfl | h)
      · exact .fallbackNamed
      · exact .fallback h
    · intro h
      cases h with
      | fallbackNamed => exact Or.inl rfl
      | fallback h => exact Or.inr h

def substitute (environment : String → Option (List Token)) : VariableExpr Token → Option (List Token)
  | .literal tokens => some tokens
  | .append left right => do
      let leftTokens ← left.substitute environment
      let rightTokens ← right.substitute environment
      pure (leftTokens ++ rightTokens)
  | .reference name => environment name
  | .fallback name expression =>
      match environment name with
      | some tokens => some tokens
      | none => expression.substitute environment

inductive Substitutes (environment : String → Option (List Token)) :
    VariableExpr Token → Option (List Token) → Prop where
  | literal : Substitutes environment (.literal tokens) (some tokens)
  | append : Substitutes environment left (some leftTokens) →
      Substitutes environment right (some rightTokens) →
      Substitutes environment (.append left right) (some (leftTokens ++ rightTokens))
  | appendLeftInvalid : Substitutes environment left none →
      Substitutes environment (.append left right) none
  | appendRightInvalid : Substitutes environment right none →
      Substitutes environment (.append left right) none
  | reference : environment name = some tokens →
      Substitutes environment (.reference name) (some tokens)
  | fallbackValue : environment name = some tokens →
      Substitutes environment (.fallback name expression) (some tokens)
  | missing : environment name = none → Substitutes environment (.reference name) none
  | fallback : environment name = none → Substitutes environment expression result →
      Substitutes environment (.fallback name expression) result

theorem Substitutes.result {value : Option (List Token)}
    (h : Substitutes environment expression value) :
    expression.substitute environment = value := by
  induction h with
  | literal => rfl
  | append _ _ left right => simp [substitute, left, right]
  | appendLeftInvalid _ ih => simp [substitute, ih]
  | appendRightInvalid _ ih =>
    simp only [substitute, ih]
    cases substitute environment _ <;> rfl
  | reference h => simp [substitute, h]
  | fallbackValue h => simp [substitute, h]
  | missing h => simp [substitute, h]
  | fallback h _ ih => simp [substitute, h, ih]

theorem substitute_spec (expression : VariableExpr Token)
    (environment : String → Option (List Token)) :
    Substitutes environment expression (expression.substitute environment) := by
  induction expression with
  | literal tokens => exact .literal
  | append left right ihLeft ihRight =>
    cases hl : left.substitute environment with
    | none => simpa [substitute, hl] using Substitutes.appendLeftInvalid (hl ▸ ihLeft)
    | some leftTokens =>
      cases hr : right.substitute environment with
      | none => simpa [substitute, hl, hr] using Substitutes.appendRightInvalid (hr ▸ ihRight)
      | some rightTokens =>
        simpa [substitute, hl, hr] using Substitutes.append (hl ▸ ihLeft) (hr ▸ ihRight)
  | reference name =>
    cases h : environment name with
    | some tokens => simpa [substitute, h] using Substitutes.reference h
    | none => simpa [substitute, h] using Substitutes.missing h
  | fallback name expression ih =>
    cases h : environment name with
    | some tokens => simpa [substitute, h] using Substitutes.fallbackValue (expression := expression) h
    | none => simpa [substitute, h] using Substitutes.fallback h ih

theorem substitute_iff (expression : VariableExpr Token)
    (environment : String → Option (List Token)) (result : Option (List Token)) :
    expression.substitute environment = result ↔ Substitutes environment expression result := by
  constructor
  · rintro rfl; exact substitute_spec expression environment
  · exact Substitutes.result

theorem Substitutes.unique (left : Substitutes environment expression a)
    (right : Substitutes environment expression b) : a = b :=
  left.result.symm.trans right.result

theorem substitute_congr (expression : VariableExpr Token)
    (left right : String → Option (List Token))
    (agree : ∀ name, expression.References name → left name = right name) :
    expression.substitute left = expression.substitute right := by
  induction expression with
  | literal tokens => rfl
  | append first second ihFirst ihSecond =>
    simp only [substitute, ihFirst (fun name h => agree name (.left h)),
      ihSecond (fun name h => agree name (.right h))]
  | reference name => exact agree name .named
  | fallback name expression ih =>
    simp only [substitute, agree name .fallbackNamed]
    cases right name with
    | some tokens => rfl
    | none => exact ih (fun name h => agree name (.fallback h))

theorem substitute_fallback_value (environment : String → Option (List Token))
    (h : environment name = some tokens) (expression : VariableExpr Token) :
    (fallback name expression).substitute environment = some tokens := by
  simp [substitute, h]

theorem empty_literal_valid (environment : String → Option (List Token)) :
    (literal []).substitute environment ≠ none := by
  simp [substitute]

end VariableExpr
end CssSemantics
