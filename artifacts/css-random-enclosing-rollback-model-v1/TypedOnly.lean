import Enclosing
open RandomIndex RandomIndex.Enclosing
example : retry false ⟨0, 5⟩ [1] 1 = retry true ⟨0, 5⟩ [1] 1 := by decide
