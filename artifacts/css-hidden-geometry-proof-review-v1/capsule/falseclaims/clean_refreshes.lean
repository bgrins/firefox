import Hidden
open Hidden
example : (geometryQuery true fixedBlock {key 32 with computed := ⟨24, 50⟩} warm).geometry = ⟨24, 50⟩ := by decide
