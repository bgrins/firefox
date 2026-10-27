import Contract
open FiniteModRemContract ModRemInfinity
example : adjust ((-17 : Int).tmod 3) 3 = 1 := by decide +kernel
example : adjust ((17 : Int).tmod (-3)) (-3) = -1 := by decide +kernel
example : candidate .mod (fun _ => 999) true false 0 3 = .zero false := by decide +kernel
example : candidate .rem (fun _ => 999) true false 0 3 = .zero true := by decide +kernel
example : candidateGrid .rem (fun _ => 999) 2 3 = 2 := by decide +kernel
example : candidate .mod (fun _ => 0) false true 1 (-3) = .zero true := by decide +kernel
example : candidateGrid .mod (fun _ => 33554432) (-1) 33554432 = 33554432 := by decide +kernel
example : NearestProjection 33554431 33554432 := endpoint_projection
