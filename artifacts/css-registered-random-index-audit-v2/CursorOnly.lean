import Rollback
open RandomIndex
example : select false ⟨0, 0⟩ [⟨1, false⟩, ⟨1, true⟩] = select true ⟨0, 0⟩ [⟨1, false⟩, ⟨1, true⟩] := by decide
