import Dependency

namespace SiblingCountRuleCache
open ContextualEasing

def leftTarget (font parentFont : Nat) : Context
  | .ownFont => font
  | .parentFont => parentFont
  | .siblingIndex => 1
  | .siblingCount => 2

def rightTarget (font parentFont : Nat) : Context
  | .ownFont => font
  | .parentFont => parentFont
  | .siblingIndex => 3
  | .siblingCount => 3

theorem equal_font_key_stale_count (font parentFont : Nat) :
    key [.ownFont, .parentFont] (leftTarget font parentFont) =
      key [.ownFont, .parentFont] (rightTarget font parentFont) ∧
    evaluate countSteps (leftTarget font parentFont) = [2] ∧
    evaluate countSteps (rightTarget font parentFont) = [3] ∧
    reuse countSteps [.ownFont, .parentFont]
      (leftTarget font parentFont) (rightTarget font parentFont) true = [2] := by
  constructor
  · funext f; cases f <;> rfl
  · exact ⟨rfl, rfl, rfl⟩

end SiblingCountRuleCache
