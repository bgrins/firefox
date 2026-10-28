import Collector
namespace NumberContext.Examples

def literal : Expr := .leaf .number
def absolute : Expr := .leaf .absolute
def ratio : Expr := .variadic .product [.leaf .font, .unary .invert absolute]
def inverseRatio : Expr := .variadic .product [absolute, .unary .invert (.leaf .font)]
def rootRatio : Expr := .variadic .product [.leaf .rootLineHeight, .unary .invert absolute]
def unsupportedRatio : Expr := .variadic .product [absolute, .unary .invert (.leaf .viewport)]

inductive Mutation where
  | unknownEmpty | dropInverse | dropRight | dropThird | dropTail | dropRoot | dropLineHeight
  deriving DecidableEq

def mutateLeaf (m : Mutation) (k : Leaf) : Option Flags :=
  match leafSummary k with
  | none => if m == .unknownEmpty then some empty else none
  | some f =>
      if m == .dropRoot then some ⟨f.font, f.lineHeight, false, false⟩
      else if m == .dropLineHeight then some ⟨f.font, false, f.rootFont, false⟩
      else some f

mutual
 def mutate (m : Mutation) : Expr → Option Flags
  | .leaf k => mutateLeaf m k
  | .unary op e => if m == .dropInverse && op == .invert then some empty else mutate m e
  | .binary _ a b => if m == .dropRight then mutate m a else merge (mutate m a) (mutate m b)
  | .ternary _ a b c =>
      if m == .dropThird then merge (mutate m a) (mutate m b)
      else merge (mutate m a) (merge (mutate m b) (mutate m c))
  | .variadic _ es =>
      if m == .dropTail then match es with
        | [] => some empty
        | e :: _ => mutate m e
      else mutateList m es
  | .unsupported _ => if m == .unknownEmpty then some empty else none
 def mutateList (m : Mutation) : List Expr → Option Flags
  | [] => some empty
  | e :: es => merge (mutate m e) (mutateList m es)
end

example : summary ratio = some (singleton .font) := by decide +kernel
example : summary inverseRatio = some (singleton .font) := by decide +kernel
example : summary rootRatio = some (union (singleton .rootFont) (singleton .rootLineHeight)) := by decide +kernel
example : summary unsupportedRatio = none := by decide +kernel
example : summary (.binary .logBase literal ratio) = some (singleton .font) := by decide +kernel
example : summary (.ternary .clamp literal literal ratio) = some (singleton .font) := by decide +kernel
example : summary (.variadic .minMax [literal, ratio]) = some (singleton .font) := by decide +kernel
example : summary (.unary .log ratio) = some (singleton .font) := by decide +kernel
example : summary (.variadic .sum [ratio, rootRatio]) = some ⟨true, false, true, true⟩ := by decide +kernel
example : summary (.variadic .hypot [literal, unsupportedRatio, ratio]) = none := by decide +kernel
example : summary (.ternary .progress literal (.leaf .lineHeight) literal) = some ⟨true, true, false, false⟩ := by decide +kernel
example : summary (.binary .round ratio (.unsupported .random)) = none := by decide +kernel

end NumberContext.Examples
