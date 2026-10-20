import Hidden
open Hidden
example : (geometryQuery true fixedBlock (key 32) (measure false true fixedBlock (key 0) warm).frame).geometry = ⟨24, 32⟩ := by decide
