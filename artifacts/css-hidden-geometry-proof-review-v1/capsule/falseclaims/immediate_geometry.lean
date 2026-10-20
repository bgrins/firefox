import Hidden
open Hidden
example : (measure true true fixedBlock (key 0) warm).frame.geometry = fixedBlock (key 0) := by decide
