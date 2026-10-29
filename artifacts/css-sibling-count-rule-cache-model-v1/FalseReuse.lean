import Witness
open ContextualEasing SiblingCountRuleCache
example : reuse countSteps [.ownFont, .parentFont]
    (leftTarget 16 16) (rightTarget 16 16) true =
      evaluate countSteps (rightTarget 16 16) := by decide
