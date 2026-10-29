import Dependency
open ContextualEasing
example : evaluate [.read .siblingIndex] before =
    evaluate [.add (.literal 1) (.read .siblingIndex)] before := by decide
