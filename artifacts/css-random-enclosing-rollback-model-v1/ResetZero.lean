import Enclosing
open RandomIndex RandomIndex.Enclosing
example : retry true ⟨0, 5⟩ [1, 1] 1 = select true ⟨0, 0⟩ [⟨1, true⟩] := by decide
